"""
scripts/embed_foods.py
foods 테이블의 각 음식에 search_text(이름+역할+성격설명) 생성 + embedding(4096) 채우기.

- 결정 C: LLM(solar-pro3)이 음식마다 맛·성격 한 줄을 생성해 검색 품질을 높인다.
  예: 김치찌개 → "얼큰하고 칼칼한 매운 국물" → search_text에 포함 → "얼큰한" 검색이 잘 걸림.
- 사용자가 원할 때만 수동 실행하는 1회성 배치.
- 재실행 안전(재개 가능): embedding이 이미 있는 행은 건너뛴다.
  --force 주면 전부 다시 생성.

실행:
    uv run python scripts/embed_foods.py
    uv run python scripts/embed_foods.py --force        # 전부 재생성
    uv run python scripts/embed_foods.py --limit 20      # 앞 N개만(샘플 확인용)
"""

import argparse
import os

from dotenv import load_dotenv

from app.services.embedding_service import embed_passage
from app.services.supabase_client import get_client

load_dotenv()

TRAIT_PROMPT = """다음 한국 음식의 맛·성격을 검색용으로 한 줄(20자 이내)로만 답하세요.
설명·부연 없이 형용사 위주 표현만. 예시) 김치찌개 → 얼큰하고 칼칼한 매운 국물
음식: """


def make_trait(food_name: str) -> str:
    """LLM으로 음식 성격 한 줄 생성. 실패 시 빈 문자열(이름+역할만으로 fallback)."""
    try:
        import litellm

        r = litellm.completion(
            model="openai/" + os.getenv("LLM_MODEL", "solar-pro3"),
            messages=[{"role": "user", "content": TRAIT_PROMPT + food_name}],
            api_key=os.getenv("UPSTAGE_API_KEY"),
            api_base="https://api.upstage.ai/v1",
            temperature=0,
            timeout=30,  # 무한 대기 방지 (매달림 버그 수정)
            num_retries=2,
        )
        return r.choices[0].message.content.strip().replace("\n", " ")[:40]
    except Exception as e:
        print(f"    [성격설명 실패 → 생략] {food_name}: {str(e)[:60]}")
        return ""


def build_search_text(food_name: str, meal_role: str, trait: str) -> str:
    parts = [food_name, meal_role]
    if trait:
        parts.append(trait)
    return " / ".join(parts)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="embedding 있어도 전부 재생성")
    ap.add_argument("--limit", type=int, default=None, help="앞 N개만 처리(샘플)")
    args = ap.parse_args()

    client = get_client()

    # embedding(4096 벡터)은 조회하지 않는다 — 값을 다 끌어오면 응답이 거대해져
    # Supabase statement timeout(57014)이 난다. 미완료 판별은 search_text 유무로.
    # (search_text가 채워진 행 = 이미 임베딩까지 끝난 행)
    rows = []
    page = 500
    start = 0
    while True:
        chunk = (
            client.table("foods")
            .select("food_id, food_name, meal_role, search_text")
            .order("food_id")
            .range(start, start + page - 1)
            .execute()
            .data
        )
        rows.extend(chunk)
        if len(chunk) < page:
            break
        start += page

    todo = rows if args.force else [r for r in rows if not r.get("search_text")]
    if args.limit:
        todo = todo[: args.limit]

    print(f"대상 {len(todo)}개 / 전체 {len(rows)}개 (force={args.force})")

    done = 0
    for r in todo:
        trait = make_trait(r["food_name"])
        search_text = build_search_text(r["food_name"], r["meal_role"], trait)
        vec = embed_passage(search_text)
        client.table("foods").update(
            {"search_text": search_text, "embedding": vec, "updated_at": "now()"}
        ).eq("food_id", r["food_id"]).execute()
        done += 1
        if done <= 5 or done % 50 == 0:
            print(f"  [{done}/{len(todo)}] {search_text}")

    print(f"완료. {done}개 임베딩 저장.")


if __name__ == "__main__":
    main()
