from __future__ import annotations

import hashlib
import json
import os
import tempfile
import time
from pathlib import Path
from typing import Any

from .config import ENABLED_PROVIDERS
from .db import connect
from .kb_writer import refresh_indexes
from .normalise import utc_now
from .providers.api_football import ApiFootballProvider
from .providers.additional_sources import FootballDataIOProvider, LiveFootballProvider, SportMonksProvider
from .providers.base import FixtureProvider, ProviderError
from .providers.catalog import list_providers
from .providers.football_data_org import FootballDataOrgProvider
from .providers.openligadb import OpenLigaDBProvider
from .providers.sportscore import SportScoreProvider
from .providers.thesportsdb import TheSportsDBProvider
from .repository import Repository


class ProviderManager:
    """Fetch only the source explicitly named by the caller and archive provenance."""

    def __init__(self, repo: Repository | None = None):
        self.repo = repo or Repository()

    @property
    def adapter_classes(self) -> dict[str, type[FixtureProvider]]:
        return {
            "api_football": ApiFootballProvider,
            "sportmonks": SportMonksProvider,
            "footballdata_io": FootballDataIOProvider,
            "livefootball": LiveFootballProvider,
            "thesportsdb": TheSportsDBProvider,
            "sportscore": SportScoreProvider,
            "openligadb": OpenLigaDBProvider,
            "football_data_org": FootballDataOrgProvider,
        }

    def catalog(self) -> list[dict[str, Any]]:
        configured = set(ENABLED_PROVIDERS)
        return [{**provider, "enabled": provider["key"] in configured} for provider in list_providers()]

    def _cache_path(self, source_key: str, kwargs: dict[str, Any]) -> Path:
        cache_key = json.dumps(
            {"provider": source_key, "arguments": kwargs},
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        )
        digest = hashlib.sha256(cache_key.encode("utf-8")).hexdigest()
        return self.repo.db_path.parent / "cache" / "provider-fetch" / f"{digest}.json"

    def _load_cached_records(self, path: Any) -> list[dict[str, Any]] | None:
        if not path.exists():
            return None
        try:
            cached = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ProviderError(f"Could not read provider cache {path.name}: {exc}") from exc
        if not isinstance(cached, dict) or not isinstance(cached.get("records"), list):
            raise ProviderError(f"Provider cache {path.name} has an invalid format.")
        if not isinstance(cached.get("expires_at"), (int, float)):
            raise ProviderError(f"Provider cache {path.name} has no valid expiry.")
        if cached["expires_at"] <= time.time():
            return None
        if any(not isinstance(row, dict) for row in cached["records"]):
            raise ProviderError(f"Provider cache {path.name} contains an invalid record.")
        return cached["records"]

    def _store_cached_records(self, path: Any, records: list[dict[str, Any]], ttl_seconds: int) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(
            {
                "cached_at": utc_now(),
                "expires_at": time.time() + ttl_seconds,
                "records": records,
            },
            ensure_ascii=False,
            sort_keys=True,
            default=str,
        )
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=path.parent,
                prefix=f"{path.stem}.",
                suffix=".tmp",
                delete=False,
            ) as cache_file:
                temp_path = cache_file.name
                cache_file.write(payload)
            os.replace(temp_path, path)
        finally:
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)

    def fetch(self, provider: str, **kwargs: Any) -> dict[str, Any]:
        source_key = provider.strip().lower()
        force_refresh = bool(kwargs.pop("force_refresh", False))
        cache_ttl_seconds = kwargs.pop("cache_ttl_seconds", 900)
        started = utc_now()
        conn = connect(self.repo.db_path)
        try:
            cur = conn.execute(
                "INSERT INTO provider_runs(provider_key,started_at,status,metadata_json) VALUES(?,?,?,?)",
                (source_key, started, "running", "{}"),
            )
            run_id = int(cur.lastrowid)
            conn.commit()
        finally:
            conn.close()

        records: list[dict[str, Any]] = []
        status = "failed"
        message = ""
        try:
            provider_config = next((row for row in self.catalog() if row["key"] == source_key), None)
            if provider_config is None:
                message = f"No adapter is registered for provider '{source_key}'."
                return {
                    "provider": source_key,
                    "status": "failed",
                    "records_received": 0,
                    "message": message,
                }
            if not provider_config["enabled"]:
                message = f"Provider '{source_key}' is not enabled."
                return {
                    "provider": source_key,
                    "status": "failed",
                    "records_received": 0,
                    "message": message,
                }

            adapter_class = self.adapter_classes.get(source_key)
            if adapter_class is None:
                raise ProviderError(f"No current live adapter is registered for '{source_key}'.")
            try:
                cache_ttl_seconds = int(cache_ttl_seconds)
            except (TypeError, ValueError) as exc:
                raise ValueError("cache_ttl_seconds must be an integer from 0 to 604800") from exc
            if not 0 <= cache_ttl_seconds <= 604800:
                raise ValueError("cache_ttl_seconds must be an integer from 0 to 604800")

            cache_path = self._cache_path(source_key, kwargs)
            cache_hit = False
            rows = None
            if cache_ttl_seconds and not force_refresh:
                rows = self._load_cached_records(cache_path)
                cache_hit = rows is not None
            if rows is None:
                adapter = adapter_class()
                rows = adapter.fetch_fixtures(**kwargs)
            for row in rows:
                source_ref = str(row.get("external_id") or f"provider:{source_key}")
                self.repo.add_fixture(
                    row,
                    source_key=source_key,
                    source_ref=source_ref,
                    source_url=row.get("source_url"),
                    raw_payload=row.get("provider_payload", row),
                )
                records.append(row)
            status = "success" if records else "empty"
            if records:
                message = f"Received {len(records)} fixture record(s) from {source_key}; records were archived with source provenance."
            else:
                message = f"{source_key} returned no usable fixture records for the requested date or range; this is not counted as a successful intake."
            cache_warning = None
            if cache_ttl_seconds and not cache_hit:
                try:
                    self._store_cached_records(cache_path, rows, cache_ttl_seconds)
                except OSError as exc:
                    cache_warning = f"Provider results were archived, but the local cache could not be written: {exc}"
            if cache_hit:
                message = f"Local cache hit. {message}"
            try:
                kb_index = refresh_indexes(self.repo)
            except Exception as exc:
                kb_index = {"warning": type(exc).__name__}
            result = {
                "provider": source_key,
                "status": status,
                "records_received": len(records),
                "message": message,
                "knowledge_base": kb_index,
                "cache_hit": cache_hit,
            }
            if cache_warning:
                result["cache_warning"] = cache_warning
            return result
        except Exception as exc:
            message = str(exc)
            return {"provider": source_key, "status": "failed", "records_received": len(records), "message": message}
        finally:
            conn = connect(self.repo.db_path)
            try:
                conn.execute(
                    "UPDATE provider_runs SET finished_at=?,status=?,records_received=?,message=? WHERE id=?",
                    (utc_now(), status, len(records), message, run_id),
                )
                conn.commit()
            finally:
                conn.close()
