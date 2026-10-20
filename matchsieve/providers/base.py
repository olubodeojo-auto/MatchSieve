from __future__ import annotations
from typing import Any, Protocol

class FixtureProvider(Protocol):
    key: str
    def fetch_fixtures(self, **kwargs: Any) -> list[dict[str, Any]]: ...

class ProviderError(RuntimeError): pass
