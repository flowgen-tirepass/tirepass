-- ========================================
-- 성능표기 시스템 완전 초기화 및 설정
-- ========================================

-- 1. 기존 데이터 삭제
DELETE FROM goods_performance_tags;
DELETE FROM performance_tags;
DELETE FROM performance_categories;

-- 2. 테이블 생성 (없으면)
CREATE TABLE IF NOT EXISTS performance_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL COMMENT '카테고리명',
    display_name VARCHAR(50) NOT NULL COMMENT '표시명',
    `order` INT DEFAULT 0 COMMENT '정렬순서',
    is_active TINYINT(1) DEFAULT 1 COMMENT '활성화',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

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

CREATE TABLE IF NOT EXISTS goods_performance_tags (
    id INT AUTO_INCREMENT PRIMARY KEY,
    goods_code VARCHAR(20) NOT NULL COMMENT '상품코드',
    tag_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tag_id) REFERENCES performance_tags(id) ON DELETE CASCADE,
    UNIQUE KEY uk_goods_tag (goods_code, tag_id),
    INDEX idx_goods_code (goods_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. 카테고리 생성 (4개만: 2x2 그리드용)
INSERT INTO performance_categories (name, display_name, `order`) VALUES
('comfort', '승차감', 1),
('handling', '핸들링', 2),
('fuel', '연비', 3),
('noise', '소음', 4);

-- 4. 태그 생성 (각 카테고리당 3개 수준)
-- 승차감 태그
INSERT INTO performance_tags (category_id, name, `order`) VALUES
((SELECT id FROM performance_categories WHERE name='comfort'), '탁월', 1),
((SELECT id FROM performance_categories WHERE name='comfort'), '우수', 2),
((SELECT id FROM performance_categories WHERE name='comfort'), '양호', 3);

-- 핸들링 태그
INSERT INTO performance_tags (category_id, name, `order`) VALUES
((SELECT id FROM performance_categories WHERE name='handling'), '탁월', 1),
((SELECT id FROM performance_categories WHERE name='handling'), '우수', 2),
((SELECT id FROM performance_categories WHERE name='handling'), '양호', 3);

-- 연비 태그
INSERT INTO performance_tags (category_id, name, `order`) VALUES
((SELECT id FROM performance_categories WHERE name='fuel'), '탁월', 1),
((SELECT id FROM performance_categories WHERE name='fuel'), '우수', 2),
((SELECT id FROM performance_categories WHERE name='fuel'), '양호', 3);

-- 소음 태그
INSERT INTO performance_tags (category_id, name, `order`) VALUES
((SELECT id FROM performance_categories WHERE name='noise'), '탁월', 1),
((SELECT id FROM performance_categories WHERE name='noise'), '우수', 2),
((SELECT id FROM performance_categories WHERE name='noise'), '양호', 3);

-- 5. 피렐리 상품 성능표기 (P-CP7R-04, P-SCOR-18)
-- P-CP7R-04 (Cinturato P7 런플랫) - 프리미엄 세단용
INSERT INTO goods_performance_tags (goods_code, tag_id) VALUES
('P-CP7R-04', (SELECT pt.id FROM performance_tags pt JOIN performance_categories pc ON pt.category_id=pc.id WHERE pc.name='comfort' AND pt.name='탁월')),
('P-CP7R-04', (SELECT pt.id FROM performance_tags pt JOIN performance_categories pc ON pt.category_id=pc.id WHERE pc.name='handling' AND pt.name='탁월')),
('P-CP7R-04', (SELECT pt.id FROM performance_tags pt JOIN performance_categories pc ON pt.category_id=pc.id WHERE pc.name='fuel' AND pt.name='우수')),
('P-CP7R-04', (SELECT pt.id FROM performance_tags pt JOIN performance_categories pc ON pt.category_id=pc.id WHERE pc.name='noise' AND pt.name='탁월'));

-- P-SCOR-18 (Scorpion MS) - SUV용
INSERT INTO goods_performance_tags (goods_code, tag_id) VALUES
('P-SCOR-18', (SELECT pt.id FROM performance_tags pt JOIN performance_categories pc ON pt.category_id=pc.id WHERE pc.name='comfort' AND pt.name='우수')),
('P-SCOR-18', (SELECT pt.id FROM performance_tags pt JOIN performance_categories pc ON pt.category_id=pc.id WHERE pc.name='handling' AND pt.name='우수')),
('P-SCOR-18', (SELECT pt.id FROM performance_tags pt JOIN performance_categories pc ON pt.category_id=pc.id WHERE pc.name='fuel' AND pt.name='양호')),
('P-SCOR-18', (SELECT pt.id FROM performance_tags pt JOIN performance_categories pc ON pt.category_id=pc.id WHERE pc.name='noise' AND pt.name='우수'));

-- 6. 확인 쿼리
SELECT
    gpt.goods_code as '상품코드',
    pc.display_name as '카테고리',
    pt.name as '태그',
    gpt.created_at as '생성일시'
FROM goods_performance_tags gpt
JOIN performance_tags pt ON gpt.tag_id = pt.id
JOIN performance_categories pc ON pt.category_id = pc.id
ORDER BY gpt.goods_code, pc.`order`;
