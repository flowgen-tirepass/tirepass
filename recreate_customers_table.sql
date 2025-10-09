-- ============================================
-- PythonAnywhere MySQL - customers 테이블 재생성
-- ============================================
-- ERP CUSTOMS 테이블 구조에 맞춰 새로 생성

USE tirepass$itire_db;

-- 기존 테이블 삭제
DROP TABLE IF EXISTS customers;

-- 새 테이블 생성 (모든 필드 포함)
CREATE TABLE customers (
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
  INDEX idx_customers_last_sync (LAST_SYNC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='ERP 서버 고객 목록 (읽기 전용, 실시간 동기화)';

SELECT 'customers 테이블이 재생성되었습니다.' AS status;
