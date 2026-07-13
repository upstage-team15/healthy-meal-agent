from __future__ import annotations

from typing import Any

import streamlit as st

ACCEPTED_FILE_TYPES = ["txt", "csv", "pdf", "png", "jpg", "jpeg"]


def render_chat_composer(disabled: bool, *, pinned: bool) -> tuple[str, list[str]]:
    if pinned:
        submission = _chat_input(disabled=disabled)
    else:
        with st.container(key="inline_composer"):
            submission = _chat_input(disabled=disabled)
    return _parse_chat_submission(submission)


def reset_attachment_widget() -> None:
    return None


def _chat_input(disabled: bool) -> Any:
    return st.chat_input(
        "식단 조건을 입력해 주세요",
        key="meal_chat_input",
        accept_file=True,
        file_type=ACCEPTED_FILE_TYPES,
        disabled=disabled,
        submit_mode="disable",
        width="stretch",
    )


def _parse_chat_submission(submission: Any) -> tuple[str, list[str]]:
    if submission is None:
        return "", []
    if isinstance(submission, str):
        return submission, []

    text = getattr(submission, "text", "") or ""
    files = getattr(submission, "files", []) or []
    file_names = [getattr(file, "name", "첨부 파일") for file in files]
    return text, file_names
