from __future__ import annotations
import json, urllib.request, urllib.error
from typing import Any
from .config import OLLAMA_BASE_URL, OLLAMA_MODEL, OLLAMA_TIMEOUT

class OllamaError(RuntimeError): pass

class OllamaClient:
    """Local-only Ollama client. It receives structured evidence, never provider secrets."""
    def __init__(self, base_url: str=OLLAMA_BASE_URL, model: str=OLLAMA_MODEL, timeout: float=OLLAMA_TIMEOUT):
        self.base_url=base_url.rstrip('/'); self.model=model; self.timeout=timeout

    def list_models(self) -> list[str]:
        req=urllib.request.Request(self.base_url+"/api/tags",headers={"Accept":"application/json"})
        try:
            with urllib.request.urlopen(req,timeout=self.timeout) as resp: payload=json.loads(resp.read().decode())
        except Exception as exc: raise OllamaError(f"Cannot reach Ollama at {self.base_url}: {exc}") from exc
        return [m.get('name','') for m in payload.get('models',[]) if m.get('name')]

    def write_commentary(self, evidence: dict[str,Any]) -> str:
        payload={k:evidence.get(k) for k in ("fixture","market","status","home_form","away_form","h2h","supporting_signals","counter_signals","missing_information","sources","method_note")}
        system=("You are the plain-English editor for MatchSieve research. Only summarise facts explicitly present in the JSON. "
                "Do not invent injury news, lineups, odds, probabilities, xG, sources, current events, player names, or causal claims. "
                "Never promise wins or profit. Explicitly mention missing context when relevant. Do not produce a betting instruction. "
                "Write 120-200 words in clear Nigerian-friendly English, presenting supportive and opposing signals fairly.")
        body=json.dumps({"model":self.model,"stream":False,"messages":[{"role":"system","content":system},{"role":"user","content":json.dumps(payload,ensure_ascii=False)}],"options":{"temperature":0.2}},ensure_ascii=False).encode()
        req=urllib.request.Request(self.base_url+"/api/chat",data=body,headers={"Content-Type":"application/json"},method="POST")
        try:
            with urllib.request.urlopen(req,timeout=self.timeout) as resp: result=json.loads(resp.read().decode())
        except urllib.error.URLError as exc: raise OllamaError(f"Local Ollama request failed: {exc}") from exc
        text=result.get('message',{}).get('content','').strip()
        return text[:6000] if text else ""
