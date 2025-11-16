"""
브랜드별 패턴 엑셀 데이터 Import 명령어
Usage: python manage.py import_brand_patterns
"""
from django.core.management.base import BaseCommand
from tire_data.models import Brand, BrandPattern
import pandas as pd
import os


class Command(BaseCommand):
    help = '브랜드별 패턴 엑셀 파일을 DB로 Import'

    def handle(self, *args, **options):
        excel_path = 'data/브랜드별패턴.xlsx'

        if not os.path.exists(excel_path):
            self.stdout.write(self.style.ERROR(f'❌ 파일을 찾을 수 없습니다: {excel_path}'))
            return

        self.stdout.write(self.style.SUCCESS(f'📁 파일 로딩: {excel_path}'))

        # 엑셀 읽기
        df = pd.read_excel(excel_path)

        # 첫 번째 행이 브랜드명
        brand_row = df.iloc[0]

        # 브랜드 매핑 (컬럼명 → 브랜드명)
        brand_columns = {}
        for col_idx, col_name in enumerate(df.columns):
            if col_idx == 0:  # '브랜드별 패턴' 컬럼
                continue
            if col_idx == 1:  # '금호' 컬럼
                brand_name = str(brand_row.iloc[1]).strip() if pd.notna(brand_row.iloc[1]) else '금호'
            else:
                brand_name = str(brand_row.iloc[col_idx]).strip() if pd.notna(brand_row.iloc[col_idx]) else col_name

            brand_columns[col_name] = brand_name

        self.stdout.write(f'\n📌 브랜드 목록:')
        for col, brand in brand_columns.items():
            self.stdout.write(f'  - {brand}')

        # 브랜드 생성
        brand_objects = {}
        for idx, (col_name, brand_name) in enumerate(brand_columns.items()):
            brand, created = Brand.objects.get_or_create(
                name=brand_name,
                defaults={
                    'display_order': idx,
                    'is_active': True
                }
            )
            brand_objects[col_name] = brand

            if created:
                self.stdout.write(self.style.SUCCESS(f'✅ 브랜드 생성: {brand_name}'))
            else:
                self.stdout.write(f'ℹ️  브랜드 존재: {brand_name}')

        # 패턴 Import (2번째 행부터)
        total_patterns = 0
        for row_idx in range(1, len(df)):
            row = df.iloc[row_idx]

            # 각 브랜드별로 패턴 처리
            for col_idx, col_name in enumerate(df.columns):
                if col_idx == 0:  # 번호 컬럼
                    continue

                if col_name not in brand_objects:
                    continue

                pattern_value = row.iloc[col_idx]

                # NaN이거나 빈 값이면 스킵
                if pd.isna(pattern_value) or str(pattern_value).strip() == '':
                    continue

                pattern_name = str(pattern_value).strip()
                brand = brand_objects[col_name]

                # 패턴 생성
                pattern, created = BrandPattern.objects.get_or_create(
                    brand=brand,
                    pattern_name=pattern_name,
                    defaults={
                        'display_order': row_idx,
                        'is_active': True
                    }
                )

                if created:
                    total_patterns += 1

        self.stdout.write(self.style.SUCCESS(f'\n✅ Import 완료!'))
        self.stdout.write(f'  - 브랜드: {len(brand_objects)}개')
        self.stdout.write(f'  - 새로운 패턴: {total_patterns}개')

        # 통계 출력
        self.stdout.write(f'\n📊 브랜드별 패턴 통계:')
        for col_name, brand in brand_objects.items():
            pattern_count = BrandPattern.objects.filter(brand=brand).count()
            self.stdout.write(f'  - {brand.name}: {pattern_count}개')
