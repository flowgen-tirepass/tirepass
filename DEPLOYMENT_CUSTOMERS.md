# ERP 고객 목록 실시간 동기화 배포 가이드

## 개요
ERP Firebird 서버의 전체 고객 목록을 pythonanywhere MySQL로 실시간 동기화하여 관리자 페이지에서 조회할 수 있도록 구현

## 데이터 구조

### 1. ERP → pythonanywhere (단방향 동기화, 읽기 전용)
- **customers 테이블**: ERP 서버 전체 고객 목록
- **goods 테이블**: ERP 서버 상품 목록

### 2. pythonanywhere 전용 (쓰기 가능)
- **customers_simple 테이블**: 모바일 회원가입 고객
- **shopping_cart, orders, order_items, payments**: 주문/결제 관련
- **year_allocations**: 연도별 재고 할당
- **customer_discounts, customer_product_discounts**: 할인 관련

## 배포 순서

### 1단계: pythonanywhere MySQL 테이블 생성

```bash
# pythonanywhere.com → 'Consoles' 탭 → 'Bash' 클릭
# MySQL 접속
mysql -u [사용자명] -p

# 데이터베이스 선택
USE [사용자명]$itire_db;

# customers 테이블 생성
```

**SQL 실행** (`pythonanywhere_customers_table.sql` 내용):
```sql
CREATE TABLE IF NOT EXISTS customers (
  CODE VARCHAR(10) PRIMARY KEY COMMENT 'ERP 고객코드',
  NAME VARCHAR(50) COMMENT '상호',
  REP VARCHAR(20) COMMENT '대표자',
  TEL1 VARCHAR(20) COMMENT '전화1',
  TEL3 VARCHAR(20) COMMENT '휴대전화',
  ENNO VARCHAR(20) COMMENT '사업자번호',
  LAST_SYNC DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '최종 동기화 시간',
  INDEX idx_customers_name (NAME),
  INDEX idx_customers_enno (ENNO),
  INDEX idx_customers_last_sync (LAST_SYNC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='ERP 서버 고객 목록 (읽기 전용, 실시간 동기화)';
```

### 2단계: Django 코드 배포

#### A. tire_data/models.py 수정

**CustomersFull 모델 추가** (Customers 모델 위에):
```python
class CustomersFull(models.Model):
    """ERP 서버 전체 고객 목록 (읽기 전용, 실시간 동기화)"""
    code = models.CharField(max_length=10, primary_key=True, verbose_name='고객코드', db_column='CODE')
    name = models.CharField(max_length=50, null=True, blank=True, verbose_name='상호', db_column='NAME')
    rep = models.CharField(max_length=20, null=True, blank=True, verbose_name='대표자', db_column='REP')
    tel1 = models.CharField(max_length=20, null=True, blank=True, verbose_name='전화1', db_column='TEL1')
    tel3 = models.CharField(max_length=20, null=True, blank=True, verbose_name='휴대전화', db_column='TEL3')
    enno = models.CharField(max_length=20, null=True, blank=True, verbose_name='사업자번호', db_column='ENNO')
    last_sync = models.DateTimeField(null=True, blank=True, verbose_name='최종동기화', db_column='LAST_SYNC')

    class Meta:
        db_table = 'customers'
        managed = False  # ERP 서버가 관리
        verbose_name = 'ERP 고객'
        verbose_name_plural = 'ERP 고객목록'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def is_real_customer(self):
        """실제 고객인지 확인 (Z로 시작하지 않는 코드)"""
        return not self.code.startswith('Z')
```

**Customers 모델 수정**:
```python
class Customers(models.Model):
    """모바일 회원가입 고객 (pythonanywhere 관리)"""
    # ... 필드는 동일 ...

    class Meta:
        db_table = 'customers_simple'
        managed = True  # pythonanywhere가 관리 (False → True 변경)
        verbose_name = '회원'  # '고객' → '회원' 변경
        verbose_name_plural = '회원목록'  # '고객목록' → '회원목록' 변경
        ordering = ['code']
```

#### B. tire_data/admin.py 수정

**import 수정**:
```python
from .models import (
    Goods, CustomersFull, Customers, YearAllocation, BrandGroup,
    BrandGroupPattern, CustomerDiscount, DiscountHistory,
    CustomerProductDiscount, ShoppingCart, Order, OrderItem, Payment
)
```

**CustomersFullAdmin 추가** (CustomersAdmin 위에):
```python
@admin.register(CustomersFull)
class CustomersFullAdmin(admin.ModelAdmin):
    """ERP 전체 고객 목록 (읽기 전용)"""
    list_display = ['code', 'name', 'rep', 'tel1', 'tel3', 'enno', 'last_sync']
    search_fields = ['code', 'name', 'rep', 'enno']
    ordering = ['code']
    list_per_page = 50

    def has_add_permission(self, request):
        """추가 불가 (ERP에서만)"""
        return False

    def has_delete_permission(self, request, obj=None):
        """삭제 불가 (ERP에서만)"""
        return False

    def has_change_permission(self, request, obj=None):
        """수정 불가 (ERP에서만)"""
        return False
```

**CustomersAdmin 주석 수정**:
```python
@admin.register(Customers)
class CustomersAdmin(admin.ModelAdmin):
    """모바일 회원가입 고객"""
    # ... 나머지는 동일 ...
```

### 3단계: pythonanywhere 파일 편집기로 코드 수정

1. **pythonanywhere.com** 로그인
2. **Files** 탭 클릭
3. `tire_data/models.py` 열기
   - CustomersFull 모델 추가
   - Customers 모델 수정
4. `tire_data/admin.py` 열기
   - import 수정
   - CustomersFullAdmin 추가
   - CustomersAdmin 주석 수정
5. **저장**

### 4단계: 웹앱 리로드

1. **Web** 탭 클릭
2. **Reload** 버튼 클릭
3. 에러 로그 확인

### 5단계: ERP 서버 트리거 설정

**ERP Firebird 서버에서 실행** (기존 goods 트리거와 유사):

```sql
-- customers 테이블 INSERT/UPDATE 트리거
CREATE TRIGGER trg_customers_sync_insert
AFTER INSERT ON CUSTOMERS
AS
BEGIN
  -- pythonanywhere MySQL로 INSERT
  -- (Firebird → MySQL 연동 로직)
END;

CREATE TRIGGER trg_customers_sync_update
AFTER UPDATE ON CUSTOMERS
AS
BEGIN
  -- pythonanywhere MySQL로 UPDATE
  -- (Firebird → MySQL 연동 로직)
END;

CREATE TRIGGER trg_customers_sync_delete
AFTER DELETE ON CUSTOMERS
AS
BEGIN
  -- pythonanywhere MySQL에서 DELETE
  -- (Firebird → MySQL 연동 로직)
END;
```

### 6단계: 테스트

#### A. 관리자 페이지 확인
1. https://tirepass.pythonanywhere.com/admin/ 로그인
2. **ERP 고객목록** 클릭 → ERP 서버 전체 고객 조회
3. **회원목록** 클릭 → 모바일 회원가입 고객만 조회

#### B. 권한 테스트
- ERP 고객목록: 추가/수정/삭제 버튼이 없어야 함 (읽기 전용)
- 회원목록: 수정 가능, 추가/삭제 가능

#### C. 동기화 테스트
1. ERP 서버에서 고객 정보 수정
2. 관리자 페이지 새로고침
3. 변경사항 즉시 반영 확인

## 테이블 구조 요약

| 테이블 | 용도 | 관리 주체 | Django managed |
|--------|------|-----------|----------------|
| customers | ERP 전체 고객 목록 | ERP 서버 트리거 | False (읽기 전용) |
| customers_simple | 모바일 회원가입 고객 | pythonanywhere | True (쓰기 가능) |
| goods | ERP 상품 목록 | ERP 서버 트리거 | False (읽기 전용) |
| shopping_cart | 장바구니 | pythonanywhere | True (쓰기 가능) |
| orders | 주문 | pythonanywhere | True (쓰기 가능) |
| year_allocations | 연도별 재고 할당 | pythonanywhere | True (쓰기 가능) |

## 주의사항

1. **customers 테이블은 읽기 전용**: Django Admin에서 수정 불가
2. **ERP 서버에서만 고객 정보 수정**: 트리거가 자동으로 MySQL 동기화
3. **회원가입은 customers_simple에만**: 모바일 앱에서 회원가입 시
4. **last_sync 필드**: 동기화 시간 자동 업데이트

## 트러블슈팅

### 고객 목록이 비어있는 경우
- ERP 서버 트리거 실행 여부 확인
- MySQL customers 테이블 데이터 확인: `SELECT COUNT(*) FROM customers;`

### 동기화 안 되는 경우
- ERP 서버 트리거 로그 확인
- 네트워크 연결 확인 (ITIRE2.iptime.org 접속 가능 여부)

### Admin 페이지 에러
- Error Log 확인: Web 탭 → Error log
- 들여쓰기 오류 확인
- 모델 import 오류 확인

## 완료 체크리스트

- [ ] pythonanywhere MySQL에 customers 테이블 생성
- [ ] tire_data/models.py에 CustomersFull 추가
- [ ] tire_data/models.py에서 Customers 수정
- [ ] tire_data/admin.py에 CustomersFullAdmin 추가
- [ ] pythonanywhere 파일 편집기로 코드 수정
- [ ] 웹앱 리로드
- [ ] ERP 서버 트리거 설정
- [ ] 관리자 페이지에서 ERP 고객목록 확인
- [ ] 읽기 전용 권한 테스트
- [ ] 동기화 테스트
