"""대화(멀티 세션) 상태 관리."""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

import streamlit as st

INITIAL_GREETING = (
    "안녕하세요! 저는 NutriAgent AI 영양사입니다 🌿\n\n"
    "2025 한국인 영양소 섭취기준(KDRI)에 기반한 맞춤형 식단을 추천해드립니다.\n\n"
    "오늘 어떤 식사를 찾고 계신가요?"
)

PROFILE_DEFAULTS = {
    "gender": "male",
    "age_group": "19-29",
    "allergens": [],
    "target_kcal": 0,
    "profile_registered": False,
}


def now_label() -> str:
    return datetime.now().strftime("%H:%M")


def new_conversation(title: str = "새 식단 상담") -> dict:
    return {
        "id": uuid4().hex,
        "title": title,
        "messages": [{"role": "assistant", "type": "text", "content": INITIAL_GREETING}],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }


def init_conversations() -> None:
    if "conversations" not in st.session_state:
        first = new_conversation()
        st.session_state.conversations = [first]
        st.session_state.active_conversation_id = first["id"]


def get_active_conversation() -> dict:
    conversations = st.session_state.conversations
    active_id = st.session_state.active_conversation_id
    for conversation in conversations:
        if conversation["id"] == active_id:
            return conversation

    st.session_state.active_conversation_id = conversations[0]["id"]
    return conversations[0]


def reset_profile() -> None:
    for key, value in PROFILE_DEFAULTS.items():
        st.session_state[key] = value
    # 프로필 위젯들은 key에 이 값을 덧붙여, 값이 바뀔 때마다 새 위젯 인스턴스로
    # 취급되게 한다 — 그래야 위젯 자체 상태가 아니라 위 기본값을 실제로 반영한다.
    st.session_state.profile_reset_token = st.session_state.get("profile_reset_token", 0) + 1


def register_profile() -> None:
    st.session_state.profile_registered = True


def create_new_chat() -> None:
    conversation = new_conversation()
    st.session_state.conversations.insert(0, conversation)
    st.session_state.active_conversation_id = conversation["id"]
    reset_profile()


def select_conversation(conversation_id: str) -> None:
    st.session_state.active_conversation_id = conversation_id


def conversation_has_started(conversation: dict) -> bool:
    """사용자 메시지가 하나라도 있으면(=인사말만 있는 새 대화가 아니면) True."""
    return any(m["role"] == "user" for m in conversation["messages"])


def update_conversation_title(conversation: dict, user_text: str) -> None:
    """첫 사용자 메시지가 들어오기 전(인사말만 있을 때)에만 제목을 자동 생성."""
    if conversation_has_started(conversation):
        return

    compact = " ".join(user_text.split())
    if not compact:
        return
    conversation["title"] = compact[:24] + ("..." if len(compact) > 24 else "")


def touch_conversation(conversation: dict) -> None:
    conversation["updated_at"] = datetime.now().isoformat()
