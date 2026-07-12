"""backend/routers/chat.py의 SSE 엔드포인트(/api/v1/chat)와 통신하는 클라이언트.

status(진행 단계) -> result(최종 ChatResponse) 또는 error 이벤트를 순서대로 yield한다.
"""

from __future__ import annotations

import json
import os
from collections.abc import Iterator

import httpx

API_BASE_URL = os.getenv("HEALTHY_MEAL_API_URL", "http://127.0.0.1:8000").rstrip("/")
CHAT_STREAM_URL = f"{API_BASE_URL}/api/v1/chat"


def stream_chat(message: str, profile: dict | None = None) -> Iterator[tuple[str, dict]]:
    payload: dict = {"message": message}
    if profile:
        payload["profile"] = profile

    try:
        with httpx.stream("POST", CHAT_STREAM_URL, json=payload, timeout=60.0) as response:
            response.raise_for_status()
            event_type = None
            for line in response.iter_lines():
                if not line:
                    continue
                if line.startswith("event:"):
                    event_type = line[len("event:") :].strip()
                elif line.startswith("data:"):
                    data = json.loads(line[len("data:") :].strip())
                    yield event_type or "message", data
    except httpx.ConnectError:
        yield (
            "error",
            {
                "message": (
                    "API 서버에 연결할 수 없어요. 백엔드를 먼저 실행해 주세요: "
                    "`uvicorn backend.main:app --reload --port 8000` "
                    f"(요청 URL: {CHAT_STREAM_URL})"
                )
            },
        )
    except httpx.HTTPStatusError as exc:
        yield (
            "error",
            {"message": f"API가 오류 응답을 반환했어요 (상태 코드 {exc.response.status_code})."},
        )
    except Exception as exc:  # noqa: BLE001
        yield "error", {"message": f"요청 처리 중 오류가 발생했어요: {exc}"}
