"""
Django management command: 성능 표기 초기 데이터 생성

실행:
    python manage.py init_performance_tags
"""

from django.core.management.base import BaseCommand
from tire_data.models import PerformanceCategory, PerformanceTag


class Command(BaseCommand):
    help = '성능 표기 카테고리 및 태그 초기 데이터 생성'

    def handle(self, *args, **options):
        self.stdout.write("=== 성능 표기 초기 데이터 생성 시작 ===\n")

        # 기존 데이터 삭제 여부 확인
        existing_count = PerformanceCategory.objects.count()
        if existing_count > 0:
            self.stdout.write(self.style.WARNING(f"기존 카테고리 {existing_count}개 발견"))
            confirm = input("기존 데이터를 삭제하고 다시 생성하시겠습니까? (yes/no): ")
            if confirm.lower() != 'yes':
                self.stdout.write(self.style.ERROR("작업 취소됨"))
                return

            # 기존 데이터 삭제
            PerformanceCategory.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("기존 데이터 삭제 완료\n"))

        # 카테고리 및 태그 데이터
        data = {
            'vehicle_type': {
                'display_name': '차량용도',
                'order': 1,
                'tags': ['전체', '승용세단', '승용 SUV/RV', '트럭/밴', '스포츠카']
            },
            'price_tier': {
                'display_name': '가격대',
                'order': 2,
                'tags': ['전체', '가성비', '고급형', '최고급형', 'OE용타이어', '전기차']
            },
            'driving_style': {
                'display_name': '주행스타일',
                'order': 3,
                'tags': ['전체', '스탠다드', '컴포트', '스포츠', '프리미엄스포츠']
            },
            'season': {
                'display_name': '계절',
                'order': 4,
                'tags': ['사계절용', '올웨더', '겨울용', '여름용']
            },
            'terrain': {
                'display_name': '지형',
                'order': 5,
                'tags': ['오프로드', '온오프로드(AT)', '온로드(HT)']
            },
        }

        total_categories = 0
        total_tags = 0

        for category_name, category_data in data.items():
            # 카테고리 생성
            category = PerformanceCategory.objects.create(
                name=category_name,
                display_name=category_data['display_name'],
                order=category_data['order'],
                is_active=True
            )
            total_categories += 1
            self.stdout.write(f"✓ 카테고리 생성: {category.display_name}")

            # 태그 생성
            for idx, tag_name in enumerate(category_data['tags'], 1):
                PerformanceTag.objects.create(
                    category=category,
                    name=tag_name,
                    order=idx,
                    is_active=True
                )
                total_tags += 1
                self.stdout.write(f"  - {tag_name}")

            self.stdout.write("")  # 빈 줄

        self.stdout.write(self.style.SUCCESS(f"\n=== 완료 ==="))
        self.stdout.write(f"생성된 카테고리: {total_categories}개")
        self.stdout.write(f"생성된 태그: {total_tags}개")
