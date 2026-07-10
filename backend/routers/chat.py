"""
backend/routers/chat.py
추천 엔드포인트.
- POST /api/v1/chat/sync : 한 번에 응답 (테스트·디버깅용)
- POST /api/v1/chat      : SSE 스트리밍 (실제 사용자용)

backend는 '정문', app은 '주방'. 여기서는 run_agent를 호출해 결과를
API 응답(ChatResponse)으로만 정리한다. 추천 로직 자체는 app에 있다.
"""

import asyncio
import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.agents.meal_agent import run_agent
from app.schemas import AgentState, UserProfile
from app.services.condition_extractor import extract_conditions_llm
from app.services.intent_router import classify_intent_llm
from backend.schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/api/v1", tags=["chat"])


def _to_response(state: AgentState) -> ChatResponse:
    """run_agent가 돌려준 AgentState를 프론트가 쓰기 좋은 형태로 평평하게 변환."""
    mp = state.meal_plan
    vr = state.validation_result
    return ChatResponse(
        intent=state.intent,
        meal_type=mp.meal_type if mp else None,
        items=mp.items if mp else [],
        nutrition=state.nutrition_total,
        reason=mp.reason if mp else "",
        status=vr.status if vr else None,
        warnings=vr.warnings if vr else [],
        final_response=state.final_response,
        retry_count=state.retry_count,
    )


def _run(req: ChatRequest) -> AgentState:
    """공용 실행부. LLM 의도분류·조건추출(각각 실패 시 stub 폴백)을 주입해 돌린다."""
    profile = req.profile or UserProfile()
    return run_agent(
        req.message,
        profile=profile,
        extractor=extract_conditions_llm,
        classifier=classify_intent_llm,
    )


@router.post("/chat/sync", response_model=ChatResponse)
def chat_sync(req: ChatRequest) -> ChatResponse:
    """한 번에 추천 결과를 돌려준다. 요청→추천 전체가 API로 도는지 확인하는 경로."""
    state = _run(req)
    return _to_response(state)


def _sse(event: str, data: dict) -> str:
    """SSE 한 프레임 포맷. 프론트는 event 타입으로 단계를 구분한다."""
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@router.post("/chat")
async def chat_stream(req: ChatRequest) -> StreamingResponse:
    """
    SSE 스트리밍. 추천 파이프라인은 동기 함수라 스레드로 돌리고,
    진행 단계(status)와 최종 결과(result)를 이벤트로 흘려보낸다.
    실패 시 error 이벤트를 보낸 뒤 스트림을 닫는다(연결이 끊기지 않게).
    """

    async def event_gen():
        yield _sse("status", {"stage": "start", "message": "요청을 분석하고 있어요..."})
        try:
            # run_agent는 동기(블로킹)라 이벤트 루프를 막지 않도록 스레드로 실행
            state = await asyncio.to_thread(_run, req)
            yield _sse("status", {"stage": "done", "message": "추천을 완성했어요."})
            payload = _to_response(state).model_dump()
            yield _sse("result", payload)
        except Exception as e:  # LLM 타임아웃 등 예기치 못한 실패
            yield _sse("error", {"message": f"추천 중 오류가 발생했어요: {e}"})

    return StreamingResponse(
        event_gen(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
