#!/usr/bin/env python3
"""
pythonanywhere goods 테이블 구조 확인 스크립트
사용법: python3 check_goods_schema.py
"""

import MySQLdb
import sys

# pythonanywhere MySQL 연결 정보
DB_HOST = 'tirepass.mysql.pythonanywhere-services.com'
DB_USER = 'tirepass'
DB_NAME = 'tirepass$itire_db'
DB_PASSWORD = input('MySQL 비밀번호 입력: ')

print(f"\n데이터베이스 연결 중: {DB_NAME}...")

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

    print("✅ 데이터베이스 연결 성공!\n")

    # goods 테이블 구조 확인
    print("=" * 60)
    print("goods 테이블 구조:")
    print("=" * 60)
    cursor.execute("DESCRIBE goods")

    columns = cursor.fetchall()
    print(f"\n{'필드명':<20} {'타입':<20} {'Null':<6} {'Key':<6}")
    print("-" * 60)
    for col in columns:
        field, type_name, null, key = col[0], col[1], col[2], col[3]
        print(f"{field:<20} {type_name:<20} {null:<6} {key:<6}")

    # 샘플 데이터 확인
    print("\n" + "=" * 60)
    print("샘플 데이터 (피렐리 상품 1개):")
    print("=" * 60)
    cursor.execute("SELECT * FROM goods WHERE CODE = 'P-CP7R-04' LIMIT 1")

    row = cursor.fetchone()
    if row:
        col_names = [desc[0] for desc in cursor.description]
        print("\n")
        for i, col_name in enumerate(col_names):
            value = row[i]
            if value is not None and len(str(value)) > 50:
                value = str(value)[:50] + "..."
            print(f"{col_name:<20}: {value}")
    else:
        print("P-CP7R-04 상품을 찾을 수 없습니다.")

    # 브랜드명 컬럼 추정
    print("\n" + "=" * 60)
    print("브랜드별 상품 수 확인 (상위 10개):")
    print("=" * 60)

    # 여러 컬럼명 시도
    possible_brand_columns = ['brand', 'bun1', 'BRAND', 'BUN1', 'maker', 'MAKER']

    for col in possible_brand_columns:
        try:
            cursor.execute(f"SELECT {col}, COUNT(*) as cnt FROM goods GROUP BY {col} ORDER BY cnt DESC LIMIT 10")
            results = cursor.fetchall()
            if results:
                print(f"\n✅ 브랜드 컬럼명: {col}")
                print(f"{'브랜드명':<20} {'상품수':<10}")
                print("-" * 30)
                for brand, count in results:
                    print(f"{str(brand):<20} {count:<10}")
                break
        except MySQLdb.Error:
            continue
    else:
        print("❌ 브랜드 컬럼을 찾을 수 없습니다.")

    cursor.close()
    conn.close()

    print("\n✅ 확인 완료!")

except MySQLdb.Error as e:
    print(f"\n❌ MySQL 오류: {e}")
    sys.exit(1)
except KeyboardInterrupt:
    print("\n\n중단되었습니다.")
    sys.exit(0)
