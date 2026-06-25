import httpx

from app.core.config import settings


class LLMService:
    async def generate_answer(self, context: dict) -> str:
        if settings.llm_api_key and settings.llm_base_url and settings.llm_model:
            try:
                async with httpx.AsyncClient(timeout=settings.llm_timeout) as client:
                    resp = await client.post(
                        settings.llm_base_url.rstrip("/") + "/chat/completions",
                        headers={"Authorization": f"Bearer {settings.llm_api_key}"},
                        json={
                            "model": settings.llm_model,
                            "messages": [
                                {"role": "system", "content": "你只根据结构化上下文生成简短中文农事辅助说明，不提供具体农药名称或剂量。"},
                                {"role": "user", "content": str(context)},
                            ],
                            "temperature": 0.2,
                        },
                    )
                    data = resp.json()
                    text = data["choices"][0]["message"]["content"]
                    if text:
                        return text
            except Exception:
                pass
        symptoms = "、".join(context.get("symptoms") or ["当前症状"])
        actions = "、".join([r["actionName"] for r in context.get("recommendations", [])])
        return f"根据当前棉田处于{context.get('growthStage')}，结合{symptoms}等症状以及最近的农事记录，系统建议优先进行{actions}等操作。未来 7 天应以监测、记录和复查为主。以上结果仅供辅助参考，实际操作需由专业人员确认。"
