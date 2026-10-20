# Mobile API Contract

The initial proposed routes have been implemented locally in `matchsieve/webserver.py`. The authoritative and tested current contract is now `docs/API_CONTRACT.md`; the corresponding Android models are in `MatchSieve-Mobile/app/src/main/java/com/matchsieve/mobile/data/Models.kt`.

The contract version is `0.2`. Changes to JSON fields should update server serialization, Android models, contract documentation and test coverage together. The API remains local-development only because authentication and production controls are not implemented.
