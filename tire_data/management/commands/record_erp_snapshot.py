"""
ERP 상태 스냅샷 기록 명령어

사용법:
    python manage.py record_erp_snapshot

크론탭 설정 (PythonAnywhere):
    0 * * * * /home/tirepass/.virtualenvs/tirepass-venv/bin/python /home/tirepass/tirepass/manage.py record_erp_snapshot
    # 매시간 정각마다 실행
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
import requests
from django.conf import settings
import time


class Command(BaseCommand):
    help = 'ERP 시스템 상태 스냅샷 기록 (매시간)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='강제 실행 (시간 제약 무시)',
        )

    def handle(self, *args, **options):
        from tire_data.models import ERPSnapshot

        now = timezone.now()

        # 매시간 0분에만 실행 (--force 옵션이 없는 경우)
        if not options['force'] and now.minute > 5:
            self.stdout.write(
                self.style.WARNING(
                    f'⏰ 스냅샷은 매시간 0~5분 사이에만 기록됩니다. (현재: {now.minute}분)'
                )
            )
            return

        self.stdout.write('🔍 ERP 상태 확인 중...')

        try:
            # ERP API 호출
            start_time = time.time()
            response = requests.get(
                f"{settings.ERP_SYNC_API_URL}/health",
                timeout=settings.ERP_SYNC_TIMEOUT
            )
            end_time = time.time()
            response_time = round((end_time - start_time) * 1000, 2)  # ms

            if response.status_code == 200:
                data = response.json()

                # 스냅샷 저장
                snapshot = ERPSnapshot.objects.create(
                    timestamp=now,
                    status='connected',
                    response_time_ms=response_time,
                    erp_goods_count=data.get('total_goods', 0),
                    database_status=data.get('database', 'unknown'),
                    api_url=settings.ERP_SYNC_API_URL
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ 스냅샷 저장 완료: {snapshot.timestamp.strftime("%Y-%m-%d %H:%M:%S")} '
                        f'| 상품: {snapshot.erp_goods_count:,}개 '
                        f'| 응답: {snapshot.response_time_ms}ms'
                    )
                )

            else:
                # 연결 실패도 기록
                snapshot = ERPSnapshot.objects.create(
                    timestamp=now,
                    status='disconnected',
                    response_time_ms=None,
                    erp_goods_count=0,
                    database_status='disconnected',
                    api_url=settings.ERP_SYNC_API_URL,
                    error_message=f'HTTP {response.status_code}'
                )

                self.stdout.write(
                    self.style.ERROR(
                        f'❌ 연결 실패: HTTP {response.status_code}'
                    )
                )

        except requests.exceptions.Timeout:
            snapshot = ERPSnapshot.objects.create(
                timestamp=now,
                status='timeout',
                response_time_ms=None,
                erp_goods_count=0,
                database_status='unknown',
                api_url=settings.ERP_SYNC_API_URL,
                error_message='Connection timeout'
            )

            self.stdout.write(
                self.style.ERROR('❌ 연결 타임아웃')
            )

        except requests.exceptions.ConnectionError:
            snapshot = ERPSnapshot.objects.create(
                timestamp=now,
                status='connection_error',
                response_time_ms=None,
                erp_goods_count=0,
                database_status='unknown',
                api_url=settings.ERP_SYNC_API_URL,
                error_message='Connection refused'
            )

            self.stdout.write(
                self.style.ERROR('❌ 연결 거부')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ 오류 발생: {str(e)}')
            )

        # 30일 이상 오래된 스냅샷 삭제 (디스크 공간 절약)
        deleted_count = ERPSnapshot.objects.filter(
            timestamp__lt=now - timezone.timedelta(days=30)
        ).delete()[0]

        if deleted_count > 0:
            self.stdout.write(
                self.style.WARNING(
                    f'🗑️ 30일 이상 오래된 스냅샷 {deleted_count}개 삭제'
                )
            )
