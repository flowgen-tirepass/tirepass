"""
ERP API에서 상품 데이터를 가져와 MySQL DB 동기화

실행:
    python scripts/sync_erp_goods_api.py
"""

import os
import sys
import django
from datetime import datetime

# Django 설정 로드
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itire.settings')
django.setup()

from tire_data.erp_api_client import ERPAPIClient
from tire_data.models import Goods
from django.db import transaction


def sync_goods():
    """ERP API에서 상품 데이터를 가져와 MySQL DB에 동기화"""
    start_time = datetime.now()
    print(f"=== ERP 상품 동기화 시작 ({start_time}) ===\n")

    try:
        # ERP API에서 전체 상품 개수 조회
        total_count = ERPAPIClient.get_goods_count()
        print(f"ERP 전체 상품: {total_count:,}개\n")

        # 전체 상품 데이터 조회
        print("상품 데이터 다운로드 중...")
        goods_list = ERPAPIClient.get_goods_list(offset=0, limit=total_count)
        print(f"다운로드 완료: {len(goods_list):,}개\n")

        # MySQL DB 동기화
        print("MySQL DB 동기화 중...")

        created_count = 0
        updated_count = 0

        with transaction.atomic():
            for i, goods_data in enumerate(goods_list, 1):
                code = goods_data.get('code')
                name = goods_data.get('name', '')
                bun1 = goods_data.get('bun1', '')
                jaego = goods_data.get('jaego', 0)
                fixp = goods_data.get('fixp', 0)

                # Goods 모델에 저장 또는 업데이트
                obj, created = Goods.objects.update_or_create(
                    code=code,
                    defaults={
                        'name': name,
                        'bun1': bun1,
                        'jaego': jaego,
                        'fixp': fixp,
                    }
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1

                # 진행률 표시 (1000개마다)
                if i % 1000 == 0:
                    print(f"  진행: {i:,} / {len(goods_list):,} ({i*100//len(goods_list)}%)")

        # 결과 출력
        end_time = datetime.now()
        elapsed = (end_time - start_time).total_seconds()

        print(f"\n=== 동기화 완료 ===")
        print(f"소요 시간: {elapsed:.1f}초")
        print(f"신규 생성: {created_count:,}개")
        print(f"업데이트: {updated_count:,}개")
        print(f"총 처리: {created_count + updated_count:,}개")

        return True

    except Exception as e:
        print(f"\n❌ 동기화 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = sync_goods()
    sys.exit(0 if success else 1)
