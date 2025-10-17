#!/usr/bin/env python3
"""
pythonanywhere에서 성능표기 일괄 등록 스크립트
사용법: python3 execute_performance_tags.py
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

    # 성능표기 등록 SQL 실행
    print("1. 미쉐린 성능표기 등록 중... (1,702개)")
    cursor.execute("""
        INSERT IGNORE INTO goods_performance_tags (goods_code, tag_id)
        SELECT
            g.CODE,
            pt.id
        FROM goods g
        CROSS JOIN (
            SELECT pt.id, pc.name as category, pt.name as tag_name
            FROM performance_tags pt
            JOIN performance_categories pc ON pt.category_id = pc.id
            WHERE (pc.name = 'comfort' AND pt.name = '탁월')
               OR (pc.name = 'handling' AND pt.name = '탁월')
               OR (pc.name = 'fuel' AND pt.name = '우수')
               OR (pc.name = 'noise' AND pt.name = '탁월')
        ) pt
        WHERE g.bun1 = '미쉐린'
    """)
    print(f"   ✅ {cursor.rowcount}개 등록 완료")

    print("\n2. 피렐리 성능표기 등록 중... (287개)")
    cursor.execute("""
        INSERT IGNORE INTO goods_performance_tags (goods_code, tag_id)
        SELECT
            g.CODE,
            pt.id
        FROM goods g
        CROSS JOIN (
            SELECT pt.id, pc.name as category, pt.name as tag_name
            FROM performance_tags pt
            JOIN performance_categories pc ON pt.category_id = pc.id
            WHERE (pc.name = 'comfort' AND pt.name = '탁월')
               OR (pc.name = 'handling' AND pt.name = '탁월')
               OR (pc.name = 'fuel' AND pt.name = '우수')
               OR (pc.name = 'noise' AND pt.name = '탁월')
        ) pt
        WHERE g.bun1 = '피렐리'
    """)
    print(f"   ✅ {cursor.rowcount}개 등록 완료")

    print("\n3. 콘티넨탈 성능표기 등록 중... (213개)")
    cursor.execute("""
        INSERT IGNORE INTO goods_performance_tags (goods_code, tag_id)
        SELECT
            g.CODE,
            pt.id
        FROM goods g
        CROSS JOIN (
            SELECT pt.id, pc.name as category, pt.name as tag_name
            FROM performance_tags pt
            JOIN performance_categories pc ON pt.category_id = pc.id
            WHERE (pc.name = 'comfort' AND pt.name = '탁월')
               OR (pc.name = 'handling' AND pt.name = '탁월')
               OR (pc.name = 'fuel' AND pt.name = '우수')
               OR (pc.name = 'noise' AND pt.name = '탁월')
        ) pt
        WHERE g.bun1 = '콘티넨탈'
    """)
    print(f"   ✅ {cursor.rowcount}개 등록 완료")

    print("\n4. 브리지스톤 성능표기 등록 중... (123개)")
    cursor.execute("""
        INSERT IGNORE INTO goods_performance_tags (goods_code, tag_id)
        SELECT
            g.CODE,
            pt.id
        FROM goods g
        CROSS JOIN (
            SELECT pt.id, pc.name as category, pt.name as tag_name
            FROM performance_tags pt
            JOIN performance_categories pc ON pt.category_id = pc.id
            WHERE (pc.name = 'comfort' AND pt.name = '우수')
               OR (pc.name = 'handling' AND pt.name = '우수')
               OR (pc.name = 'fuel' AND pt.name = '우수')
               OR (pc.name = 'noise' AND pt.name = '우수')
        ) pt
        WHERE g.bun1 = '브리지스톤'
    """)
    print(f"   ✅ {cursor.rowcount}개 등록 완료")

    print("\n5. 던롭 성능표기 등록 중... (66개)")
    cursor.execute("""
        INSERT IGNORE INTO goods_performance_tags (goods_code, tag_id)
        SELECT
            g.CODE,
            pt.id
        FROM goods g
        CROSS JOIN (
            SELECT pt.id, pc.name as category, pt.name as tag_name
            FROM performance_tags pt
            JOIN performance_categories pc ON pt.category_id = pc.id
            WHERE (pc.name = 'comfort' AND pt.name = '우수')
               OR (pc.name = 'handling' AND pt.name = '우수')
               OR (pc.name = 'fuel' AND pt.name = '우수')
               OR (pc.name = 'noise' AND pt.name = '우수')
        ) pt
        WHERE g.bun1 = '던롭'
    """)
    print(f"   ✅ {cursor.rowcount}개 등록 완료")

    print("\n6. 굳이어 성능표기 등록 중... (114개)")
    cursor.execute("""
        INSERT IGNORE INTO goods_performance_tags (goods_code, tag_id)
        SELECT
            g.CODE,
            pt.id
        FROM goods g
        CROSS JOIN (
            SELECT pt.id, pc.name as category, pt.name as tag_name
            FROM performance_tags pt
            JOIN performance_categories pc ON pt.category_id = pc.id
            WHERE (pc.name = 'comfort' AND pt.name = '우수')
               OR (pc.name = 'handling' AND pt.name = '우수')
               OR (pc.name = 'fuel' AND pt.name = '우수')
               OR (pc.name = 'noise' AND pt.name = '우수')
        ) pt
        WHERE g.bun1 = '굳이어'
    """)
    print(f"   ✅ {cursor.rowcount}개 등록 완료")

    print("\n7. 금호 성능표기 등록 중... (1,739개)")
    cursor.execute("""
        INSERT IGNORE INTO goods_performance_tags (goods_code, tag_id)
        SELECT
            g.CODE,
            pt.id
        FROM goods g
        CROSS JOIN (
            SELECT pt.id, pc.name as category, pt.name as tag_name
            FROM performance_tags pt
            JOIN performance_categories pc ON pt.category_id = pc.id
            WHERE (pc.name = 'comfort' AND pt.name = '우수')
               OR (pc.name = 'handling' AND pt.name = '양호')
               OR (pc.name = 'fuel' AND pt.name = '탁월')
               OR (pc.name = 'noise' AND pt.name = '우수')
        ) pt
        WHERE g.bun1 = '금호'
    """)
    print(f"   ✅ {cursor.rowcount}개 등록 완료")

    print("\n8. 넥센 성능표기 등록 중... (810개)")
    cursor.execute("""
        INSERT IGNORE INTO goods_performance_tags (goods_code, tag_id)
        SELECT
            g.CODE,
            pt.id
        FROM goods g
        CROSS JOIN (
            SELECT pt.id, pc.name as category, pt.name as tag_name
            FROM performance_tags pt
            JOIN performance_categories pc ON pt.category_id = pc.id
            WHERE (pc.name = 'comfort' AND pt.name = '우수')
               OR (pc.name = 'handling' AND pt.name = '양호')
               OR (pc.name = 'fuel' AND pt.name = '탁월')
               OR (pc.name = 'noise' AND pt.name = '우수')
        ) pt
        WHERE g.bun1 = '넥센'
    """)
    print(f"   ✅ {cursor.rowcount}개 등록 완료")

    print("\n9. 한국 성능표기 등록 중... (746개)")
    cursor.execute("""
        INSERT IGNORE INTO goods_performance_tags (goods_code, tag_id)
        SELECT
            g.CODE,
            pt.id
        FROM goods g
        CROSS JOIN (
            SELECT pt.id, pc.name as category, pt.name as tag_name
            FROM performance_tags pt
            JOIN performance_categories pc ON pt.category_id = pc.id
            WHERE (pc.name = 'comfort' AND pt.name = '우수')
               OR (pc.name = 'handling' AND pt.name = '양호')
               OR (pc.name = 'fuel' AND pt.name = '탁월')
               OR (pc.name = 'noise' AND pt.name = '우수')
        ) pt
        WHERE g.bun1 = '한국'
    """)
    print(f"   ✅ {cursor.rowcount}개 등록 완료")

    print("\n10. 기타 브랜드 성능표기 등록 중...")
    cursor.execute("""
        INSERT IGNORE INTO goods_performance_tags (goods_code, tag_id)
        SELECT
            g.CODE,
            pt.id
        FROM goods g
        CROSS JOIN (
            SELECT pt.id, pc.name as category, pt.name as tag_name
            FROM performance_tags pt
            JOIN performance_categories pc ON pt.category_id = pc.id
            WHERE (pc.name = 'comfort' AND pt.name = '양호')
               OR (pc.name = 'handling' AND pt.name = '양호')
               OR (pc.name = 'fuel' AND pt.name = '우수')
               OR (pc.name = 'noise' AND pt.name = '양호')
        ) pt
        WHERE g.bun1 IN ('하이로', 'BFG', '안나이트', '맥시스', '하이플라이', '파이어스톤')
    """)
    print(f"   ✅ {cursor.rowcount}개 등록 완료")

    # 커밋
    conn.commit()
    print("\n" + "="*60)
    print("✅ 모든 성능표기 등록 완료!")
    print("="*60)

    # 결과 확인
    print("\n📊 등록 결과:")
    cursor.execute("""
        SELECT
            COUNT(DISTINCT goods_code) as total_products,
            COUNT(*) as total_tags
        FROM goods_performance_tags
    """)
    result = cursor.fetchone()
    print(f"   - 성능표기가 있는 상품: {result[0]:,}개")
    print(f"   - 총 성능표기 개수: {result[1]:,}개")

    # 브랜드별 확인
    print("\n📊 브랜드별 등록 현황:")
    cursor.execute("""
        SELECT
            g.bun1 as brand,
            COUNT(DISTINCT g.CODE) as total_products,
            COUNT(DISTINCT gpt.goods_code) as tagged_products
        FROM goods g
        LEFT JOIN goods_performance_tags gpt ON g.CODE = gpt.goods_code
        WHERE g.bun1 IN ('금호', '미쉐린', '넥센', '한국', '피렐리', '콘티넨탈', '브리지스톤', '굳이어', '던롭')
        GROUP BY g.bun1
        ORDER BY COUNT(DISTINCT g.CODE) DESC
    """)

    for row in cursor.fetchall():
        brand, total, tagged = row
        rate = (tagged / total * 100) if total > 0 else 0
        print(f"   {brand:10s}: {tagged:4d}/{total:4d} ({rate:5.1f}%)")

    cursor.close()
    conn.close()

    print("\n✅ 완료! 웹앱을 Reload 하세요.")
    print("   https://www.pythonanywhere.com/user/tirepass/webapps/")

except MySQLdb.Error as e:
    print(f"\n❌ MySQL 오류: {e}")
    sys.exit(1)
except KeyboardInterrupt:
    print("\n\n중단되었습니다.")
    sys.exit(0)
