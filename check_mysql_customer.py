"""
MySQL 데이터베이스에서 직접 확인
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itire.settings')
django.setup()

from tire_data.models import Customers, CustomersFull

print("=" * 80)
print("MySQL 데이터베이스 확인: 0-1-0003 광주전자공업고등학교")
print("=" * 80)

# 1. customers_simple 테이블 (모바일 회원)
print("\n1️⃣ customers_simple 테이블 (Customers 모델):")
print("-" * 80)

customer = Customers.objects.filter(code='0-1-0003').first()

if customer:
    print(f"✅ 발견!")
    print(f"   코드: {customer.code}")
    print(f"   이름: {customer.name}")
    print(f"   대표자: {customer.rep}")
    print(f"   전화1: {customer.tel1}")
    print(f"   사업자번호: {customer.enno}")
    print(f"   비밀번호 설정: {'예' if customer.password else '아니오'}")
    print(f"   회원가입 여부: {customer.is_registered}")
    print(f"   User ID: {customer.user_id}")
else:
    print("❌ customers_simple 테이블에 없습니다!")

# 2. customers 테이블 (ERP 동기화)
print("\n2️⃣ customers 테이블 (CustomersFull 모델, ERP 동기화):")
print("-" * 80)

try:
    customer_full = CustomersFull.objects.filter(code='0-1-0003').first()

    if customer_full:
        print(f"✅ 발견!")
        print(f"   코드: {customer_full.code}")
        print(f"   이름: {customer_full.name}")
        print(f"   대표자: {customer_full.rep}")
        print(f"   전화1: {customer_full.tel1}")
        print(f"   사업자번호: {customer_full.enno}")
        print(f"   최종 동기화: {customer_full.last_sync}")
    else:
        print("❌ customers 테이블에 없습니다!")
        print("   → ERP에 실제로 존재하지 않는 고객입니다!")
except Exception as e:
    print(f"❌ 오류: {str(e)}")

# 3. 사업자번호로 검색
print("\n3️⃣ 사업자번호 '410-83-05068'로 검색:")
print("-" * 80)

# customers_simple
simple_customers = Customers.objects.filter(enno__contains='4108305068')
print(f"customers_simple: {simple_customers.count()}개")
for c in simple_customers:
    print(f"   - {c.code} | {c.name}")

# customers (ERP)
try:
    full_customers = CustomersFull.objects.filter(enno__contains='4108305068')
    print(f"customers (ERP): {full_customers.count()}개")
    for c in full_customers:
        print(f"   - {c.code} | {c.name}")
except Exception as e:
    print(f"customers (ERP): 오류 - {str(e)}")

# 4. 테이블 통계
print("\n4️⃣ 테이블 통계:")
print("-" * 80)
print(f"customers_simple (모바일 회원): {Customers.objects.count():,}개")

try:
    print(f"customers (ERP 동기화): {CustomersFull.objects.count():,}개")
except Exception as e:
    print(f"customers (ERP 동기화): 조회 불가 - {str(e)}")

print("\n" + "=" * 80)
print("결론:")
print("-" * 80)
if customer and not customer_full:
    print("⚠️  이 고객은 모바일 회원가입으로만 생성된 고객입니다.")
    print("    ERP에는 존재하지 않습니다!")
    print("    테스트용 계정일 가능성이 높습니다.")
elif customer and customer_full:
    print("✅ 이 고객은 ERP와 동기화된 정상 고객입니다.")
else:
    print("❓ 확인 필요")
print("=" * 80)
