"""
Django management command: 실시간 재고 스냅샷 수집

실행:
    python manage.py collect_realtime_snapshots

용도:
    - 매시간 변화가 많은 상위 5개 상품의 재고 스냅샷 수집
    - 이전 스냅샷과 비교하여 변화량 자동 계산
    - Admin 위젯에서 실시간성 증명용
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from tire_data.erp_api_client import ERPAPIClient
from tire_data.models import GoodsRealtimeSnapshot, Goods
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = '실시간 재고 스냅샷 수집 (변화가 많은 상위 5개 상품)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--top',
            type=int,
            default=5,
            help='수집할 상품 개수 (기본값: 5)'
        )

    def handle(self, *args, **options):
        top_n = options['top']
        now = timezone.now()

        self.stdout.write(f"=== 실시간 재고 스냅샷 수집 ({now}) ===\n")

        try:
            # 방법 1: 재고가 많은 상품 (변화 가능성 높음)
            # ERP API에서 전체 상품 조회
            self.stdout.write("ERP API에서 상품 데이터 조회 중...")

            # 간단히 재고 상위 상품만 조회
            goods_list = ERPAPIClient.get_goods_list(offset=0, limit=100)

            # 재고 많은 순으로 정렬
            goods_list_sorted = sorted(
                goods_list,
                key=lambda x: x.get('jaego', 0),
                reverse=True
            )

            # 상위 N개만 선택
            top_goods = goods_list_sorted[:top_n]

            self.stdout.write(f"수집 대상: {len(top_goods)}개 상품\n")

            # 스냅샷 저장
            collected_count = 0

            for goods_data in top_goods:
                code = goods_data.get('code')
                name = goods_data.get('name', '')
                bun1 = goods_data.get('bun1', '')
                jaego = goods_data.get('jaego', 0)

                # 이전 스냅샷 조회 (변화량 계산)
                prev_snapshot = GoodsRealtimeSnapshot.objects.filter(
                    code=code
                ).order_by('-snapshot_time').first()

                if prev_snapshot:
                    change = jaego - prev_snapshot.jaego
                else:
                    change = 0

                # 스냅샷 저장
                snapshot = GoodsRealtimeSnapshot.objects.create(
                    code=code,
                    name=name,
                    bun1=bun1,
                    jaego=jaego,
                    snapshot_time=now,
                    change_from_prev=change
                )

                change_indicator = '🔴' if change < 0 else ('🟢' if change > 0 else '⚪')
                self.stdout.write(
                    f"  {code} | {name[:30]:30s} | {jaego:4d}개 ({change:+3d}) {change_indicator}"
                )

                collected_count += 1

            self.stdout.write(self.style.SUCCESS(f"\n✅ 스냅샷 수집 완료: {collected_count}개"))

            # 오래된 스냅샷 정리 (30일 이상)
            cutoff_date = now - timedelta(days=30)
            deleted_count, _ = GoodsRealtimeSnapshot.objects.filter(
                snapshot_time__lt=cutoff_date
            ).delete()

            if deleted_count > 0:
                self.stdout.write(f"🗑️  오래된 스냅샷 정리: {deleted_count}개")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n❌ 스냅샷 수집 실패: {e}"))
            import traceback
            traceback.print_exc()
            raise
