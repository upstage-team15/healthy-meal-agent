"""
app/services/food_retriever.py
음식 후보 검색.

검색은 두 축으로 나뉜다(docs/08):
  - 의미 축: 사용자 표현("얼큰한", "담백한")을 임베딩 유사도로 검색 (Supabase pgvector).
  - 사실 축: kcal 상한·나트륨·알레르기/제외어는 SQL 필터(RPC 파라미터)로 처리.

기존의 PREFERENCE_KEYWORDS 하드코딩 매핑은 제거했다.
Supabase가 없거나 실패하면 CSV 전량을 fallback 후보로 반환한다(테스트/오프라인).

retrieve_foods의 시그니처·반환형(역할별 dict)은 유지 → LangGraph retrieve 노드 무변경.
"""

from pathlib import Path

import pandas as pd

from app.schemas import FoodItem

CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "foods_clean.csv"

ROLES = ["밥", "국물", "반찬", "한그릇"]
PER_ROLE = 20  # 역할별로 가져올 후보 수

_FOODS_CACHE: list[FoodItem] | None = None


def load_foods() -> list[FoodItem]:
    """CSV → FoodItem 리스트 (한 번 읽고 캐시). Supabase fallback·테스트용."""
    global _FOODS_CACHE
    if _FOODS_CACHE is not None:
        return _FOODS_CACHE

    df = pd.read_csv(CSV_PATH)
    if "food_id" not in df.columns:
        df["food_id"] = df.index + 1

    foods = [
        FoodItem(
            food_id=int(row["food_id"]),
            food_name=str(row["food_name"]),
            meal_role=str(row["meal_role"]),
            serving_size=float(row["serving_size"]),
            kcal=float(row["kcal"]),
            carbohydrate=float(row["carbohydrate"]),
            protein=float(row["protein"]),
            fat=float(row["fat"]),
            sugar=float(row["sugar"]),
            sodium=float(row["sodium"]),
        )
        for _, row in df.iterrows()
    ]
    _FOODS_CACHE = foods
    return foods


def build_search_query(conditions) -> str:
    """조건에서 '의미 축' 검색문을 만든다. 숫자/제외는 넣지 않는다(사실 축은 SQL)."""
    parts: list[str] = []
    parts.extend(conditions.preferences or [])
    parts.extend(conditions.nutrition_goals or [])
    parts.extend(conditions.wanted_foods or [])
    if conditions.meal_style:
        parts.append(conditions.meal_style)
    query = " ".join(p for p in parts if p).strip()
    # 아무 의미 조건도 없으면 일반적인 검색문으로 (전 음식과 고루 가까움)
    return query or "건강한 한 끼 식사"


def _row_to_food(r: dict) -> FoodItem:
    return FoodItem(
        food_id=int(r["food_id"]),
        food_name=str(r["food_name"]),
        meal_role=str(r["meal_role"]),
        serving_size=float(r["serving_size"]),
        kcal=float(r["kcal"]),
        carbohydrate=float(r["carbohydrate"]),
        protein=float(r["protein"]),
        fat=float(r["fat"]),
        sugar=float(r["sugar"]),
        sodium=float(r["sodium"]),
    )


def _retrieve_supabase(conditions, profile, relax: bool) -> dict:
    """Supabase pgvector 의미검색. 역할별로 match_foods RPC를 호출해 dict 구성."""
    from app.services.embedding_service import embed_query
    from app.services.supabase_client import get_client

    client = get_client()
    query_vec = embed_query(build_search_query(conditions))

    excluded = [x for x in (list(profile.allergies) + list(conditions.exclude_foods)) if x]
    max_kcal = conditions.target_kcal if (conditions.target_kcal and not relax) else None

    result: dict[str, list[FoodItem]] = {role: [] for role in ROLES}
    for role in ROLES:
        params = {
            "query_embedding": query_vec,
            "match_count": PER_ROLE,
            "role_filter": [role],
            "excluded_terms": excluded,
        }
        if max_kcal is not None:
            params["max_kcal"] = max_kcal
        rows = client.rpc("match_foods", params).execute().data or []
        result[role] = [_row_to_food(r) for r in rows]
    return result


def _retrieve_csv(conditions, profile, foods, relax: bool) -> dict:
    """Supabase 불가 시 fallback: CSV 전량에서 사실 축 필터만 적용(의미검색 없음)."""
    if foods is None:
        foods = load_foods()
    excluded = [x for x in (list(profile.allergies) + list(conditions.exclude_foods)) if x]
    max_kcal = conditions.target_kcal if (conditions.target_kcal and not relax) else None

    result: dict[str, list[FoodItem]] = {role: [] for role in ROLES}
    for food in foods:
        if food.meal_role not in ROLES:  # 기타 제외
            continue
        if any(x in food.food_name for x in excluded):
            continue
        if max_kcal and food.kcal > max_kcal:
            continue
        result[food.meal_role].append(food)
    return result


def retrieve_foods(conditions, profile, foods=None, relax=False) -> dict:
    """역할별 후보 반환: {"밥":[], "국물":[], "반찬":[], "한그릇":[]}.

    기본은 Supabase 의미검색. foods를 명시하거나 Supabase 실패 시 CSV fallback.
    """
    if foods is not None:  # 테스트에서 후보를 직접 주입한 경우
        return _retrieve_csv(conditions, profile, foods, relax)
    try:
        return _retrieve_supabase(conditions, profile, relax)
    except Exception as e:
        print(f"[retrieve Supabase 실패 → CSV fallback] {str(e)[:80]}")
        return _retrieve_csv(conditions, profile, None, relax)
