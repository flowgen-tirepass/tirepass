"""
성능표시 옵션 Excel 데이터 Import 명령어
Usage: python manage.py import_performance_options
"""
from django.core.management.base import BaseCommand
import pandas as pd
import os


class Command(BaseCommand):
    help = '성능표시 옵션 Excel 파일을 DB로 Import (Choice 선택용)'

    def handle(self, *args, **options):
        excel_path = r'data\브랜드 패턴\성능표시.xlsx'

        if not os.path.exists(excel_path):
            self.stdout.write(self.style.ERROR(f'❌ 파일을 찾을 수 없습니다: {excel_path}'))
            return

        self.stdout.write(self.style.SUCCESS(f'📁 파일 로딩: {excel_path}'))

        # 엑셀 읽기
        df = pd.read_excel(excel_path)

        self.stdout.write(f'\n📊 읽은 데이터:')
        self.stdout.write(f'  - 컬럼: {df.columns.tolist()}')
        self.stdout.write(f'  - 총 {len(df)}행')

        # 각 컬럼별 고유값 수집
        classifications = set()
        grades = set()
        performances = set()
        seasons = set()
        road_types = set()

        for col in df.columns:
            for value in df[col]:
                if pd.notna(value) and str(value).strip():
                    clean_value = str(value).strip()

                    if col == '분류1':
                        classifications.add(clean_value)
                    elif col == '상품등급':
                        grades.add(clean_value)
                    elif col == '상품성능':
                        performances.add(clean_value)
                    elif col == '계절':
                        seasons.add(clean_value)
                    elif col == 'ON/OFF로드':
                        road_types.add(clean_value)

        # 결과 출력
        self.stdout.write(f'\n✅ Import 완료!')
        self.stdout.write(f'\n📌 분류1 옵션 ({len(classifications)}개):')
        for item in sorted(classifications):
            self.stdout.write(f'  - {item}')

        self.stdout.write(f'\n📌 상품등급 옵션 ({len(grades)}개):')
        for item in sorted(grades):
            self.stdout.write(f'  - {item}')

        self.stdout.write(f'\n📌 상품성능 옵션 ({len(performances)}개):')
        for item in sorted(performances):
            self.stdout.write(f'  - {item}')

        self.stdout.write(f'\n📌 계절 옵션 ({len(seasons)}개):')
        for item in sorted(seasons):
            self.stdout.write(f'  - {item}')

        self.stdout.write(f'\n📌 ON/OFF로드 옵션 ({len(road_types)}개):')
        for item in sorted(road_types):
            self.stdout.write(f'  - {item}')

        # 안내 메시지
        self.stdout.write(self.style.SUCCESS(f'\n💡 Admin에서 브랜드/패턴별로 위 옵션 중 선택하여 설정할 수 있습니다.'))
        self.stdout.write(f'   경로: Admin > D. 📱 모바일 > 01. 브랜드/패턴 성능표시')
