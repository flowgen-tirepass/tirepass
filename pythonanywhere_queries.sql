-- ================================================================================
-- PythonAnywhere MySQL 콘솔에서 실행할 쿼리
-- ================================================================================

-- 1. 승인번호 47705227 찾기 (10월 31일 결제)
SELECT
    '=== 승인번호 47705227 검색 ===' as info;

SELECT
    p.id as payment_id,
    p.payment_status,
    p.payment_amount,
    p.payment_date,
    p.payment_method,
    p.payment_key,
    p.transaction_id,
    p.pg_name,
    o.order_number,
    o.customer_name,
    o.customer_code,
    o.order_date,
    o.order_status
FROM tire_data_payment p
LEFT JOIN tire_data_order o ON p.order_id = o.id
WHERE p.transaction_id LIKE '%47705227%'
   OR p.payment_key LIKE '%47705227%'
   OR p.raw_response LIKE '%47705227%'
   OR p.memo LIKE '%47705227%';

-- 2. 승인번호가 포함된 raw_response 상세 보기
SELECT
    '=== Raw Response 상세 (승인번호 47705227) ===' as info;

SELECT
    p.id,
    o.order_number,
    p.payment_key,
    p.raw_response
FROM tire_data_payment p
LEFT JOIN tire_data_order o ON p.order_id = o.id
WHERE p.raw_response LIKE '%47705227%';

-- 3. 10월 31일 전체 주문 및 결제 내역
SELECT
    '=== 2024-10-31 전체 주문 ===' as info;

SELECT
    o.order_number,
    o.customer_name,
    o.customer_code,
    o.order_date,
    o.order_status,
    o.payment_status,
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
FROM tire_data_order o
LEFT JOIN tire_data_payment p ON p.order_id = o.id
WHERE DATE(o.order_date) = '2024-10-31'
ORDER BY o.order_date DESC;

-- 4. 11월 11일 광주 업체 미결제 주문 (ORD20251111008, ORD20251111009)
SELECT
    '=== 2024-11-11 미결제 주문 (광주 업체) ===' as info;

SELECT
    o.id,
    o.order_number,
    o.customer_name,
    o.customer_code,
    o.order_date,
    o.order_status,
    o.payment_status,
    o.payment_method,
    o.final_amount,
    p.id as payment_id,
    p.payment_status as payment_record_status,
    p.payment_key,
    p.memo
FROM tire_data_order o
LEFT JOIN tire_data_payment p ON p.order_id = o.id
WHERE o.order_number IN ('ORD20251111008', 'ORD20251111009')
ORDER BY o.order_date DESC;

-- 5. 11월 11일 전체 미결제 주문
SELECT
    '=== 2024-11-11 전체 미결제 주문 ===' as info;

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
        WHEN EXISTS (SELECT 1 FROM tire_data_payment p WHERE p.order_id = o.id)
        THEN 'Payment 있음'
        ELSE 'Payment 없음'
    END as has_payment
FROM tire_data_order o
WHERE DATE(o.order_date) = '2024-11-11'
  AND o.payment_status = 'unpaid'
ORDER BY o.order_date DESC;

-- 6. 10월 전체 결제 통계
SELECT
    '=== 2024년 10월 결제 통계 ===' as info;

SELECT
    COUNT(*) as total_payments,
    SUM(payment_amount) as total_amount,
    payment_status,
    payment_method
FROM tire_data_payment
WHERE YEAR(payment_date) = 2024
  AND MONTH(payment_date) = 10
GROUP BY payment_status, payment_method
ORDER BY payment_status, payment_method;

-- 7. PaymentMethod 테이블 확인 (등록된 결제 수단)
SELECT
    '=== 등록된 결제 수단 (PaymentMethod) ===' as info;

SELECT
    pm.id,
    pm.customer_code,
    c.name as customer_name,
    pm.payment_type,
    pm.billing_key,
    pm.masked_info,
    pm.is_default,
    pm.created_at
FROM tire_data_paymentmethod pm
LEFT JOIN tire_data_customers c ON pm.customer_code = c.code
WHERE pm.is_active = 1
ORDER BY pm.created_at DESC
LIMIT 20;
