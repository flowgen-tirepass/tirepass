"""
기존 customers_simple 고객들에게 초기 비밀번호 일괄 설정

기능:
    - customers_simple 테이블에서 사업자번호가 있는 고객 조회
    - 사업자번호 뒤 5자리를 초기 비밀번호로 설정
    - 비밀번호가 없거나 must_change_password=1인 고객만 업데이트

요구사항:
    pip install mysql-connector-python

실행:
    로컬 DB: python scripts/set_initial_passwords.py
    PythonAnywhere DB: python scripts/set_initial_passwords.py --target pythonanywhere
"""

import mysql.connector
import argparse
import hashlib
import os
import base64


def make_password_pbkdf2(password):
    """Django 호환 PBKDF2 비밀번호 해싱"""
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
parser = argparse.ArgumentParser(description='기존 고객에게 초기 비밀번호 설정')
parser.add_argument('--target', choices=['local', 'pythonanywhere'], default='local',
                    help='MySQL 타겟 환경 (기본: local)')
parser.add_argument('--force', action='store_true',
                    help='이미 비밀번호가 있는 고객도 강제 업데이트')
args = parser.parse_args()

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


def set_initial_passwords():
    """기존 고객들에게 초기 비밀번호 설정"""
    print("\n=== MySQL 데이터베이스 연결 중... ===")

    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor(dictionary=True)

        # 사업자번호가 있는 고객 조회
        if args.force:
            query = """
                SELECT code, name, enno, password, is_registered
                FROM customers_simple
                WHERE enno IS NOT NULL AND enno != ''
                ORDER BY code
            """
            print("⚠️  강제 모드: 모든 고객의 비밀번호를 초기화합니다.")
        else:
            query = """
                SELECT code, name, enno, password, is_registered
                FROM customers_simple
                WHERE enno IS NOT NULL AND enno != ''
                  AND (password IS NULL OR password = '' OR must_change_password = 1)
                ORDER BY code
            """
            print("✅ 안전 모드: 비밀번호가 없거나 변경 필요한 고객만 업데이트합니다.")

        cursor.execute(query)
        customers = cursor.fetchall()

        print(f"✅ 총 {len(customers)}명의 고객을 찾았습니다.\n")

        if len(customers) == 0:
            print("ℹ️  업데이트할 고객이 없습니다.")
            return 0

        success_count = 0
        skip_count = 0
        error_count = 0

        for customer in customers:
            code = customer['code']
            name = customer['name']
            enno = customer['enno']

            # 사업자번호 정제
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
                # 비밀번호 업데이트
                update_query = """
                    UPDATE customers_simple
                    SET password = %s,
                        must_change_password = 1,
                        is_registered = 1
                    WHERE code = %s
                """

                cursor.execute(update_query, (hashed_password, code))

                success_count += 1
                print(f"✅ 설정: {code} - {name} (초기 비밀번호: {initial_password})")

                if success_count % 50 == 0:
                    print(f"\n--- 진행 중... {success_count}명 처리됨 ---\n")

            except Exception as e:
                error_count += 1
                print(f"❌ 에러: {code} - {name}: {e}")

        conn.commit()
        cursor.close()
        conn.close()

        print("\n" + "="*60)
        print("=== 처리 완료 ===")
        print("="*60)
        print(f"✅ 성공: {success_count}명")
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
    print("TirePASS B2B 초기 비밀번호 일괄 설정")
    print("="*60)
    print("\n📋 작업 내용:")
    print("  - customers_simple에서 사업자번호 있는 고객 조회")
    print("  - 사업자번호 뒤 5자리를 초기 비밀번호로 설정")
    print("  - must_change_password = 1 (변경 필수)")
    print("  - is_registered = 1 (등록 완료)")

    if args.force:
        print("\n⚠️  경고: --force 옵션 사용 중!")
        print("  - 이미 비밀번호가 설정된 고객도 초기화됩니다!")

    print()

    confirm = input("계속 진행하시겠습니까? (y/n): ")
    if confirm.lower() != 'y':
        print("작업이 취소되었습니다.")
        return

    # 초기 비밀번호 설정
    process_count = set_initial_passwords()

    print(f"\n🎉 총 {process_count}명의 고객 비밀번호가 설정되었습니다.")
    print("\n📌 다음 단계:")
    print("  1. 고객들에게 로그인 정보 안내")
    print("     - 아이디: 사업자등록번호 10자리")
    print("     - 초기 비밀번호: 사업자번호 뒤 5자리")
    print("  2. 최초 로그인 시 비밀번호 변경 필수")
    print("  3. 테스트: /mobile/login/ 페이지에서 로그인 테스트\n")


if __name__ == '__main__':
    main()
