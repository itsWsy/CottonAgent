import json
from pathlib import Path


class KnowledgeService:
    def __init__(self, path: Path | None = None):
        self.path = path or Path(__file__).resolve().parents[1] / "data" / "cotton_knowledge.json"
        self.items = json.loads(self.path.read_text(encoding="utf-8"))

    def search(self, growth_stage: str, symptoms: list[str], weather_tags: list[str], description: str) -> list[dict]:
        scored = []
        description = description or ""
        for item in self.items:
            score = 0
            reasons = []
            for symptom in symptoms:
                if symptom in item.get("symptoms", []):
                    score += 3
                    reasons.append(f"症状匹配：{symptom}")
            if growth_stage in item.get("growthStages", []):
                score += 2
                reasons.append(f"生育阶段匹配：{growth_stage}")
            for tag in weather_tags:
                if tag in item.get("weatherTags", []):
                    score += 1
                    reasons.append(f"天气标签匹配：{tag}")
            keywords = [item.get("title", ""), *item.get("keywords", [])]
            if any(word and word in description for word in keywords):
                score += 1
                reasons.append("问题描述命中关键词")
            if score > 0:
                enriched = {**item, "matchScore": score, "matchReasons": reasons}
                scored.append(enriched)
        return sorted(scored, key=lambda x: (-x["matchScore"], x["id"]))[:3]
