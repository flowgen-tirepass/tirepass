#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DOT 정보 확인 스크립트
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itire.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from tire_data.models import YearAllocation, Goods

# 상품 코드
GOODS_CODE = 'P-SCOR-18'

print("=" * 70)
print(f"  상품 코드: {GOODS_CODE}")
print("=" * 70)
print()

# 상품 정보 확인
try:
    goods = Goods.objects.get(code=GOODS_CODE)
    print("[상품 정보]")
    print(f"  코드: {goods.code}")
    print(f"  상품명: {goods.name}")
    print(f"  브랜드: {goods.bun1}")
    print(f"  재고: {int(goods.jaego)}개")
    print(f"  가격: {int(goods.fixp):,}원")
    print()
except Goods.DoesNotExist:
    print(f"[오류] 상품을 찾을 수 없습니다: {GOODS_CODE}")
    print()

# DOT 정보 확인
try:
    ya = YearAllocation.objects.get(goods_code=GOODS_CODE)
    print("[DOT 재고 배분]")
    print(f"  2025년: {ya.year_2025}개")
    print(f"  2024년: {ya.year_2024}개 (할인: {ya.year_2024_discount}%)")
    print(f"  2023년: {ya.year_2023}개 (할인: {ya.year_2023_discount}%)")
    print(f"  2022년: {ya.year_2022}개 (할인: {ya.year_2022_discount}%)")
    print(f"  2021년 이전: {ya.year_2021_before}개 (할인: {ya.year_2021_before_discount}%)")
    print()
    print(f"[합계 정보]")
    print(f"  총 배분: {ya.total_allocated}개")
    print(f"  기본 할인율: {ya.base_discount}%")
    print(f"  마지막 업데이트: {ya.last_updated}")
except YearAllocation.DoesNotExist:
    print("[정보] DOT 배분 정보가 없습니다.")
    print()
    print("[설정 방법]")
    print(f"  Admin 페이지에서 설정 가능:")
    print(f"  https://tirepass.pythonanywhere.com/admin/tire_data/yearallocation/")
    print()

print()
print("=" * 70)
