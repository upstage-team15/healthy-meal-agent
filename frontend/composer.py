from __future__ import annotations

import streamlit as st


def render_chat_composer(disabled: bool, *, pinned: bool) -> tuple[str, list[str]]:
    if pinned:
        submission = _chat_input(disabled=disabled)
    else:
        with st.container(key="inline_composer"):
            submission = _chat_input(disabled=disabled)
    return _parse_chat_submission(submission)


def reset_attachment_widget() -> None:
    return None


def _chat_input(disabled: bool) -> str | None:
    return st.chat_input(
        "식단 조건을 입력해 주세요",
        key="meal_chat_input",
        disabled=disabled,
        submit_mode="disable",
        width="stretch",
    )


def _parse_chat_submission(submission: str | None) -> tuple[str, list[str]]:
    if submission is None:
        return "", []
    return submission, []
