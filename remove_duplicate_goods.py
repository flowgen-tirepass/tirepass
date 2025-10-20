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

    # 2. 각 중복 CODE의 상세 정보 확인
    print("\n2단계: 중복 레코드 상세 확인...")
    for code, count in duplicates:
        print(f"\n  상품코드: {code}")
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT CODE, NAME, BUN1, JAEGO, FIXP
                FROM goods
                WHERE CODE = %s
            """, [code])
            rows = cursor.fetchall()
            for i, (c, name, bun1, jaego, fixp) in enumerate(rows, 1):
                print(f"    [{i}] 상품명: {name}")
                print(f"        브랜드: {bun1}")
                print(f"        재고: {jaego}")
                print(f"        가격: {fixp}")

    # 3. 중복 제거 방법 안내
    print("\n" + "=" * 60)
    print("⚠️  주의: Goods 테이블의 Primary Key는 CODE입니다.")
    print("중복된 레코드가 존재하는 것은 비정상적인 상황입니다.")
    print("")
    print("=== 방법 1: 간단한 중복 제거 (추천) ===")
    print("PythonAnywhere MySQL Console에서 실행:")
    print("")
    print("-- 중복된 모든 레코드를 삭제하고 하나만 남기기")
    print("DELETE t1 FROM goods t1")
    print("INNER JOIN goods t2")
    print("WHERE t1.CODE = t2.CODE")
    print("  AND (t1.JAEGO < t2.JAEGO OR (t1.JAEGO = t2.JAEGO AND t1.NAME > t2.NAME));")
    print("")
    print("-- 설명: 재고가 많은 레코드를 우선 유지, 재고 동일하면 NAME 순서로 첫 번째 유지")
    print("")
    print("=== 방법 2: 수동으로 확인 후 제거 ===")
    print("")
    for code, count in duplicates:
        print(f"-- {code} 중복 제거")
        print(f"SELECT * FROM goods WHERE CODE = '{code}';")
        print(f"-- 위 결과를 보고 남길 레코드를 결정한 후:")
        print(f"-- (예시) 두 번째 레코드를 삭제하려면:")
        print(f"DELETE FROM goods WHERE CODE = '{code}' AND NAME = '...(삭제할 레코드의 NAME)';")
        print("")

    removed_count = 0  # 자동 삭제는 하지 않음

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
