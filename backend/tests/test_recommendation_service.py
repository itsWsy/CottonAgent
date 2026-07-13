from app.services.recommendation_service import RecommendationService


def codes(recommendations):
    return [item["actionCode"] for item in recommendations]


def test_aphid_and_curled_leaf_prioritize_monitoring_actions():
    service = RecommendationService()
    knowledge = [
        {"matchScore": 9, "recommendedActions": ["PEST_SAMPLE", "COUNT_DENSITY", "RECHECK_LEAF"]},
        {"matchScore": 5, "recommendedActions": ["RECHECK_LEAF", "PEST_SAMPLE"]},
    ]
    recs = service.recommend([], "花铃期", knowledge, ["发现蚜虫", "叶片卷曲"], ["高温", "少雨"])
    result_codes = codes(recs)
    assert "PEST_SAMPLE" in result_codes
    assert "COUNT_DENSITY" in result_codes
    assert "RECHECK_LEAF" in result_codes
    assert "knowledgeScore" in recs[0]["scoreBreakdown"]
    assert "weatherSuitabilityScore" in recs[0]["scoreBreakdown"]
    assert "symptomUrgencyScore" in recs[0]["scoreBreakdown"]


def test_continuous_rain_boosts_drainage_and_scouting():
    service = RecommendationService()
    recs = service.recommend([], "花铃期", [], [], ["连续降雨"])
    result_codes = codes(recs)
    assert "DRAINAGE_CHECK" in result_codes
    assert "FIELD_SCOUTING" in result_codes


def test_bollworm_and_square_shedding_prioritize_boll_check():
    service = RecommendationService()
    recs = service.recommend([], "花铃期", [], ["发现棉铃虫", "落蕾"], ["高温"])
    result_codes = codes(recs)
    assert "PEST_SAMPLE" in result_codes
    assert "BOLL_CHECK" in result_codes


def test_weed_symptom_recommends_weed_monitor():
    service = RecommendationService()
    recs = service.recommend([], "苗期", [], ["杂草较多"], ["正常"])
    assert "WEED_MONITOR" in codes(recs)


def test_recent_duplicate_is_penalized_without_strong_knowledge():
    service = RecommendationService()
    history = [
        {"actionCode": "FIELD_SCOUTING", "actionName": "田间巡查"},
        {"actionCode": "GROWTH_ASSESSMENT", "actionName": "长势评估"},
        {"actionCode": "PEST_SAMPLE", "actionName": "增加虫情采样"},
    ]
    recs = service.recommend(history, "花铃期", [], ["发现蚜虫"], [])
    pest = next(item for item in recs if item["actionCode"] == "PEST_SAMPLE")
    assert pest["scoreBreakdown"]["recencyPenaltyScore"] == 0


def test_update_record_is_not_top_recommendation_and_plan_appends_it():
    service = RecommendationService()
    recs = service.recommend([], "花铃期", [{"matchScore": 5, "recommendedActions": ["UPDATE_RECORD", "FIELD_SCOUTING"]}], [], [])
    assert "UPDATE_RECORD" not in codes(recs)
    plan = service.build_plan([{"actionCode": "PEST_SAMPLE", "actionName": "增加虫情采样", "expectedDay": 1, "reason": "测试"}])
    assert plan[-1]["actionCode"] == "UPDATE_RECORD"


def test_recommend_without_history_is_stable_and_score_range_valid():
    service = RecommendationService()
    recs = service.recommend([], "花铃期", [], [], [])
    assert len(recs) == 3
    assert all(0 <= item["score"] <= 1 for item in recs)
    assert all(0 <= value <= 1 for item in recs for value in item["scoreBreakdown"].values())
