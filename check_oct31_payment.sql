-- 10월 31일 결제 기록 조회
-- 승인번호: 47705227

-- 1. Payment 테이블에서 승인번호로 검색
SELECT
    p.*,
    o.order_number,
    o.customer_name,
    o.order_date,
    o.order_status,
    o.payment_status
FROM tire_data_payment p
LEFT JOIN tire_data_order o ON p.order_id = o.id
WHERE p.transaction_id LIKE '%47705227%'
   OR p.payment_key LIKE '%47705227%'
   OR p.raw_response LIKE '%47705227%'
   OR p.memo LIKE '%47705227%';

-- 2. 10월 31일 전체 결제 내역 (혹시 승인번호가 다른 필드에 있을 경우)
SELECT
    p.id,
    p.payment_key,
    p.transaction_id,
    p.payment_status,
    p.payment_amount,
    p.payment_date,
    p.pg_name,
    p.memo,
    o.order_number,
    o.customer_name,
    o.order_date
FROM tire_data_payment p
LEFT JOIN tire_data_order o ON p.order_id = o.id
WHERE DATE(p.payment_date) = '2024-10-31'
   OR DATE(o.order_date) = '2024-10-31'
ORDER BY p.payment_date DESC;

-- 3. 10월 31일 주문 전체 (결제 없는 것도 포함)
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
    COUNT(p.id) as payment_count
FROM tire_data_order o
LEFT JOIN tire_data_payment p ON p.order_id = o.id
WHERE DATE(o.order_date) = '2024-10-31'
GROUP BY o.id
ORDER BY o.order_date DESC;

-- 4. raw_response에서 승인번호 검색 (JSON 안에 있을 수 있음)
SELECT
    p.id,
    p.payment_key,
    p.payment_status,
    p.payment_amount,
    p.payment_date,
    o.order_number,
    p.raw_response
FROM tire_data_payment p
LEFT JOIN tire_data_order o ON p.order_id = o.id
WHERE p.raw_response IS NOT NULL
  AND p.raw_response LIKE '%47705227%';
