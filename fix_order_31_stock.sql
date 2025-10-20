-- 주문 31번의 재고를 수동으로 차감하는 SQL
-- PythonAnywhere MySQL Console에서 실행

-- 1. 먼저 주문 31번의 상품과 수량 확인
SELECT
    oi.product_code,
    oi.selected_year,
    oi.quantity,
    ya.year_2023 as current_stock_2023,
    g.JAEGO as current_total_stock
FROM order_items oi
LEFT JOIN year_allocations ya ON oi.product_code = ya.goods_code
LEFT JOIN goods g ON oi.product_code = g.CODE
WHERE oi.order_id = 31;

-- 2. YearAllocation 재고 차감 (예: P-0PZR0000001, 2023년, 수량 2)
-- 실제 값으로 교체하여 실행
-- UPDATE year_allocations
-- SET year_2023 = GREATEST(0, year_2023 - 2)
-- WHERE goods_code = 'P-0PZR0000001';

-- 3. Goods 테이블 재고 차감
-- UPDATE goods
-- SET JAEGO = GREATEST(0, JAEGO - 2)
-- WHERE CODE = 'P-0PZR0000001';

-- 4. 결과 확인
-- SELECT
--     goods_code,
--     year_2023,
--     (year_2025 + year_2024 + year_2023 + year_2022 + year_2021_before) as total_allocated
-- FROM year_allocations
-- WHERE goods_code = 'P-0PZR0000001';
