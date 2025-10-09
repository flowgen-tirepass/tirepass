"""
ERP 고객 데이터를 customers_simple로 마이그레이션하는 스크립트

사용법:
    python manage.py migrate_erp_customers
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from tire_data.models import CustomersFull, Customers


class Command(BaseCommand):
    help = 'ERP 고객 데이터를 customers_simple로 마이그레이션 (사업자번호 기반 계정 생성)'

    def handle(self, *args, **options):
        """
        ERP customers 테이블에서 데이터를 가져와 customers_simple에 회원 등록
        - 사업자번호가 있는 고객만 처리
        - 계정: 사업자등록번호 10자리
        - 초기 비밀번호: 사업자등록번호 뒤 5자리
        """
        self.stdout.write(self.style.SUCCESS('=== ERP 고객 마이그레이션 시작 ==='))

        # ERP 전체 고객 가져오기
        erp_customers = CustomersFull.objects.all()
        total_count = erp_customers.count()

        self.stdout.write(f'총 {total_count}명의 ERP 고객 발견')

        success_count = 0
        skip_count = 0
        error_count = 0

        for erp_customer in erp_customers:
            # 사업자번호 확인
            if not erp_customer.enno:
                skip_count += 1
                self.stdout.write(
                    self.style.WARNING(
                        f'건너뜀: {erp_customer.code} - {erp_customer.name} (사업자번호 없음)'
                    )
                )
                continue

            # 사업자번호 정제 (하이픈 제거, 10자리 확인)
            enno_clean = erp_customer.enno.replace('-', '').strip()

            if not enno_clean.isdigit() or len(enno_clean) != 10:
                skip_count += 1
                self.stdout.write(
                    self.style.WARNING(
                        f'건너뜀: {erp_customer.code} - {erp_customer.name} (사업자번호 형식 오류: {erp_customer.enno})'
                    )
                )
                continue

            # 이미 등록된 계정인지 확인
            if Customers.objects.filter(code=enno_clean).exists():
                skip_count += 1
                self.stdout.write(
                    self.style.WARNING(
                        f'이미 존재: {enno_clean} - {erp_customer.name}'
                    )
                )
                continue

            try:
                # 초기 비밀번호: 사업자번호 뒤 5자리
                initial_password = enno_clean[-5:]
                hashed_password = make_password(initial_password)

                # customers_simple에 회원 등록
                Customers.objects.create(
                    code=enno_clean,  # 사업자번호를 고객코드로 사용
                    name=erp_customer.name or '',
                    rep=erp_customer.rep or '',
                    tel1=erp_customer.tel1 or '',
                    tel3=erp_customer.tel3 or '',
                    enno=enno_clean,
                    password=hashed_password,
                    is_registered=True,
                    must_change_password=True  # 최초 로그인 시 비밀번호 변경 요구
                )

                success_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'성공: {enno_clean} - {erp_customer.name} (비밀번호: {initial_password})'
                    )
                )

            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(
                        f'에러: {erp_customer.code} - {erp_customer.name}: {str(e)}'
                    )
                )

        # 결과 요약
        self.stdout.write(self.style.SUCCESS('\n=== 마이그레이션 완료 ==='))
        self.stdout.write(f'총 처리: {total_count}명')
        self.stdout.write(self.style.SUCCESS(f'성공: {success_count}명'))
        self.stdout.write(self.style.WARNING(f'건너뜀: {skip_count}명'))
        self.stdout.write(self.style.ERROR(f'에러: {error_count}명'))

        self.stdout.write(self.style.SUCCESS('\n모든 계정의 초기 비밀번호는 사업자번호 뒤 5자리입니다.'))
        self.stdout.write(self.style.WARNING('최초 로그인 시 비밀번호 변경이 필요합니다.'))
