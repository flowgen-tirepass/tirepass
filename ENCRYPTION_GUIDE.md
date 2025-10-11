# MySQL 고객정보 암호화 가이드

## 개요
Django에서 민감한 고객 정보(이름, 전화번호, 사업자번호)를 MySQL에 암호화하여 저장하고, 관리자 페이지에서 복호화하여 표시하는 방법

## 암호화 방식

### 1. django-cryptography (권장)
- AES-256 암호화
- 자동 암호화/복호화
- Django ORM과 완벽 통합

### 2. django-encrypted-model-fields
- Fernet 암호화
- 간단한 설정

## 구현 방법 (django-cryptography)

### 1단계: 패키지 설치

```bash
# 로컬
pip install django-cryptography

# pythonanywhere
# Bash 콘솔에서
pip install --user django-cryptography
```

### 2단계: requirements.txt 업데이트

```txt
django-cryptography==1.1
cryptography>=41.0.0
```

### 3단계: 암호화 키 생성

```python
# 로컬에서 실행
from cryptography.fernet import Fernet
key = Fernet.generate_key()
print(key.decode())
# 출력 예: 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx='
```

### 4단계: settings.py 수정

```python
# itire/settings.py

# 암호화 키 (환경변수로 관리 - 절대 코드에 하드코딩 금지!)
CRYPTOGRAPHY_KEY = os.environ.get('CRYPTOGRAPHY_KEY', 'your-generated-key-here')

# pythonanywhere 환경변수 설정:
# Web 탭 → Environment variables 섹션
# Name: CRYPTOGRAPHY_KEY
# Value: (생성한 키)
```

### 5단계: models.py 수정

```python
# tire_data/models.py
from encrypted_model_fields.fields import EncryptedCharField

class CustomersFull(models.Model):
    """ERP 서버 전체 고객 목록 (읽기 전용, 실시간 동기화)"""
    code = models.CharField(max_length=10, primary_key=True, verbose_name='고객코드', db_column='CODE')

    # 암호화 필드
    name = EncryptedCharField(max_length=255, null=True, blank=True, verbose_name='상호', db_column='NAME')
    rep = EncryptedCharField(max_length=255, null=True, blank=True, verbose_name='대표자', db_column='REP')
    tel1 = EncryptedCharField(max_length=255, null=True, blank=True, verbose_name='전화1', db_column='TEL1')
    tel3 = EncryptedCharField(max_length=255, null=True, blank=True, verbose_name='휴대전화', db_column='TEL3')
    enno = EncryptedCharField(max_length=255, null=True, blank=True, verbose_name='사업자번호', db_column='ENNO')

    # 비암호화 필드
    last_sync = models.DateTimeField(null=True, blank=True, verbose_name='최종동기화', db_column='LAST_SYNC')

    class Meta:
        db_table = 'customers'
        managed = False
        verbose_name = 'ERP 고객'
        verbose_name_plural = 'ERP 고객목록'
        ordering = ['code']


class Customers(models.Model):
    """모바일 회원가입 고객 (pythonanywhere 관리)"""
    code = models.CharField(max_length=10, primary_key=True, verbose_name='고객코드', db_column='code')

    # 암호화 필드
    name = EncryptedCharField(max_length=255, null=True, blank=True, verbose_name='상호', db_column='name')
    rep = EncryptedCharField(max_length=255, null=True, blank=True, verbose_name='대표자', db_column='rep')
    tel1 = EncryptedCharField(max_length=255, null=True, blank=True, verbose_name='전화1', db_column='tel1')
    tel3 = EncryptedCharField(max_length=255, null=True, blank=True, verbose_name='휴대전화', db_column='tel3')
    enno = EncryptedCharField(max_length=255, null=True, blank=True, verbose_name='사업자번호', db_column='enno')

    # 비밀번호는 별도 해싱 (암호화 아님)
    password = models.CharField(max_length=255, null=True, blank=True, verbose_name='비밀번호', db_column='password')

    # 비암호화 필드
    is_registered = models.BooleanField(default=False, verbose_name='회원가입여부', db_column='is_registered')
    user_id = models.IntegerField(null=True, blank=True, verbose_name='사용자ID', db_column='user_id')
    must_change_password = models.BooleanField(default=True, verbose_name='비밀번호변경필요', db_column='must_change_password')

    class Meta:
        db_table = 'customers_simple'
        managed = True
        verbose_name = '회원'
        verbose_name_plural = '회원목록'
        ordering = ['code']
```

### 6단계: MySQL 테이블 구조 수정

암호화된 데이터는 Base64 인코딩되어 저장되므로 컬럼 크기를 늘려야 합니다:

```sql
-- customers 테이블 수정
ALTER TABLE customers
MODIFY COLUMN NAME VARCHAR(255),
MODIFY COLUMN REP VARCHAR(255),
MODIFY COLUMN TEL1 VARCHAR(255),
MODIFY COLUMN TEL3 VARCHAR(255),
MODIFY COLUMN ENNO VARCHAR(255);

-- customers_simple 테이블 수정
ALTER TABLE customers_simple
MODIFY COLUMN name VARCHAR(255),
MODIFY COLUMN rep VARCHAR(255),
MODIFY COLUMN tel1 VARCHAR(255),
MODIFY COLUMN tel3 VARCHAR(255),
MODIFY COLUMN enno VARCHAR(255);
```

### 7단계: Admin 페이지 - 자동 복호화

**변경 필요 없음!** Django ORM이 자동으로 처리합니다:

```python
# tire_data/admin.py
@admin.register(CustomersFull)
class CustomersFullAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'rep', 'tel1', 'tel3', 'enno', 'last_sync']
    # name, rep, tel1, tel3, enno는 자동으로 복호화되어 표시됨!
```

## 동작 방식

### 저장 (암호화)
```python
customer = Customers(
    code='C001',
    name='타이어킹',  # 평문 입력
    tel1='02-1234-5678'
)
customer.save()
# MySQL에 저장: name='gAAAAABl...' (암호화됨)
```

### 조회 (복호화)
```python
customer = Customers.objects.get(code='C001')
print(customer.name)  # '타이어킹' (자동 복호화)
```

### 관리자 페이지
- **목록 화면**: 자동 복호화되어 '타이어킹' 표시
- **상세 화면**: 자동 복호화되어 편집 가능
- **MySQL 직접 조회**: 'gAAAAABl...' (암호화된 상태)

## ERP 서버 연동 주의사항

### 방법 1: ERP에서 암호화하여 전송 (권장)
```python
# ERP Firebird 트리거 (Python 또는 stored procedure)
# 1. 고객 정보 가져오기
# 2. 암호화 (동일한 CRYPTOGRAPHY_KEY 사용)
# 3. MySQL에 INSERT/UPDATE
```

### 방법 2: pythonanywhere에서 암호화
```python
# tire_data/utils.py
from cryptography.fernet import Fernet
from django.conf import settings

def encrypt_field(value):
    """필드 값 암호화"""
    if not value:
        return None
    f = Fernet(settings.CRYPTOGRAPHY_KEY.encode())
    return f.encrypt(value.encode()).decode()

def decrypt_field(encrypted_value):
    """필드 값 복호화"""
    if not encrypted_value:
        return None
    f = Fernet(settings.CRYPTOGRAPHY_KEY.encode())
    return f.decrypt(encrypted_value.encode()).decode()
```

## 보안 고려사항

### 1. 암호화 키 관리
- ✅ 환경변수로 관리 (pythonanywhere Environment variables)
- ❌ 코드에 하드코딩 금지
- ❌ Git에 커밋 금지

### 2. 키 백업
- 키를 잃어버리면 **복호화 불가능**
- 안전한 곳에 백업 (Password Manager 등)

### 3. 검색 제한
```python
# ❌ 암호화 필드로 검색 불가
Customers.objects.filter(name__icontains='타이어킹')  # 작동 안 함

# ✅ 비암호화 필드로 검색
Customers.objects.filter(code='C001')  # OK
```

### 4. 인덱스 제한
- 암호화된 필드는 인덱스 효과가 없음
- 검색이 필요한 필드(code)는 암호화하지 않음

## 대안: 부분 암호화

민감도에 따라 선택적 암호화:

```python
class Customers(models.Model):
    # 비암호화 (검색 필요)
    code = models.CharField(max_length=10, primary_key=True)

    # 암호화 (민감 정보)
    name = EncryptedCharField(max_length=255)
    rep = EncryptedCharField(max_length=255)
    tel1 = EncryptedCharField(max_length=255)
    tel3 = EncryptedCharField(max_length=255)
    enno = EncryptedCharField(max_length=255)

    # 비암호화 (검색/필터링 필요)
    is_registered = models.BooleanField(default=False)
```

## 마이그레이션 전략

### 기존 데이터가 있는 경우

```python
# tire_data/management/commands/encrypt_customers.py
from django.core.management.base import BaseCommand
from tire_data.models import Customers

class Command(BaseCommand):
    def handle(self, *args, **options):
        # 1. 모든 고객 가져오기 (암호화 전)
        customers = Customers.objects.all()

        for customer in customers:
            # 2. 각 필드를 다시 저장 (자동 암호화)
            customer.save()

        self.stdout.write(f'{customers.count()} 고객 암호화 완료')

# 실행: python manage.py encrypt_customers
```

## 성능 고려사항

- **암호화/복호화 오버헤드**: 미미함 (ms 단위)
- **대량 조회 시**: 약간 느림 (각 레코드 복호화)
- **캐싱 권장**: 자주 조회되는 데이터는 캐싱

## 테스트

```python
# tire_data/tests.py
from django.test import TestCase
from tire_data.models import Customers

class EncryptionTestCase(TestCase):
    def test_customer_encryption(self):
        # 저장
        customer = Customers.objects.create(
            code='TEST001',
            name='테스트상호',
            tel1='02-1234-5678'
        )

        # 복호화 확인
        loaded = Customers.objects.get(code='TEST001')
        self.assertEqual(loaded.name, '테스트상호')
        self.assertEqual(loaded.tel1, '02-1234-5678')

        # DB에서 직접 조회 (암호화 확인)
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM customers_simple WHERE code='TEST001'")
            row = cursor.fetchone()
            self.assertTrue(row[0].startswith('gAAAAA'))  # Fernet 암호화 시작 문자
```

## 배포 체크리스트

- [ ] django-cryptography 설치
- [ ] 암호화 키 생성 및 백업
- [ ] pythonanywhere 환경변수 설정 (CRYPTOGRAPHY_KEY)
- [ ] MySQL 컬럼 크기 변경 (VARCHAR(255))
- [ ] models.py 수정 (EncryptedCharField)
- [ ] 기존 데이터 암호화 (마이그레이션 스크립트)
- [ ] Admin 페이지 테스트
- [ ] ERP 서버 트리거 수정 (암호화 적용)

## 결론

**가능합니다!**

- ✅ MySQL에 암호화 저장
- ✅ 관리자 페이지에서 자동 복호화
- ✅ Django ORM 완벽 통합
- ✅ 투명한 암호화/복호화

**주의:**
- 암호화 키 관리 필수
- 검색 성능 저하 가능
- ERP 서버 트리거도 암호화 로직 필요
