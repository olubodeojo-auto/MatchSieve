from __future__ import annotations
from datetime import datetime, timezone
from typing import Any

class DataQualityAgent:
    """Rates evidence fitness, not the market or the eventual recommendation."""
    name = "data_quality"
    REQUIRED = ("home_team","away_team","competition","kickoff")

    def assess(self, collection: dict[str, Any], max_age_hours: int = 72) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        assessments, conflicts, seen = [], [], {}
        for record in collection.get("records", []):
            facts = record.get("facts") or {}
            missing = [field for field in self.REQUIRED if not facts.get(field)]
            warnings = []
            if facts.get("home_team") and facts.get("away_team") and str(facts["home_team"]).strip().casefold() == str(facts["away_team"]).strip().casefold():
                warnings.append("Home and away team names are identical.")
            for key, value in facts.items():
                ref = str(facts.get("source_ref") or record.get("source_url") or "")
                ck = (ref, key)
                if ck in seen and seen[ck] != value:
                    conflicts.append({"source_ref":ref,"field":key,"values":[seen[ck],value]})
                else:
                    seen[ck] = value
            age = None
            try:
                stamp = datetime.fromisoformat(str(record.get("captured_at")).replace("Z","+00:00"))
                age = max(0, (now - stamp.astimezone(timezone.utc)).total_seconds()/3600)
                if age > max_age_hours:
                    warnings.append(f"Capture is {age:.1f} hours old.")
            except (ValueError, TypeError):
                warnings.append("Capture timestamp is unreadable.")
            score = max(0, 100 - 15*len(missing) - 20*len(warnings))
            label = "insufficient" if missing else ("review" if warnings or score < 80 else "usable")
            assessments.append({"record_id":record.get("record_id"),"source":record.get("source"),
                "source_url":record.get("source_url"),"missing_required_fields":missing,"warnings":warnings,
                "age_hours":age,"quality_score":score,"quality_label":label})
        counts = {label:sum(x["quality_label"] == label for x in assessments) for label in ("usable","review","insufficient")}
        return {"agent":self.name,"assessment_at":now.isoformat(),"records_assessed":len(assessments),
                **counts,"assessments":assessments,"conflicts":conflicts,
                "overall_status":"usable" if counts["usable"] and not conflicts else ("review" if assessments else "empty"),
                "authority":"evidence_fitness_only","rules":{"required_fields":list(self.REQUIRED),"max_age_hours":max_age_hours}}
