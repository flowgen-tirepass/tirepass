#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itire.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from tire_data.models import Customers

def create_test_user():
    """테스트용 사용자 생성"""

    # 테스트 계정 정보
    username = '1234567890'  # 사업자번호 (하이픈 제거)
    password = '67890'  # 비밀번호 (사업자번호 뒤 5자리)
    business_number = '123-45-67890'  # 표시용 사업자번호

    print(f"\n=== 테스트 계정 생성 ===")
    print(f"사업자번호: {business_number}")
    print(f"로그인 ID: {username}")
    print(f"비밀번호: {password}")
    print("-" * 30)

    # 기존 사용자 삭제
    if User.objects.filter(username=username).exists():
        user = User.objects.get(username=username)
        user.delete()
        print("기존 테스트 계정 삭제 완료")

    # 새 사용자 생성
    user = User.objects.create_user(
        username=username,
        password=password,
        first_name='TEST',
        last_name='TestCompany'
    )
    user.is_active = True
    user.is_staff = False  # 일반 사용자
    user.is_superuser = False  # 일반 사용자
    user.save()
    print(f"[OK] Django User 생성 완료: {username}")

    # 고객 정보 생성 또는 업데이트
    try:
        # 기존 TEST001 고객이 있는지 확인
        customer = Customers.objects.filter(code='TEST001').first()

        if customer:
            # 기존 고객 정보 업데이트
            customer.name = 'TestIndustry'  # 테스트공업사
            customer.enno = business_number
            customer.rep = 'Hong Gildong'  # 홍길동
            customer.tel1 = '02-1234-5678'
            customer.tel3 = '010-1234-5678'
            customer.is_registered = True
            customer.user_id = user.id
            customer.must_change_password = False  # 테스트 계정은 비밀번호 변경 불필요
            customer.save()
            print("[OK] 기존 고객 정보 업데이트 완료")
        else:
            # 새 고객 정보 생성
            customer = Customers.objects.create(
                code='TEST001',
                name='TestIndustry',  # 테스트공업사
                enno=business_number,
                rep='Hong Gildong',  # 홍길동
                tel1='02-1234-5678',
                tel3='010-1234-5678',
                is_registered=True,
                user_id=user.id,
                must_change_password=False  # 테스트 계정은 비밀번호 변경 불필요
            )
            print("[OK] 새 고객 정보 생성 완료")

    except Exception as e:
        print(f"고객 정보 처리 중 오류: {e}")
        # 고객 정보가 없어도 로그인은 가능
        print("[NOTE] 고객 정보 없이 사용자만 생성됨")

    print("\n=== 테스트 계정 생성 완료 ===")
    print("\n테스트 방법:")
    print("1. 브라우저에서 http://192.168.10.113:8080/mobile/login/ 접속")
    print(f"2. 사업자번호: {username}")
    print(f"3. 비밀번호: {password}")
    print("4. 로그인 후 모든 기능 테스트 가능")
    print("\n[NOTE] 이 계정은 비밀번호 변경이 필요하지 않도록 설정되어 있습니다.")

    return user, customer

if __name__ == '__main__':
    try:
        user, customer = create_test_user()
        print("\n[SUCCESS] 성공적으로 완료!")
    except Exception as e:
        print(f"\n[ERROR] 오류 발생: {e}")
        import traceback
        traceback.print_exc()