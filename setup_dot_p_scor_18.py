#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
P-SCOR-18 상품 DOT 정보 설정
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itire.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from tire_data.models import YearAllocation, Goods
from decimal import Decimal

# 상품 코드
GOODS_CODE = 'P-SCOR-18'

print("=" * 70)
print(f"  {GOODS_CODE} DOT 정보 설정")
print("=" * 70)
print()

# 상품 정보 확인
try:
    goods = Goods.objects.get(code=GOODS_CODE)
    total_stock = int(goods.jaego)
    print(f"[상품 정보]")
    print(f"  코드: {goods.code}")
    print(f"  상품명: {goods.name}")
    print(f"  현재 재고: {total_stock:,}개")
    print()
except Goods.DoesNotExist:
    print(f"[오류] 상품을 찾을 수 없습니다: {GOODS_CODE}")
    sys.exit(1)

# DOT 배분 계획 (재고 147개 기준)
year_2025 = 100  # 최신 제품
year_2024 = 47   # 1년 전 제품
year_2023 = 0
year_2022 = 0
year_2021_before = 0

# DOT 할인율
discount_2024 = Decimal('5.00')   # 1년 전: 5% 할인
discount_2023 = Decimal('10.00')  # 2년 전: 10% 할인
discount_2022 = Decimal('15.00')  # 3년 전: 15% 할인
discount_2021 = Decimal('20.00')  # 4년 이상: 20% 할인

print(f"[DOT 배분 계획]")
print(f"  2025년 (최신):    {year_2025:3d}개 (할인 없음)")
print(f"  2024년 (1년 전):  {year_2024:3d}개 (할인: {discount_2024}%)")
print(f"  2023년 (2년 전):  {year_2023:3d}개 (할인: {discount_2023}%)")
print(f"  2022년 (3년 전):  {year_2022:3d}개 (할인: {discount_2022}%)")
print(f"  2021년 이전:      {year_2021_before:3d}개 (할인: {discount_2021}%)")
print(f"  {'─' * 40}")
print(f"  합계:           {year_2025 + year_2024 + year_2023 + year_2022 + year_2021_before:3d}개")
print()

# YearAllocation 생성 또는 업데이트
ya, created = YearAllocation.objects.update_or_create(
    goods_code=GOODS_CODE,
    defaults={
        'year_2025': year_2025,
        'year_2024': year_2024,
        'year_2023': year_2023,
        'year_2022': year_2022,
        'year_2021_before': year_2021_before,
        'year_2024_discount': discount_2024,
        'year_2023_discount': discount_2023,
        'year_2022_discount': discount_2022,
        'year_2021_before_discount': discount_2021,
    }
)

if created:
    print(f"[완료] ✓ 새로운 DOT 정보를 생성했습니다.")
else:
    print(f"[완료] ✓ 기존 DOT 정보를 업데이트했습니다.")

print()
print(f"[저장된 정보]")
print(f"  총 배분: {ya.total_allocated}개")
print(f"  기본 할인율: {ya.base_discount}%")
print(f"  마지막 업데이트: {ya.last_updated}")
print()
print("=" * 70)
print()
print(f"[확인]")
print(f"  Admin: https://tirepass.pythonanywhere.com/admin/tire_data/yearallocation/")
print()
