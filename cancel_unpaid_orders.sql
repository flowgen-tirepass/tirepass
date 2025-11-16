-- 미결제 주문 취소 및 재고 복구 SQL
-- ORD20251111008, ORD20251111009

-- 1. 현재 상태 확인
SELECT
    o.order_number,
    o.customer_name,
    o.order_status,
    o.payment_status,
    o.final_amount,
    COUNT(oi.id) as item_count
FROM tire_data_order o
LEFT JOIN tire_data_orderitem oi ON oi.order_id = o.id
WHERE o.order_number IN ('ORD20251111008', 'ORD20251111009')
GROUP BY o.id;

-- 2. 주문 상품 확인 (재고 복구용)
SELECT
    o.order_number,
    oi.product_code,
    oi.product_name,
    oi.selected_year,
    oi.quantity
FROM tire_data_order o
JOIN tire_data_orderitem oi ON oi.order_id = o.id
WHERE o.order_number IN ('ORD20251111008', 'ORD20251111009');

-- ⚠️ 위 결과를 확인한 후, 재고 복구는 YearAllocation 테이블에서 수동으로 처리해야 합니다.
-- 예: UPDATE tire_data_yearallocation SET year_2025 = year_2025 + 수량
--     WHERE goods_code = '상품코드';

-- 3. Payment 테이블 업데이트 (취소 처리)
UPDATE tire_data_payment p
JOIN tire_data_order o ON p.order_id = o.id
SET
    p.payment_status = 'cancelled',
    p.memo = '등록된 결제 수단 미구현으로 인한 시스템 취소'
WHERE o.order_number IN ('ORD20251111008', 'ORD20251111009');

-- 4. 주문 상태 업데이트 (취소 처리)
UPDATE tire_data_order
SET
    order_status = 'cancelled',
    payment_status = 'cancelled'
WHERE order_number IN ('ORD20251111008', 'ORD20251111009');

-- 5. 최종 확인
SELECT
    order_number,
    order_status,
    payment_status,
    customer_name,
    final_amount
FROM tire_data_order
WHERE order_number IN ('ORD20251111008', 'ORD20251111009');
