import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

EXPECTED_DAY = {
    "PEST_SAMPLE": 1,
    "COUNT_DENSITY": 2,
    "FIELD_SCOUTING": 2,
    "RECHECK_LEAF": 4,
    "GROWTH_ASSESSMENT": 4,
    "UPDATE_RECORD": 7,
    "WEED_MONITOR": 2,
    "DRAINAGE_CHECK": 1,
    "BOLL_CHECK": 3,
}

ACTION_NAMES = {
    "PEST_SAMPLE": "增加虫情采样",
    "COUNT_DENSITY": "记录虫口密度",
    "FIELD_SCOUTING": "田间巡查",
    "RECHECK_LEAF": "复查叶片状态",
    "GROWTH_ASSESSMENT": "长势评估",
    "UPDATE_RECORD": "更新棉田记录并复盘",
    "WEED_MONITOR": "杂草监测",
    "DRAINAGE_CHECK": "雨后排水检查",
    "BOLL_CHECK": "棉铃发育检查",
}

WEIGHTS = {
    "transitionScore": 0.30,
    "knowledgeScore": 0.25,
    "growthStageScore": 0.20,
    "weatherSuitabilityScore": 0.10,
    "symptomUrgencyScore": 0.10,
    "recencyPenaltyScore": 0.05,
}


class RecommendationService:
    def __init__(self, path: Path | None = None, rules_path: Path | None = None):
        data_dir = Path(__file__).resolve().parents[1] / "data"
        self.path = path or data_dir / "farm_sequences.csv"
        self.rules_path = rules_path or data_dir / "recommendation_rules.json"
        self.rows = self._load_rows()
        self.rules = json.loads(self.rules_path.read_text(encoding="utf-8"))

    def _load_rows(self) -> list[dict]:
        with self.path.open("r", encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f))

    def recommend(
        self,
        history_records: list[dict],
        growth_stage: str,
        knowledge_items: list[dict],
        symptoms: list[str] | None = None,
        weather_tags: list[str] | None = None,
    ) -> list[dict]:
        symptoms = symptoms or []
        weather_tags = weather_tags or []
        stats = self._build_sequence_stats(growth_stage)
        transitions, previous_total = self._transition_stats(history_records)
        knowledge_scores, knowledge_hit_count = self._knowledge_stats(knowledge_items)
        candidates, candidate_sources = self._collect_candidates(transitions, stats, knowledge_scores, symptoms, weather_tags)

        results = []
        for code in candidates:
            if code in self.rules.get("excludedTopActions", []):
                continue
            scored = self._score_candidate(
                code=code,
                growth_stage=growth_stage,
                history_records=history_records,
                transitions=transitions,
                previous_total=previous_total,
                stage_counts=stats["stage_counts"],
                action_stages=stats["action_stages"],
                knowledge_scores=knowledge_scores,
                knowledge_hit_count=knowledge_hit_count,
                symptoms=symptoms,
                weather_tags=weather_tags,
                candidate_sources=sorted(candidate_sources[code]),
            )
            if scored["score"] > 0:
                results.append(scored)

        results = sorted(results, key=lambda x: (-x["score"], x["actionCode"]))
        return results[:3]

    def _build_sequence_stats(self, growth_stage: str) -> dict:
        stage_counts = Counter()
        action_stages = defaultdict(set)
        action_names = dict(ACTION_NAMES)
        for row in self.rows:
            code = row["action_code"]
            action_names[code] = row["action_name"]
            action_stages[code].add(row["growth_stage"])
            if row["growth_stage"] == growth_stage:
                stage_counts[code] += 1
        return {"stage_counts": stage_counts, "action_stages": action_stages, "action_names": action_names}

    def _transition_stats(self, history_records: list[dict]) -> tuple[Counter, int]:
        by_sequence = defaultdict(list)
        for row in self.rows:
            by_sequence[row["sequence_id"]].append(row)

        transitions = Counter()
        previous_total = 0
        last_action = history_records[-1]["actionCode"] if history_records else None
        if not last_action:
            return transitions, previous_total
        for sequence in by_sequence.values():
            ordered = sorted(sequence, key=lambda x: int(x["step"]))
            for prev, nxt in zip(ordered, ordered[1:]):
                if prev["action_code"] == last_action:
                    transitions[nxt["action_code"]] += 1
                    previous_total += 1
        return transitions, previous_total

    def _knowledge_stats(self, knowledge_items: list[dict]) -> tuple[dict[str, float], Counter]:
        weighted = Counter()
        hit_count = Counter()
        total_score = sum(max(0, item.get("matchScore", 1)) for item in knowledge_items) or 1
        for item in knowledge_items:
            item_score = max(0, item.get("matchScore", 1))
            for code in item.get("recommendedActions", []):
                weighted[code] += item_score
                hit_count[code] += 1
        return {code: min(1, score / total_score) for code, score in weighted.items()}, hit_count

    def _collect_candidates(self, transitions, stats, knowledge_scores, symptoms, weather_tags):
        candidates = set()
        sources = defaultdict(set)

        for code in transitions:
            candidates.add(code)
            sources[code].add("transition")
        for code in knowledge_scores:
            candidates.add(code)
            sources[code].add("knowledge")
        for code, _ in stats["stage_counts"].most_common(8):
            candidates.add(code)
            sources[code].add("stage_frequency")
        for tag in weather_tags:
            for code in self.rules.get("weatherActionBoosts", {}).get(tag, []):
                candidates.add(code)
                sources[code].add("weather_rule")
        for symptom in symptoms:
            for code in self.rules.get("symptomActionBoosts", {}).get(symptom, []):
                candidates.add(code)
                sources[code].add("symptom_rule")
        return candidates, sources

    def _score_candidate(
        self,
        code: str,
        growth_stage: str,
        history_records: list[dict],
        transitions: Counter,
        previous_total: int,
        stage_counts: Counter,
        action_stages: dict,
        knowledge_scores: dict[str, float],
        knowledge_hit_count: Counter,
        symptoms: list[str],
        weather_tags: list[str],
        candidate_sources: list[str],
    ) -> dict:
        transition_score = transitions[code] / previous_total if previous_total else 0
        knowledge_score = knowledge_scores.get(code, 0)
        growth_stage_score = self._growth_stage_score(code, growth_stage, action_stages)
        weather_score = self._rule_score(code, weather_tags, self.rules.get("weatherActionBoosts", {}))
        symptom_score = self._rule_score(code, symptoms, self.rules.get("symptomActionBoosts", {}))
        recency_score = self._recency_penalty_score(code, history_records, knowledge_score)

        raw_score = (
            WEIGHTS["transitionScore"] * transition_score
            + WEIGHTS["knowledgeScore"] * knowledge_score
            + WEIGHTS["growthStageScore"] * growth_stage_score
            + WEIGHTS["weatherSuitabilityScore"] * weather_score
            + WEIGHTS["symptomUrgencyScore"] * symptom_score
            + WEIGHTS["recencyPenaltyScore"] * recency_score
        )
        final_score = min(1, max(0, round(raw_score, 2)))
        source_labels = self._source_labels(candidate_sources)
        return {
            "actionCode": code,
            "actionName": ACTION_NAMES.get(code, code),
            "score": final_score,
            "scoreBreakdown": {
                "transitionScore": round(transition_score, 2),
                "knowledgeScore": round(knowledge_score, 2),
                "growthStageScore": round(growth_stage_score, 2),
                "weatherSuitabilityScore": round(weather_score, 2),
                "symptomUrgencyScore": round(symptom_score, 2),
                "recencyPenaltyScore": round(recency_score, 2),
                "finalScore": final_score,
            },
            "expectedDay": EXPECTED_DAY.get(code, 3),
            "reason": "、".join(source_labels) + "共同支持该操作，建议先做监测、记录和复查。",
            "reasonItems": self._reason_items(
                code,
                growth_stage,
                history_records,
                transition_score,
                knowledge_hit_count[code],
                growth_stage_score,
                weather_score,
                symptom_score,
                recency_score,
            ),
            "sourceType": "+".join(candidate_sources),
            "candidateSources": candidate_sources,
        }

    def _growth_stage_score(self, code: str, growth_stage: str, action_stages: dict) -> float:
        stages = self.rules.get("growthStageOrder", [])
        appeared = action_stages.get(code, set())
        if growth_stage in appeared:
            return 1
        if growth_stage in stages:
            index = stages.index(growth_stage)
            adjacent = {stages[i] for i in (index - 1, index + 1) if 0 <= i < len(stages)}
            if appeared & adjacent:
                return 0.6
        return 0.2 if appeared else 0

    def _rule_score(self, code: str, tags: list[str], rule_map: dict[str, list[str]]) -> float:
        if not tags:
            return 0
        hits = sum(1 for tag in tags if code in rule_map.get(tag, []))
        return min(1, hits / max(1, len(tags)))

    def _recency_penalty_score(self, code: str, history_records: list[dict], knowledge_score: float) -> float:
        if not history_records:
            return 1
        recent = [item["actionCode"] for item in history_records[-3:]]
        if recent[-1] == code and code not in self.rules.get("reviewActions", []) and knowledge_score < 0.8:
            return 0
        if code in recent:
            return 0.5
        return 1

    def _source_labels(self, sources: list[str]) -> list[str]:
        labels = {
            "transition": "历史转移",
            "knowledge": "知识匹配",
            "stage_frequency": "阶段高频",
            "weather_rule": "天气规则",
            "symptom_rule": "症状规则",
        }
        return [labels.get(source, source) for source in sources]

    def _reason_items(
        self,
        code: str,
        growth_stage: str,
        history_records: list[dict],
        transition_score: float,
        knowledge_hit_count: int,
        growth_stage_score: float,
        weather_score: float,
        symptom_score: float,
        recency_score: float,
    ) -> list[str]:
        action_name = ACTION_NAMES.get(code, code)
        reasons = []
        if transition_score:
            last_action_name = history_records[-1].get("actionName", history_records[-1]["actionCode"])
            reasons.append(f"最近一次操作为“{last_action_name}”，历史序列中存在转向“{action_name}”的模式。")
        elif not history_records:
            reasons.append("当前棉田暂无历史操作，系统使用阶段高频、知识和规则候选补齐。")
        if knowledge_hit_count:
            reasons.append(f"本地知识库中有 {knowledge_hit_count} 条相关知识建议该操作。")
        if growth_stage_score >= 1:
            reasons.append(f"该操作在“{growth_stage}”样例序列中高适配。")
        elif growth_stage_score >= 0.6:
            reasons.append(f"该操作在相邻生育阶段出现过，可作为辅助观察候选。")
        if weather_score:
            reasons.append("当前天气标签提升了该操作的优先级。")
        if symptom_score:
            reasons.append("当前症状标签提升了该操作的优先级。")
        if recency_score == 1:
            reasons.append("最近 3 条历史记录中未重复执行该操作。")
        elif recency_score == 0.5:
            reasons.append("最近 3 条历史记录中出现过该操作，已降低重复推荐权重。")
        else:
            reasons.append("最近一次已执行该操作，且未达到强知识要求，已显著降低推荐权重。")
        return reasons

    def build_plan(self, recommendations: list[dict]) -> list[dict]:
        seen = set()
        plan = []
        for item in recommendations:
            if item["actionCode"] in seen:
                continue
            seen.add(item["actionCode"])
            plan.append({
                "day": item["expectedDay"],
                "actionCode": item["actionCode"],
                "actionName": item["actionName"],
                "reason": item["reason"],
                "status": "pending",
            })
        if "UPDATE_RECORD" not in seen:
            plan.append({
                "day": 7,
                "actionCode": "UPDATE_RECORD",
                "actionName": "更新棉田记录并复盘",
                "reason": "沉淀本轮观察结果，便于后续推荐持续校准。",
                "status": "pending",
            })
        return sorted(plan, key=lambda x: (x["day"], x["actionCode"]))
