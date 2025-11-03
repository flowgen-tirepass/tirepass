#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ERP API에서 P-SCOR-18 재고 확인
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itire.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from tire_data.erp_api_client import ERPAPIClient
from tire_data.models import Goods

GOODS_CODE = 'P-SCOR-18'

print("=" * 70)
print(f"  P-SCOR-18 재고 비교")
print("=" * 70)
print()

# 1. 로컬 DB
try:
    goods = Goods.objects.get(code=GOODS_CODE)
    local_stock = int(goods.jaego)
    print(f"[로컬 DB]")
    print(f"  재고: {local_stock:,}개")
    print()
except Goods.DoesNotExist:
    local_stock = None
    print(f"[로컬 DB] 상품 없음")
    print()

# 2. ERP API
print(f"[ERP API 실시간 조회]")
try:
    erp_goods_list = ERPAPIClient.get_goods_list(offset=0, limit=100, search='SCOR')

    found = False
    for erp_goods in erp_goods_list:
        if GOODS_CODE in erp_goods.get('code', ''):
            erp_stock = int(erp_goods.get('jaego', 0))
            print(f"  코드: {erp_goods.get('code')}")
            print(f"  상품명: {erp_goods.get('name')}")
            print(f"  재고: {erp_stock:,}개")
            print(f"  가격: {int(erp_goods.get('fixp', 0)):,}원")
            found = True

            # 비교
            if local_stock and erp_stock != local_stock:
                diff = erp_stock - local_stock
                print()
                print(f"  [차이] ERP와 로컬 DB 재고 불일치: {diff:+,}개")
            break

    if not found:
        print(f"  [정보] ERP API에서 상품을 찾을 수 없습니다.")
    print()

except Exception as e:
    print(f"  [오류] ERP API 호출 실패: {e}")
    import traceback
    traceback.print_exc()
    print()

print("=" * 70)
print()
print("[분석]")
print("  Admin 페이지: ERP API 실시간 데이터")
print("  모바일 페이지: Goods 테이블 (DB)")
print()
print("  → 재고 수량이 다르면 동기화가 필요합니다.")
print()
print("[해결 방법]")
print("  PythonAnywhere에서 DB 동기화:")
print("  1. Goods 테이블이 ERP DB를 참조하도록 설정 확인")
print("  2. 또는 정기적 동기화 스케줄러 실행")
print()
