"""
ERP Firebird에서 고객 데이터를 가져와 SQL INSERT 파일 생성

실행:
    python scripts/export_erp_to_sql.py
"""

import fdb

# ERP Firebird 연결 정보
FIREBIRD_CONFIG = {
    'host': 'ITIRE2.iptime.org',
    'database': r'C:\Program Files\PsimCarS\Data\ITIRE.GDB',
    'user': 'SYSDBA',
    'password': 'masterkey',
    'charset': 'UTF8'
}


def export_to_sql():
    """ERP 데이터를 SQL INSERT 문으로 생성"""
    print("=== ERP Firebird 서버 연결 중... ===")

    try:
        conn = fdb.connect(**FIREBIRD_CONFIG)
        cursor = conn.cursor()

        # CUSTOMS 테이블에서 데이터 조회
        query = """
            SELECT CODE, NAME, REP, ENNO
            FROM CUSTOMS
            WHERE ENNO IS NOT NULL AND ENNO <> ''
        """

        cursor.execute(query)
        customers = cursor.fetchall()

        print(f"총 {len(customers)}명의 고객 데이터를 가져왔습니다.")

        cursor.close()
        conn.close()

        # SQL 파일 생성
        output_file = 'erp_customers_insert.sql'

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("-- ERP 고객 데이터 INSERT\n")
            f.write(f"-- 생성일: {datetime.now()}\n")
            f.write(f"-- 총 {len(customers)}명\n\n")

            f.write("USE tirepass$itire_db;\n\n")

            batch_size = 100
            valid_count = 0

            for i, customer in enumerate(customers):
                code, name, rep, enno = customer

                # 사업자번호 정제
                if not enno:
                    continue

                enno_clean = str(enno).replace('-', '').strip()

                if not enno_clean.isdigit() or len(enno_clean) != 10:
                    continue

                # 특수문자 이스케이프
                code_clean = str(code).strip().replace("'", "''")
                name_clean = str(name).strip().replace("'", "''") if name else ''
                rep_clean = str(rep).strip().replace("'", "''") if rep else ''

                if valid_count % batch_size == 0:
                    if valid_count > 0:
                        f.write(";\n\n")
                    f.write("INSERT INTO customers (CODE, NAME, REP, ENNO, LAST_SYNC) VALUES\n")
                else:
                    f.write(",\n")

                f.write(f"  ('{code_clean}', '{name_clean}', '{rep_clean}', '{enno_clean}', NOW())")

                valid_count += 1

            if valid_count > 0:
                f.write(";\n")

        print(f"\n=== SQL 파일 생성 완료 ===")
        print(f"파일: {output_file}")
        print(f"유효한 고객: {valid_count}명")
        print(f"\n다음 단계:")
        print(f"1. {output_file} 파일을 PythonAnywhere로 업로드")
        print(f"2. PythonAnywhere Bash에서 실행:")
        print(f"   mysql -h tirepass.mysql.pythonanywhere-services.com -u tirepass -p < {output_file}")

    except Exception as e:
        print(f"에러: {e}")


if __name__ == '__main__':
    from datetime import datetime
    export_to_sql()
