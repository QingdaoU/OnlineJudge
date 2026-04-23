from django.conf import settings
from sparkai.llm.llm import ChatSparkLLM
from sparkai.core.messages import ChatMessage

def get_spark_client():
    return ChatSparkLLM(
        spark_api_url=settings.SPARKAI_URL,
        spark_app_id=settings.SPARKAI_APP_ID,
        spark_api_key=settings.SPARKAI_API_KEY,
        spark_api_secret=settings.SPARKAI_API_SECRET,
        spark_llm_domain=settings.SPARKAI_DOMAIN,
        streaming=False,
    )

def ask_spark(prompt: str) -> str:
    try:
        client = get_spark_client()
        messages = [ChatMessage(role="user", content=prompt)]
        response = client.generate([messages])
        answer = response.generations[0][0].text
        return answer.strip()
    except Exception as e:
        return f"【错误】调用星火大模型失败：{str(e)}"
