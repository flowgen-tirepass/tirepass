# 포인트 시스템 배포 가이드

## 변경 사항 요약

### 구현 기능
- **CustomerPoint 모델**: 고객별 포인트 잔액 관리
  - balance: 현재 포인트 잔액
  - total_earned: 누적 적립 포인트
  - total_used: 누적 사용 포인트

- **PointTransaction 모델**: 포인트 적립/사용 내역
  - 거래 유형: 주문 적립, 회원가입 적립, 이벤트 적립, 관리자 지급, 사용, 만료, 취소
  - 거래 전후 잔액 기록
  - 주문번호 연동
  - 만료일 관리

- **PointPolicy 모델**: 포인트 정책 설정
  - 적립률 (%)
  - 최소 주문 금액
  - 회원가입 보너스
  - 포인트 유효기간
  - 최소 사용 포인트
  - 최대 사용 비율 (%)

- **Admin 관리 기능**
  - 고객 목록에서 포인트 잔액 표시
  - 포인트 잔액 관리 메뉴
  - 포인트 거래 내역 조회
  - 포인트 정책 설정

## 변경된 파일 목록

### 1. 모델 변경
- `tire_data/models.py`
  - ✅ Customers 모델에 point_balance 프로퍼티 추가
  - ✅ CustomerPoint 모델 추가 (OneToOneField)
  - ✅ PointTransaction 모델 추가 (거래 내역)
  - ✅ PointPolicy 모델 추가 (정책 설정)
  - ✅ add_points(), use_points() 메서드 구현

### 2. Admin 변경
- `tire_data/admin.py`
  - ✅ CustomersAdmin에 point_balance_display 추가
  - ✅ CustomerPointAdmin 클래스 추가
  - ✅ PointTransactionAdmin 클래스 추가
  - ✅ PointPolicyAdmin 클래스 추가
  - ✅ custom_admin_site에 포인트 모델 3개 등록

### 3. 마이그레이션
- `tire_data/migrations/0023_merge_20251117_1557.py`
  - 의존성 수정 (존재하지 않는 0022_merge 제거)
- `tire_data/migrations/0024_add_point_system.py`
  - CustomerPoint, PointTransaction, PointPolicy 모델 생성
  - Brand 모델에 logo_image 필드 추가
  - BrandPattern 성능 필드에 choices 추가

## 배포 절차

### 1단계: PythonAnywhere에서 Git Pull
```bash
# PythonAnywhere Bash 콘솔
cd /home/tirepass/tirepass

# 최신 코드 가져오기
git pull origin main
```

### 2단계: 마이그레이션 적용
```bash
# 마이그레이션 상태 확인
python manage.py showmigrations tire_data | tail -5

# 0024 마이그레이션 적용
python manage.py migrate tire_data

# 결과 확인 - 아래와 같이 표시되어야 함:
# [X] 0023_merge_20251117_1557
# [X] 0024_add_point_system
```

**예상 출력:**
```
Running migrations:
  Applying tire_data.0024_add_point_system... OK
```

### 3단계: 데이터베이스 확인
```bash
# MySQL 콘솔에서 확인
python manage.py dbshell
```

```sql
-- 포인트 관련 테이블 생성 확인
SHOW TABLES LIKE '%point%';

-- customer_points 테이블 구조 확인
DESCRIBE customer_points;

-- point_transactions 테이블 구조 확인
DESCRIBE point_transactions;

-- point_policies 테이블 구조 확인
DESCRIBE point_policies;

exit;
```

### 4단계: 기본 포인트 정책 생성
```bash
# Django shell에서 기본 정책 생성
python manage.py shell
```

```python
from tire_data.models import PointPolicy

# 기본 포인트 정책 생성
policy = PointPolicy.objects.create(
    name='기본 포인트 정책',
    earn_rate=1.0,  # 1% 적립
    min_order_amount=10000,  # 최소 주문 금액 10,000원
    signup_bonus=5000,  # 회원가입 보너스 5,000P
    point_validity_days=365,  # 1년 유효
    min_use_amount=1000,  # 최소 사용 1,000P
    max_use_rate=50.0,  # 최대 50% 사용 가능
    is_active=True
)
print(f"✓ 정책 생성 완료: {policy.name}")

exit()
```

### 5단계: Python 캐시 삭제
```bash
cd /home/tirepass/tirepass

# Python 캐시 완전 삭제
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
```

### 6단계: 웹 앱 재시작
1. PythonAnywhere 웹 페이지 접속
2. **Web** 탭 클릭
3. **Reload** 버튼 (초록색) 클릭
4. 재시작 완료 메시지 확인

### 7단계: 관리자 페이지 확인
1. **새 시크릿 모드 창** 열기
2. https://tirepass.pythonanywhere.com/admin/ 접속
3. 로그인
4. **C. 💳 포인트** 섹션 확인 (새로 추가됨)
   - **01. 포인트 정책 설정**
   - **02. 고객 포인트 관리**
   - **03. 포인트 거래 내역**
5. **A. 🚗 재고/고객** 섹션
   - **02. 고객 관리** → 목록에서 "보유 포인트" 컬럼 확인

## 새로운 사용 방법

### 1. 포인트 정책 설정하기
1. **C. 💳 포인트 | 01. 포인트 정책 설정** 메뉴 접속
2. 기본 정책 확인 또는 수정
   - **적립률 (%)**: 주문 금액의 몇 %를 적립할지 (예: 1.0 = 1%)
   - **최소 주문 금액**: 포인트 적립이 가능한 최소 주문 금액
   - **회원가입 보너스**: 신규 회원 가입 시 지급할 포인트
   - **포인트 유효기간 (일)**: 적립된 포인트의 유효 기간
   - **최소 사용 포인트**: 한 번에 사용 가능한 최소 포인트
   - **최대 사용 비율 (%)**: 주문 금액의 최대 몇 %까지 포인트로 결제 가능
   - **활성화**: 이 정책을 사용할지 여부 (활성화 시 다른 정책은 자동 비활성화)

### 2. 고객 포인트 조회하기
1. **A. 🚗 재고/고객 | 02. 고객 관리** 메뉴 접속
2. 목록에서 **보유 포인트** 컬럼 확인
   - 파란색: 포인트 있음
   - 회색: 포인트 없음
3. 고객 상세 페이지에서 **포인트 정보** 섹션 확인

### 3. 포인트 거래 내역 보기
1. **C. 💳 포인트 | 03. 포인트 거래 내역** 메뉴 접속
2. 거래 유형별 필터링 가능
   - 주문 적립, 회원가입 적립, 이벤트 적립, 관리자 지급
   - 포인트 사용, 포인트 만료, 적립 취소
3. 고객명, 주문번호로 검색 가능
4. 날짜별 조회 가능

### 4. 관리자가 직접 포인트 지급하기
```python
# Django shell에서 실행
python manage.py shell

from tire_data.models import Customers, CustomerPoint

# 고객 찾기
customer = Customers.objects.get(code='고객코드')

# CustomerPoint 가져오기 또는 생성
customer_point, created = CustomerPoint.objects.get_or_create(customer=customer)

# 포인트 지급 (예: 이벤트 보상 10,000P)
customer_point.add_points(
    amount=10000,
    transaction_type='EARN_EVENT',
    description='11월 프로모션 이벤트 보상'
)

print(f"✓ {customer.name}님에게 10,000P 지급 완료")
print(f"현재 잔액: {customer_point.balance:,}P")

exit()
```

## 향후 구현 예정 기능

### 주문 완료 시 자동 포인트 적립
```python
# tire_data/api_views.py의 주문 완료 처리에 추가 예정

from tire_data.models import CustomerPoint, PointPolicy

def complete_order(order):
    # 주문 완료 처리...

    # 포인트 적립
    policy = PointPolicy.get_active_policy()
    if policy and order.final_amount >= policy.min_order_amount:
        # 고객 포인트 가져오기 또는 생성
        customer_point, created = CustomerPoint.objects.get_or_create(
            customer=order.customer
        )

        # 적립 포인트 계산 (주문 금액의 적립률%)
        earn_amount = int(order.final_amount * policy.earn_rate / 100)

        # 포인트 적립
        customer_point.add_points(
            amount=earn_amount,
            transaction_type='EARN_ORDER',
            description=f'주문 완료 적립 ({order.final_amount:,}원의 {policy.earn_rate}%)',
            order_code=order.code
        )
```

### 결제 시 포인트 사용
```python
# tire_data/api_views.py의 결제 처리에 추가 예정

def process_payment(order, use_points=0):
    if use_points > 0:
        policy = PointPolicy.get_active_policy()
        customer_point = CustomerPoint.objects.get(customer=order.customer)

        # 사용 가능 검증
        max_use = int(order.amount * policy.max_use_rate / 100)
        if use_points > max_use:
            raise ValueError(f'최대 {max_use:,}P까지만 사용 가능합니다')

        if use_points < policy.min_use_amount:
            raise ValueError(f'최소 {policy.min_use_amount:,}P부터 사용 가능합니다')

        # 포인트 사용
        if customer_point.use_points(
            amount=use_points,
            description=f'주문 결제 사용',
            order_code=order.code
        ):
            order.point_discount = use_points
            order.final_amount = order.amount - use_points
            order.save()
```

## 테스트 체크리스트

- [ ] Git pull 완료
- [ ] 마이그레이션 0024 적용 완료
- [ ] customer_points 테이블 생성 확인
- [ ] point_transactions 테이블 생성 확인
- [ ] point_policies 테이블 생성 확인
- [ ] 기본 포인트 정책 생성 완료
- [ ] Python 캐시 삭제 완료
- [ ] 웹 앱 재시작 완료
- [ ] 관리자 페이지 접속 확인
- [ ] C.💳 포인트 메뉴 표시 확인
- [ ] 고객 목록에서 보유 포인트 컬럼 확인
- [ ] 포인트 정책 설정 메뉴 작동 확인
- [ ] 포인트 거래 내역 메뉴 작동 확인
- [ ] Django shell에서 수동 포인트 지급 테스트

## 롤백 방법 (문제 발생 시)

문제가 발생하면 이전 마이그레이션으로 되돌릴 수 있습니다:

```bash
# 0023 마이그레이션으로 롤백 (포인트 시스템 제거)
python manage.py migrate tire_data 0023

# 이전 코드로 되돌리기
git log --oneline -5  # 커밋 해시 확인
git reset --hard <이전_커밋_해시>
git push origin main --force  # 주의: 강제 푸시

# 웹 앱 재시작
```

## 문의사항
문제가 발생하면 로그를 확인하세요:
- PythonAnywhere 웹 탭 > **Log files**
- **Error log** 확인
- **Server log** 확인
