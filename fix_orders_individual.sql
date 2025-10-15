-- Orders 테이블 컬럼 개별 추가 (오류 무시)
-- PythonAnywhere MySQL Console에서 실행

USE tirepass$itire_db;

-- 현재 테이블 구조 확인
DESCRIBE orders;

-- 각 컬럼을 개별적으로 추가 (이미 있으면 오류 발생 - 무시하고 계속)

-- 1. cancelled_date
ALTER TABLE orders ADD COLUMN cancelled_date DATETIME NULL COMMENT '취소일시' AFTER delivered_date;

-- 2. cancelled_reason
ALTER TABLE orders ADD COLUMN cancelled_reason TEXT NULL COMMENT '취소사유' AFTER cancelled_date;

-- 3. returned_date
ALTER TABLE orders ADD COLUMN returned_date DATETIME NULL COMMENT '반품일시' AFTER cancelled_reason;

-- 4. returned_reason
ALTER TABLE orders ADD COLUMN returned_reason TEXT NULL COMMENT '반품사유' AFTER returned_date;

-- 5. order_source (이 컬럼이 핵심!)
ALTER TABLE orders ADD COLUMN order_source VARCHAR(20) NOT NULL DEFAULT 'mobile' COMMENT '주문 출처' AFTER returned_reason;

-- 6. erp_order_number
ALTER TABLE orders ADD COLUMN erp_order_number VARCHAR(50) NULL COMMENT 'ERP 주문번호' AFTER order_source;

-- 최종 확인
DESCRIBE orders;

-- order_source 컬럼이 있는지 확인
SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'tirepass$itire_db'
  AND TABLE_NAME = 'orders'
  AND COLUMN_NAME IN ('order_source', 'erp_order_number');
