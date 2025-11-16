-- ================================================================================
-- 재고 복구 SQL
-- ORD20251111008, ORD20251111009 취소로 인한 재고 복구
-- ================================================================================

-- 상품: 145R13 8L POWER GRIP KC12 (K-LT-S036)
-- 제조년도: 2025년
-- 복구 수량: 2개 (각 주문에서 1개씩)

-- 1. 현재 재고 확인
SELECT
    goods_code,
    year_2025 as current_2025_stock,
    year_2024,
    year_2023
FROM year_allocations
WHERE goods_code = 'K-LT-S036';

-- 2. 재고 복구 (2025년 재고 +2)
UPDATE year_allocations
SET year_2025 = year_2025 + 2
WHERE goods_code = 'K-LT-S036';

-- 3. 복구 후 재고 확인
SELECT
    goods_code,
    year_2025 as updated_2025_stock,
    year_2024,
    year_2023
FROM year_allocations
WHERE goods_code = 'K-LT-S036';

-- 4. 최종 확인 메시지
SELECT
    CONCAT('재고 복구 완료: K-LT-S036 (2025년 +2개)') as result;
