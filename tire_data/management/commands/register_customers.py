from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from tire_data.models import Customers
import re


class Command(BaseCommand):
    help = '사업자번호가 있는 모든 고객을 Django User로 일괄 등록합니다.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='실제로 등록하지 않고 시뮬레이션만 수행',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='이미 등록된 사용자도 다시 처리',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']

        self.stdout.write(self.style.SUCCESS('\n=== 고객 일괄 회원가입 시작 ===\n'))

        # 사업자번호가 있는 고객 조회
        if force:
            customers = Customers.objects.filter(
                enno__isnull=False
            ).exclude(enno='')
        else:
            customers = Customers.objects.filter(
                enno__isnull=False,
                is_registered=False
            ).exclude(enno='')

        total_count = customers.count()
        self.stdout.write(f'처리할 고객 수: {total_count}명\n')

        if total_count == 0:
            self.stdout.write(self.style.WARNING('처리할 고객이 없습니다.'))
            return

        success_count = 0
        skip_count = 0
        error_count = 0
        errors = []

        with transaction.atomic():
            for customer in customers:
                try:
                    # 사업자번호 정제 (숫자만 추출)
                    enno_clean = re.sub(r'[^0-9]', '', customer.enno)

                    if len(enno_clean) != 10:
                        error_count += 1
                        errors.append(f"{customer.code}: 잘못된 사업자번호 형식 ({customer.enno})")
                        continue

                    # 사용자명: 사업자번호 10자리
                    username = enno_clean

                    # 초기 비밀번호: 사업자번호 뒤 5자리
                    initial_password = enno_clean[-5:]

                    # 이미 존재하는 사용자 확인
                    if User.objects.filter(username=username).exists():
                        if force:
                            user = User.objects.get(username=username)
                            # 비밀번호 재설정
                            user.set_password(initial_password)
                            user.save()
                            self.stdout.write(f'  [업데이트] {customer.code} - {customer.name} ({username})')
                        else:
                            skip_count += 1
                            self.stdout.write(f'  [스킵] {customer.code} - {customer.name} (이미 등록됨)')
                            continue
                    else:
                        if not dry_run:
                            # 새 사용자 생성
                            user = User.objects.create_user(
                                username=username,
                                password=initial_password,
                                first_name=customer.rep or '',  # 대표자명
                                last_name=customer.name or '',  # 회사명
                            )

                            # 추가 정보 저장 (UserProfile이 있다면)
                            user.email = f'{username}@tirepass.com'  # 임시 이메일
                            user.save()

                            # 고객 정보 업데이트
                            customer.is_registered = True
                            customer.user_id = user.id
                            customer.must_change_password = True
                            customer.save()

                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'  [등록] {customer.code} - {customer.name} '
                                    f'(ID: {username}, PW: {initial_password})'
                                )
                            )
                        else:
                            self.stdout.write(
                                f'  [시뮬레이션] {customer.code} - {customer.name} '
                                f'(ID: {username}, PW: {initial_password})'
                            )

                    success_count += 1

                except Exception as e:
                    error_count += 1
                    errors.append(f"{customer.code}: {str(e)}")
                    self.stdout.write(
                        self.style.ERROR(f'  [오류] {customer.code} - {customer.name}: {str(e)}')
                    )

            if dry_run:
                # 드라이런 모드에서는 롤백
                transaction.set_rollback(True)

        # 결과 요약
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS(f'\n처리 완료!'))
        self.stdout.write(f'  - 성공: {success_count}명')
        self.stdout.write(f'  - 스킵: {skip_count}명')
        self.stdout.write(f'  - 오류: {error_count}명')

        if errors and error_count <= 10:
            self.stdout.write(self.style.ERROR('\n오류 목록:'))
            for error in errors:
                self.stdout.write(f'  - {error}')

        if dry_run:
            self.stdout.write(
                self.style.WARNING('\n[드라이런 모드] 실제로 등록되지 않았습니다.')
            )

        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(
            self.style.WARNING(
                '\n[!] 보안 주의사항:\n'
                '  - 모든 사용자의 초기 비밀번호는 사업자번호 뒤 5자리입니다.\n'
                '  - 첫 로그인 시 반드시 비밀번호를 변경하도록 안내하세요.\n'
            )
        )