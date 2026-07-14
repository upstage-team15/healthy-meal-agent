"""
app/services/llm_client.py
litellm Router 기반 LLM 호출 (강의 2강 정석 Fallback).

메인 모델(Upstage Solar Pro3)이 장애/타임아웃이면 보험 모델(OpenAI)로 자동 전환한다.
  Solar → (실패) → OpenAI → (그것도 실패) → 호출부의 규칙기반 stub 폴백

- Router는 여러 프로바이더를 하나의 인터페이스로 통합(litellm). "litellm으로 Fallback 구현".
- OPENAI_API_KEY가 없으면 Solar 단독으로 동작(보험만 빠질 뿐 서비스 정상).
- Router 인스턴스는 한 번 만들고 캐시.
"""

import os

from dotenv import load_dotenv

load_dotenv()

_ROUTER = None  # litellm.Router 캐시
_PRIMARY = "solar"  # Router model_list의 논리 이름(호출 시 이 이름을 model로 넘긴다)


def _build_router():
    """Solar(메인) + OpenAI(보험) Router 생성. OpenAI 키 없으면 Solar만."""
    from litellm import Router

    solar_model = os.getenv("LLM_MODEL", "solar-pro3")
    model_list = [
        {
            "model_name": _PRIMARY,  # 논리 이름
            "litellm_params": {
                "model": "openai/" + solar_model,  # openai 호환 형식 + upstage api_base
                "api_key": os.getenv("UPSTAGE_API_KEY"),
                "api_base": "https://api.upstage.ai/v1",
                "timeout": 30,
            },
        }
    ]
    fallbacks = []
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        # 보험 모델도 같은 논리 이름으로 등록 → Solar 실패 시 이 그룹으로 넘어감
        model_list.append(
            {
                "model_name": _PRIMARY,
                "litellm_params": {
                    "model": os.getenv("FALLBACK_MODEL", "gpt-4o-mini"),
                    "api_key": openai_key,
                    "timeout": 30,
                },
            }
        )
        # 명시적 fallback 규칙도 등록(같은 그룹 내 순차 시도 + 방어적 이중화)
        fallbacks = [{_PRIMARY: [_PRIMARY]}]

    return Router(
        model_list=model_list,
        fallbacks=fallbacks or None,
        num_retries=2,  # 일시적 오류(429/5xx/타임아웃) 지수 백오프 재시도
        retry_after=1,
    )


def get_router():
    """Router 인스턴스(캐시)."""
    global _ROUTER
    if _ROUTER is None:
        _ROUTER = _build_router()
    return _ROUTER


def complete(messages: list[dict], temperature: float = 0) -> str:
    """
    LLM 호출 후 응답 텍스트를 돌려준다. Solar 실패 시 OpenAI로 자동 Fallback.
    실패가 끝까지 전파되면 예외를 올리고, 호출부(intent/extractor)가 stub으로 폴백한다.
    """
    router = get_router()
    response = router.completion(
        model=_PRIMARY,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message.content
