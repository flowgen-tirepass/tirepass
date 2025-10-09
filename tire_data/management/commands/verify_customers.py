"""
customers 테이블의 UTF-8 인코딩 확인

사용법:
    python manage.py verify_customers
"""
from django.core.management.base import BaseCommand
from tire_data.models import CustomersFull


class Command(BaseCommand):
    help = 'customers 테이블의 UTF-8 인코딩 확인'

    def handle(self, *args, **options):
        """customers 테이블 데이터 확인"""
        self.stdout.write(self.style.SUCCESS('=== customers 테이블 인코딩 확인 ===\n'))

        try:
            # 전체 고객 수
            total = CustomersFull.objects.count()
            self.stdout.write(f'총 {total}명의 고객 데이터')

            if total == 0:
                self.stdout.write(self.style.WARNING('데이터가 없습니다.'))
                return

            # 샘플 데이터 5개 가져오기
            customers = CustomersFull.objects.all()[:5]

            self.stdout.write('\n샘플 5개:')
            self.stdout.write('-' * 80)

            for customer in customers:
                self.stdout.write(f'CODE: {customer.code}')
                self.stdout.write(f'NAME: {customer.name}')
                self.stdout.write(f'REP: {customer.rep}')
                self.stdout.write(f'TEL1: {customer.tel1}')
                self.stdout.write(f'TEL3: {customer.tel3}')
                self.stdout.write(f'ENNO: {customer.enno}')
                self.stdout.write(f'ADDRESS1: {customer.address1}')
                self.stdout.write('-' * 80)

            # 한글이 제대로 표시되는지 확인
            first_customer = customers[0]
            if first_customer.name:
                has_korean = any('\uac00' <= c <= '\ud7a3' for c in first_customer.name)
                if has_korean:
                    self.stdout.write(
                        self.style.SUCCESS('\n✓ 한글이 정상적으로 저장되어 있습니다!')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING('\n✗ 한글이 감지되지 않았습니다. 인코딩 문제가 있을 수 있습니다.')
                    )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'에러: {e}'))
            import traceback
            traceback.print_exc()
