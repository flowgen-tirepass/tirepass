"""
Goods 테이블에서 중복된 레코드 제거

PythonAnywhere Bash console에서 실행:
cd ~/1.0_tirepass
source venv/bin/activate
python manage.py shell < remove_duplicate_goods.py
"""

from tire_data.models import Goods
from django.db.models import Count
from django.db import connection

print("=" * 60)
print("Goods 테이블 중복 레코드 확인 및 제거")
print("=" * 60)

# 1. 중복된 CODE 찾기
print("\n1단계: 중복된 상품 코드 확인...")
with connection.cursor() as cursor:
    cursor.execute("""
        SELECT CODE, COUNT(*) as cnt
        FROM goods
        GROUP BY CODE
        HAVING COUNT(*) > 1
        ORDER BY cnt DESC
    """)
    duplicates = cursor.fetchall()

if not duplicates:
    print("✓ 중복된 상품 코드가 없습니다!")
else:
    print(f"\n⚠️  총 {len(duplicates)}개의 중복된 상품 코드 발견:")
    for code, count in duplicates:
        print(f"  - {code}: {count}개")

    # 2. 각 중복 CODE에 대해 가장 최근 레코드만 남기고 나머지 삭제
    print("\n2단계: 중복 레코드 제거 중...")
    removed_count = 0

    for code, count in duplicates:
        # 해당 CODE의 모든 레코드 조회 (PK 기준 정렬)
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id FROM goods
                WHERE CODE = %s
                ORDER BY id DESC
            """, [code])
            ids = [row[0] for row in cursor.fetchall()]

        if len(ids) > 1:
            # 첫 번째(최신) ID를 제외한 나머지 삭제
            keep_id = ids[0]
            delete_ids = ids[1:]

            with connection.cursor() as cursor:
                placeholders = ','.join(['%s'] * len(delete_ids))
                cursor.execute(f"""
                    DELETE FROM goods
                    WHERE id IN ({placeholders})
                """, delete_ids)
                deleted = cursor.rowcount
                removed_count += deleted

            print(f"  ✓ {code}: {deleted}개 제거 (ID {keep_id} 유지)")

    print(f"\n완료! 총 {removed_count}개의 중복 레코드를 제거했습니다.")

# 3. 최종 확인
print("\n3단계: 최종 확인...")
with connection.cursor() as cursor:
    cursor.execute("""
        SELECT CODE, COUNT(*) as cnt
        FROM goods
        GROUP BY CODE
        HAVING COUNT(*) > 1
    """)
    remaining_duplicates = cursor.fetchall()

if not remaining_duplicates:
    print("✓ 모든 중복이 제거되었습니다!")
else:
    print(f"⚠️  아직 {len(remaining_duplicates)}개의 중복이 남아있습니다:")
    for code, count in remaining_duplicates:
        print(f"  - {code}: {count}개")

print("\n" + "=" * 60)
