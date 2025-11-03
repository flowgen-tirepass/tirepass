#!/usr/bin/env python
"""
ERP 원본 데이터에서 휴대전화 번호 위치 확인 스크립트
- ERP API를 통해 CUSTOMS 테이블의 TEL1, TEL3 데이터 확인
- 010으로 시작하는 휴대전화가 TEL1, TEL3 중 어디에 있는지 분석
"""

import os
import django
import sys

# Django 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itire.settings')
django.setup()

from tire_data.erp_api_client import ERPAPIClient


def check_erp_phone_data():
    """ERP 원본 데이터의 전화번호 분석"""
    print("=" * 80)
    print("ERP 원본 CUSTOMS 테이블 전화번호 데이터 분석")
    print("=" * 80)

    # ERP API 서버 연결 확인
    print("\n🔍 ERP API 서버 연결 확인 중...")
    if not ERPAPIClient.health_check():
        print("❌ ERP API 서버에 연결할 수 없습니다.")
        print("   http://itire2.iptime.org:8000 서버가 실행 중인지 확인하세요.")
        return

    print("✅ ERP API 서버 연결 성공\n")

    # 전체 고객 수 확인
    total_customers = ERPAPIClient.get_customers_count()
    print(f"📊 ERP 전체 고객 수: {total_customers}명\n")

    # 샘플 데이터 가져오기 (처음 200명)
    print("📥 샘플 데이터 가져오는 중 (최대 200명)...")
    customers = ERPAPIClient.get_customers_list(offset=0, limit=200)

    if not customers:
        print("❌ 고객 데이터를 가져올 수 없습니다.")
        return

    print(f"✅ {len(customers)}명의 샘플 데이터 로드 완료\n")

    # 데이터 분석
    tel1_mobile = []  # TEL1에 휴대전화(010)가 있는 경우
    tel3_mobile = []  # TEL3에 휴대전화(010)가 있는 경우
    tel1_landline = []  # TEL1에 일반전화가 있는 경우
    tel3_landline = []  # TEL3에 일반전화가 있는 경우
    both_mobile = []  # TEL1, TEL3 모두 휴대전화인 경우
    both_empty = []  # 둘 다 비어있는 경우

    for customer in customers:
        tel1 = customer.get('tel1', '') or ''
        tel3 = customer.get('tel3', '') or ''

        tel1_is_mobile = tel1.strip().startswith('010')
        tel3_is_mobile = tel3.strip().startswith('010')
        tel1_is_landline = tel1.strip() and not tel1_is_mobile and (
            tel1.strip().startswith('02') or
            tel1.strip().startswith('031') or
            tel1.strip().startswith('032') or
            tel1.strip().startswith('0')
        )
        tel3_is_landline = tel3.strip() and not tel3_is_mobile and (
            tel3.strip().startswith('02') or
            tel3.strip().startswith('031') or
            tel3.strip().startswith('032') or
            tel3.strip().startswith('0')
        )

        if tel1_is_mobile and tel3_is_mobile:
            both_mobile.append(customer)
        elif tel1_is_mobile:
            tel1_mobile.append(customer)
        elif tel3_is_mobile:
            tel3_mobile.append(customer)

        if tel1_is_landline:
            tel1_landline.append(customer)
        if tel3_is_landline:
            tel3_landline.append(customer)

        if not tel1.strip() and not tel3.strip():
            both_empty.append(customer)

    # 분석 결과 출력
    print("=" * 80)
    print("📊 ERP 원본 데이터 분석 결과")
    print("=" * 80)

    print(f"\n1️⃣  TEL1에만 휴대전화(010)가 있는 경우: {len(tel1_mobile)}건")
    if len(tel1_mobile) > 0:
        print("   샘플 (최대 5건):")
        for customer in tel1_mobile[:5]:
            print(f"     {customer['code']} | {customer['name']} | TEL1: {customer.get('tel1', '')} | TEL3: {customer.get('tel3', '')}")

    print(f"\n2️⃣  TEL3에만 휴대전화(010)가 있는 경우: {len(tel3_mobile)}건 ✅ 올바른 위치")
    if len(tel3_mobile) > 0:
        print("   샘플 (최대 5건):")
        for customer in tel3_mobile[:5]:
            print(f"     {customer['code']} | {customer['name']} | TEL1: {customer.get('tel1', '')} | TEL3: {customer.get('tel3', '')}")

    print(f"\n3️⃣  TEL1, TEL3 모두 휴대전화(010)인 경우: {len(both_mobile)}건")
    if len(both_mobile) > 0:
        print("   샘플 (최대 5건):")
        for customer in both_mobile[:5]:
            print(f"     {customer['code']} | {customer['name']} | TEL1: {customer.get('tel1', '')} | TEL3: {customer.get('tel3', '')}")

    print(f"\n4️⃣  TEL1에 일반전화가 있는 경우: {len(tel1_landline)}건 ✅ 올바른 위치")

    print(f"\n5️⃣  TEL3에 일반전화가 있는 경우: {len(tel3_landline)}건 ⚠️ 잘못된 위치 (휴대전화 컬럼)")
    if len(tel3_landline) > 0:
        print("   샘플 (최대 5건):")
        for customer in tel3_landline[:5]:
            print(f"     {customer['code']} | {customer['name']} | TEL1: {customer.get('tel1', '')} | TEL3: {customer.get('tel3', '')}")

    print(f"\n6️⃣  TEL1, TEL3 모두 비어있는 경우: {len(both_empty)}건")

    # 결론 및 권장사항
    print("\n" + "=" * 80)
    print("💡 분석 결과 및 권장 조치")
    print("=" * 80)

    total_mobile_in_tel1 = len(tel1_mobile) + len(both_mobile)
    total_mobile_in_tel3 = len(tel3_mobile) + len(both_mobile)
    total_landline_in_tel3 = len(tel3_landline)

    print(f"\n📊 요약:")
    print(f"   - TEL1에 휴대전화: {total_mobile_in_tel1}건 (잘못된 위치)")
    print(f"   - TEL3에 휴대전화: {total_mobile_in_tel3}건 (올바른 위치)")
    print(f"   - TEL3에 일반전화: {total_landline_in_tel3}건 (잘못된 위치)")

    print(f"\n🎯 문제 원인:")
    print(f"   ✅ ERP 원본 데이터에서 TEL1, TEL3가 혼재되어 있음")
    print(f"   ✅ TEL1 = '전화1' (일반전화 예정) 이지만 {total_mobile_in_tel1}건의 휴대전화 포함")
    print(f"   ✅ TEL3 = '휴대전화' (휴대전화 예정) 이지만 {total_landline_in_tel3}건의 일반전화 포함")

    print(f"\n💡 권장 조치:")
    print(f"   1. ERP 담당자에게 데이터 정리 요청")
    print(f"      - TEL1에 있는 휴대전화({total_mobile_in_tel1}건) → TEL3로 이동")
    print(f"      - TEL3에 있는 일반전화({total_landline_in_tel3}건) → TEL1로 이동")
    print(f"   2. 또는 Django에서 자동 정리 스크립트 실행")
    print(f"      - 010으로 시작하면 무조건 TEL3로")
    print(f"      - 02/031/032 등으로 시작하면 TEL1로")

    print("\n" + "=" * 80)


if __name__ == '__main__':
    try:
        check_erp_phone_data()
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
