"""
YearAllocation에는 있지만 Goods 테이블에 없는 상품을 추가하는 스크립트

PythonAnywhere Bash console에서 실행:
cd ~/1.0_tirepass
source venv/bin/activate
python manage.py shell < add_missing_goods.py
"""

from tire_data.models import YearAllocation, Goods
from tire_data.erp_api_client import ERPAPIClient

# YearAllocation에는 있지만 Goods에 없는 상품 찾기
print("YearAllocation 상품 확인 중...")
allocations = YearAllocation.objects.all()

missing_products = []
for allocation in allocations:
    try:
        Goods.objects.get(code=allocation.goods_code)
    except Goods.DoesNotExist:
        missing_products.append(allocation.goods_code)
        print(f"✗ Goods 테이블에 없음: {allocation.goods_code}")

if not missing_products:
    print("✓ 모든 상품이 Goods 테이블에 존재합니다!")
else:
    print(f"\n총 {len(missing_products)}개 상품이 Goods 테이블에 없습니다.")
    print("\nERP에서 상품 정보를 가져와서 추가합니다...")

    success_count = 0
    error_count = 0

    for product_code in missing_products:
        try:
            # ERP API에서 상품 정보 조회
            erp_data = ERPAPIClient.get_goods_detail(product_code)

            if not erp_data:
                print(f"✗ {product_code}: ERP에서 데이터를 가져올 수 없습니다.")
                error_count += 1
                continue

            # Goods 테이블에 추가 (Raw SQL 사용)
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO goods (CODE, NAME, BUN1, JAEGO, FIXP)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        NAME = VALUES(NAME),
                        BUN1 = VALUES(BUN1),
                        JAEGO = VALUES(JAEGO),
                        FIXP = VALUES(FIXP)
                """, [
                    product_code,
                    erp_data.get('NAME', ''),
                    erp_data.get('BUN1', ''),
                    erp_data.get('JAEGO', 0),
                    erp_data.get('FIXP', 0)
                ])

            print(f"✓ {product_code}: Goods 테이블에 추가/업데이트 완료")
            success_count += 1

        except Exception as e:
            print(f"✗ {product_code}: 오류 - {str(e)}")
            error_count += 1

    print(f"\n완료!")
    print(f"성공: {success_count}개")
    print(f"실패: {error_count}개")

# 특정 상품 하나만 처리하는 함수
def add_single_product(product_code):
    """특정 상품 하나만 Goods 테이블에 추가"""
    print(f"상품 {product_code} 추가 중...")

    # ERP API에서 상품 정보 조회
    erp_data = ERPAPIClient.get_goods_detail(product_code)

    if not erp_data:
        print(f"✗ ERP에서 데이터를 가져올 수 없습니다.")
        return False

    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO goods (CODE, NAME, BUN1, JAEGO, FIXP)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    NAME = VALUES(NAME),
                    BUN1 = VALUES(BUN1),
                    JAEGO = VALUES(JAEGO),
                    FIXP = VALUES(FIXP)
            """, [
                product_code,
                erp_data.get('NAME', ''),
                erp_data.get('BUN1', ''),
                erp_data.get('JAEGO', 0),
                erp_data.get('FIXP', 0)
            ])

        print(f"✓ {product_code}: Goods 테이블에 추가 완료")
        print(f"  상품명: {erp_data.get('NAME')}")
        print(f"  브랜드: {erp_data.get('BUN1')}")
        print(f"  재고: {erp_data.get('JAEGO')}")
        print(f"  가격: {erp_data.get('FIXP')}")
        return True

    except Exception as e:
        print(f"✗ 오류: {str(e)}")
        return False

# P-0PZR0000001 상품만 추가하려면:
# add_single_product('P-0PZR0000001')
