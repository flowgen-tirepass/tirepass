"""
브랜드 그룹 및 패턴 초기 데이터 생성

실행 방법:
pythonanywhere에서:
cd ~/tirepass
python setup_brand_groups.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itire.settings')
django.setup()

from tire_data.models import BrandGroup, BrandGroupPattern


def setup_brand_groups():
    """주요 타이어 브랜드의 그룹 및 패턴 설정"""

    # 브랜드별 그룹 및 패턴 데이터
    brand_data = {
        '피렐리': [
            {
                'group_name': 'P ZERO 시리즈',
                'group_order': 1,
                'description': '고성능 스포츠 타이어',
                'patterns': ['P ZERO', 'P ZERO NERO', 'P ZERO ROSSO', 'P ZERO RUN FLAT']
            },
            {
                'group_name': 'CINTURATO 시리즈',
                'group_order': 2,
                'description': '프리미엄 컴포트 타이어',
                'patterns': ['CINTURATO P7', 'CINTURATO P1', 'CINTURATO']
            },
            {
                'group_name': 'SCORPION 시리즈',
                'group_order': 3,
                'description': 'SUV 전용 타이어',
                'patterns': ['SCORPION VERDE', 'SCORPION ATR', 'SCORPION']
            },
        ],
        '미쉐린': [
            {
                'group_name': 'PILOT 시리즈',
                'group_order': 1,
                'description': '고성능 스포츠 타이어',
                'patterns': ['PILOT SPORT', 'PILOT SPORT A/S', 'PILOT SUPER SPORT']
            },
            {
                'group_name': 'PRIMACY 시리즈',
                'group_order': 2,
                'description': '프리미엄 컴포트 타이어',
                'patterns': ['PRIMACY 4', 'PRIMACY 3', 'PRIMACY']
            },
            {
                'group_name': 'X-ICE 시리즈',
                'group_order': 3,
                'description': '겨울용 스노우 타이어',
                'patterns': ['X-ICE', 'X-ICE SNOW']
            },
        ],
        '금호': [
            {
                'group_name': 'ECSTA 시리즈',
                'group_order': 1,
                'description': '고성능 스포츠 타이어',
                'patterns': ['ECSTA PS', 'ECSTA LE', 'ECSTA']
            },
            {
                'group_name': 'SOLUS 시리즈',
                'group_order': 2,
                'description': '컴포트 승용 타이어',
                'patterns': ['SOLUS TA', 'SOLUS KH', 'SOLUS']
            },
            {
                'group_name': 'CRUGEN 시리즈',
                'group_order': 3,
                'description': 'SUV 전용 타이어',
                'patterns': ['CRUGEN HP', 'CRUGEN']
            },
        ],
        '한국': [
            {
                'group_name': 'VENTUS 시리즈',
                'group_order': 1,
                'description': '고성능 스포츠 타이어',
                'patterns': ['VENTUS S', 'VENTUS V', 'VENTUS']
            },
            {
                'group_name': 'KINERGY 시리즈',
                'group_order': 2,
                'description': '친환경 컴포트 타이어',
                'patterns': ['KINERGY GT', 'KINERGY EX', 'KINERGY']
            },
            {
                'group_name': 'DYNAPRO 시리즈',
                'group_order': 3,
                'description': 'SUV 전용 타이어',
                'patterns': ['DYNAPRO HP', 'DYNAPRO AT', 'DYNAPRO']
            },
        ],
        '넥센': [
            {
                'group_name': 'N\'FERA 시리즈',
                'group_order': 1,
                'description': '고성능 스포츠 타이어',
                'patterns': ['N\'FERA SU', 'N\'FERA RU', 'N\'FERA']
            },
            {
                'group_name': 'ROADIAN 시리즈',
                'group_order': 2,
                'description': 'SUV 전용 타이어',
                'patterns': ['ROADIAN HP', 'ROADIAN AT', 'ROADIAN']
            },
            {
                'group_name': 'NBLUE 시리즈',
                'group_order': 3,
                'description': '친환경 컴포트 타이어',
                'patterns': ['NBLUE HD', 'NBLUE']
            },
        ],
        '브리지스톤': [
            {
                'group_name': 'POTENZA 시리즈',
                'group_order': 1,
                'description': '고성능 스포츠 타이어',
                'patterns': ['POTENZA RE', 'POTENZA S', 'POTENZA']
            },
            {
                'group_name': 'TURANZA 시리즈',
                'group_order': 2,
                'description': '프리미엄 투어링 타이어',
                'patterns': ['TURANZA T', 'TURANZA ER', 'TURANZA']
            },
            {
                'group_name': 'ECOPIA 시리즈',
                'group_order': 3,
                'description': '친환경 연비 타이어',
                'patterns': ['ECOPIA EP', 'ECOPIA']
            },
        ],
        '콘티넨탈': [
            {
                'group_name': 'SportContact 시리즈',
                'group_order': 1,
                'description': '고성능 스포츠 타이어',
                'patterns': ['ContiSportContact', 'SportContact']
            },
            {
                'group_name': 'PremiumContact 시리즈',
                'group_order': 2,
                'description': '프리미엄 컴포트 타이어',
                'patterns': ['PremiumContact', 'ContiPremiumContact']
            },
            {
                'group_name': 'EcoContact 시리즈',
                'group_order': 3,
                'description': '친환경 연비 타이어',
                'patterns': ['EcoContact', 'ContiEcoContact']
            },
        ],
        '굳이어': [
            {
                'group_name': 'EAGLE 시리즈',
                'group_order': 1,
                'description': '고성능 스포츠 타이어',
                'patterns': ['EAGLE F1', 'EAGLE LS', 'EAGLE']
            },
            {
                'group_name': 'ASSURANCE 시리즈',
                'group_order': 2,
                'description': '컴포트 승용 타이어',
                'patterns': ['ASSURANCE', 'ASSURANCE TRIPLEMAX']
            },
            {
                'group_name': 'EFFICIENTGRIP 시리즈',
                'group_order': 3,
                'description': '친환경 연비 타이어',
                'patterns': ['EFFICIENTGRIP']
            },
        ],
        '던롭': [
            {
                'group_name': 'SP SPORT 시리즈',
                'group_order': 1,
                'description': '고성능 스포츠 타이어',
                'patterns': ['SP SPORT MAXX', 'SP SPORT', 'SPORT MAXX']
            },
            {
                'group_name': 'GRANDTREK 시리즈',
                'group_order': 2,
                'description': 'SUV 전용 타이어',
                'patterns': ['GRANDTREK AT', 'GRANDTREK PT', 'GRANDTREK']
            },
        ],
        '요코하마': [
            {
                'group_name': 'ADVAN 시리즈',
                'group_order': 1,
                'description': '고성능 스포츠 타이어',
                'patterns': ['ADVAN SPORT', 'ADVAN NEOVA', 'ADVAN']
            },
            {
                'group_name': 'GEOLANDAR 시리즈',
                'group_order': 2,
                'description': 'SUV 전용 타이어',
                'patterns': ['GEOLANDAR A/T', 'GEOLANDAR H/T', 'GEOLANDAR']
            },
        ],
    }

    created_groups = 0
    created_patterns = 0
    skipped_groups = 0

    for brand, groups in brand_data.items():
        print(f"\n=== {brand} ===")

        for group_info in groups:
            # 그룹 생성 또는 가져오기
            group, created = BrandGroup.objects.get_or_create(
                brand=brand,
                group_name=group_info['group_name'],
                defaults={
                    'group_order': group_info['group_order'],
                    'description': group_info['description'],
                    'is_active': True
                }
            )

            if created:
                print(f"  ✓ 그룹 생성: {group_info['group_name']}")
                created_groups += 1
            else:
                print(f"  - 그룹 존재: {group_info['group_name']}")
                skipped_groups += 1

            # 패턴 추가
            for pattern in group_info['patterns']:
                pattern_obj, created = BrandGroupPattern.objects.get_or_create(
                    group=group,
                    pattern=pattern
                )

                if created:
                    print(f"    ✓ 패턴 추가: {pattern}")
                    created_patterns += 1
                else:
                    print(f"    - 패턴 존재: {pattern}")

    print(f"\n===== 완료 =====")
    print(f"생성된 그룹: {created_groups}개")
    print(f"기존 그룹: {skipped_groups}개")
    print(f"생성된 패턴: {created_patterns}개")
    print(f"\n브랜드 그룹 설정이 완료되었습니다!")


if __name__ == '__main__':
    setup_brand_groups()
