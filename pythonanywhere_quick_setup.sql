-- ========================================
-- pythonanywhere MySQL 빠른 설정 스크립트
-- ========================================
-- 이 파일을 pythonanywhere Bash Console에서 실행하세요:
-- mysql -u tirepass -p tirepass$itire_db < setup.sql
-- 또는 MySQL 콘솔에서 직접 복사/붙여넣기 하세요
-- ========================================

-- 1. goods_display_names 테이블 생성
CREATE TABLE IF NOT EXISTS goods_display_names (
    goods_code VARCHAR(20) PRIMARY KEY,
    korean_name VARCHAR(200) NOT NULL,
    english_name VARCHAR(200) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. 피렐리 상품 한글/영문명 추가
INSERT INTO goods_display_names (goods_code, korean_name, english_name) VALUES
('P-CP7R-04', '피렐리 친투라토 P7 245/45R18 100Y *MOE RFT', 'Pirelli CINTURATO P7 245/45R18 100Y *MOE RFT'),
('P-SCOR-18', '피렐리 스콜피온 MS 235/55R19 105V XL', 'Pirelli SCORPION MS 235/55R19 105V XL')
ON DUPLICATE KEY UPDATE
    korean_name = VALUES(korean_name),
    english_name = VALUES(english_name);

-- 3. 성능표기 카테고리 테이블 생성
CREATE TABLE IF NOT EXISTS performance_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL COMMENT '카테고리명',
    display_name VARCHAR(50) NOT NULL COMMENT '표시명',
    `order` INT DEFAULT 0 COMMENT '정렬순서',
    is_active TINYINT(1) DEFAULT 1 COMMENT '활성화',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. 성능표기 태그 테이블 생성
CREATE TABLE IF NOT EXISTS performance_tags (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT NOT NULL,
    name VARCHAR(50) NOT NULL COMMENT '태그명',
    `order` INT DEFAULT 0 COMMENT '정렬순서',
    is_active TINYINT(1) DEFAULT 1 COMMENT '활성화',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES performance_categories(id) ON DELETE CASCADE,
    UNIQUE KEY uk_category_tag (category_id, name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. 상품별 성능표기 배정 테이블 생성
CREATE TABLE IF NOT EXISTS goods_performance_tags (
    id INT AUTO_INCREMENT PRIMARY KEY,
    goods_code VARCHAR(20) NOT NULL COMMENT '상품코드',
    tag_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tag_id) REFERENCES performance_tags(id) ON DELETE CASCADE,
    UNIQUE KEY uk_goods_tag (goods_code, tag_id),
    INDEX idx_goods_code (goods_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. 카테고리 데이터 입력 (4개: 승차감, 핸들링, 연비, 소음)
INSERT IGNORE INTO performance_categories (name, display_name, `order`) VALUES
('comfort', '승차감', 1),
('handling', '핸들링', 2),
('fuel', '연비', 3),
('noise', '소음', 4);

-- 7. 승차감 태그 (탁월, 우수, 양호)
INSERT IGNORE INTO performance_tags (category_id, name, `order`) VALUES
((SELECT id FROM performance_categories WHERE name='comfort'), '탁월', 1),
((SELECT id FROM performance_categories WHERE name='comfort'), '우수', 2),
((SELECT id FROM performance_categories WHERE name='comfort'), '양호', 3);

-- 8. 핸들링 태그
INSERT IGNORE INTO performance_tags (category_id, name, `order`) VALUES
((SELECT id FROM performance_categories WHERE name='handling'), '탁월', 1),
((SELECT id FROM performance_categories WHERE name='handling'), '우수', 2),
((SELECT id FROM performance_categories WHERE name='handling'), '양호', 3);

-- 9. 연비 태그
INSERT IGNORE INTO performance_tags (category_id, name, `order`) VALUES
((SELECT id FROM performance_categories WHERE name='fuel'), '탁월', 1),
((SELECT id FROM performance_categories WHERE name='fuel'), '우수', 2),
((SELECT id FROM performance_categories WHERE name='fuel'), '양호', 3);

-- 10. 소음 태그
INSERT IGNORE INTO performance_tags (category_id, name, `order`) VALUES
((SELECT id FROM performance_categories WHERE name='noise'), '탁월', 1),
((SELECT id FROM performance_categories WHERE name='noise'), '우수', 2),
((SELECT id FROM performance_categories WHERE name='noise'), '양호', 3);

-- 11. P-CP7R-04 성능표기 (Cinturato P7 런플랫) - 프리미엄 세단용
INSERT IGNORE INTO goods_performance_tags (goods_code, tag_id) VALUES
('P-CP7R-04', (SELECT pt.id FROM performance_tags pt JOIN performance_categories pc ON pt.category_id=pc.id WHERE pc.name='comfort' AND pt.name='탁월')),
('P-CP7R-04', (SELECT pt.id FROM performance_tags pt JOIN performance_categories pc ON pt.category_id=pc.id WHERE pc.name='handling' AND pt.name='탁월')),
('P-CP7R-04', (SELECT pt.id FROM performance_tags pt JOIN performance_categories pc ON pt.category_id=pc.id WHERE pc.name='fuel' AND pt.name='우수')),
('P-CP7R-04', (SELECT pt.id FROM performance_tags pt JOIN performance_categories pc ON pt.category_id=pc.id WHERE pc.name='noise' AND pt.name='탁월'));

-- 12. P-SCOR-18 성능표기 (Scorpion MS) - SUV용
INSERT IGNORE INTO goods_performance_tags (goods_code, tag_id) VALUES
('P-SCOR-18', (SELECT pt.id FROM performance_tags pt JOIN performance_categories pc ON pt.category_id=pc.id WHERE pc.name='comfort' AND pt.name='우수')),
('P-SCOR-18', (SELECT pt.id FROM performance_tags pt JOIN performance_categories pc ON pt.category_id=pc.id WHERE pc.name='handling' AND pt.name='우수')),
('P-SCOR-18', (SELECT pt.id FROM performance_tags pt JOIN performance_categories pc ON pt.category_id=pc.id WHERE pc.name='fuel' AND pt.name='양호')),
('P-SCOR-18', (SELECT pt.id FROM performance_tags pt JOIN performance_categories pc ON pt.category_id=pc.id WHERE pc.name='noise' AND pt.name='우수'));

-- 13. 확인 쿼리
SELECT '=== 한글/영문명 확인 ===' as '';
SELECT goods_code, korean_name, english_name FROM goods_display_names;

SELECT '=== 성능표기 확인 ===' as '';
SELECT
    gpt.goods_code as '상품코드',
    pc.display_name as '카테고리',
    pt.name as '태그'
FROM goods_performance_tags gpt
JOIN performance_tags pt ON gpt.tag_id = pt.id
JOIN performance_categories pc ON pt.category_id = pc.id
ORDER BY gpt.goods_code, pc.`order`;
