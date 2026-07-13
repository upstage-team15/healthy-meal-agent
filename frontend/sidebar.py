from __future__ import annotations

import streamlit as st

from chat_state import create_new_chat, select_conversation


def render_sidebar_header() -> None:
    st.html(
        """
        <div class="sidebar-brand">
            <div class="sidebar-title">Healthy Meal Agent</div>
            <div class="sidebar-caption">조건을 듣고 한 끼를 깔끔하게 정리합니다.</div>
        </div>
        """,
    )


def format_conversation_title(conversation: dict) -> str:
    title = conversation["title"].strip() or "새 식단 상담"
    return title[:28] + ("..." if len(title) > 28 else "")


def render_sidebar() -> None:
    render_sidebar_header()

    if st.button(
        "새 대화",
        key="sidebar_new_chat",
        icon=":material/add:",
        width="stretch",
    ):
        create_new_chat()
        st.rerun()

    query = st.text_input(
        "대화 검색",
        key="conversation_search",
        placeholder="대화 검색",
        label_visibility="collapsed",
    ).strip()

    st.html('<div class="sidebar-section-label">대화</div>')

    conversations = st.session_state.conversations
    filtered = [
        conversation
        for conversation in conversations
        if query.lower() in conversation["title"].lower()
    ]

    if not filtered:
        st.html('<div class="sidebar-empty">검색 결과가 없습니다.</div>')
        return

    option_ids = [conversation["id"] for conversation in filtered]
    current_id = st.session_state.active_conversation_id
    if current_id not in option_ids:
        current_id = option_ids[0]

    selected_id = st.radio(
        "대화 목록",
        option_ids,
        index=option_ids.index(current_id),
        format_func=lambda option_id: format_conversation_title(
            next(conversation for conversation in filtered if conversation["id"] == option_id)
        ),
        key="conversation_radio",
        label_visibility="collapsed",
        width="stretch",
    )

    if selected_id != st.session_state.active_conversation_id:
        select_conversation(selected_id)
        st.rerun()
