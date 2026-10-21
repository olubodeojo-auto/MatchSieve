from __future__ import annotations

import os
from typing import Any

from .config import ENABLED_PROVIDERS
from .db import connect
from .kb_writer import refresh_indexes
from .normalise import utc_now
from .providers.api_football import ApiFootballProvider
from .providers.additional_sources import FootballDataIOProvider, LiveFootballProvider, SportMonksProvider
from .providers.base import ProviderError
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

    def catalog(self) -> list[dict[str, Any]]:
        configured = set(ENABLED_PROVIDERS)
        rows = []
        for provider in list_providers():
            key = provider["key"]
            env_key = provider.get("env_key")
            has_credential = not env_key or bool(os.getenv(env_key, "").strip())
            rows.append({**provider, "enabled": key in configured or has_credential})
        return rows

    def fetch(self, provider: str, **kwargs: Any) -> dict[str, Any]:
        source_key = provider.strip().lower()
        adapters = {
            "api_football": ApiFootballProvider(),
            "sportmonks": SportMonksProvider(),
            "footballdata_io": FootballDataIOProvider(),
            "livefootball": LiveFootballProvider(),
            "thesportsdb": TheSportsDBProvider(),
            "sportscore": SportScoreProvider(),
            "openligadb": OpenLigaDBProvider(),
            "football_data_org": FootballDataOrgProvider(),
        }
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
            adapter = adapters.get(source_key)
            if adapter is None:
                raise ProviderError(f"No current live adapter is registered for '{source_key}'.")
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
            try:
                kb_index = refresh_indexes(self.repo)
            except Exception as exc:
                kb_index = {"warning": type(exc).__name__}
            return {
                "provider": source_key,
                "status": status,
                "records_received": len(records),
                "message": message,
                "knowledge_base": kb_index,
            }
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
