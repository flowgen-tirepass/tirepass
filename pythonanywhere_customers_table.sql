-- ============================================
-- PythonAnywhere MySQL - ERP 고객 테이블 생성
-- ============================================
-- 작성일: 2025-10-09
-- 용도: ERP Firebird 서버 고객 데이터를 실시간 동기화하기 위한 테이블
-- 주의: 이 테이블은 ERP 서버 트리거가 INSERT/UPDATE/DELETE 관리
-- ============================================

-- customers 테이블 생성 (ERP 전체 고객 목록)
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

-- ============================================
-- 테이블 구조 확인
-- ============================================
DESCRIBE customers;

-- ============================================
-- 초기 데이터 확인 (ERP에서 동기화되기 전에는 빈 테이블)
-- ============================================
SELECT COUNT(*) AS total_customers FROM customers;

-- ============================================
-- 완료 메시지
-- ============================================
SELECT 'customers 테이블 생성 완료! ERP 서버 트리거로 데이터가 실시간 동기화됩니다.' AS status;
