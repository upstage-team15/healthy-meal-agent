from __future__ import annotations

import sys
import time
from pathlib import Path

import streamlit as st

FRONTEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = FRONTEND_DIR.parent
for import_path in (str(PROJECT_ROOT), str(FRONTEND_DIR)):
    if import_path in sys.path:
        sys.path.remove(import_path)
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(1, str(FRONTEND_DIR))

from api_client import run_recommendation  # noqa: E402
from chat_state import (  # noqa: E402
    append_message,
    get_active_conversation,
    init_state,
    update_conversation_title,
)
from chat_view import (  # noqa: E402
    render_app_header,
    render_empty_state,
    render_message,
    render_suggestion_buttons,
    render_typing_indicator,
)
from composer import render_chat_composer, reset_attachment_widget  # noqa: E402
from sidebar import render_sidebar  # noqa: E402
from styles import inject_global_styles  # noqa: E402


st.set_page_config(
    page_title="Healthy Meal Agent",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def submit_user_message(text: str, attachments: list[str] | None = None) -> None:
    clean_text = text.strip()
    if not clean_text and not attachments:
        return

    conversation = get_active_conversation()
    display_text = clean_text or "첨부 파일을 기준으로 건강한 한 끼를 추천해줘"

    update_conversation_title(conversation, display_text)
    user_message = append_message(
        conversation,
        "user",
        display_text,
        attachments=attachments,
    )

    render_message(user_message)
    render_typing_indicator()

    st.session_state.is_generating = True
    time.sleep(0.25)
    assistant_text, agent_payload = run_recommendation(display_text)
    append_message(
        conversation,
        "assistant",
        assistant_text,
        agent_payload=agent_payload,
    )
    if attachments:
        reset_attachment_widget()
    st.session_state.is_generating = False
    st.rerun()


inject_global_styles()
init_state()

with st.sidebar:
    render_sidebar()

active = get_active_conversation()

queued_prompt: str | None = None
submitted_text = ""
submitted_files: list[str] = []

if not active["messages"]:
    with st.container(key="welcome_stage"):
        render_empty_state()
        queued_prompt = render_suggestion_buttons()
        submitted_text, submitted_files = render_chat_composer(
            disabled=st.session_state.is_generating,
            pinned=False,
        )
else:
    render_app_header(
        service_name="Healthy Meal Agent",
        message_count=len(active["messages"]),
    )
    for message in active["messages"]:
        render_message(message)
    submitted_text, submitted_files = render_chat_composer(
        disabled=st.session_state.is_generating,
        pinned=True,
    )

if queued_prompt:
    submit_user_message(queued_prompt)
elif submitted_text or submitted_files:
    submit_user_message(submitted_text, attachments=submitted_files)
