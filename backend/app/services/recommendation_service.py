import csv
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


class RecommendationService:
    def __init__(self, path: Path | None = None):
        self.path = path or Path(__file__).resolve().parents[1] / "data" / "farm_sequences.csv"
        self.rows = self._load_rows()

    def _load_rows(self) -> list[dict]:
        with self.path.open("r", encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f))

    def recommend(self, history_records: list[dict], growth_stage: str, knowledge_items: list[dict]) -> list[dict]:
        by_sequence = defaultdict(list)
        action_names = dict(ACTION_NAMES)
        stage_actions = Counter()
        for row in self.rows:
            by_sequence[row["sequence_id"]].append(row)
            action_names[row["action_code"]] = row["action_name"]
            if row["growth_stage"] == growth_stage:
                stage_actions[row["action_code"]] += 1

        transitions = Counter()
        previous_total = 0
        last_action = history_records[-1]["actionCode"] if history_records else None
        last_action_name = history_records[-1].get("actionName", last_action) if history_records else ""
        if last_action:
            for sequence in by_sequence.values():
                ordered = sorted(sequence, key=lambda x: int(x["step"]))
                for prev, nxt in zip(ordered, ordered[1:]):
                    if prev["action_code"] == last_action:
                        transitions[nxt["action_code"]] += 1
                        previous_total += 1

        knowledge_actions = []
        knowledge_hit_count = Counter()
        for item in knowledge_items:
            for code in item.get("recommendedActions", []):
                knowledge_actions.append(code)
                knowledge_hit_count[code] += 1

        candidates = set(transitions) | set(knowledge_actions) | {code for code, _ in stage_actions.most_common(6)}
        if last_action and last_action in candidates and last_action not in knowledge_actions:
            candidates.remove(last_action)

        results = []
        for code in candidates:
            transition_score = transitions[code] / previous_total if previous_total else 0
            growth_stage_score = 1 if stage_actions[code] else 0
            knowledge_match_score = 1 if code in knowledge_actions else 0
            final_score = round(0.5 * transition_score + 0.3 * growth_stage_score + 0.2 * knowledge_match_score, 2)
            if final_score <= 0:
                continue

            source = []
            reason_items = []
            if transition_score:
                source.append("历史序列")
                reason_items.append(f"最近一次操作为“{last_action_name}”，历史序列中常转向“{action_names.get(code, code)}”。")
            elif not history_records:
                reason_items.append("当前棉田暂无历史操作，系统使用当前生育阶段的高频操作补齐候选。")
            if growth_stage_score:
                source.append("生育阶段")
                reason_items.append(f"该操作在“{growth_stage}”样例序列中出现过，适合纳入近期观察计划。")
            if knowledge_match_score:
                source.append("知识匹配")
                reason_items.append(f"本地知识库中有 {knowledge_hit_count[code]} 条相关知识建议该操作。")

            results.append({
                "actionCode": code,
                "actionName": action_names.get(code, code),
                "score": min(1, max(0, final_score)),
                "scoreBreakdown": {
                    "transitionScore": round(transition_score, 2),
                    "growthStageScore": growth_stage_score,
                    "knowledgeMatchScore": knowledge_match_score,
                    "finalScore": min(1, max(0, final_score)),
                },
                "expectedDay": EXPECTED_DAY.get(code, 3),
                "reason": "、".join(source) + "共同支持该操作，建议先做监测、记录和复查。",
                "reasonItems": reason_items,
                "sourceType": "+".join(source) or "阶段高频",
            })
        results = sorted(results, key=lambda x: (-x["score"], x["actionCode"]))
        return results[:3]

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
