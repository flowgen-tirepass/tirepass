# PythonAnywhere 배포 단계별 가이드

## 현재 상태
✅ 로컬에서 404명 ERP 고객 마이그레이션 완료
✅ CustomersFull 모델 추가 (tel4, address1 포함)
✅ Admin 페이지 설정 완료

## 배포 순서

--- 

## 1단계: MySQL customers 테이블 생성

### 1-1. PythonAnywhere Bash 콘솔 접속
1. https://www.pythonanywhere.com 로그인
2. **Consoles** 탭 클릭
3. **Bash** 클릭 (새 콘솔 시작)

### 1-2. MySQL 접속
```bash
mysql -u tirepass -p
# 비밀번호 입력
```

### 1-3. 데이터베이스 선택
```sql
USE tirepass$itire_db;
```

### 1-4. customers 테이블 생성
```sql
CREATE TABLE IF NOT EXISTS customers (
  CODE VARCHAR(10) PRIMARY KEY COMMENT 'ERP 고객코드',
  NAME VARCHAR(100) COMMENT '상호',
  REP VARCHAR(50) COMMENT '대표자',
  TEL1 VARCHAR(20) COMMENT '전화1',
  TEL3 VARCHAR(20) COMMENT '휴대전화',
  TEL4 VARCHAR(20) COMMENT '전화4',
  ENNO VARCHAR(20) COMMENT '사업자번호',
  ADDRESS1 VARCHAR(255) COMMENT '주소',
  LAST_SYNC DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '최종 동기화 시간',
  INDEX idx_customers_name (NAME),
  INDEX idx_customers_enno (ENNO),
  INDEX idx_customers_address1 (ADDRESS1(100)),
  INDEX idx_customers_last_sync (LAST_SYNC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='ERP 서버 고객 목록 (읽기 전용, 실시간 동기화)';
```

### 1-5. 테이블 확인
```sql
DESCRIBE customers;
SELECT COUNT(*) FROM customers;  -- 0이어야 정상 (ERP 동기화 전)
```

### 1-6. MySQL 종료
```sql
EXIT;
```

---

## 2단계: Django 코드 배포

### 2-1. tire_data/models.py 수정

**Files** 탭 → `tire_data/models.py` 열기

**CustomersFull 모델을 Customers 모델 위에 추가:**

```python
class CustomersFull(models.Model):
    """ERP 서버 전체 고객 목록 (읽기 전용, 실시간 동기화)"""
    code = models.CharField(max_length=10, primary_key=True, verbose_name='고객코드', db_column='CODE')
    name = models.CharField(max_length=100, null=True, blank=True, verbose_name='상호', db_column='NAME')
    rep = models.CharField(max_length=50, null=True, blank=True, verbose_name='대표자', db_column='REP')
    tel1 = models.CharField(max_length=20, null=True, blank=True, verbose_name='전화1', db_column='TEL1')
    tel3 = models.CharField(max_length=20, null=True, blank=True, verbose_name='휴대전화', db_column='TEL3')
    tel4 = models.CharField(max_length=20, null=True, blank=True, verbose_name='전화4', db_column='TEL4')
    enno = models.CharField(max_length=20, null=True, blank=True, verbose_name='사업자번호', db_column='ENNO')
    address1 = models.CharField(max_length=255, null=True, blank=True, verbose_name='주소', db_column='ADDRESS1')
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

**Customers 모델의 Meta 클래스 수정:**
```python
class Customers(models.Model):
    """모바일 회원가입 고객 (pythonanywhere 관리)"""
    # ... 필드는 기존과 동일 ...

    class Meta:
        db_table = 'customers_simple'
        managed = True  # False → True 변경
        verbose_name = '회원'  # '고객' → '회원' 변경
        verbose_name_plural = '회원목록'  # '고객목록' → '회원목록' 변경
        ordering = ['code']
```

**저장** (Ctrl+S 또는 Save 버튼)

### 2-2. tire_data/admin.py 수정

**Files** 탭 → `tire_data/admin.py` 열기

**import 수정 (6-10번 라인):**
```python
from .models import (
    Goods, CustomersFull, Customers, YearAllocation, BrandGroup,
    BrandGroupPattern, CustomerDiscount, DiscountHistory,
    CustomerProductDiscount, ShoppingCart, Order, OrderItem, Payment
)
```

**CustomersFullAdmin 추가 (CustomersAdmin 위에 추가):**
```python
@admin.register(CustomersFull)
class CustomersFullAdmin(admin.ModelAdmin):
    """ERP 전체 고객 목록 (읽기 전용)"""
    list_display = ['code', 'name', 'rep', 'tel1', 'tel3', 'tel4', 'enno', 'last_sync']
    search_fields = ['code', 'name', 'rep', 'enno', 'address1']
    ordering = ['code']
    list_per_page = 50

    fieldsets = (
        ('기본 정보', {
            'fields': ('code', 'name', 'rep')
        }),
        ('연락처', {
            'fields': ('tel1', 'tel3', 'tel4')
        }),
        ('사업자 정보', {
            'fields': ('enno', 'address1')
        }),
        ('시스템 정보', {
            'fields': ('last_sync',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['code', 'name', 'rep', 'tel1', 'tel3', 'tel4', 'enno', 'address1', 'last_sync']

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

**CustomersAdmin 주석 수정:**
```python
@admin.register(Customers)
class CustomersAdmin(admin.ModelAdmin):
    """모바일 회원가입 고객"""  # 주석 변경
    # ... 나머지는 동일 ...
```

**저장** (Ctrl+S 또는 Save 버튼)

---

## 3단계: 웹앱 리로드

1. **Web** 탭 클릭
2. **Reload tirepass.pythonanywhere.com** 버튼 클릭 (녹색 버튼)
3. 리로드 완료 대기 (약 10초)

---

## 4단계: 에러 확인

### 4-1. Error Log 확인
1. **Web** 탭 → **Log files** 섹션
2. **Error log** 클릭
3. 최근 에러 메시지 확인

### 4-2. 정상 동작 확인
- 에러가 없으면 다음 단계 진행
- 에러가 있으면:
  - 들여쓰기 오류 확인
  - 문법 오류 확인
  - 에러 메시지 복사하여 공유

---

## 5단계: 관리자 페이지 확인

### 5-1. 관리자 로그인
https://tirepass.pythonanywhere.com/admin/

### 5-2. 메뉴 확인
- ✅ **ERP 고객목록** (새로 추가됨) - CustomersFull
- ✅ **회원목록** (기존 고객목록) - Customers
- ✅ **상품목록** - Goods

### 5-3. ERP 고객목록 클릭
- 현재는 비어있음 (ERP 동기화 전)
- 추가/수정/삭제 버튼이 없어야 함 (읽기 전용)

### 5-4. 회원목록 클릭
- 404명의 고객이 표시되어야 함
- 추가/수정/삭제 가능

---

## 6단계: 테스트 계정 로그인

### 6-1. Bash 콘솔에서 테스트 계정 확인
```bash
cd ~/tirepass
source .virtualenvs/itire-venv/bin/activate
python manage.py shell
```

### 6-2. Python Shell에서 실행
```python
from tire_data.models import Customers

# 첫 번째 회원 확인
customer = Customers.objects.filter(is_registered=True).first()
if customer:
    print(f"계정: {customer.enno}")
    print(f"상호: {customer.name}")
    print(f"초기 비밀번호: {customer.enno[-5:]}")
else:
    print("등록된 회원이 없습니다.")

# 여러 회원 확인
customers = Customers.objects.filter(is_registered=True)[:5]
for c in customers:
    print(f"{c.enno} / {c.name} / 비밀번호: {c.enno[-5:]}")

exit()
```

### 6-3. 모바일 로그인 테스트
1. https://tirepass.pythonanywhere.com/mobile/login/ 접속
2. **계정**: 사업자등록번호 10자리 (예: 4101967194)
3. **비밀번호**: 사업자등록번호 뒤 5자리 (예: 67194)
4. 로그인 클릭
5. **최초 로그인 시**: "최초 로그인입니다. 보안을 위해 비밀번호를 변경해주세요." 메시지 표시
6. 자동으로 프로필 페이지로 이동 (`/mobile/profile/?change_password=true`)
7. 비밀번호 변경 폼 자동 표시 확인

### 6-4. 비밀번호 변경 테스트
1. 프로필 페이지에서 비밀번호 변경 폼 확인
2. **현재 비밀번호**: 초기 비밀번호 (사업자번호 뒤 5자리)
3. **새 비밀번호**: 원하는 비밀번호 (4자 이상)
4. **새 비밀번호 확인**: 새 비밀번호 재입력
5. "비밀번호 변경" 버튼 클릭
6. "비밀번호가 변경되었습니다" 메시지 확인

### 6-5. 변경된 비밀번호로 재로그인
1. 로그아웃
2. 다시 로그인
3. 변경한 비밀번호로 로그인 성공 확인
4. 홈 화면으로 바로 이동 (비밀번호 변경 페이지로 리다이렉트 안 됨)

### 6-6. 로그인 성공 확인
- ✅ 홈 화면 표시
- ✅ 상단에 고객명 표시
- ✅ 상품 목록 조회 가능

---

## 7단계: YearAllocation 500 에러 해결

### 7-1. Error Log 확인
https://tirepass.pythonanywhere.com/admin/tire_data/yearallocation/ 접속 시 500 에러

### 7-2. 테이블 존재 여부 확인
```bash
mysql -u tirepass -p
USE tirepass$itire_db;
SHOW TABLES LIKE 'year_allocations';
DESCRIBE year_allocations;
EXIT;
```

### 7-3. 테이블이 없으면 생성
```sql
CREATE TABLE IF NOT EXISTS year_allocations (
  id BIGINT NOT NULL AUTO_INCREMENT,
  goods_code VARCHAR(20) NOT NULL,
  year_2025 INT NOT NULL,
  year_2024 INT NOT NULL,
  year_2023 INT NOT NULL,
  year_2022 INT NOT NULL,
  year_2021_before INT NOT NULL,
  year_2024_discount DECIMAL(5,2) DEFAULT 0.00 COMMENT '2024년 할인율(%)',
  year_2023_discount DECIMAL(5,2) DEFAULT 0.00 COMMENT '2023년 할인율(%)',
  year_2022_discount DECIMAL(5,2) DEFAULT 0.00 COMMENT '2022년 할인율(%)',
  year_2021_before_discount DECIMAL(5,2) DEFAULT 0.00 COMMENT '2021년 이전 할인율(%)',
  last_updated DATETIME(6) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY year_allocations_goods_code_81a5f7ce_uniq (goods_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

## 8단계: ERP 서버 트리거 설정 (선택)

**로컬 화성 데스크톱에서 실행**

### 8-1. ERP Firebird → MySQL 동기화 스크립트 작성
```python
# scripts/sync_erp_to_pythonanywhere.py
import fdb
import mysql.connector
from datetime import datetime

# Firebird 연결
fb_conn = fdb.connect(
    dsn='ITIRE2.iptime.org:C:/MRNSOFT/DATA/HWADATA.FDB',
    user='sysdba',
    password='masterkey',
    charset='UTF8'
)

# MySQL 연결 (pythonanywhere)
mysql_conn = mysql.connector.connect(
    host='tirepass.mysql.pythonanywhere-services.com',
    user='tirepass',
    password='your_mysql_password',
    database='tirepass$itire_db',
    charset='utf8mb4'
)

fb_cursor = fb_conn.cursor()
mysql_cursor = mysql_conn.cursor()

# ERP 고객 가져오기
fb_cursor.execute("""
    SELECT CODE, NAME, REP, TEL1, TEL3, TEL4, ENNO, ADDRESS1
    FROM CUSTOMERS
    WHERE CODE NOT LIKE 'Z%'
""")

customers = fb_cursor.fetchall()

# MySQL에 동기화
for customer in customers:
    code, name, rep, tel1, tel3, tel4, enno, address1 = customer

    mysql_cursor.execute("""
        INSERT INTO customers (CODE, NAME, REP, TEL1, TEL3, TEL4, ENNO, ADDRESS1, LAST_SYNC)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
        ON DUPLICATE KEY UPDATE
            NAME = VALUES(NAME),
            REP = VALUES(REP),
            TEL1 = VALUES(TEL1),
            TEL3 = VALUES(TEL3),
            TEL4 = VALUES(TEL4),
            ENNO = VALUES(ENNO),
            ADDRESS1 = VALUES(ADDRESS1),
            LAST_SYNC = NOW()
    """, (code, name, rep, tel1, tel3, tel4, enno, address1))

mysql_conn.commit()

print(f"동기화 완료: {len(customers)}명")

fb_conn.close()
mysql_conn.close()
```

### 8-2. 스크립트 실행
```bash
python scripts/sync_erp_to_pythonanywhere.py
```

---

## 완료 체크리스트

### 기본 배포
- [ ] 1단계: MySQL customers 테이블 생성
- [ ] 2-1단계: tire_data/models.py 수정
- [ ] 2-2단계: tire_data/admin.py 수정
- [ ] 3단계: 웹앱 리로드
- [ ] 4단계: 에러 로그 확인 (에러 없음)
- [ ] 5단계: 관리자 페이지 확인 (ERP 고객목록/회원목록)

### 로그인 & 비밀번호 변경
- [ ] 6-1단계: Bash 콘솔에서 테스트 계정 확인
- [ ] 6-2단계: Python Shell에서 계정 정보 조회
- [ ] 6-3단계: 모바일 로그인 테스트 (초기 비밀번호)
- [ ] 6-4단계: 비밀번호 변경 테스트
- [ ] 6-5단계: 변경된 비밀번호로 재로그인
- [ ] 6-6단계: 홈 화면 정상 표시 확인

### 추가 작업
- [ ] 7단계: YearAllocation 페이지 정상 작동
- [ ] 8단계: ERP 동기화 스크립트 실행 (선택)

---

## 트러블슈팅

### 문제 1: SyntaxError 발생
**원인**: 들여쓰기 오류
**해결**: 스페이스 4개로 일관성 있게 들여쓰기

### 문제 2: ImportError: cannot import name 'CustomersFull'
**원인**: models.py 저장 안 됨
**해결**: models.py 다시 저장 후 웹앱 리로드

### 문제 3: Table 'customers' doesn't exist
**원인**: MySQL 테이블 생성 안 됨
**해결**: 1단계 다시 실행

### 문제 4: 관리자 페이지에 ERP 고객목록 안 보임
**원인**: admin.py 수정 안 됨
**해결**: 2-2단계 다시 실행

### 문제 5: 로그인 안 됨
**원인**: migrate_erp_customers 실행 안 됨
**해결**: Bash 콘솔에서 `python manage.py migrate_erp_customers` 실행

---

## 추가 참고 문서

- `DEPLOYMENT_CUSTOMERS.md`: 상세 설명
- `pythonanywhere_customers_table.sql`: SQL 스크립트
- `ENCRYPTION_GUIDE.md`: 고객 정보 암호화 가이드

---

## 다음 단계

배포 완료 후:
1. ERP 서버 실시간 동기화 구현
2. 고객 정보 암호화 적용 (선택)
3. 모바일 앱 추가 기능 개발
