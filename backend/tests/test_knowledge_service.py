from app.services.knowledge_service import KnowledgeService


def test_search_returns_top_matches():
    service = KnowledgeService()
    results = service.search("花铃期", ["叶片卷曲", "发现蚜虫"], ["高温", "少雨"], "发现蚜虫和叶片卷曲")
    assert len(results) == 3
    assert results[0]["matchScore"] >= results[1]["matchScore"]
    assert results[0]["matchReasons"]
