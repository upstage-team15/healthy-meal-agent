"""
scripts/import_foods_to_supabase.py
foods_clean.csv → Supabase foods 테이블 upsert.

- 사용자가 원할 때만 수동 실행하는 1회성 배치 (배포 런타임에는 안 돎).
- food_id 기준 upsert → 재실행 안전. 같은 id는 영양값 갱신, 새 id는 추가.
- 이 스크립트는 영양/이름/역할만 넣는다. search_text/embedding은 embed_foods.py가 채운다.

실행:
    uv run python scripts/import_foods_to_supabase.py
"""

from pathlib import Path

import pandas as pd

from app.services.supabase_client import get_client

CSV_PATH = Path(__file__).resolve().parent.parent / "app" / "data" / "foods_clean.csv"
COLUMNS = [
    "food_id",
    "food_name",
    "meal_role",
    "serving_size",
    "kcal",
    "carbohydrate",
    "protein",
    "fat",
    "sugar",
    "sodium",
]


def main() -> None:
    df = pd.read_csv(CSV_PATH)
    missing = [c for c in COLUMNS if c not in df.columns]
    if missing:
        raise SystemExit(f"CSV에 누락된 컬럼: {missing}")

    records = df[COLUMNS].to_dict(orient="records")
    for r in records:
        r["food_id"] = int(r["food_id"])
        for k in COLUMNS[3:]:
            r[k] = float(r[k])

    client = get_client()
    # food_id 유니크 제약 기준 upsert. 큰 배치는 나눠서.
    batch = 500
    total = 0
    for i in range(0, len(records), batch):
        chunk = records[i : i + batch]
        client.table("foods").upsert(chunk, on_conflict="food_id").execute()
        total += len(chunk)
        print(f"  upsert {total}/{len(records)}")

    count = client.table("foods").select("food_id", count="exact").limit(1).execute().count
    print(f"완료. foods 테이블 총 {count}개.")


if __name__ == "__main__":
    main()
