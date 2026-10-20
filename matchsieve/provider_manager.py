from __future__ import annotations
from typing import Any
from .config import ENABLED_PROVIDERS
from .providers.catalog import list_providers
from .providers.sportscore import SportScoreProvider
from .providers.openligadb import OpenLigaDBProvider
from .providers.football_data_org import FootballDataOrgProvider
from .repository import Repository
from .normalise import utc_now
from .db import connect

class ProviderManager:
    """Explicit execution only: never silently fan out to every configured source."""
    def __init__(self, repo: Repository | None=None): self.repo=repo or Repository()

    def catalog(self) -> list[dict[str,Any]]:
        configured=set(ENABLED_PROVIDERS)
        return [{**p,"enabled":p['key'] in configured} for p in list_providers()]

    def fetch(self, provider: str, **kwargs: Any) -> dict[str,Any]:
        started=utc_now(); records=[]; status='failed'; message=''; source_key=provider.lower()
        adapters={"sportscore":SportScoreProvider(),"openligadb":OpenLigaDBProvider(),"football_data_org":FootballDataOrgProvider()}
        conn=connect(self.repo.db_path)
        run_id=None
        try:
            cur=conn.execute("INSERT INTO provider_runs(provider_key,started_at,status,metadata_json) VALUES(?,?,?,?)",(source_key,started,'running','{}'))
            run_id=int(cur.lastrowid); conn.commit()
        finally: conn.close()
        try:
            if source_key not in ENABLED_PROVIDERS:
                raise RuntimeError(f"Provider '{source_key}' is not enabled. Add it to MATCHSIEVE_ENABLED_PROVIDERS in .env deliberately after reviewing cost and coverage.")
            if source_key not in adapters:
                raise RuntimeError(f"'{source_key}' is catalogued but has no verified adapter in this build; see docs/PROVIDERS.md.")
            if source_key=='sportscore': rows=adapters[source_key].fetch_fixtures(**kwargs)
            elif source_key=='openligadb': rows=adapters[source_key].fetch_fixtures(**kwargs)
            else: rows=adapters[source_key].fetch_fixtures(**kwargs)
            for row in rows:
                ref=row.get('source_ref') or f"provider:{source_key}"
                self.repo.add_fixture(row,source_key=source_key,source_ref=ref,source_url=row.get('source_url'),raw_payload=row.get('provider_payload',row))
                records.append(row)
            status='success'; message=f"Fetched {len(records)} record(s). Review the stored source snapshots and fixture coverage."
            try:
                from .kb_writer import refresh_indexes
                kb_index = refresh_indexes(self.repo)
            except Exception as exc:
                kb_index = {"warning": str(exc)}
            return {"provider":source_key,"status":status,"records_received":len(records),"message":message,"knowledge_base":kb_index}
        except Exception as exc:
            message=str(exc)
            return {"provider":source_key,"status":"failed","records_received":len(records),"message":message}
        finally:
            conn=connect(self.repo.db_path)
            try:
                conn.execute("UPDATE provider_runs SET finished_at=?,status=?,records_received=?,message=? WHERE id=?",(utc_now(),status,len(records),message,run_id))
                conn.commit()
            finally: conn.close()
