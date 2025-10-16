#!/usr/bin/env python3
"""
실시간 재고 스냅샷 추가 스크립트

최근 동기화된 상품 5개를 GoodsRealtimeSnapshot에 추가
"""

import os
import sys
import django
from datetime import datetime

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itire.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from tire_data.models import GoodsRealtimeSnapshot

# 추가할 상품 데이터 (MariaDB에서 조회한 실제 데이터)
TARGET_GOODS = [
    {
        'CODE': 'P-021',
        'NAME': '245/40R20 P ZERO RFT MOE (99Y)',
        'BUN1': '피렐리',
        'JAEGO': 37
    },
    {
        'CODE': 'P-030',
        'NAME': '245/45R18 P ZERO VOL (100W) ',
        'BUN1': '피렐리',
        'JAEGO': 0
    },
    {
        'CODE': 'P-CP7-11',
        'NAME': '245/45R18 CINTURATO P7 A/S * ',
        'BUN1': '피렐리',
        'JAEGO': 0
    },
    {
        'CODE': 'N-택시-05',
        'NAME': '205/65R16 MILECAP 2',
        'BUN1': '넥센',
        'JAEGO': 2
    },
    {
        'CODE': 'N-택시-07',
        'NAME': '205/55R16 MILECAP 2',
        'BUN1': '넥센',
        'JAEGO': 10
    }
]

def create_snapshots(goods_list):
    """스냅샷 생성"""
    created_count = 0
    updated_count = 0

    for goods in goods_list:
        code = goods['CODE']
        name = goods['NAME']
        bun1 = goods['BUN1'] or ''
        jaego = goods['JAEGO']
        snapshot_time = datetime.now()

        # 이전 스냅샷 확인
        prev_snapshot = GoodsRealtimeSnapshot.objects.filter(
            code=code
        ).order_by('-snapshot_time').first()

        # 변화량 계산
        change_from_prev = 0
        if prev_snapshot:
            change_from_prev = jaego - prev_snapshot.jaego

        # 스냅샷 생성
        snapshot = GoodsRealtimeSnapshot.objects.create(
            code=code,
            name=name,
            bun1=bun1,
            jaego=jaego,
            snapshot_time=snapshot_time,
            change_from_prev=change_from_prev
        )

        created_count += 1

        print(f"[생성] {code} | {name} | 재고: {jaego}개 | 변화: {change_from_prev:+d}")

    return created_count

def main():
    print("=" * 70)
    print("  실시간 재고 스냅샷 추가")
    print("=" * 70)
    print()

    print(f"대상 상품: {len(TARGET_GOODS)}개")
    codes = [g['CODE'] for g in TARGET_GOODS]
    print(f"상품 코드: {', '.join(codes)}")
    print()

    # 상품 정보 출력
    print("[대상 상품 정보]")
    for goods in TARGET_GOODS:
        print(f"  - {goods['CODE']}: {goods['NAME']} ({goods['BUN1']}) - 재고: {goods['JAEGO']}개")
    print()

    # 스냅샷 생성
    print("[스냅샷 생성 중...]")
    created_count = create_snapshots(TARGET_GOODS)

    print()
    print("=" * 70)
    print(f"[완료] {created_count}개 스냅샷 생성 완료")
    print("=" * 70)
    print()
    print("확인: https://tirepass.pythonanywhere.com/admin/tire_data/goodsrealtimesnapshot/")
    print()

if __name__ == '__main__':
    main()
