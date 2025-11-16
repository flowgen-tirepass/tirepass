"""
ERP 주소 데이터 통계 확인 (DB 연결 불필요)
로컬에서 실행 가능
"""
import sys
import os

# Django 설정 없이 ERP API만 사용
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ERP API 클라이언트 간단 버전
import requests
from typing import List, Dict, Optional

ERP_API_BASE_URL = "http://ITIRE2.iptime.org:8000"
ERP_API_KEY = "tirepass-erp-secret-2024"

def get_customers_count() -> int:
    """고객 총 수 조회"""
    url = f"{ERP_API_BASE_URL}/api/customers/count"
    params = {"api_key": ERP_API_KEY}
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()["count"]

def get_customers_list(offset: int = 0, limit: int = 100) -> List[Dict]:
    """고객 목록 조회"""
    url = f"{ERP_API_BASE_URL}/api/customers"
    params = {
        "api_key": ERP_API_KEY,
        "offset": offset,
        "limit": limit
    }
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()

print("\n" + "=" * 80)
print("ERP 주소 데이터 통계 확인 (로컬 실행)")
print("=" * 80)

# 1. ERP에서 전체 고객 데이터 가져오기
print("\n1️⃣ ERP 전체 고객 데이터 가져오기")
print("-" * 80)

try:
    total_count = get_customers_count()
    print(f"ERP 전체 고객 수: {total_count:,}명")

    print(f"\n데이터 가져오는 중... (최대 30초 소요)")
    all_customers = get_customers_list(offset=0, limit=total_count)
    print(f"✅ 가져온 고객 수: {len(all_customers):,}명")

except Exception as e:
    print(f"❌ ERP 연결 실패: {e}")
    exit(1)

# 2. 주소 데이터 통계
print("\n2️⃣ 주소 데이터 통계")
print("-" * 80)

stats = {
    'total': 0,
    'has_address1': 0,
    'has_address2': 0,
    'no_address': 0,
    'has_zip1': 0,
    'has_enno': 0,
    'no_enno': 0,
    'sync_target': 0,  # 주소 + 사업자번호 모두 있음
}

address_samples = []

for customer in all_customers:
    stats['total'] += 1

    address1 = customer.get('address1', '').strip() if customer.get('address1') else ''
    address2 = customer.get('address2', '').strip() if customer.get('address2') else ''
    zip1 = customer.get('zip1', '').strip() if customer.get('zip1') else ''
    enno = customer.get('enno', '').strip() if customer.get('enno') else ''

    if address1:
        stats['has_address1'] += 1
    else:
        stats['no_address'] += 1

    if address2:
        stats['has_address2'] += 1

    if zip1:
        stats['has_zip1'] += 1

    if enno:
        stats['has_enno'] += 1
    else:
        stats['no_enno'] += 1

    # 주소와 사업자번호가 모두 있는 고객 = 동기화 대상
    if address1 and enno:
        stats['sync_target'] += 1
        if len(address_samples) < 10:
            address_samples.append(customer)

print(f"전체 고객: {stats['total']:,}명")
print(f"\n[주소 필드]")
print(f"  ADDRESS1 있음: {stats['has_address1']:,}명 ({stats['has_address1']/stats['total']*100:.1f}%)")
print(f"  ADDRESS2 있음: {stats['has_address2']:,}명 ({stats['has_address2']/stats['total']*100:.1f}%)")
print(f"  ZIP1 있음: {stats['has_zip1']:,}명 ({stats['has_zip1']/stats['total']*100:.1f}%)")
print(f"  주소 없음: {stats['no_address']:,}명")
print(f"\n[사업자번호]")
print(f"  사업자번호 있음: {stats['has_enno']:,}명 ({stats['has_enno']/stats['total']*100:.1f}%)")
print(f"  사업자번호 없음: {stats['no_enno']:,}명")
print(f"\n✅ 배송지 동기화 가능 고객: {stats['sync_target']:,}명 (주소 + 사업자번호 모두 있음)")

# 3. 주소 샘플 출력
print("\n3️⃣ 주소 샘플 데이터 (10개)")
print("-" * 80)

for i, customer in enumerate(address_samples, 1):
    code = customer.get('code', '')
    name = customer.get('name', '')
    enno = customer.get('enno', '')
    address1 = customer.get('address1', '')
    zip1 = customer.get('zip1', '')
    tel1 = customer.get('tel1', '')
    tel4 = customer.get('tel4', '')

    phone = tel4 if tel4 else tel1 if tel1 else '없음'

    print(f"\n[{i}] {code} - {name}")
    print(f"    사업자번호: {enno}")
    print(f"    주소: {address1}")
    if zip1:
        print(f"    우편번호: {zip1}")
    print(f"    전화번호: {phone}")

# 4. 요약
print("\n" + "=" * 80)
print("📊 동기화 예상 결과")
print("=" * 80)
print(f"\n총 {stats['sync_target']:,}명의 고객에게 기본 배송지가 등록됩니다.")
print(f"\n배송지 정보:")
print(f"  - 수령인: 상호명")
print(f"  - 주소: ADDRESS1 필드")
print(f"  - 우편번호: ZIP1 필드 (있는 경우)")
print(f"  - 전화번호: TEL4(휴대폰) 우선, 없으면 TEL1(일반전화)")
print(f"  - 기본배송지: ✅ (자동 설정)")

print("\n⚠️  주의사항:")
print("  1. 이미 배송지가 있는 고객은 스킵됩니다")
print("  2. Django DB에 없는 고객은 스킵됩니다")
print("  3. 실제 등록 수는 이보다 적을 수 있습니다")

print("\n" + "=" * 80)
print("✅ 통계 확인 완료!")
print("\n다음 단계: PythonAnywhere에서 sync_erp_addresses.py 실행")
print("=" * 80)
