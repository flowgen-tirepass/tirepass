"""
ERP Firebird 서버에서 고객 데이터를 가져와 초기 비밀번호로 일괄 등록 (Django 독립 버전)

기능:
    - ERP CUSTOMS 테이블에서 사업자등록번호가 있는 고객 가져오기
    - 사업자등록번호 뒤 5자리를 초기 비밀번호로 설정
    - customers_simple 테이블에 등록 (이미 등록된 고객은 건너뜀)

요구사항:
    pip install fdb mysql-connector-python

실행:
    로컬 DB에 등록: python scripts/register_initial_customers_simple.py
    PythonAnywhere DB에 등록: python scripts/register_initial_customers_simple.py --target pythonanywhere
"""

import fdb
import mysql.connector
import argparse
import hashlib
from datetime import datetime


def make_password_pbkdf2(password):
    """Django 호환 PBKDF2 비밀번호 해싱"""
    import hashlib
    import os
    import base64

    algorithm = 'pbkdf2_sha256'
    iterations = 600000  # Django 4.2+ 기본값
    salt = base64.b64encode(os.urandom(12)).decode('utf-8')

    hash_value = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        iterations
    )
    hash_b64 = base64.b64encode(hash_value).decode('utf-8').strip()

    return f"{algorithm}${iterations}${salt}${hash_b64}"


# 명령줄 인수 파싱
parser = argparse.ArgumentParser(description='ERP 고객 데이터 일괄 등록')
parser.add_argument('--target', choices=['local', 'pythonanywhere'], default='local',
                    help='MySQL 타겟 환경 (기본: local)')
args = parser.parse_args()

# ERP Firebird 연결 정보
FIREBIRD_CONFIG = {
    'host': 'ITIRE2.iptime.org',
    'database': r'C:\Program Files\PsimCarS\Data\ITIRE.GDB',
    'user': 'SYSDBA',
    'password': 'masterkey',
    'charset': 'UTF8'
}

# MySQL 연결 정보
if args.target == 'pythonanywhere':
    MYSQL_CONFIG = {
        'host': 'tirepass.mysql.pythonanywhere-services.com',
        'database': 'tirepass$itire_db',
        'user': 'tirepass',
        'password': '#flowgen9569yjm*',
        'charset': 'utf8mb4'
    }
    print("🌐 MySQL 타겟: PythonAnywhere")
else:
    MYSQL_CONFIG = {
        'host': 'localhost',
        'database': 'itire_db',
        'user': 'root',
        'password': 'tirepass',
        'charset': 'utf8mb4'
    }
    print("💻 MySQL 타겟: 로컬")


def fetch_erp_customers():
    """ERP Firebird에서 고객 데이터 가져오기"""
    print("\n=== ERP Firebird 서버 연결 중... ===")

    try:
        conn = fdb.connect(**FIREBIRD_CONFIG)
        cursor = conn.cursor()

        # CUSTOMS 테이블에서 사업자번호가 있는 고객 조회
        query = """
            SELECT CODE, NAME, REP, TEL1, TEL3, ENNO
            FROM CUSTOMS
            WHERE ENNO IS NOT NULL AND ENNO <> ''
            ORDER BY CODE
        """

        cursor.execute(query)
        customers = cursor.fetchall()

        print(f"✅ 총 {len(customers)}명의 고객 데이터를 가져왔습니다.\n")

        cursor.close()
        conn.close()

        return customers

    except Exception as e:
        print(f"❌ ERP 연결 에러: {e}")
        return []


def register_customers(customers):
    """고객을 customers_simple에 초기 비밀번호로 등록"""
    print("=== MySQL 데이터베이스에 등록 중... ===\n")

    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()

        success_count = 0
        skip_count = 0
        error_count = 0
        already_registered_count = 0

        for customer in customers:
            code, name, rep, tel1, tel3, enno = customer

            # 사업자번호 정제
            if not enno:
                skip_count += 1
                continue

            enno_clean = str(enno).replace('-', '').strip()

            # 사업자번호 유효성 검사 (10자리 숫자)
            if not enno_clean.isdigit() or len(enno_clean) != 10:
                skip_count += 1
                print(f"⚠️  건너뜀: {code} - {name} (사업자번호 형식 오류: {enno})")
                continue

            # 초기 비밀번호: 사업자번호 뒤 5자리
            initial_password = enno_clean[-5:]
            hashed_password = make_password_pbkdf2(initial_password)

            try:
                # 이미 등록된 고객인지 확인
                check_query = "SELECT code, is_registered FROM customers_simple WHERE code = %s"
                cursor.execute(check_query, (str(code).strip(),))
                existing = cursor.fetchone()

                if existing:
                    # 이미 등록된 고객
                    already_registered_count += 1
                    continue

                # 새 고객 등록
                insert_query = """
                    INSERT INTO customers_simple
                    (code, name, rep, tel1, tel3, enno, password, signup_source, is_registered, must_change_password)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

                cursor.execute(insert_query, (
                    str(code).strip(),
                    str(name).strip() if name else '',
                    str(rep).strip() if rep else '',
                    str(tel1).strip() if tel1 else '',
                    str(tel3).strip() if tel3 else '',
                    enno_clean,
                    hashed_password,
                    'erp_initial',  # 초기 등록임을 표시
                    1,  # is_registered = True
                    1   # must_change_password = True
                ))

                success_count += 1
                print(f"✅ 등록: {code} - {name} (초기 비밀번호: {initial_password})")

                if success_count % 50 == 0:
                    print(f"\n--- 진행 중... {success_count}명 등록됨 ---\n")

            except Exception as e:
                error_count += 1
                print(f"❌ 에러: {code} - {name}: {e}")

        conn.commit()
        cursor.close()
        conn.close()

        print("\n" + "="*60)
        print("=== 등록 완료 ===")
        print("="*60)
        print(f"✅ 신규 등록: {success_count}명")
        print(f"ℹ️  이미 등록됨: {already_registered_count}명")
        print(f"⚠️  건너뜀: {skip_count}명 (사업자번호 오류)")
        print(f"❌ 에러: {error_count}명")
        print("="*60)

        return success_count

    except Exception as e:
        print(f"❌ MySQL 연결 에러: {e}")
        return 0


def main():
    """메인 실행 함수"""
    print("\n" + "="*60)
    print("TirePASS B2B 초기 고객 일괄 등록")
    print("="*60)
    print("\n📋 작업 내용:")
    print("  - ERP에서 사업자등록번호가 있는 고객 가져오기")
    print("  - 사업자번호 뒤 5자리를 초기 비밀번호로 설정")
    print("  - customers_simple 테이블에 등록")
    print("  - 최초 로그인 시 비밀번호 변경 강제\n")

    confirm = input("계속 진행하시겠습니까? (y/n): ")
    if confirm.lower() != 'y':
        print("작업이 취소되었습니다.")
        return

    # 1. ERP에서 데이터 가져오기
    customers = fetch_erp_customers()

    if not customers:
        print("가져온 데이터가 없습니다.")
        return

    # 2. MySQL에 등록
    register_count = register_customers(customers)

    print(f"\n🎉 총 {register_count}명의 고객이 신규 등록되었습니다.")
    print("\n📌 다음 단계:")
    print("  1. 고객들에게 로그인 정보 안내")
    print("     - 아이디: 사업자등록번호 10자리")
    print("     - 초기 비밀번호: 사업자번호 뒤 5자리")
    print("  2. 최초 로그인 시 비밀번호 변경 필수")
    print("  3. 테스트: /mobile/login/ 페이지에서 로그인 테스트\n")


if __name__ == '__main__':
    main()
