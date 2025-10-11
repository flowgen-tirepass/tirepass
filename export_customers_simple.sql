-- 로컬 DB에서 customers_simple 데이터 덤프
-- 실행: mysql -uroot -ptirepass itire_db < export_customers_simple.sql > customers_simple_data.sql

-- UTF-8 설정
SET NAMES utf8mb4;

-- customers_simple 데이터 덤프 (INSERT 문만)
SELECT CONCAT(
    'INSERT INTO customers_simple (code, name, rep, tel1, tel3, enno, password, is_registered, user_id, must_change_password) VALUES (',
    QUOTE(code), ', ',
    QUOTE(IFNULL(name, '')), ', ',
    QUOTE(IFNULL(rep, '')), ', ',
    QUOTE(IFNULL(tel1, '')), ', ',
    QUOTE(IFNULL(tel3, '')), ', ',
    QUOTE(IFNULL(enno, '')), ', ',
    QUOTE(IFNULL(password, '')), ', ',
    IF(is_registered, '1', '0'), ', ',
    IFNULL(user_id, 'NULL'), ', ',
    IF(must_change_password, '1', '0'),
    ');'
) AS sql_statement
FROM customers_simple
WHERE is_registered = 1
ORDER BY code;
