"""
모든 상품의 연식 할인율 일괄 업데이트 스크립트

연식 할인율:
- 2024년: 3%
- 2023년: 4%
- 2022년: 5%
- 2021년 이전: 10%
"""
import os
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itire.settings')
django.setup()

from tire_data.models import YearAllocation

def update_year_discounts():
    """모든 상품의 연식 할인율 일괄 업데이트"""

    print("연식 할인율 일괄 업데이트 시작...")
    print("-" * 60)

    # 모든 YearAllocation 레코드 조회
    allocations = YearAllocation.objects.all()
    total_count = allocations.count()

    print(f"총 {total_count}개 상품의 연식 할인율을 업데이트합니다.")
    print()
    print("적용할 연식 할인율:")
    print("  - 2024년: 3%")
    print("  - 2023년: 4%")
    print("  - 2022년: 5%")
    print("  - 2021년 이전: 10%")
    print("-" * 60)

    # 일괄 업데이트
    updated_count = allocations.update(
        year_2024_discount=3.00,
        year_2023_discount=4.00,
        year_2022_discount=5.00,
        year_2021_before_discount=10.00
    )

    print(f"\n✓ {updated_count}개 상품 업데이트 완료!")

    # 샘플 확인 (처음 5개)
    print("\n샘플 확인 (처음 5개):")
    print("-" * 60)
    samples = YearAllocation.objects.all()[:5]

    for ya in samples:
        print(f"{ya.goods_code}:")
        print(f"  2024년: {ya.year_2024_discount}%")
        print(f"  2023년: {ya.year_2023_discount}%")
        print(f"  2022년: {ya.year_2022_discount}%")
        print(f"  2021년 이전: {ya.year_2021_before_discount}%")

    # P-PZERO-25 확인
    try:
        pzero = YearAllocation.objects.get(goods_code='P-PZERO-25')
        print("\nP-PZERO-25 확인:")
        print("-" * 60)
        print(f"기본 할인율: {pzero.base_discount}%")
        print(f"2024년: 재고 {pzero.year_2024}개, 할인 {pzero.year_2024_discount}%")
        print(f"2023년: 재고 {pzero.year_2023}개, 할인 {pzero.year_2023_discount}%")
        print(f"2022년: 재고 {pzero.year_2022}개, 할인 {pzero.year_2022_discount}%")
        print(f"2021년 이전: 재고 {pzero.year_2021_before}개, 할인 {pzero.year_2021_before_discount}%")
    except YearAllocation.DoesNotExist:
        print("\nP-PZERO-25를 찾을 수 없습니다.")

    print("\n" + "=" * 60)
    print("연식 할인율 업데이트 완료!")
    print("=" * 60)

if __name__ == '__main__':
    update_year_discounts()
