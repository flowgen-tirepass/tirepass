"""
Django management command: ERP 상품 데이터 동기화

실행:
    python manage.py sync_erp_goods
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from tire_data.erp_api_client import ERPAPIClient
from tire_data.models import Goods, ExcludedGoods
from datetime import datetime


class Command(BaseCommand):
    help = 'ERP API에서 상품 데이터를 가져와 MySQL DB에 동기화'

    def handle(self, *args, **options):
        start_time = datetime.now()
        self.stdout.write(f"=== ERP 상품 동기화 시작 ({start_time}) ===\n")

        try:
            # ERP API에서 전체 상품 개수 조회
            total_count = ERPAPIClient.get_goods_count()
            self.stdout.write(f"ERP 전체 상품: {total_count:,}개\n")

            # 전체 상품 데이터 조회
            self.stdout.write("상품 데이터 다운로드 중...")
            goods_list = ERPAPIClient.get_goods_list(offset=0, limit=total_count)
            self.stdout.write(self.style.SUCCESS(f"다운로드 완료: {len(goods_list):,}개\n"))

            # 제외 목록 조회
            excluded_codes = set(ExcludedGoods.objects.values_list('code', flat=True))
            if excluded_codes:
                self.stdout.write(f"⚠️  제외 목록: {len(excluded_codes)}개 상품은 동기화하지 않습니다.")
                for code in excluded_codes:
                    self.stdout.write(f"  - {code}")

            # MySQL DB 동기화
            self.stdout.write("\nMySQL DB 동기화 중...")

            created_count = 0
            updated_count = 0
            skipped_count = 0

            with transaction.atomic():
                for i, goods_data in enumerate(goods_list, 1):
                    code = goods_data.get('code')

                    # 제외 목록에 있으면 건너뛰기
                    if code in excluded_codes:
                        skipped_count += 1
                        continue

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
                        self.stdout.write(f"  진행: {i:,} / {len(goods_list):,} ({i*100//len(goods_list)}%)")

            # 결과 출력
            end_time = datetime.now()
            elapsed = (end_time - start_time).total_seconds()

            self.stdout.write(self.style.SUCCESS(f"\n=== 동기화 완료 ==="))
            self.stdout.write(f"소요 시간: {elapsed:.1f}초")
            self.stdout.write(f"신규 생성: {created_count:,}개")
            self.stdout.write(f"업데이트: {updated_count:,}개")
            if skipped_count > 0:
                self.stdout.write(f"제외됨: {skipped_count:,}개 (ERP 동기화 제외 목록)")
            self.stdout.write(f"총 처리: {created_count + updated_count:,}개")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n❌ 동기화 실패: {e}"))
            import traceback
            traceback.print_exc()
            raise
