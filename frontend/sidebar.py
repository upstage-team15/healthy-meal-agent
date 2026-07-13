from __future__ import annotations

import streamlit as st

from chat_state import create_new_chat, select_conversation


def render_sidebar_header() -> None:
    st.html(
        """
        <div class="sidebar-brand">
            <div>
                <div class="sidebar-title">Meal Agent</div>
            </div>
        </div>
        """,
    )


def format_conversation_title(conversation: dict) -> str:
    title = conversation["title"].strip() or "새 식단 상담"
    return title[:28] + ("..." if len(title) > 28 else "")


def render_sidebar() -> None:
    render_sidebar_header()

    if st.button(
        "새 채팅",
        key="sidebar_new_chat",
        icon=":material/add:",
        width="stretch",
    ):
        create_new_chat()
        st.rerun()

    query = st.text_input(
        "대화 검색",
        key="conversation_search",
        placeholder="채팅 검색",
        label_visibility="collapsed",
    ).strip()

    st.html('<div class="sidebar-section-label">최근</div>')

    conversations = st.session_state.conversations
    filtered = [
        conversation
        for conversation in conversations
        if query.lower() in conversation["title"].lower()
    ]

    if not filtered:
        st.html('<div class="sidebar-empty">검색 결과가 없습니다.</div>')
        return

    for conversation in filtered:
        label = format_conversation_title(conversation)
        is_active = conversation["id"] == st.session_state.active_conversation_id
        if st.button(
            label,
            key=f"conversation_{conversation['id']}",
            icon=":material/chat_bubble:",
            type="primary" if is_active else "secondary",
            width="stretch",
        ):
            if not is_active:
                select_conversation(conversation["id"])
                st.rerun()
