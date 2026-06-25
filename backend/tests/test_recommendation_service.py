from app.services.recommendation_service import RecommendationService


def test_recommend_with_history():
    service = RecommendationService()
    recs = service.recommend([{"actionCode": "PEST_SAMPLE"}], "花铃期", [{"recommendedActions": ["COUNT_DENSITY"]}])
    assert recs
    assert recs[0]["score"] <= 1
    assert "scoreBreakdown" in recs[0]
    assert "reasonItems" in recs[0]


def test_recommend_without_history_and_stable_sort():
    service = RecommendationService()
    recs = service.recommend([], "花铃期", [])
    assert len(recs) == 3
    assert all(0 <= item["score"] <= 1 for item in recs)


def test_build_plan_appends_update_record():
    service = RecommendationService()
    plan = service.build_plan([{"actionCode": "PEST_SAMPLE", "actionName": "采样", "expectedDay": 1, "reason": "测试"}])
    assert plan[-1]["actionCode"] == "UPDATE_RECORD"
