# PythonAnywhere 긴급 수정 가이드

## 문제 1: Orders 테이블 order_source 컬럼 누락

**오류 메시지:**
```
OperationalError: (1054, "Unknown column 'orders.order_source' in 'field list'")
```

**원인:**
- Migration `0007_add_order_fields.py`가 PythonAnywhere DB에 적용되지 않음
- 로컬에서는 정상이지만 PythonAnywhere에서는 누락

---

## 해결 방법 (3가지 중 선택)

### 방법 1: Django Migration 적용 (추천)

**SSH 터미널 접속:**

```bash
cd ~/tirepass
source ~/.virtualenvs/itire-venv/bin/activate

# 1. 코드 업데이트
git pull origin main

# 2. Migration 상태 확인
python manage.py showmigrations tire_data

# 3. Migration 적용
python manage.py migrate tire_data

# 4. 웹앱 재시작
touch /var/www/tirepass_pythonanywhere_com_wsgi.py
```

**예상 출력:**
```
Running migrations:
  Applying tire_data.0007_add_order_fields... OK
  Applying tire_data.0012_goodsrealtimesnapshot... OK
```

---

### 방법 2: SQL 직접 실행 (Migration 실패 시)

**MySQL 콘솔 접속:**

PythonAnywhere → Databases → MySQL console

```sql
USE tirepass$itire_db;

-- 컬럼 추가
ALTER TABLE orders
ADD COLUMN cancelled_date DATETIME NULL COMMENT '취소일시' AFTER delivered_date,
ADD COLUMN cancelled_reason TEXT NULL COMMENT '취소사유' AFTER cancelled_date,
ADD COLUMN returned_date DATETIME NULL COMMENT '반품일시' AFTER cancelled_reason,
ADD COLUMN returned_reason TEXT NULL COMMENT '반품사유' AFTER returned_date,
ADD COLUMN order_source VARCHAR(20) NOT NULL DEFAULT 'mobile' COMMENT '주문 출처' AFTER returned_reason,
ADD COLUMN erp_order_number VARCHAR(50) NULL COMMENT 'ERP 주문번호' AFTER order_source;

-- 확인
DESCRIBE orders;
```

**그 다음:**
```bash
cd ~/tirepass
source ~/.virtualenvs/itire-venv/bin/activate

# Migration을 fake로 표시 (이미 적용됨)
python manage.py migrate tire_data 0007_add_order_fields --fake

# 웹앱 재시작
touch /var/www/tirepass_pythonanywhere_com_wsgi.py
```

---

### 방법 3: 간편 스크립트 (원격 실행)

**SSH 터미널에서:**

```bash
cd ~/tirepass
source ~/.virtualenvs/itire-venv/bin/activate

# 스크립트 실행
python << 'EOF'
from django.db import connection

sql_commands = [
    """
    ALTER TABLE orders
    ADD COLUMN IF NOT EXISTS cancelled_date DATETIME NULL COMMENT '취소일시' AFTER delivered_date
    """,
    """
    ALTER TABLE orders
    ADD COLUMN IF NOT EXISTS cancelled_reason TEXT NULL COMMENT '취소사유' AFTER cancelled_date
    """,
    """
    ALTER TABLE orders
    ADD COLUMN IF NOT EXISTS returned_date DATETIME NULL COMMENT '반품일시' AFTER cancelled_reason
    """,
    """
    ALTER TABLE orders
    ADD COLUMN IF NOT EXISTS returned_reason TEXT NULL COMMENT '반품사유' AFTER returned_date
    """,
    """
    ALTER TABLE orders
    ADD COLUMN IF NOT EXISTS order_source VARCHAR(20) NOT NULL DEFAULT 'mobile' COMMENT '주문 출처' AFTER returned_reason
    """,
    """
    ALTER TABLE orders
    ADD COLUMN IF NOT EXISTS erp_order_number VARCHAR(50) NULL COMMENT 'ERP 주문번호' AFTER order_source
    """
]

with connection.cursor() as cursor:
    for sql in sql_commands:
        try:
            cursor.execute(sql)
            print(f"✅ {sql[:50]}...")
        except Exception as e:
            print(f"⚠️ {sql[:50]}... - {e}")

print("\n✅ Orders 테이블 수정 완료!")
EOF

# Migration fake
python manage.py migrate tire_data 0007_add_order_fields --fake

# 웹앱 재시작
touch /var/www/tirepass_pythonanywhere_com_wsgi.py
```

**참고:** MySQL은 `IF NOT EXISTS`를 컬럼에 지원하지 않으므로, 에러 발생 시 이미 존재한다는 의미입니다.

---

## 확인

**Admin 접속:**
```
https://tirepass.pythonanywhere.com/admin/tire_data/order/
```

**오류 없이 주문 목록이 표시되면 성공!**

---

## 문제 2: 모바일 페이지 브랜드 로고 크기 조정

**작업 후 별도 처리 예정**

---

**작성일:** 2025-10-16
**우선순위:** 긴급 (주문 관리 기능 차단)
