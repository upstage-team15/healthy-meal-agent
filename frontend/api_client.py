from __future__ import annotations

import os

import httpx


API_BASE_URL = os.getenv("HEALTHY_MEAL_API_URL", "http://127.0.0.1:8000").rstrip("/")
CHAT_SYNC_URL = f"{API_BASE_URL}/api/v1/chat/sync"


def build_agent_payload(api_response: dict) -> dict | None:
    meal_type = api_response.get("meal_type")
    items = api_response.get("items") or []
    nutrition = api_response.get("nutrition")
    if not meal_type and not items and not nutrition:
        return None

    return {
        "meal_plan": {
            "meal_type": meal_type or "추천",
            "items": items,
            "reason": api_response.get("reason", ""),
        },
        "nutrition_total": nutrition,
        "validation_result": {
            "status": api_response.get("status"),
            "warnings": api_response.get("warnings") or [],
        },
        "retry_count": api_response.get("retry_count", 0),
        "intent": api_response.get("intent"),
    }


def run_recommendation(user_text: str) -> tuple[str, dict | None]:
    try:
        response = httpx.post(
            CHAT_SYNC_URL,
            json={"message": user_text, "profile": {}},
            timeout=45,
        )
        response.raise_for_status()
        data = response.json()
        content = data.get("final_response") or "조건을 조금 더 알려주시면 식단을 다시 맞춰볼게요."
        return content, build_agent_payload(data)
    except httpx.ConnectError:
        return (
            "API 서버에 연결할 수 없어요.\n\n"
            "백엔드를 먼저 실행해 주세요: `uv run uvicorn backend.main:app --reload --port 8000`\n\n"
            f"요청 URL: `{CHAT_SYNC_URL}`",
            None,
        )
    except httpx.HTTPStatusError as exc:
        return (
            "API가 오류 응답을 반환했어요.\n\n"
            f"상태 코드: `{exc.response.status_code}`\n\n"
            f"응답: `{exc.response.text[:500]}`",
            None,
        )
    except Exception as exc:
        return (
            "API 요청을 처리하는 중 오류가 발생했어요.\n\n"
            f"```text\n{exc}\n```",
            None,
        )
