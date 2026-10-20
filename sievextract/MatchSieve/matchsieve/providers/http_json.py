from __future__ import annotations
import json, urllib.parse, urllib.request, urllib.error
from typing import Any
from ..config import REQUEST_TIMEOUT
from .base import ProviderError


def get_json(url: str, params: dict[str,Any] | None=None, headers: dict[str,str] | None=None, timeout: float | None=None) -> Any:
    if params:
        separator='&' if '?' in url else '?'
        url=url+separator+urllib.parse.urlencode({k:v for k,v in params.items() if v is not None})
    req=urllib.request.Request(url,headers={"Accept":"application/json","User-Agent":"MatchSieve/0.3.0 (football research client)",**(headers or {})})
    try:
        with urllib.request.urlopen(req,timeout=timeout or REQUEST_TIMEOUT) as resp:
            raw=resp.read()
            if resp.status<200 or resp.status>=300: raise ProviderError(f"HTTP {resp.status} from source")
            return json.loads(raw.decode('utf-8'))
    except urllib.error.HTTPError as exc:
        raise ProviderError(f"HTTP {exc.code} from configured source URL") from exc
    except urllib.error.URLError as exc:
        raise ProviderError(f"Network request failed: {exc.reason}") from exc
    except json.JSONDecodeError as exc:
        raise ProviderError("Source returned invalid JSON") from exc
