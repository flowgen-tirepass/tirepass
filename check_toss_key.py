#!/usr/bin/env python
"""
토스페이먼츠 API 키 유효성 테스트 스크립트
PythonAnywhere에서 실행하여 키가 정상적으로 설정되었는지 확인합니다.
"""
import os
import sys
import base64
import requests

# Django 설정 로드
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itire.settings')

def check_toss_payments_keys():
    """토스페이먼츠 키 설정 확인"""
    print("=" * 50)
    print("토스페이먼츠 API 키 확인")
    print("=" * 50)

    # 환경변수에서 키 가져오기
    client_key = os.environ.get('TOSS_PAYMENTS_CLIENT_KEY', '')
    secret_key = os.environ.get('TOSS_PAYMENTS_SECRET_KEY', '')

    # 1. 키 존재 여부 확인
    print("\n[1] 키 설정 확인")
    print("-" * 30)

    if client_key:
        # 보안을 위해 앞 15자만 표시
        masked_client = client_key[:15] + "..." if len(client_key) > 15 else client_key
        print(f"  Client Key: {masked_client}")

        if client_key.startswith('live_ck_') or client_key.startswith('live_gck_'):
            print("  -> 라이브 클라이언트 키 형식 OK")
        elif client_key.startswith('test_ck_') or client_key.startswith('test_gck_'):
            print("  -> 테스트 클라이언트 키 형식 (라이브키 아님!)")
        else:
            print("  -> 알 수 없는 키 형식")
    else:
        print("  Client Key: 설정되지 않음!")

    if secret_key:
        masked_secret = secret_key[:15] + "..." if len(secret_key) > 15 else secret_key
        print(f"  Secret Key: {masked_secret}")

        if secret_key.startswith('live_sk_') or secret_key.startswith('live_gsk_'):
            print("  -> 라이브 시크릿 키 형식 OK")
        elif secret_key.startswith('test_sk_') or secret_key.startswith('test_gsk_'):
            print("  -> 테스트 시크릿 키 형식 (라이브키 아님!)")
        else:
            print("  -> 알 수 없는 키 형식")
    else:
        print("  Secret Key: 설정되지 않음!")

    # 2. API 호출 테스트
    if secret_key:
        print("\n[2] 토스페이먼츠 API 연결 테스트")
        print("-" * 30)

        # Basic Auth 헤더 생성
        auth_string = f"{secret_key}:"
        auth_bytes = base64.b64encode(auth_string.encode()).decode()

        headers = {
            "Authorization": f"Basic {auth_bytes}",
            "Content-Type": "application/json"
        }

        # 존재하지 않는 결제를 조회하여 API 키 유효성만 확인
        # 404 = 키는 유효하지만 결제가 없음
        # 401 = 키가 유효하지 않음
        test_url = "https://api.tosspayments.com/v1/payments/test_payment_id_12345"

        try:
            response = requests.get(test_url, headers=headers, timeout=10)

            if response.status_code == 404:
                print("  API 키 유효성: OK")
                print("  -> 토스페이먼츠 API와 정상적으로 통신 가능")
                print("  -> (404는 테스트 결제ID가 없어서 발생, 정상)")
                return True
            elif response.status_code == 401:
                print("  API 키 유효성: 실패!")
                print("  -> 인증 실패: API 키가 유효하지 않습니다")
                print(f"  -> 응답: {response.text}")
                return False
            else:
                print(f"  응답 코드: {response.status_code}")
                print(f"  응답 내용: {response.text[:200]}")
                return response.status_code != 401

        except requests.exceptions.RequestException as e:
            print(f"  API 호출 오류: {e}")
            return False
    else:
        print("\n[2] API 테스트 건너뜀 (Secret Key 없음)")
        return False

if __name__ == "__main__":
    result = check_toss_payments_keys()
    print("\n" + "=" * 50)
    if result:
        print("결과: 토스페이먼츠 라이브키가 정상적으로 설정되었습니다!")
    else:
        print("결과: 토스페이먼츠 키 설정에 문제가 있습니다.")
    print("=" * 50)
