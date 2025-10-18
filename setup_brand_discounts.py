#!/usr/bin/env python3
"""
브랜드별 기본 할인율 일괄 설정 스크립트

사용법:
- 로컬: python3 setup_brand_discounts.py
- pythonanywhere: python3 setup_brand_discounts.py

할인율:
- 프리미엄 브랜드 (미쉐린, 피렐리, 콘티넨탈): 20%
- 중급 수입 브랜드 (브리지스톤, 던롭, 굳이어, 요코하마): 15%
- 국산 브랜드 (금호, 넥센, 한국): 10%
- 기타 브랜드 (하이로, BFG, 안나이트, 맥시스, 하이플라이, 파이어스톤): 5%
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
    print("현재 할인율 설정 상태")
    print("=" * 60)

    cursor.execute("""
        SELECT g.bun1, COUNT(*) as total, AVG(ya.base_discount) as avg_discount
        FROM year_allocations ya
        JOIN goods g ON ya.goods_code = g.CODE
        WHERE g.bun1 IS NOT NULL AND g.bun1 != ''
        GROUP BY g.bun1
        ORDER BY total DESC
        LIMIT 10
    """)

    print(f"\n{'브랜드':<15} {'상품수':<10} {'평균 할인율':<15}")
    print("-" * 60)
    for row in cursor.fetchall():
        brand, total, avg_discount = row
        print(f"{brand:<15} {total:<10} {avg_discount:>12.2f}%")

    # 사용자 확인
    print("\n" + "=" * 60)
    print("브랜드별 할인율 설정 규칙:")
    print("=" * 60)
    print("프리미엄 브랜드 (20%): 미쉐린, 피렐리, 콘티넨탈")
    print("중급 수입 브랜드 (15%): 브리지스톤, 던롭, 굳이어, 요코하마")
    print("국산 브랜드 (10%): 금호, 넥센, 한국")
    print("기타 브랜드 (5%): 하이로, BFG, 안나이트, 맥시스, 하이플라이, 파이어스톤")
    print("=" * 60)

    confirm = input("\n계속 진행하시겠습니까? (yes/no): ").lower()
    if confirm != 'yes':
        print("취소되었습니다.")
        sys.exit(0)

    # 할인율 설정 시작
    print("\n" + "=" * 60)
    print("브랜드별 할인율 설정 시작 (안전 모드)")
    print("=" * 60)

    # 브랜드별 할인율 매핑
    brand_discounts = [
        ('미쉐린', 20.00, '프리미엄'),
        ('피렐리', 20.00, '프리미엄'),
        ('콘티넨탈', 20.00, '프리미엄'),
        ('브리지스톤', 15.00, '중급 수입'),
        ('던롭', 15.00, '중급 수입'),
        ('굳이어', 15.00, '중급 수입'),
        ('요코하마', 15.00, '중급 수입'),
        ('금호', 10.00, '국산'),
        ('넥센', 10.00, '국산'),
        ('한국', 10.00, '국산'),
        ('하이로', 5.00, '기타'),
        ('BFG', 5.00, '기타'),
        ('안나이트', 5.00, '기타'),
        ('맥시스', 5.00, '기타'),
        ('하이플라이', 5.00, '기타'),
        ('파이어스톤', 5.00, '기타'),
    ]

    total_updated = 0

    # 브랜드별로 하나씩 순차적으로 업데이트 (데드락 방지)
    for idx, (brand, discount, category) in enumerate(brand_discounts, 1):
        print(f"\n{idx}. {brand} ({category}) 할인율 설정 중... ({discount}%)")

        try:
            # 해당 브랜드의 상품 코드 조회
            cursor.execute("""
                SELECT CODE FROM goods WHERE bun1 = %s
            """, (brand,))

            codes = [row[0] for row in cursor.fetchall()]

            if not codes:
                print(f"   [건너뜀] {brand} 상품이 없습니다.")
                continue

            # 작은 배치로 나누어 업데이트 (한 번에 100개씩)
            batch_size = 100
            updated_count = 0

            for i in range(0, len(codes), batch_size):
                batch_codes = codes[i:i+batch_size]
                placeholders = ','.join(['%s'] * len(batch_codes))

                cursor.execute(f"""
                    UPDATE year_allocations
                    SET base_discount = %s
                    WHERE goods_code IN ({placeholders})
                """, [discount] + batch_codes)

                updated_count += cursor.rowcount

                # 각 배치마다 커밋 (데드락 방지)
                conn.commit()

            total_updated += updated_count
            print(f"   [성공] {updated_count}개 상품 업데이트 완료")

        except MySQLdb.Error as e:
            print(f"   [오류] {brand} 업데이트 실패: {e}")
            conn.rollback()
            continue

    print(f"\n[성공] 총 {total_updated}개 상품 할인율 설정 완료!")

    # 결과 확인
    print("\n" + "=" * 60)
    print("설정 결과 확인")
    print("=" * 60)

    cursor.execute("""
        SELECT g.bun1, COUNT(*) as total, AVG(ya.base_discount) as avg_discount
        FROM year_allocations ya
        JOIN goods g ON ya.goods_code = g.CODE
        WHERE g.bun1 IS NOT NULL AND g.bun1 != ''
        GROUP BY g.bun1
        ORDER BY avg_discount DESC, total DESC
        LIMIT 20
    """)

    print(f"\n{'브랜드':<15} {'상품수':<10} {'평균 할인율':<15}")
    print("-" * 60)
    for row in cursor.fetchall():
        brand, total, avg_discount = row
        print(f"{brand:<15} {total:<10} {avg_discount:>12.2f}%")

    # 샘플 확인
    print("\n" + "=" * 60)
    print("샘플 확인 (할인율 높은 상품)")
    print("=" * 60)

    cursor.execute("""
        SELECT
            g.CODE,
            g.NAME,
            g.bun1,
            g.FIXP as factory_price,
            ya.base_discount,
            ROUND(g.FIXP * (1 - ya.base_discount / 100)) as supply_price
        FROM goods g
        JOIN year_allocations ya ON g.CODE = ya.goods_code
        WHERE ya.base_discount > 0
        ORDER BY ya.base_discount DESC, g.FIXP DESC
        LIMIT 5
    """)

    print(f"\n{'코드':<15} {'상품명':<40} {'브랜드':<10} {'공장도가':<12} {'할인율':<8} {'공급가':<12}")
    print("-" * 120)
    for row in cursor.fetchall():
        code, name, brand, factory_price, discount, supply_price = row
        # 상품명이 길면 잘라내기
        name_short = name[:37] + '...' if len(name) > 40 else name
        print(f"{code:<15} {name_short:<40} {brand:<10} {factory_price:>10,}원 {discount:>6.0f}% {supply_price:>10,}원")

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
