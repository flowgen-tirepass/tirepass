#!/usr/bin/env python3
"""
DOT 재고 자동 배정 스크립트
- 재고 1~4개: 2025년에 전체 등록
- 재고 5개 이상: 2021년 이전~2024년 각 1개씩, 나머지는 2025년

사용법: python3 auto_assign_dot_inventory.py
"""

import MySQLdb
import sys
from datetime import datetime

# MySQL 연결 정보 (로컬/pythonanywhere 자동 감지)
DB_HOST = input('MySQL 호스트 (로컬이면 Enter, pythonanywhere면 전체 주소 입력): ').strip()
if not DB_HOST:
    DB_HOST = 'localhost'
    DB_USER = 'root'
    DB_PASSWORD = 'tirepass'
    DB_NAME = 'itire_db'
else:
    DB_USER = 'tirepass'
    DB_NAME = 'tirepass$itire_db'
    DB_PASSWORD = input('MySQL 비밀번호 입력: ')

print(f"\n데이터베이스 연결 중: {DB_NAME} @ {DB_HOST}...")

try:
    # MySQL 연결
    conn = MySQLdb.connect(
        host=DB_HOST,
        user=DB_USER,
        passwd=DB_PASSWORD,
        db=DB_NAME,
        charset='utf8mb4'
    )
    cursor = conn.cursor()

    print("[성공] 데이터베이스 연결 성공!\n")

    # 현재 상태 확인
    print("=" * 60)
    print("현재 DOT 재고 상태 확인")
    print("=" * 60)

    cursor.execute("SELECT COUNT(*) FROM year_allocations")
    existing_count = cursor.fetchone()[0]
    print(f"기존 year_allocations 레코드: {existing_count}개")

    cursor.execute("SELECT COUNT(*) FROM goods WHERE JAEGO >= 1")
    total_with_stock = cursor.fetchone()[0]
    print(f"재고 있는 상품: {total_with_stock}개")

    cursor.execute("SELECT COUNT(*) FROM goods WHERE JAEGO >= 5")
    stock_5_or_more = cursor.fetchone()[0]
    print(f"재고 5개 이상 상품: {stock_5_or_more}개")

    cursor.execute("SELECT COUNT(*) FROM goods WHERE JAEGO BETWEEN 1 AND 4")
    stock_1_to_4 = cursor.fetchone()[0]
    print(f"재고 1~4개 상품: {stock_1_to_4}개")

    # 사용자 확인
    print("\n" + "=" * 60)
    print("DOT 재고 자동 배정 규칙:")
    print("=" * 60)
    print("재고 1~4개   : 2025년에 전체 등록")
    print("재고 5개 이상 : 2021년 이전~2024년 각 1개, 나머지는 2025년")
    print("\n예시:")
    print("  재고 3개  → 2025년: 3개")
    print("  재고 5개  → 2025년: 1개, 2024년: 1개, 2023년: 1개, 2022년: 1개, 2021년 이전: 1개")
    print("  재고 15개 → 2025년: 11개, 2024년: 1개, 2023년: 1개, 2022년: 1개, 2021년 이전: 1개")
    print("=" * 60)

    confirm = input("\n계속 진행하시겠습니까? (yes/no): ").lower()
    if confirm != 'yes':
        print("취소되었습니다.")
        sys.exit(0)

    # 기존 데이터 삭제 (재실행 시)
    print("\n기존 year_allocations 데이터 삭제 중...")
    cursor.execute("DELETE FROM year_allocations")
    deleted_count = cursor.rowcount
    print(f"[성공] {deleted_count}개 레코드 삭제 완료")

    # 재고 있는 모든 상품 조회
    print("\n재고 있는 상품 조회 중...")
    cursor.execute("""
        SELECT CODE, JAEGO
        FROM goods
        WHERE JAEGO >= 1
        ORDER BY JAEGO DESC
    """)

    products = cursor.fetchall()
    print(f"[성공] {len(products)}개 상품 조회 완료\n")

    # DOT 배정 로직
    print("=" * 60)
    print("DOT 재고 배정 시작")
    print("=" * 60)

    inserted_count = 0
    now = datetime.now()

    for code, stock in products:
        if stock <= 4:
            # 재고 1~4개: 2025년에 전체
            year_2025 = stock
            year_2024 = 0
            year_2023 = 0
            year_2022 = 0
            year_2021_before = 0
        else:
            # 재고 5개 이상: 각 연도 1개씩, 나머지는 2025년
            year_2025 = stock - 4
            year_2024 = 1
            year_2023 = 1
            year_2022 = 1
            year_2021_before = 1

        # 삽입
        cursor.execute("""
            INSERT INTO year_allocations
            (goods_code, year_2025, year_2024, year_2023, year_2022, year_2021_before,
             last_updated, base_discount, year_2024_discount, year_2023_discount,
             year_2022_discount, year_2021_before_discount)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 0.00, 0.00, 0.00, 0.00, 0.00)
        """, (code, year_2025, year_2024, year_2023, year_2022, year_2021_before, now))

        inserted_count += 1

        # 진행상황 표시 (100개마다)
        if inserted_count % 100 == 0:
            print(f"  진행중... {inserted_count}/{len(products)}개")

    # 커밋
    conn.commit()
    print(f"\n[성공] {inserted_count}개 상품 DOT 재고 배정 완료!")

    # 결과 확인
    print("\n" + "=" * 60)
    print("배정 결과 통계")
    print("=" * 60)

    cursor.execute("""
        SELECT
            COUNT(*) as total,
            SUM(year_2025) as total_2025,
            SUM(year_2024) as total_2024,
            SUM(year_2023) as total_2023,
            SUM(year_2022) as total_2022,
            SUM(year_2021_before) as total_2021_before
        FROM year_allocations
    """)

    result = cursor.fetchone()
    print(f"총 상품 수: {result[0]:,}개")
    print(f"2025년 재고: {result[1]:,}개")
    print(f"2024년 재고: {result[2]:,}개")
    print(f"2023년 재고: {result[3]:,}개")
    print(f"2022년 재고: {result[4]:,}개")
    print(f"2021년 이전: {result[5]:,}개")
    print(f"총 DOT 재고: {sum(result[1:]):,}개")

    # 샘플 확인
    print("\n" + "=" * 60)
    print("샘플 확인 (재고 많은 상위 5개)")
    print("=" * 60)

    cursor.execute("""
        SELECT
            ya.goods_code,
            g.JAEGO as stock,
            ya.year_2025,
            ya.year_2024,
            ya.year_2023,
            ya.year_2022,
            ya.year_2021_before
        FROM year_allocations ya
        JOIN goods g ON ya.goods_code = g.CODE
        ORDER BY g.JAEGO DESC
        LIMIT 5
    """)

    print(f"\n{'상품코드':<15} {'재고':<6} {'2025':<6} {'2024':<6} {'2023':<6} {'2022':<6} {'2021이전':<8}")
    print("-" * 60)
    for row in cursor.fetchall():
        code, stock, y2025, y2024, y2023, y2022, y2021 = row
        print(f"{code:<15} {stock:<6} {y2025:<6} {y2024:<6} {y2023:<6} {y2022:<6} {y2021:<8}")

    # 재고 1~4개 샘플
    print("\n" + "=" * 60)
    print("샘플 확인 (재고 1~4개 중 5개)")
    print("=" * 60)

    cursor.execute("""
        SELECT
            ya.goods_code,
            g.JAEGO as stock,
            ya.year_2025,
            ya.year_2024,
            ya.year_2023,
            ya.year_2022,
            ya.year_2021_before
        FROM year_allocations ya
        JOIN goods g ON ya.goods_code = g.CODE
        WHERE g.JAEGO BETWEEN 1 AND 4
        LIMIT 5
    """)

    print(f"\n{'상품코드':<15} {'재고':<6} {'2025':<6} {'2024':<6} {'2023':<6} {'2022':<6} {'2021이전':<8}")
    print("-" * 60)
    for row in cursor.fetchall():
        code, stock, y2025, y2024, y2023, y2022, y2021 = row
        print(f"{code:<15} {stock:<6} {y2025:<6} {y2024:<6} {y2023:<6} {y2022:<6} {y2021:<8}")

    cursor.close()
    conn.close()

    print("\n[완료] 웹앱을 Reload 하세요.")
    if 'pythonanywhere' in DB_HOST:
        print("   https://www.pythonanywhere.com/user/tirepass/webapps/")

except MySQLdb.Error as e:
    print(f"\n[오류] MySQL 오류: {e}")
    sys.exit(1)
except KeyboardInterrupt:
    print("\n\n중단되었습니다.")
    sys.exit(0)
