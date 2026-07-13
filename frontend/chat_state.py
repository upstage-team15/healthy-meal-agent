from __future__ import annotations

from datetime import datetime
from uuid import uuid4

import streamlit as st


def now_label() -> str:
    return datetime.now().strftime("%H:%M")


def new_conversation(title: str = "새 식단 상담") -> dict:
    return {
        "id": uuid4().hex,
        "title": title,
        "messages": [],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }


def init_state() -> None:
    if "conversations" not in st.session_state:
        first = new_conversation()
        st.session_state.conversations = [first]
        st.session_state.active_conversation_id = first["id"]
    if "is_generating" not in st.session_state:
        st.session_state.is_generating = False


def get_active_conversation() -> dict:
    conversations = st.session_state.conversations
    active_id = st.session_state.active_conversation_id
    for conversation in conversations:
        if conversation["id"] == active_id:
            return conversation

    st.session_state.active_conversation_id = conversations[0]["id"]
    return conversations[0]


def create_new_chat() -> None:
    conversation = new_conversation()
    st.session_state.conversations.insert(0, conversation)
    st.session_state.active_conversation_id = conversation["id"]


def select_conversation(conversation_id: str) -> None:
    st.session_state.active_conversation_id = conversation_id


def update_conversation_title(conversation: dict, user_text: str) -> None:
    if conversation["messages"]:
        return

    compact = " ".join(user_text.split())
    if not compact:
        return

    conversation["title"] = compact[:24] + ("..." if len(compact) > 24 else "")


def append_message(
    conversation: dict,
    role: str,
    content: str,
    *,
    attachments: list[str] | None = None,
    agent_payload: dict | None = None,
) -> dict:
    message = {
        "id": uuid4().hex,
        "role": role,
        "content": content,
        "attachments": attachments or [],
        "agent": agent_payload,
        "created_at": now_label(),
    }
    conversation["messages"].append(message)
    conversation["updated_at"] = datetime.now().isoformat()
    return message
