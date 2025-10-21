-- =====================================================================
-- ERP 동기화 제외 상품 설정 및 삭제 스크립트
--
-- 실행 위치: PythonAnywhere MySQL Console
-- 목적: P-0PZR0000001, P-PZERO-58을 삭제하고 자동 재생성 방지
-- =====================================================================

-- 1단계: excluded_goods 테이블 생성
CREATE TABLE IF NOT EXISTS excluded_goods (
    code VARCHAR(20) PRIMARY KEY COMMENT '상품코드',
    reason VARCHAR(200) NOT NULL COMMENT '제외 사유',
    excluded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '제외일시',
    excluded_by VARCHAR(50) NOT NULL DEFAULT 'admin' COMMENT '제외자'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='ERP 동기화 제외 상품 목록';

-- 2단계: 제외 목록에 등록 (이미 있으면 무시)
INSERT IGNORE INTO excluded_goods (code, reason, excluded_by)
VALUES
    ('P-0PZR0000001', 'ERP에 존재하지 않는 상품 (자동 생성 방지)', 'system'),
    ('P-PZERO-58', 'ERP에 존재하지 않는 상품 (자동 생성 방지)', 'system');

-- 3단계: 제외 목록 확인
SELECT
    code AS '상품코드',
    reason AS '제외 사유',
    excluded_at AS '제외일시',
    excluded_by AS '제외자'
FROM excluded_goods
ORDER BY excluded_at DESC;

-- 4단계: Goods 테이블에서 삭제
DELETE FROM goods
WHERE CODE IN ('P-0PZR0000001', 'P-PZERO-58');

-- 5단계: 최종 확인
SELECT
    '✓ 제외 목록에 등록됨' AS '상태',
    COUNT(*) AS '등록 개수'
FROM excluded_goods
WHERE code IN ('P-0PZR0000001', 'P-PZERO-58');

SELECT
    '✓ Goods 테이블에서 삭제됨' AS '상태',
    COUNT(*) AS '남은 개수 (0이어야 함)'
FROM goods
WHERE CODE IN ('P-0PZR0000001', 'P-PZERO-58');

-- =====================================================================
-- 완료!
--
-- 결과:
-- 1. excluded_goods 테이블에 2개 등록됨
-- 2. goods 테이블에서 2개 삭제됨
-- 3. 매일 새벽 2시 sync_erp_goods 실행 시 이 상품들은 건너뜀
--
-- 제외 목록에서 제거하려면:
-- DELETE FROM excluded_goods WHERE code = 'P-0PZR0000001';
-- =====================================================================
