"""
PythonAnywhere에서 customers 테이블의 UTF-8 인코딩 확인

실행:
    python3 scripts/verify_customers_encoding.py
"""
import os
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itire.settings')
django.setup()

from tire_data.models import CustomersFull

def verify_encoding():
    """customers 테이블 데이터 확인"""
    print("=== customers 테이블 인코딩 확인 ===\n")

    try:
        # 샘플 데이터 5개 가져오기
        customers = CustomersFull.objects.all()[:5]

        if not customers:
            print("데이터가 없습니다.")
            return

        print(f"총 {CustomersFull.objects.count()}명의 고객 데이터")
        print("\n샘플 5개:")
        print("-" * 80)

        for customer in customers:
            print(f"CODE: {customer.code}")
            print(f"NAME: {customer.name}")
            print(f"REP: {customer.rep}")
            print(f"TEL1: {customer.tel1}")
            print(f"TEL3: {customer.tel3}")
            print(f"ENNO: {customer.enno}")
            print(f"ADDRESS1: {customer.address1}")
            print("-" * 80)

        # 한글이 제대로 표시되는지 확인
        first_customer = customers[0]
        if first_customer.name:
            has_korean = any('\uac00' <= c <= '\ud7a3' for c in first_customer.name)
            if has_korean:
                print("\n✓ 한글이 정상적으로 저장되어 있습니다!")
            else:
                print("\n✗ 한글이 감지되지 않았습니다. 인코딩 문제가 있을 수 있습니다.")

    except Exception as e:
        print(f"에러: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    verify_encoding()
