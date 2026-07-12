from __future__ import annotations

import streamlit as st


def inject_global_styles() -> None:
    st.html(
        """
        <style>
        :root {
            --bg: #fbfcfd;
            --surface: #ffffff;
            --surface-muted: #f2f4f6;
            --line: #e5e8eb;
            --line-strong: #d1d6db;
            --text: #333333;
            --muted: #6b7684;
            --muted-2: #8b95a1;
            --blue: #1f6fff;
            --blue-soft: #eaf2ff;
            --teal: #7fe7dc;
            --teal-ink: #12413d;
            --warning: #b7791f;
            --warning-bg: #fff7e6;
            --danger: #d92d20;
            --danger-bg: #fff1f0;
            --radius-lg: 20px;
            --radius-md: 16px;
            --radius-sm: 14px;
            --shadow-sm: 0 1px 2px rgba(25, 28, 33, 0.06);
            --shadow-md: 0 10px 32px rgba(25, 28, 33, 0.08);
            --shadow-float: 0 28px 90px rgba(48, 65, 76, 0.13);
        }

        .stApp {
            background:
                radial-gradient(circle at 52% 43%, rgba(127, 231, 220, 0.22) 0, rgba(127, 231, 220, 0.12) 20%, rgba(230, 240, 255, 0.14) 42%, rgba(251, 252, 253, 0) 68%),
                var(--bg);
            color: var(--text);
        }

        [data-testid="stHeader"] {
            background: rgba(247, 248, 250, 0.92);
            backdrop-filter: blur(10px);
        }

        [data-testid="stToolbar"],
        [data-testid="stDecoration"] {
            display: none !important;
        }

        [data-testid="stAppViewContainer"] > .main .block-container,
        .block-container {
            max-width: 1040px !important;
            padding: 24px 32px 132px !important;
        }

        [data-testid="stSidebar"] {
            width: 280px !important;
            min-width: 280px !important;
            background: #fbfcfd;
            border-right: 1px solid var(--line);
            box-shadow: 18px 0 56px rgba(25, 28, 33, 0.08);
        }

        [data-testid="stSidebarCollapsedControl"] {
            top: 18px !important;
            left: 18px !important;
            width: 40px !important;
            height: 40px !important;
            border-radius: 14px !important;
            background: rgba(255, 255, 255, 0.84) !important;
            border: 1px solid rgba(209, 214, 219, 0.72) !important;
            box-shadow: var(--shadow-sm) !important;
            backdrop-filter: blur(12px);
        }

        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
            gap: 0.42rem;
        }

        .sidebar-brand {
            padding: 4px 2px 12px;
        }

        .sidebar-title {
            color: var(--text);
            font-size: 18px;
            font-weight: 800;
            line-height: 1.2;
        }

        .sidebar-caption {
            margin-top: 5px;
            color: var(--muted);
            font-size: 13px;
            line-height: 1.45;
        }

        .sidebar-section-label {
            margin: 10px 0 2px;
            color: var(--muted-2);
            font-size: 12px;
            font-weight: 800;
        }

        .sidebar-empty {
            padding: 12px;
            border-radius: 10px;
            color: var(--muted);
            font-size: 13px;
            background: var(--surface-muted);
        }

        [data-testid="stSidebar"] .stButton > button {
            min-height: 40px;
            border-radius: 12px;
            border: 1px solid var(--line);
            background: var(--surface);
            color: var(--text);
            font-size: 13px;
            font-weight: 700;
            box-shadow: var(--shadow-sm);
        }

        [data-testid="stSidebar"] [role="radiogroup"] {
            gap: 2px;
        }

        [data-testid="stSidebar"] [role="radiogroup"] label {
            min-height: 36px;
            padding: 7px 10px !important;
            border-radius: 10px;
            border: 0 !important;
            background: transparent;
            transition: background 120ms ease, box-shadow 120ms ease;
        }

        [data-testid="stSidebar"] [role="radiogroup"] label:hover {
            background: var(--surface-muted);
        }

        [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
            background: var(--blue-soft);
            box-shadow: inset 3px 0 0 var(--blue);
        }

        [data-testid="stSidebar"] [role="radiogroup"] label > div:first-child {
            display: none;
        }

        [data-testid="stSidebar"] [role="radiogroup"] p {
            font-size: 13px;
            font-weight: 650;
            color: var(--text);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) p {
            color: var(--blue);
            font-weight: 750;
        }

        .stButton > button:focus-visible,
        textarea:focus,
        input:focus {
            outline: 3px solid rgba(127, 231, 220, 0.34) !important;
            outline-offset: 2px;
            border-color: var(--teal) !important;
        }

        [data-testid="stBottom"],
        [data-testid="stBottomBlockContainer"],
        .stBottomBlockContainer {
            background: transparent !important;
            border: 0 !important;
            box-shadow: none !important;
            pointer-events: none;
        }

        [data-testid="stBottom"] *,
        [data-testid="stBottomBlockContainer"] *,
        .stBottomBlockContainer * {
            box-shadow: none;
        }

        [data-testid="stBottomBlockContainer"] > div,
        .stBottomBlockContainer > div {
            max-width: 920px !important;
            margin: 0 auto 24px !important;
            padding: 0 24px !important;
            background: transparent !important;
            border: 0 !important;
            box-shadow: none !important;
            pointer-events: auto;
        }

        [data-testid="stChatInput"] {
            position: relative !important;
            max-width: 920px;
            margin: 0 auto;
            padding: 0 !important;
            min-height: 56px !important;
            height: 56px !important;
            background: transparent !important;
        }

        .st-key-inline_composer {
            max-width: 820px;
            margin: 24px auto 0;
        }

        .st-key-welcome_stage {
            min-height: calc(100vh - 156px);
            display: flex;
            align-items: center;
            justify-content: center;
            width: 100%;
        }

        .st-key-welcome_stage [data-testid="stVerticalBlock"] {
            width: min(920px, 100%);
            margin: 0 auto;
            gap: 0.85rem;
        }

        .st-key-welcome_stage [data-testid="stChatInput"] {
            max-width: 820px;
            height: 76px !important;
            min-height: 76px !important;
        }

        [data-testid="stChatInput"] > div,
        [data-testid="stChatInput"] > div:focus-within {
            padding: 0 !important;
            border: 0 !important;
            background: transparent !important;
            box-shadow: none !important;
            outline: none !important;
        }

        [data-testid="stChatInput"] textarea {
            min-height: 56px !important;
            height: 56px !important;
            padding: 15px 62px !important;
            border-radius: 18px !important;
            border: 1px solid var(--line-strong) !important;
            background: var(--surface) !important;
            color: var(--text) !important;
            font-size: 15px !important;
            line-height: 1.45 !important;
            box-shadow: var(--shadow-md) !important;
        }

        .st-key-welcome_stage [data-testid="stChatInput"] textarea {
            min-height: 76px !important;
            height: 76px !important;
            padding: 24px 76px !important;
            border: 0 !important;
            border-radius: 26px !important;
            background: rgba(255, 255, 255, 0.94) !important;
            font-size: 16px !important;
            box-shadow: var(--shadow-float) !important;
            backdrop-filter: blur(10px);
        }

        [data-testid="stChatInput"] textarea::placeholder {
            color: var(--muted-2);
            opacity: 1;
        }

        [data-testid="stChatInput"] button {
            position: absolute !important;
            top: 9px !important;
            z-index: 5 !important;
            width: 38px !important;
            height: 38px !important;
            min-width: 38px !important;
            border-radius: 999px !important;
            box-shadow: none !important;
        }

        .st-key-welcome_stage [data-testid="stChatInput"] button {
            top: 17px !important;
            width: 42px !important;
            height: 42px !important;
            min-width: 42px !important;
        }

        [data-testid="stChatInput"] button[aria-label="Upload a file"] {
            left: 10px !important;
            background: transparent !important;
            color: var(--muted) !important;
        }

        .st-key-welcome_stage [data-testid="stChatInput"] button[aria-label="Upload a file"] {
            left: 16px !important;
        }

        [data-testid="stChatInput"] button[data-testid="stChatInputSubmitButton"] {
            right: 10px !important;
            background: var(--teal) !important;
            color: var(--teal-ink) !important;
            border: 0 !important;
        }

        .st-key-welcome_stage [data-testid="stChatInput"] button[data-testid="stChatInputSubmitButton"] {
            right: 16px !important;
        }

        [data-testid="stChatInput"] button:disabled {
            background: #eef4f3 !important;
            color: var(--muted-2) !important;
        }

        .app-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 18px;
            max-width: 920px;
            min-height: 58px;
            padding: 12px 16px;
            margin: 0 auto 10px;
            border: 1px solid var(--line);
            border-radius: var(--radius-md);
            background: var(--surface);
            box-shadow: var(--shadow-sm);
        }

        .brand-row {
            display: flex;
            align-items: center;
            gap: 12px;
            min-width: 0;
        }

        .brand-mark {
            width: 34px;
            height: 34px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 14px;
            background: var(--blue);
            color: #fff;
            font-weight: 800;
        }

        .service-name {
            color: var(--text);
            font-size: 15px;
            font-weight: 780;
            line-height: 1.2;
        }

        .service-caption {
            margin-top: 2px;
            color: var(--muted);
            font-size: 12px;
            font-weight: 650;
            line-height: 1.35;
        }

        .header-meta {
            flex: 0 0 auto;
            display: flex;
            align-items: center;
            gap: 8px;
            color: var(--muted);
            font-size: 13px;
            font-weight: 650;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 999px;
            background: var(--blue);
        }

        .empty-state {
            max-width: 920px;
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            padding: 0 18px 14px;
            margin: 0 auto;
        }

        .empty-kicker {
            margin-bottom: 12px;
            padding: 7px 11px;
            border-radius: 999px;
            border: 1px solid var(--line);
            background: var(--surface);
            color: var(--teal-ink);
            font-size: 12px;
            font-weight: 800;
            box-shadow: var(--shadow-sm);
        }

        .empty-state h1 {
            margin: 0;
            color: var(--text);
            font-size: 35px;
            line-height: 1.18;
            font-weight: 680;
        }

        .empty-state p {
            max-width: 560px;
            margin: 12px auto 0;
            color: var(--muted);
            font-size: 16px;
            line-height: 1.65;
        }

        .st-key-example_prompt_choice {
            max-width: 920px;
            margin: 2px auto 0;
        }

        .st-key-example_prompt_choice [role="radiogroup"],
        .st-key-example_prompt_choice [data-baseweb="radio"] {
            justify-content: center;
            gap: 10px;
        }

        .st-key-example_prompt_choice button,
        .st-key-example_prompt_choice label {
            min-height: 42px;
            border-radius: 999px !important;
            border-color: transparent !important;
            background: rgba(242, 244, 246, 0.68) !important;
            color: var(--text) !important;
            font-size: 14px !important;
            font-weight: 620 !important;
            box-shadow: none !important;
        }

        .st-key-example_prompt_choice button:hover,
        .st-key-example_prompt_choice label:hover {
            border-color: transparent !important;
            background: rgba(255, 255, 255, 0.86) !important;
            color: var(--text) !important;
            box-shadow: var(--shadow-sm) !important;
        }

        .message-row {
            display: flex;
            width: 100%;
            margin: 16px 0;
            animation: rise-in 220ms ease both;
        }

        .message-row.user {
            justify-content: flex-end;
        }

        .message-row.assistant {
            justify-content: flex-start;
        }

        .message-stack {
            width: min(78%, 760px);
        }

        .message-row.user .message-stack {
            width: min(68%, 680px);
        }

        .message-meta {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 10px;
            margin: 0 4px 7px;
            color: var(--muted-2);
            font-size: 12px;
            font-weight: 750;
        }

        .message-actions {
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }

        .copy-btn {
            height: 26px;
            padding: 0 9px;
            border: 1px solid var(--line);
            border-radius: 999px;
            background: var(--surface);
            color: var(--muted);
            font: 700 12px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            cursor: pointer;
        }

        .copy-btn:hover {
            border-color: var(--blue);
            color: var(--blue);
        }

        .message-bubble {
            padding: 15px 17px;
            border-radius: var(--radius-md);
            line-height: 1.72;
            font-size: 15px;
            overflow-wrap: anywhere;
            word-break: keep-all;
        }

        .message-row.assistant .message-bubble {
            border: 1px solid var(--line);
            background: var(--surface);
            color: var(--text);
            box-shadow: var(--shadow-sm);
        }

        .message-row.user .message-bubble {
            background: var(--blue);
            color: #fff;
        }

        .message-bubble pre {
            margin: 12px 0 4px;
            padding: 13px;
            overflow-x: auto;
            border-radius: 14px;
            background: #111827;
            color: #f9fafb;
            font-size: 13px;
            line-height: 1.65;
        }

        .attachment-list {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 10px;
        }

        .attachment-chip {
            padding: 6px 9px;
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.18);
            color: inherit;
            font-size: 12px;
            font-weight: 700;
        }

        .meal-card {
            width: min(78%, 760px);
            margin: 8px 0 18px;
            padding: 18px;
            border: 1px solid var(--line);
            border-radius: var(--radius-lg);
            background: var(--surface);
            box-shadow: var(--shadow-md);
            animation: rise-in 240ms ease both;
        }

        .meal-card-title {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 12px;
            margin-bottom: 14px;
        }

        .meal-card-title strong {
            color: var(--text);
            font-size: 17px;
            line-height: 1.25;
        }

        .status-pill {
            padding: 6px 10px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 850;
            color: var(--blue);
            background: var(--blue-soft);
        }

        .status-pill.warning {
            color: var(--warning);
            background: var(--warning-bg);
        }

        .status-pill.fail {
            color: var(--danger);
            background: var(--danger-bg);
        }

        .nutrition-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 10px;
            margin-bottom: 14px;
        }

        .nutrition-item {
            padding: 12px;
            border-radius: var(--radius-sm);
            background: var(--surface-muted);
        }

        .nutrition-label {
            color: var(--muted);
            font-size: 12px;
            font-weight: 750;
        }

        .nutrition-value {
            margin-top: 4px;
            color: var(--text);
            font-size: 18px;
            font-weight: 850;
            line-height: 1.2;
        }

        .food-list {
            display: grid;
            gap: 8px;
            margin-top: 8px;
        }

        .food-row {
            display: flex;
            justify-content: space-between;
            gap: 12px;
            padding: 11px 0;
            border-top: 1px solid var(--line);
            color: var(--text);
            font-size: 14px;
            line-height: 1.45;
        }

        .food-row span:last-child {
            flex: 0 0 auto;
            color: var(--muted);
            font-weight: 750;
        }

        .warning-list {
            margin-top: 12px;
            padding: 12px;
            border-radius: var(--radius-sm);
            background: var(--warning-bg);
            color: var(--warning);
            font-size: 13px;
            font-weight: 700;
            line-height: 1.55;
        }

        .typing-row {
            display: flex;
            justify-content: flex-start;
            margin: 16px 0;
            animation: rise-in 180ms ease both;
        }

        .typing-bubble {
            display: inline-flex;
            align-items: center;
            gap: 7px;
            padding: 16px 18px;
            border: 1px solid var(--line);
            border-radius: var(--radius-md);
            background: var(--surface);
            box-shadow: var(--shadow-sm);
        }

        .typing-dot {
            width: 7px;
            height: 7px;
            border-radius: 999px;
            background: var(--blue);
            opacity: 0.35;
            animation: typing-dot 1s infinite ease-in-out;
        }

        .typing-dot:nth-child(2) {
            animation-delay: 120ms;
        }

        .typing-dot:nth-child(3) {
            animation-delay: 240ms;
        }

        @keyframes typing-dot {
            0%, 80%, 100% { transform: translateY(0); opacity: 0.35; }
            40% { transform: translateY(-4px); opacity: 1; }
        }

        @keyframes rise-in {
            from { opacity: 0; transform: translateY(8px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @media (max-width: 760px) {
            [data-testid="stAppViewContainer"] > .main .block-container,
            .block-container {
                padding: 16px 14px 118px !important;
            }

            [data-testid="stBottomBlockContainer"] > div,
            .stBottomBlockContainer > div {
                padding: 0 14px !important;
                margin-bottom: 18px !important;
            }

            .app-header {
                align-items: center;
                padding: 16px;
            }

            .header-meta {
                display: none;
            }

            .empty-state {
                padding-top: 34px;
            }

            .empty-state h1 {
                font-size: 29px;
            }

            .message-stack,
            .message-row.user .message-stack,
            .meal-card {
                width: 100%;
            }

            .message-bubble {
                font-size: 14px;
            }

            .nutrition-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }
        }
        </style>
        """,
    )
