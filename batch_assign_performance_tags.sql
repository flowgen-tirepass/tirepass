-- ========================================
-- 모든 타이어 상품에 브랜드별 성능표기 일괄 등록
-- ========================================
-- pythonanywhere Bash Console에서 실행:
-- mysql -u tirepass -p tirepass$itire_db < batch_assign_performance_tags.sql
-- ========================================

-- 기존 성능표기 모두 삭제 (재실행 시)
-- DELETE FROM goods_performance_tags;

-- ========================================
-- 1. 프리미엄 브랜드 (승차감:탁월, 핸들링:탁월, 연비:우수, 소음:탁월)
-- 미쉐린, 피렐리, 콘티넨탈
-- ========================================

-- 1-1. 미쉐린 (1,702개)
INSERT IGNORE INTO goods_performance_tags (goods_code, tag_id)
SELECT
    g.CODE,
    pt.id
FROM goods g
CROSS JOIN (
    SELECT pt.id, pc.name as category, pt.name as tag_name
    FROM performance_tags pt
    JOIN performance_categories pc ON pt.category_id = pc.id
    WHERE (pc.name = 'comfort' AND pt.name = '탁월')
       OR (pc.name = 'handling' AND pt.name = '탁월')
       OR (pc.name = 'fuel' AND pt.name = '우수')
       OR (pc.name = 'noise' AND pt.name = '탁월')
) pt
WHERE g.is_tire = 1
  AND g.brand = '미쉐린';

-- 1-2. 피렐리 (287개)
INSERT IGNORE INTO goods_performance_tags (goods_code, tag_id)
SELECT
    g.CODE,
    pt.id
FROM goods g
CROSS JOIN (
    SELECT pt.id, pc.name as category, pt.name as tag_name
    FROM performance_tags pt
    JOIN performance_categories pc ON pt.category_id = pc.id
    WHERE (pc.name = 'comfort' AND pt.name = '탁월')
       OR (pc.name = 'handling' AND pt.name = '탁월')
       OR (pc.name = 'fuel' AND pt.name = '우수')
       OR (pc.name = 'noise' AND pt.name = '탁월')
) pt
WHERE g.is_tire = 1
  AND g.brand = '피렐리';

-- 1-3. 콘티넨탈 (213개)
INSERT IGNORE INTO goods_performance_tags (goods_code, tag_id)
SELECT
    g.CODE,
    pt.id
FROM goods g
CROSS JOIN (
    SELECT pt.id, pc.name as category, pt.name as tag_name
    FROM performance_tags pt
    JOIN performance_categories pc ON pt.category_id = pc.id
    WHERE (pc.name = 'comfort' AND pt.name = '탁월')
       OR (pc.name = 'handling' AND pt.name = '탁월')
       OR (pc.name = 'fuel' AND pt.name = '우수')
       OR (pc.name = 'noise' AND pt.name = '탁월')
) pt
WHERE g.is_tire = 1
  AND g.brand = '콘티넨탈';

-- ========================================
-- 2. 중상급 브랜드 (승차감:우수, 핸들링:우수, 연비:우수, 소음:우수)
-- 브리지스톤, 던롭, 굳이어
-- ========================================

-- 2-1. 브리지스톤 (123개)
INSERT IGNORE INTO goods_performance_tags (goods_code, tag_id)
SELECT
    g.CODE,
    pt.id
FROM goods g
CROSS JOIN (
    SELECT pt.id, pc.name as category, pt.name as tag_name
    FROM performance_tags pt
    JOIN performance_categories pc ON pt.category_id = pc.id
    WHERE (pc.name = 'comfort' AND pt.name = '우수')
       OR (pc.name = 'handling' AND pt.name = '우수')
       OR (pc.name = 'fuel' AND pt.name = '우수')
       OR (pc.name = 'noise' AND pt.name = '우수')
) pt
WHERE g.is_tire = 1
  AND g.brand = '브리지스톤';

-- 2-2. 던롭 (66개)
INSERT IGNORE INTO goods_performance_tags (goods_code, tag_id)
SELECT
    g.CODE,
    pt.id
FROM goods g
CROSS JOIN (
    SELECT pt.id, pc.name as category, pt.name as tag_name
    FROM performance_tags pt
    JOIN performance_categories pc ON pt.category_id = pc.id
    WHERE (pc.name = 'comfort' AND pt.name = '우수')
       OR (pc.name = 'handling' AND pt.name = '우수')
       OR (pc.name = 'fuel' AND pt.name = '우수')
       OR (pc.name = 'noise' AND pt.name = '우수')
) pt
WHERE g.is_tire = 1
  AND g.brand = '던롭';

-- 2-3. 굳이어 (114개)
INSERT IGNORE INTO goods_performance_tags (goods_code, tag_id)
SELECT
    g.CODE,
    pt.id
FROM goods g
CROSS JOIN (
    SELECT pt.id, pc.name as category, pt.name as tag_name
    FROM performance_tags pt
    JOIN performance_categories pc ON pt.category_id = pc.id
    WHERE (pc.name = 'comfort' AND pt.name = '우수')
       OR (pc.name = 'handling' AND pt.name = '우수')
       OR (pc.name = 'fuel' AND pt.name = '우수')
       OR (pc.name = 'noise' AND pt.name = '우수')
) pt
WHERE g.is_tire = 1
  AND g.brand = '굳이어';

-- ========================================
-- 3. 경제형 브랜드 (승차감:우수, 핸들링:양호, 연비:탁월, 소음:우수)
-- 금호, 넥센, 한국
-- ========================================

-- 3-1. 금호 (1,739개)
INSERT IGNORE INTO goods_performance_tags (goods_code, tag_id)
SELECT
    g.CODE,
    pt.id
FROM goods g
CROSS JOIN (
    SELECT pt.id, pc.name as category, pt.name as tag_name
    FROM performance_tags pt
    JOIN performance_categories pc ON pt.category_id = pc.id
    WHERE (pc.name = 'comfort' AND pt.name = '우수')
       OR (pc.name = 'handling' AND pt.name = '양호')
       OR (pc.name = 'fuel' AND pt.name = '탁월')
       OR (pc.name = 'noise' AND pt.name = '우수')
) pt
WHERE g.is_tire = 1
  AND g.brand = '금호';

-- 3-2. 넥센 (810개)
INSERT IGNORE INTO goods_performance_tags (goods_code, tag_id)
SELECT
    g.CODE,
    pt.id
FROM goods g
CROSS JOIN (
    SELECT pt.id, pc.name as category, pt.name as tag_name
    FROM performance_tags pt
    JOIN performance_categories pc ON pt.category_id = pc.id
    WHERE (pc.name = 'comfort' AND pt.name = '우수')
       OR (pc.name = 'handling' AND pt.name = '양호')
       OR (pc.name = 'fuel' AND pt.name = '탁월')
       OR (pc.name = 'noise' AND pt.name = '우수')
) pt
WHERE g.is_tire = 1
  AND g.brand = '넥센';

-- 3-3. 한국 (746개)
INSERT IGNORE INTO goods_performance_tags (goods_code, tag_id)
SELECT
    g.CODE,
    pt.id
FROM goods g
CROSS JOIN (
    SELECT pt.id, pc.name as category, pt.name as tag_name
    FROM performance_tags pt
    JOIN performance_categories pc ON pt.category_id = pc.id
    WHERE (pc.name = 'comfort' AND pt.name = '우수')
       OR (pc.name = 'handling' AND pt.name = '양호')
       OR (pc.name = 'fuel' AND pt.name = '탁월')
       OR (pc.name = 'noise' AND pt.name = '우수')
) pt
WHERE g.is_tire = 1
  AND g.brand = '한국';

-- ========================================
-- 4. 기타 브랜드 (승차감:양호, 핸들링:양호, 연비:우수, 소음:양호)
-- 하이로, BFG, 안나이트, 맥시스, 하이플라이, 파이어스톤
-- ========================================

INSERT IGNORE INTO goods_performance_tags (goods_code, tag_id)
SELECT
    g.CODE,
    pt.id
FROM goods g
CROSS JOIN (
    SELECT pt.id, pc.name as category, pt.name as tag_name
    FROM performance_tags pt
    JOIN performance_categories pc ON pt.category_id = pc.id
    WHERE (pc.name = 'comfort' AND pt.name = '양호')
       OR (pc.name = 'handling' AND pt.name = '양호')
       OR (pc.name = 'fuel' AND pt.name = '우수')
       OR (pc.name = 'noise' AND pt.name = '양호')
) pt
WHERE g.is_tire = 1
  AND g.brand IN ('하이로', 'BFG', '안나이트', '맥시스', '하이플라이', '파이어스톤');

-- ========================================
-- 5. 확인 쿼리
-- ========================================

-- 5-1. 브랜드별 성능표기 등록 현황
SELECT '=== 브랜드별 성능표기 등록 현황 ===' as '';
SELECT
    g.brand as '브랜드',
    COUNT(DISTINCT g.CODE) as '전체상품수',
    COUNT(DISTINCT gpt.goods_code) as '성능표기등록수',
    ROUND(COUNT(DISTINCT gpt.goods_code) / COUNT(DISTINCT g.CODE) * 100, 1) as '등록율(%)'
FROM goods g
LEFT JOIN goods_performance_tags gpt ON g.CODE = gpt.goods_code
WHERE g.is_tire = 1
GROUP BY g.brand
ORDER BY COUNT(DISTINCT g.CODE) DESC;

-- 5-2. 총 등록 현황
SELECT '=== 전체 등록 현황 ===' as '';
SELECT
    COUNT(DISTINCT goods_code) as '성능표기가있는상품수',
    COUNT(*) as '총성능표기개수'
FROM goods_performance_tags;

-- 5-3. 샘플 확인 (각 브랜드별 1개씩)
SELECT '=== 샘플 확인 (각 브랜드별 1개) ===' as '';
SELECT
    g.CODE as '상품코드',
    g.NAME as '상품명',
    g.brand as '브랜드',
    GROUP_CONCAT(CONCAT(pc.display_name, ':', pt.name) ORDER BY pc.`order` SEPARATOR ' | ') as '성능표기'
FROM goods g
JOIN goods_performance_tags gpt ON g.CODE = gpt.goods_code
JOIN performance_tags pt ON gpt.tag_id = pt.id
JOIN performance_categories pc ON pt.category_id = pc.id
WHERE g.is_tire = 1
GROUP BY g.CODE, g.NAME, g.brand
HAVING COUNT(gpt.id) = 4
ORDER BY g.brand, g.CODE
LIMIT 10;
