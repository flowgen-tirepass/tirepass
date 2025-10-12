"""
ERP 상품 데이터 자동 동기화 스케줄러

5분마다 자동으로 ERP API에서 상품 데이터를 가져와 MySQL에 동기화합니다.

실행:
    python scripts/auto_sync_scheduler.py

백그라운드 실행 (Linux/PythonAnywhere):
    nohup python scripts/auto_sync_scheduler.py > logs/sync_scheduler.log 2>&1 &

중지:
    ps aux | grep auto_sync_scheduler
    kill <PID>
"""

import os
import sys
import time
import django
from datetime import datetime
import logging

# Django 설정 로드
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itire.settings')
django.setup()

from tire_data.erp_api_client import ERPAPIClient
from tire_data.models import Goods
from django.db import transaction

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/sync_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def sync_goods():
    """ERP API에서 상품 데이터를 가져와 MySQL DB에 동기화"""
    start_time = datetime.now()
    logger.info("=" * 60)
    logger.info(f"동기화 시작: {start_time}")

    try:
        # ERP API에서 전체 상품 개수 조회
        total_count = ERPAPIClient.get_goods_count()
        logger.info(f"ERP 전체 상품: {total_count:,}개")

        # 전체 상품 데이터 조회
        goods_list = ERPAPIClient.get_goods_list(offset=0, limit=total_count)
        logger.info(f"다운로드 완료: {len(goods_list):,}개")

        # MySQL DB 동기화
        created_count = 0
        updated_count = 0

        with transaction.atomic():
            for goods_data in goods_list:
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

        # 결과 출력
        end_time = datetime.now()
        elapsed = (end_time - start_time).total_seconds()

        logger.info(f"✅ 동기화 완료 - 소요시간: {elapsed:.1f}초")
        logger.info(f"   신규: {created_count:,}개 / 업데이트: {updated_count:,}개 / 총: {created_count + updated_count:,}개")

        return True

    except Exception as e:
        logger.error(f"❌ 동기화 실패: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def run_scheduler(interval_minutes=5):
    """
    주기적으로 동기화 실행

    Args:
        interval_minutes (int): 동기화 간격 (분)
    """
    logger.info("=" * 60)
    logger.info(f"🚀 자동 동기화 스케줄러 시작")
    logger.info(f"   동기화 간격: {interval_minutes}분")
    logger.info(f"   Ctrl+C로 중지")
    logger.info("=" * 60)

    # 즉시 첫 동기화 실행
    logger.info("첫 번째 동기화 실행...")
    sync_goods()

    # 주기적 실행
    interval_seconds = interval_minutes * 60

    try:
        while True:
            logger.info(f"\n⏰ {interval_minutes}분 대기 중... (다음 실행: {datetime.now().replace(second=0, microsecond=0).strftime('%H:%M')})")
            time.sleep(interval_seconds)
            sync_goods()

    except KeyboardInterrupt:
        logger.info("\n🛑 스케줄러 중지됨 (Ctrl+C)")
    except Exception as e:
        logger.error(f"\n💥 스케줄러 오류: {e}")
        import traceback
        logger.error(traceback.format_exc())


if __name__ == '__main__':
    # logs 디렉토리 생성
    os.makedirs('logs', exist_ok=True)

    # 동기화 간격 (분) - 기본 5분
    SYNC_INTERVAL_MINUTES = int(os.getenv('SYNC_INTERVAL_MINUTES', 5))

    run_scheduler(interval_minutes=SYNC_INTERVAL_MINUTES)
