-- Orders 테이블에 누락된 컬럼 추가
-- PythonAnywhere MySQL 콘솔에서 실행

USE tirepass$itire_db;

-- 1. 컬럼 존재 여부 확인
DESCRIBE orders;

-- 2. order_source 컬럼 추가 (이미 있으면 에러 발생 - 무시)
ALTER TABLE orders
ADD COLUMN cancelled_date DATETIME NULL COMMENT '취소일시' AFTER delivered_date;

ALTER TABLE orders
ADD COLUMN cancelled_reason TEXT NULL COMMENT '취소사유' AFTER cancelled_date;

ALTER TABLE orders
ADD COLUMN returned_date DATETIME NULL COMMENT '반품일시' AFTER cancelled_reason;

ALTER TABLE orders
ADD COLUMN returned_reason TEXT NULL COMMENT '반품사유' AFTER returned_date;

ALTER TABLE orders
ADD COLUMN order_source VARCHAR(20) NOT NULL DEFAULT 'mobile' COMMENT '주문 출처' AFTER returned_reason;

ALTER TABLE orders
ADD COLUMN erp_order_number VARCHAR(50) NULL COMMENT 'ERP 주문번호' AFTER order_source;

-- 3. order_status 컬럼 choices 확장 (이미 VARCHAR이면 ALTER 필요 없음)
-- ALTER TABLE orders MODIFY COLUMN order_status VARCHAR(20) NOT NULL DEFAULT 'pending';

-- 4. 확인
DESCRIBE orders;

SELECT
    order_number,
    order_source,
    erp_order_number,
    order_status
FROM orders
LIMIT 5;
