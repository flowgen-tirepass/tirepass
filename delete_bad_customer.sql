-- PythonAnywhere MySQL에서 실행할 쿼리

-- 1단계: 잘못된 고객 레코드 확인
SELECT
    id,
    code,
    name,
    rep,
    enno,
    tel1,
    password
FROM tire_data_customers
WHERE name LIKE '%정확한%'
   OR (code = '4108305068' AND name LIKE '%정확한%');

-- 2단계: 삭제 (위 쿼리 확인 후 실행)
-- DELETE FROM tire_data_customers
-- WHERE code = '4108305068' AND name LIKE '%정확한%';

-- 3단계: 올바른 레코드 확인
SELECT
    id,
    code,
    name,
    rep,
    enno,
    tel1
FROM tire_data_customers
WHERE enno LIKE '%410%83%05068%'
   OR code = '0-1-0003';
