"""
ERP Firebird 서버에서 고객 데이터를 가져와 PythonAnywhere MySQL로 동기화

요구사항:
    pip install fdb mysql-connector-python

실행:
    python scripts/sync_erp_customers.py
"""

import fdb
import mysql.connector
from datetime import datetime

# ERP Firebird 연결 정보
FIREBIRD_CONFIG = {
    'host': 'ITIRE2.iptime.org',
    'database': r'C:\Program Files\PsimCarS\Data\ITIRE.GDB',
    'user': 'SYSDBA',
    'password': 'masterkey',
    'charset': 'UTF8'
}

# PythonAnywhere MySQL 연결 정보
MYSQL_CONFIG = {
    'host': 'tirepass.mysql.pythonanywhere-services.com',
    'database': 'tirepass$itire_db',
    'user': 'tirepass',
    'password': '#flowgen9569yjm*',
    'charset': 'utf8mb4'
}


def fetch_erp_customers():
    """ERP Firebird에서 고객 데이터 가져오기"""
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

        return customers

    except Exception as e:
        print(f"ERP 연결 에러: {e}")
        return []


def sync_to_mysql(customers):
    """PythonAnywhere MySQL에 동기화"""
    print("\n=== PythonAnywhere MySQL 동기화 중... ===")

    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()

        success_count = 0
        skip_count = 0
        error_count = 0

        for customer in customers:
            code, name, rep, enno = customer

            # 사업자번호 정제
            if not enno:
                skip_count += 1
                continue

            enno_clean = str(enno).replace('-', '').strip()

            if not enno_clean.isdigit() or len(enno_clean) != 10:
                skip_count += 1
                print(f"건너뜀: {code} - {name} (사업자번호 형식 오류: {enno})")
                continue

            try:
                # INSERT OR UPDATE (REPLACE)
                insert_query = """
                    INSERT INTO customers (CODE, NAME, REP, ENNO, LAST_SYNC)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        NAME = VALUES(NAME),
                        REP = VALUES(REP),
                        ENNO = VALUES(ENNO),
                        LAST_SYNC = VALUES(LAST_SYNC)
                """

                cursor.execute(insert_query, (
                    str(code).strip(),
                    str(name).strip() if name else '',
                    str(rep).strip() if rep else '',
                    enno_clean,
                    datetime.now()
                ))

                success_count += 1

                if success_count % 100 == 0:
                    print(f"진행 중... {success_count}명 처리됨")

            except Exception as e:
                error_count += 1
                print(f"에러: {code} - {name}: {e}")

        conn.commit()
        cursor.close()
        conn.close()

        print("\n=== 동기화 완료 ===")
        print(f"성공: {success_count}명")
        print(f"건너뜀: {skip_count}명")
        print(f"에러: {error_count}명")

        return success_count

    except Exception as e:
        print(f"MySQL 연결 에러: {e}")
        return 0


def main():
    """메인 실행 함수"""
    print("========================================")
    print("ERP → PythonAnywhere 고객 데이터 동기화")
    print("========================================\n")

    # 1. ERP에서 데이터 가져오기
    customers = fetch_erp_customers()

    if not customers:
        print("가져온 데이터가 없습니다.")
        return

    # 2. MySQL로 동기화
    sync_count = sync_to_mysql(customers)

    print(f"\n총 {sync_count}명의 고객이 동기화되었습니다.")
    print("\n다음 단계: PythonAnywhere에서 migrate_erp_customers 명령 실행")
    print("  python3 manage.py migrate_erp_customers")


if __name__ == '__main__':
    main()
