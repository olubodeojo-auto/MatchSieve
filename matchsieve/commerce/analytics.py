from __future__ import annotations
import json, sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

class CommerceStore:
    """Event ledger and credit balance. Purchase grants require a verified server webhook."""
    ALLOWED_EVENTS = {"report_view","cta_click","checkout_start","purchase_completed","report_repeat_purchase","purchase_failed","credit_spent"}

    def __init__(self, db_path: str | Path = "data/matchsieve_commerce.sqlite3"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.executescript("""
            CREATE TABLE IF NOT EXISTS commerce_events(
              id INTEGER PRIMARY KEY AUTOINCREMENT,event_name TEXT NOT NULL,user_id TEXT,anonymous_id TEXT,
              report_id TEXT,country_code TEXT,currency TEXT,experiment_id TEXT,amount_minor INTEGER,
              product_code TEXT,payment_reference TEXT,occurred_at TEXT NOT NULL,properties_json TEXT NOT NULL DEFAULT '{}');
            CREATE INDEX IF NOT EXISTS idx_commerce_events_name_time ON commerce_events(event_name,occurred_at);
            CREATE INDEX IF NOT EXISTS idx_commerce_events_user ON commerce_events(user_id,anonymous_id,occurred_at);
            CREATE TABLE IF NOT EXISTS credit_balances(user_id TEXT PRIMARY KEY,credits INTEGER NOT NULL DEFAULT 0 CHECK(credits>=0),updated_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS processed_payments(payment_reference TEXT PRIMARY KEY,user_id TEXT NOT NULL,product_code TEXT NOT NULL,credits_granted INTEGER NOT NULL,processed_at TEXT NOT NULL);
            """)

    def _connect(self):
        conn = sqlite3.connect(self.db_path, timeout=15)
        conn.row_factory = sqlite3.Row
        return conn

    def track(self,event_name:str,*,user_id:str|None=None,anonymous_id:str|None=None,report_id:str|None=None,
              country_code:str|None=None,currency:str|None=None,experiment_id:str|None=None,amount_minor:int|None=None,
              product_code:str|None=None,payment_reference:str|None=None,properties:dict[str,Any]|None=None)->int:
        if event_name not in self.ALLOWED_EVENTS: raise ValueError(f"Unsupported commerce event: {event_name}")
        safe = dict(properties or {})
        for key in ("card_number","cvv","password","access_token","service_role_key","ip_address"): safe.pop(key,None)
        with self._connect() as conn:
            cur=conn.execute("""INSERT INTO commerce_events(event_name,user_id,anonymous_id,report_id,country_code,currency,
                experiment_id,amount_minor,product_code,payment_reference,occurred_at,properties_json)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",(event_name,user_id,anonymous_id,report_id,country_code,currency,
                experiment_id,amount_minor,product_code,payment_reference,_now(),json.dumps(safe,ensure_ascii=False,default=str)))
            return int(cur.lastrowid)

    def record_verified_purchase(self,*,payment_reference:str,user_id:str,product_code:str,credits:int,
              amount_minor:int,country_code:str,currency:str,experiment_id:str|None=None)->bool:
        """Only call after verifying the provider's signed webhook on the server.
        This method is idempotent, but it does not itself verify payment authenticity.
        """
        if not payment_reference or not user_id or not product_code: raise ValueError("Payment reference, user and product are required.")
        if credits<1 or amount_minor<0: raise ValueError("Credits must be positive and amount cannot be negative.")
        with self._connect() as conn:
            if conn.execute("SELECT 1 FROM processed_payments WHERE payment_reference=?",(payment_reference,)).fetchone(): return False
            conn.execute("INSERT INTO processed_payments VALUES(?,?,?,?,?)",(payment_reference,user_id,product_code,credits,_now()))
            conn.execute("""INSERT INTO credit_balances(user_id,credits,updated_at) VALUES(?,?,?)
              ON CONFLICT(user_id) DO UPDATE SET credits=credits+excluded.credits,updated_at=excluded.updated_at""",(user_id,credits,_now()))
            conn.execute("""INSERT INTO commerce_events(event_name,user_id,country_code,currency,experiment_id,amount_minor,
              product_code,payment_reference,occurred_at,properties_json) VALUES('purchase_completed',?,?,?,?,?,?,?,?, '{}')""",
              (user_id,country_code,currency,experiment_id,amount_minor,product_code,payment_reference,_now()))
            prior=conn.execute("SELECT COUNT(*) FROM commerce_events WHERE user_id=? AND event_name='purchase_completed' AND payment_reference<>?",(user_id,payment_reference)).fetchone()[0]
            if prior:
                conn.execute("""INSERT INTO commerce_events(event_name,user_id,country_code,currency,experiment_id,amount_minor,
                  product_code,payment_reference,occurred_at,properties_json) VALUES('report_repeat_purchase',?,?,?,?,?,?,?,?, '{}')""",
                  (user_id,country_code,currency,experiment_id,amount_minor,product_code,payment_reference,_now()))
            return True

    def spend_credit(self,user_id:str,report_id:str|None=None)->bool:
        with self._connect() as conn:
            row=conn.execute("SELECT credits FROM credit_balances WHERE user_id=?",(user_id,)).fetchone()
            if not row or row["credits"]<1: return False
            conn.execute("UPDATE credit_balances SET credits=credits-1,updated_at=? WHERE user_id=?",(_now(),user_id))
            conn.execute("INSERT INTO commerce_events(event_name,user_id,report_id,occurred_at,properties_json) VALUES('credit_spent',?,?,?,'{}')",(user_id,report_id,_now()))
            return True

    def balance(self,user_id:str)->int:
        with self._connect() as conn:
            row=conn.execute("SELECT credits FROM credit_balances WHERE user_id=?",(user_id,)).fetchone()
            return int(row["credits"]) if row else 0

    def funnel_summary(self,*,country_code:str|None=None,experiment_id:str|None=None)->dict[str,Any]:
        clauses,params=[],[]
        if country_code: clauses.append("country_code=?"); params.append(country_code.upper())
        if experiment_id: clauses.append("experiment_id=?"); params.append(experiment_id)
        where=(" WHERE "+" AND ".join(clauses)) if clauses else ""
        with self._connect() as conn:
            rows=conn.execute(f"SELECT event_name,COUNT(*) events,COUNT(DISTINCT COALESCE(user_id,anonymous_id)) people FROM commerce_events{where} GROUP BY event_name",params).fetchall()
        return {r["event_name"]:{"events":r["events"],"people":r["people"]} for r in rows}
