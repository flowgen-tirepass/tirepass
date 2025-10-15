# Orders 테이블 긴급 수정 가이드 (5분)

## 오류
```
OperationalError: (1054, "Unknown column 'orders.order_source' in 'field list'")
```

---

## 📌 해결 방법 (2가지 중 선택)

---

### 🔥 방법 1: PythonAnywhere MySQL 콘솔 (가장 빠름, 3분)

#### 1단계: MySQL 콘솔 접속
1. PythonAnywhere 대시보드 접속
2. 상단 메뉴 **Databases** 클릭
3. **MySQL console** 버튼 클릭 (또는 아래 명령 실행)

```bash
mysql -u tirepass -h tirepass.mysql.pythonanywhere-services.com 'tirepass$itire_db'
```

#### 2단계: SQL 실행 (복사하여 붙여넣기)

```sql
-- 데이터베이스 선택
USE tirepass$itire_db;

-- 현재 테이블 구조 확인
DESCRIBE orders;

-- 컬럼 추가 (한 번에 실행)
ALTER TABLE orders
ADD COLUMN cancelled_date DATETIME NULL COMMENT '취소일시' AFTER delivered_date,
ADD COLUMN cancelled_reason TEXT NULL COMMENT '취소사유' AFTER cancelled_date,
ADD COLUMN returned_date DATETIME NULL COMMENT '반품일시' AFTER cancelled_reason,
ADD COLUMN returned_reason TEXT NULL COMMENT '반품사유' AFTER returned_date,
ADD COLUMN order_source VARCHAR(20) NOT NULL DEFAULT 'mobile' COMMENT '주문 출처' AFTER returned_reason,
ADD COLUMN erp_order_number VARCHAR(50) NULL COMMENT 'ERP 주문번호' AFTER order_source;

-- 확인
DESCRIBE orders;

-- 종료
exit;
```

#### 3단계: Migration fake 표시

SSH 터미널:

```bash
cd ~/tirepass
source ~/.virtualenvs/itire-venv/bin/activate
python manage.py migrate tire_data 0007_add_order_fields --fake
```

#### 4단계: 웹앱 재시작

```bash
touch /var/www/tirepass_pythonanywhere_com_wsgi.py
```

---

### 🔧 방법 2: Django Management Command (안전함, 5분)

#### 1단계: SSH 접속 및 코드 업데이트

```bash
cd ~/tirepass
source ~/.virtualenvs/itire-venv/bin/activate
git pull origin main
```

#### 2단계: Migration 상태 확인

```bash
python manage.py showmigrations tire_data
```

**예상 출력:**
```
tire_data
 [X] 0001_initial
 [X] 0002_...
 [ ] 0007_add_order_fields  ← 아직 적용 안됨
 [ ] 0012_goodsrealtimesnapshot
```

#### 3단계: Migration 적용

```bash
python manage.py migrate tire_data
```

**예상 출력:**
```
Running migrations:
  Applying tire_data.0007_add_order_fields... OK
  Applying tire_data.0012_goodsrealtimesnapshot... OK
```

#### 4단계: 웹앱 재시작

```bash
touch /var/www/tirepass_pythonanywhere_com_wsgi.py
```

---

## ✅ 확인

**Admin 접속:**
```
https://tirepass.pythonanywhere.com/admin/tire_data/order/
```

오류 없이 주문 목록이 표시되면 성공!

---

## 🔍 문제가 계속되면?

### 에러: "Duplicate column name"

**의미:** 컬럼이 이미 존재함 (성공)

**해결:**
```bash
cd ~/tirepass
source ~/.virtualenvs/itire-venv/bin/activate
python manage.py migrate tire_data 0007_add_order_fields --fake
touch /var/www/tirepass_pythonanywhere_com_wsgi.py
```

### 에러: Migration dependency 오류

**해결:**
```bash
cd ~/tirepass
source ~/.virtualenvs/itire-venv/bin/activate

# Migration 히스토리 확인
python manage.py showmigrations tire_data

# 문제 있는 migration fake
python manage.py migrate tire_data 0007_add_order_fields --fake
python manage.py migrate tire_data

# 웹앱 재시작
touch /var/www/tirepass_pythonanywhere_com_wsgi.py
```

---

## 📋 추가 확인 사항

### 컬럼이 제대로 추가되었는지 확인

MySQL 콘솔:

```sql
USE tirepass$itire_db;

SELECT
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    COLUMN_DEFAULT,
    COLUMN_COMMENT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'tirepass$itire_db'
  AND TABLE_NAME = 'orders'
  AND COLUMN_NAME IN ('order_source', 'erp_order_number', 'cancelled_date', 'cancelled_reason', 'returned_date', 'returned_reason');
```

**예상 출력:**
```
+------------------+--------------+-------------+----------------+------------------+
| COLUMN_NAME      | DATA_TYPE    | IS_NULLABLE | COLUMN_DEFAULT | COLUMN_COMMENT   |
+------------------+--------------+-------------+----------------+------------------+
| cancelled_date   | datetime     | YES         | NULL           | 취소일시         |
| cancelled_reason | text         | YES         | NULL           | 취소사유         |
| returned_date    | datetime     | YES         | NULL           | 반품일시         |
| returned_reason  | text         | YES         | NULL           | 반품사유         |
| order_source     | varchar(20)  | NO          | mobile         | 주문 출처        |
| erp_order_number | varchar(50)  | YES         | NULL           | ERP 주문번호     |
+------------------+--------------+-------------+----------------+------------------+
```

---

## 🎯 권장 방법

**가장 빠르고 확실한 방법:**
1. **방법 1 (MySQL 콘솔)** 사용
2. SQL 직접 실행
3. Migration fake 표시
4. 웹앱 재시작

**예상 소요 시간:** 3분

---

**작성일:** 2025-10-16
**우선순위:** 긴급 (주문 관리 기능 차단 중)
