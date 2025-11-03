"""
ERP에서 특정 고객 정보를 동기화하는 스크립트

PythonAnywhere Bash console에서 실행:
cd ~/1.0_tirepass
source venv/bin/activate
python manage.py shell

# 그 다음 아래 코드를 복사해서 실행:
"""

from tire_data.erp_api_client import ERPAPIClient
from tire_data.models import Customers

def sync_customer_from_erp(customer_code):
    """ERP에서 고객 정보를 가져와서 customers_simple 테이블 업데이트"""
    print(f"고객 {customer_code} 동기화 시작...")

    # ERP API에서 고객 정보 조회
    erp_data = ERPAPIClient.get_customer_detail(customer_code)

    if not erp_data:
        print(f"✗ ERP에서 고객 {customer_code} 정보를 가져올 수 없습니다.")
        print("  - ERP API 서버가 실행 중인지 확인하세요.")
        return False

    print(f"ERP 데이터: {erp_data}")

    try:
        # customers_simple 테이블 업데이트
        customer, created = Customers.objects.update_or_create(
            code=customer_code,
            defaults={
                'name': erp_data.get('NAME', ''),
                'rep': erp_data.get('REP', ''),
                'tel1': erp_data.get('TEL1', ''),
                'tel3': erp_data.get('TEL3', ''),
                'enno': erp_data.get('ENNO', ''),
            }
        )

        if created:
            print(f"✓ 새 고객 생성: {customer.code} - {customer.name}")
        else:
            print(f"✓ 고객 정보 업데이트: {customer.code} - {customer.name}")
            print(f"  상호: {customer.name}")
            print(f"  대표자: {customer.rep}")
            print(f"  전화1: {customer.tel1}")
            print(f"  휴대전화: {customer.tel3}")
            print(f"  사업자번호: {customer.enno}")

        return True

    except Exception as e:
        print(f"✗ 데이터베이스 업데이트 오류: {str(e)}")
        return False


def sync_all_customers_from_erp():
    """모든 고객 정보를 ERP에서 동기화"""
    print("모든 고객 정보 동기화 시작...")

    # 기존 customers_simple 테이블의 모든 고객 코드 조회
    customer_codes = Customers.objects.values_list('code', flat=True)

    success_count = 0
    error_count = 0

    for code in customer_codes:
        if sync_customer_from_erp(code):
            success_count += 1
        else:
            error_count += 1

    print(f"\n완료!")
    print(f"성공: {success_count}개")
    print(f"실패: {error_count}개")


# 단일 고객 동기화 예제
# sync_customer_from_erp('4108305068')

# 모든 고객 동기화 예제 (주의: 시간이 오래 걸릴 수 있음)
# sync_all_customers_from_erp()
