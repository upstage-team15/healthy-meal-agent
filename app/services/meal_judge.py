"""
app/services/meal_judge.py
조합 자연성 판정 (Meal Coherence Judge) — 기획서 검증표 5번 항목.

규칙(kcal·나트륨·탄단지)으로 거른 상위 조합 후보들 중에서, "사람이 한 끼로 먹기에
자연스러운 조합"을 LLM이 고른다. 규칙이 못 잡는 어색함을 걸러낸다:
  - 겹치는 재료(토마토라면+토마토김치)
  - 안 어울리는 조합(죽+튀김, 샌드위치+팬케익)
  - 국물 없이 마른 것만 / 비슷한 음식 중복

'판단은 LLM, 사실은 코드' 원칙: 자연스러움은 판단이라 LLM, 영양은 코드가 이미 검증.
실패/타임아웃 시 예외를 올려 호출부(composer)가 규칙 1등으로 폴백한다(무중단).
"""

import json


def _fmt(items) -> str:
    return " + ".join(f.food_name for f in items)


def pick_most_coherent(candidates: list[list], conditions) -> int:
    """
    candidates: 조합 후보 리스트(각 후보는 FoodItem 리스트).
    반환: 가장 자연스러운 후보의 인덱스(0-based).

    LLM에게 번호 매긴 조합들을 주고 "한 끼로 가장 자연스러운 것의 번호"를 받는다.
    """
    if len(candidates) <= 1:
        return 0

    lines = [f"{i + 1}. {_fmt(c)}" for i, c in enumerate(candidates)]
    pref = ", ".join(conditions.preferences or []) or "특별한 선호 없음"
    prompt = (
        "당신은 한식 식단 전문가입니다. 아래는 영양 기준을 통과한 한 끼 식단 후보들입니다.\n"
        "사람이 실제로 '한 끼'로 먹기에 가장 자연스럽고 조화로운 조합의 번호만 답하세요.\n"
        "판단 기준:\n"
        "- 재료·맛이 겹치지 않을 것(예: 토마토라면+토마토김치는 감점)\n"
        "- 서로 어울릴 것(예: 죽+튀김, 샌드위치+팬케익처럼 어색한 조합 감점)\n"
        "- 밥류에는 국이나 반찬이 곁들여지면 좋고, 한 그릇 요리는 단독이나 가벼운 반찬이 자연스러움\n"
        f"- 사용자 선호: {pref}\n\n"
        "후보:\n" + "\n".join(lines) + "\n\n"
        "가장 자연스러운 후보의 번호 하나만 숫자로 답하세요. 설명 금지."
    )

    from app.services.llm_client import complete

    raw = complete([{"role": "user", "content": prompt}], temperature=0).strip()
    # 숫자만 뽑아 인덱스로 변환 (범위 벗어나면 0)
    digits = "".join(ch for ch in raw if ch.isdigit())
    if not digits:
        return 0
    choice = int(digits[: len(str(len(candidates)))] or digits[0]) - 1
    return choice if 0 <= choice < len(candidates) else 0


def coherence_scores(candidates: list[list], conditions) -> list[dict]:
    """(선택) 각 후보에 점수+이유를 매긴다. 발표/디버깅용. 지금은 pick만 쓰면 됨."""
    lines = [f"{i + 1}. {_fmt(c)}" for i, c in enumerate(candidates)]
    prompt = (
        "각 한 끼 조합이 얼마나 자연스러운지 0~10점으로 평가하고 이유를 한 줄로.\n"
        'JSON 배열로만: [{"no":1,"score":8,"reason":"..."}]\n\n' + "\n".join(lines)
    )
    from app.services.llm_client import complete

    raw = complete([{"role": "user", "content": prompt}], temperature=0).strip()
    return json.loads(raw[raw.find("[") : raw.rfind("]") + 1])
