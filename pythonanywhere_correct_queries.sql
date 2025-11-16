-- ================================================================================
-- PythonAnywhere MySQL 콘솔 - 올바른 테이블 이름으로 수정된 쿼리
-- ================================================================================

-- 테이블 이름:
-- orders (tire_data_order가 아님)
-- payments (tire_data_payment가 아님)
-- order_items (tire_data_orderitem가 아님)
-- payment_methods (tire_data_paymentmethod가 아님)
-- customers (tire_data_customers가 아님)

-- ================================================================================
-- 쿼리 1: 승인번호 47705227 찾기 ⭐⭐⭐ 가장 중요
-- ================================================================================
SELECT
    p.id as payment_id,
    p.payment_status,
    p.payment_amount,
    p.payment_date,
    p.payment_method,
    p.payment_key,
    p.transaction_id,
    o.order_number,
    o.customer_name,
    o.customer_code,
    o.order_date
FROM payments p
LEFT JOIN orders o ON p.order_id = o.id
WHERE p.transaction_id LIKE '%47705227%'
   OR p.payment_key LIKE '%47705227%'
   OR p.raw_response LIKE '%47705227%';


-- ================================================================================
-- 쿼리 2: Raw Response 상세 보기 (승인번호가 있으면)
-- ================================================================================
SELECT
    p.id,
    o.order_number,
    p.payment_key,
    LEFT(p.raw_response, 2000) as raw_response_preview
FROM payments p
LEFT JOIN orders o ON p.order_id = o.id
WHERE p.raw_response LIKE '%47705227%';


-- ================================================================================
-- 쿼리 3: 10월 31일 전체 주문 및 결제
-- ================================================================================
SELECT
    o.order_number,
    o.customer_name,
    o.customer_code,
    o.order_date,
    o.order_status,
    o.payment_status as order_payment_status,
    o.payment_method,
    o.final_amount,
    p.id as payment_id,
    p.payment_status as payment_record_status,
    p.payment_key,
    p.transaction_id,
    CASE
        WHEN p.raw_response LIKE '%approveNo%' THEN 'Has approveNo'
        ELSE 'No approveNo'
    END as has_approve_no
FROM orders o
LEFT JOIN payments p ON p.order_id = o.id
WHERE DATE(o.order_date) = '2024-10-31'
ORDER BY o.order_date DESC;


-- ================================================================================
-- 쿼리 4: 11월 11일 광주 업체 미결제 주문 ⭐⭐⭐ 매우 중요
-- ================================================================================
SELECT
    o.id,
    o.order_number,
    o.customer_name,
    o.customer_code,
    o.order_date,
    o.order_status,
    o.payment_status as order_payment_status,
    o.payment_method,
    o.final_amount,
    o.order_source,
    p.id as payment_id,
    p.payment_status as payment_record_status,
    p.payment_key,
    p.memo
FROM orders o
LEFT JOIN payments p ON p.order_id = o.id
WHERE o.order_number IN ('ORD20251111008', 'ORD20251111009')
ORDER BY o.order_date DESC;


-- ================================================================================
-- 쿼리 5: 11월 11일 전체 미결제 주문
-- ================================================================================
SELECT
    o.order_number,
    o.customer_name,
    o.customer_code,
    o.order_date,
    o.order_status,
    o.payment_status,
    o.payment_method,
    o.final_amount,
    CASE
        WHEN EXISTS (SELECT 1 FROM payments p WHERE p.order_id = o.id)
        THEN 'Payment 있음'
        ELSE 'Payment 없음'
    END as has_payment
FROM orders o
WHERE DATE(o.order_date) = '2024-11-11'
  AND o.payment_status = 'unpaid'
ORDER BY o.order_date DESC;


-- ================================================================================
-- 쿼리 6: 등록된 결제 수단 확인
-- ================================================================================
SELECT
    pm.id,
    pm.customer_code,
    c.name as customer_name,
    pm.payment_type,
    pm.billing_key,
    pm.masked_info,
    pm.is_default,
    pm.created_at
FROM payment_methods pm
LEFT JOIN customers c ON pm.customer_code = c.code
WHERE pm.is_active = 1
ORDER BY pm.created_at DESC
LIMIT 20;


-- ================================================================================
-- 쿼리 7: 10월 전체 결제 통계
-- ================================================================================
SELECT
    COUNT(*) as total_payments,
    SUM(payment_amount) as total_amount,
    payment_status,
    payment_method
FROM payments
WHERE YEAR(payment_date) = 2024
  AND MONTH(payment_date) = 10
GROUP BY payment_status, payment_method
ORDER BY payment_status, payment_method;


-- ================================================================================
-- 쿼리 8: 광주 업체 주문 상세 (order_items 포함)
-- ================================================================================
SELECT
    o.order_number,
    o.customer_name,
    oi.product_code,
    oi.product_name,
    oi.quantity,
    oi.final_price,
    oi.selected_year
FROM orders o
JOIN order_items oi ON oi.order_id = o.id
WHERE o.order_number IN ('ORD20251111008', 'ORD20251111009')
ORDER BY o.order_number, oi.id;
