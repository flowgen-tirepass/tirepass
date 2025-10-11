-- customers_simple 테이블 구조 확인
DESCRIBE customers_simple;

-- 샘플 데이터 확인
SELECT code, name, enno, password, must_change_password, is_registered
FROM customers_simple
WHERE is_registered = 1
LIMIT 5;
