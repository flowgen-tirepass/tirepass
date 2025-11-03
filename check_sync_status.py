#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
재고 동기화 상태 확인
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itire.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from tire_data.models import Goods
from tire_data.erp_api_client import ERPAPIClient
from datetime import datetime, timedelta

GOODS_CODE = 'P-SCOR-18'

print("=" * 70)
print(f"  재고 동기화 상태 확인: {GOODS_CODE}")
print("=" * 70)
print()

# 1. 로컬 DB 확인
try:
    goods = Goods.objects.get(code=GOODS_CODE)
    print(f"[로컬 DB (Goods 테이블)]")
    print(f"  재고: {int(goods.jaego)}개")
    print(f"  마지막 동기화: {goods.last_sync}")

    # 동기화 시간 경과 확인
    if goods.last_sync:
        time_diff = datetime.now(goods.last_sync.tzinfo) - goods.last_sync
        hours_ago = time_diff.total_seconds() / 3600
        print(f"  경과 시간: {hours_ago:.1f}시간 전")
    print()
except Goods.DoesNotExist:
    print(f"[오류] 로컬 DB에 상품이 없습니다: {GOODS_CODE}")
    print()

# 2. ERP API 실시간 확인
print(f"[ERP API 실시간 조회]")
try:
    # ERP에서 상품 검색
    erp_goods_list = ERPAPIClient.get_goods_list(offset=0, limit=100, search=GOODS_CODE)

    found = False
    for erp_goods in erp_goods_list:
        if erp_goods.get('code') == GOODS_CODE:
            print(f"  재고: {int(erp_goods.get('jaego', 0))}개")
            print(f"  상품명: {erp_goods.get('name', 'N/A')}")
            print(f"  가격: {int(erp_goods.get('fixp', 0)):,}원")
            found = True
            break

    if not found:
        print(f"  [정보] ERP API에서 상품을 찾을 수 없습니다.")
    print()
except Exception as e:
    print(f"  [오류] ERP API 호출 실패: {e}")
    print()

# 3. 동기화 권장 사항
print(f"[분석]")
print(f"  - Admin 페이지는 ERP API 실시간 데이터 표시")
print(f"  - 모바일 페이지는 Goods 테이블(DB) 데이터 표시")
print(f"  - 두 값이 다르면 DB 동기화 필요")
print()

print(f"[해결 방법]")
print(f"  1. 수동 동기화:")
print(f"     python manage.py sync_erp_goods")
print()
print(f"  2. PythonAnywhere Scheduled Task 확인:")
print(f"     https://www.pythonanywhere.com/user/tirepass/tasks_tab/")
print(f"     예정된 작업: python manage.py sync_erp_goods (매시간)")
print()

print("=" * 70)
