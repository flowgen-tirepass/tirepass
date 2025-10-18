-- ================================================================
-- 고객 할인율 추가: 4618603360 - 피렐리 브랜드 4% 할인
-- ================================================================

-- 1. 기존 데이터 확인
SELECT
    id,
    customer_code,
    brand,
    group_id,
    discount_rate,
    priority,
    is_active,
    created_at
FROM customer_discounts
WHERE customer_code = '4618603360' AND brand = '피렐리';

-- 2. 기존 데이터 삭제 (있는 경우)
DELETE FROM customer_discounts
WHERE customer_code = '4618603360' AND brand = '피렐리';

-- 3. 새로운 고객 할인율 추가
INSERT INTO customer_discounts (
    customer_code,
    brand,
    group_id,
    discount_rate,
    priority,
    is_active,
    created_at,
    updated_at
) VALUES (
    '4618603360',          -- 고객 코드 (사업자번호)
    '피렐리',               -- 브랜드
    NULL,                  -- 그룹 ID (브랜드 전체 할인이므로 NULL)
    4.00,                  -- 할인율 4%
    1,                     -- 우선순위
    1,                     -- 활성화 (TRUE)
    NOW(),                 -- 생성일시
    NOW()                  -- 수정일시
);

-- 4. 추가 결과 확인
SELECT
    id,
    customer_code,
    brand,
    group_id,
    discount_rate,
    priority,
    is_active,
    created_at
FROM customer_discounts
WHERE customer_code = '4618603360'
ORDER BY brand;

-- 5. 고객 정보 확인
SELECT code, name, enno
FROM customers_simple
WHERE code = '4618603360';

-- ================================================================
-- 실행 결과 예상:
-- - 고객 4618603360에게 피렐리 브랜드 4% 할인이 추가됩니다.
-- - 이후 P-PZERO-25 상품의 할인율이 다음과 같이 계산됩니다:
--   * 기본 할인율: 20%
--   * 고객 할인율: 4% (피렐리 브랜드)
--   * 추가 할인율: 4% (개별 상품)
--   * DOT 할인율: 4% (2023년)
--   * 총 할인율: 32%
--   * 최종 가격: 551,100 × (1 - 0.32) = 374,748원
-- ================================================================
