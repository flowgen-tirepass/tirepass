#!/usr/bin/env python
"""
고객 테이블의 휴대전화 데이터 확인 스크립트
- tel1, tel3 컬럼의 실제 데이터 확인
- 010으로 시작하는 전화번호 찾기
"""

import os
import django
import sys

# Django 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itire.settings')
django.setup()

from tire_data.models import Customers

def analyze_phone_data():
    print("=" * 80)
    print("고객 전화번호 데이터 분석")
    print("=" * 80)

    total_customers = Customers.objects.count()
    print(f"\n📊 전체 고객 수: {total_customers}명")

    # tel1 분석
    print("\n" + "=" * 80)
    print("1️⃣  tel1 (전화1) 분석")
    print("=" * 80)

    tel1_exists = Customers.objects.exclude(tel1__isnull=True).exclude(tel1='').count()
    tel1_starts_010 = Customers.objects.filter(tel1__startswith='010').count()
    tel1_starts_02 = Customers.objects.filter(tel1__startswith='02').count()
    tel1_starts_031 = Customers.objects.filter(tel1__startswith='031').count()

    print(f"  - 데이터 있음: {tel1_exists}개")
    print(f"  - 010으로 시작 (휴대전화): {tel1_starts_010}개")
    print(f"  - 02로 시작 (서울 일반전화): {tel1_starts_02}개")
    print(f"  - 031로 시작 (경기 일반전화): {tel1_starts_031}개")

    # tel1에서 010으로 시작하는 샘플 출력
    if tel1_starts_010 > 0:
        print(f"\n  📱 tel1에 휴대전화가 있는 고객 샘플 (최대 10명):")
        samples = Customers.objects.filter(tel1__startswith='010')[:10]
        for customer in samples:
            print(f"    - {customer.code} | {customer.name} | tel1: {customer.tel1} | tel3: {customer.tel3}")

    # tel3 분석
    print("\n" + "=" * 80)
    print("2️⃣  tel3 (휴대전화) 분석")
    print("=" * 80)

    tel3_exists = Customers.objects.exclude(tel3__isnull=True).exclude(tel3='').count()
    tel3_starts_010 = Customers.objects.filter(tel3__startswith='010').count()
    tel3_starts_02 = Customers.objects.filter(tel3__startswith='02').count()
    tel3_starts_031 = Customers.objects.filter(tel3__startswith='031').count()

    print(f"  - 데이터 있음: {tel3_exists}개")
    print(f"  - 010으로 시작 (실제 휴대전화): {tel3_starts_010}개 ✅")
    print(f"  - 02로 시작 (서울 일반전화): {tel3_starts_02}개 ⚠️  잘못된 데이터")
    print(f"  - 031로 시작 (경기 일반전화): {tel3_starts_031}개 ⚠️  잘못된 데이터")

    # tel3에 일반전화가 있는 샘플 출력
    if tel3_starts_02 > 0 or tel3_starts_031 > 0:
        print(f"\n  ⚠️  tel3(휴대전화)에 일반전화가 있는 고객 샘플 (최대 10명):")
        samples = Customers.objects.filter(tel3__startswith='02')[:5]
        for customer in samples:
            print(f"    - {customer.code} | {customer.name} | tel1: {customer.tel1} | tel3: {customer.tel3}")
        samples = Customers.objects.filter(tel3__startswith='031')[:5]
        for customer in samples:
            print(f"    - {customer.code} | {customer.name} | tel1: {customer.tel1} | tel3: {customer.tel3}")

    # tel3에 실제 휴대전화가 있는 샘플
    if tel3_starts_010 > 0:
        print(f"\n  ✅ tel3에 휴대전화가 올바르게 있는 고객 샘플 (최대 10명):")
        samples = Customers.objects.filter(tel3__startswith='010')[:10]
        for customer in samples:
            print(f"    - {customer.code} | {customer.name} | tel1: {customer.tel1} | tel3: {customer.tel3}")

    # 결론 및 권장사항
    print("\n" + "=" * 80)
    print("3️⃣  분석 결과 및 권장사항")
    print("=" * 80)

    print(f"\n  📊 현재 상태:")
    print(f"    - tel1에 휴대전화: {tel1_starts_010}개")
    print(f"    - tel3에 휴대전화: {tel3_starts_010}개")
    print(f"    - tel3에 일반전화(잘못됨): {tel3_starts_02 + tel3_starts_031}개")

    print(f"\n  💡 권장 조치:")
    if tel1_starts_010 > tel3_starts_010:
        print(f"    1. tel1에 있는 휴대전화({tel1_starts_010}개)를 tel3로 이동")
        print(f"    2. tel3에 있는 일반전화({tel3_starts_02 + tel3_starts_031}개)를 tel1로 이동")
        print(f"    3. ERP에서 원본 데이터 확인 필요")

    print("\n" + "=" * 80)

if __name__ == '__main__':
    try:
        analyze_phone_data()
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
