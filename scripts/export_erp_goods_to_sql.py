"""
ERP Firebird에서 GOODS 데이터를 가져와 SQL INSERT 파일 생성

실행:
    python scripts/export_erp_goods_to_sql.py
"""

import fdb
from datetime import datetime

# ERP Firebird 연결 정보
FIREBIRD_CONFIG = {
    'host': 'ITIRE2.iptime.org',
    'database': r'C:\Program Files\PsimCarS\Data\ITIRE.GDB',
    'user': 'SYSDBA',
    'password': 'masterkey',
    'charset': 'UTF8'
}


def safe_str(value):
    """안전하게 문자열 변환 및 이스케이프"""
    if value is None:
        return ''

    str_value = str(value).strip()
    # SQL 이스케이프 (작은따옴표)
    return str_value.replace("'", "''")


def export_goods_to_sql():
    """ERP GOODS 데이터를 SQL INSERT 문으로 생성"""
    print("=== ERP Firebird 서버 연결 중 ===")
    print(f"호스트: {FIREBIRD_CONFIG['host']}")

    try:
        conn = fdb.connect(**FIREBIRD_CONFIG)
        cursor = conn.cursor()

        # GOODS 테이블에서 데이터 조회
        query = """
            SELECT CODE, NAME, BUN1, JAEGO, FIXP
            FROM GOODS
            ORDER BY CODE
        """

        print("\nGOODS 테이블 조회 중...")
        cursor.execute(query)
        goods = cursor.fetchall()

        print(f"총 {len(goods)}개의 상품 데이터를 가져왔습니다.")

        # 샘플 데이터 출력
        if goods:
            sample = goods[0]
            print(f"\n샘플 데이터:")
            print(f"  CODE: {sample[0]}")
            print(f"  NAME: {sample[1]}")
            print(f"  BUN1: {sample[2]}")
            print(f"  JAEGO: {sample[3]}")
            print(f"  FIXP: {sample[4]}")

        cursor.close()
        conn.close()

        # SQL 파일 생성
        output_file = 'erp_goods_insert.sql'

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("-- ERP GOODS 데이터 INSERT (UTF-8)\n")
            f.write(f"-- 생성일: {datetime.now()}\n")
            f.write(f"-- 총 {len(goods)}개\n\n")

            f.write("-- pythonanywhere MySQL 사용\n")
            f.write("-- mysql -h tirepass.mysql.pythonanywhere-services.com -u tirepass -p tirepass$itire_db < erp_goods_insert.sql\n\n")

            # 기존 데이터 삭제
            f.write("TRUNCATE TABLE goods;\n\n")

            batch_size = 100
            count = 0

            for i, row in enumerate(goods):
                code, name, bun1, jaego, fixp = row

                # NULL 처리
                code_clean = safe_str(code)
                name_clean = safe_str(name)
                bun1_clean = safe_str(bun1) if bun1 else ''
                jaego_val = int(jaego) if jaego else 0
                fixp_val = int(fixp) if fixp else 0

                if count % batch_size == 0:
                    if count > 0:
                        f.write(";\n\n")
                    f.write("INSERT INTO goods (CODE, NAME, BUN1, JAEGO, FIXP) VALUES\n")
                else:
                    f.write(",\n")

                f.write(f"  ('{code_clean}', '{name_clean}', '{bun1_clean}', {jaego_val}, {fixp_val})")

                count += 1

            if count > 0:
                f.write(";\n")

        print(f"\n=== SQL 파일 생성 완료 ===")
        print(f"파일: {output_file}")
        print(f"상품 수: {count}개")
        print(f"\npythonanywhere에서 실행:")
        print(f"  mysql -h tirepass.mysql.pythonanywhere-services.com -u tirepass -p tirepass\\$itire_db < {output_file}")

    except Exception as e:
        print(f"에러: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    export_goods_to_sql()
