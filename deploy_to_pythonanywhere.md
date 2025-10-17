# pythonanywhere 배포 가이드

## 1단계: MySQL 데이터베이스 설정

### Bash Console 접속
```bash
mysql -u tirepass -p tirepass$itire_db
```

### 1.1 goods_display_names 테이블 생성 및 데이터 추가
```sql
-- 테이블 생성
CREATE TABLE IF NOT EXISTS goods_display_names (
    goods_code VARCHAR(20) PRIMARY KEY,
    korean_name VARCHAR(200) NOT NULL,
    english_name VARCHAR(200) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 피렐리 상품 한글/영문명 추가
INSERT INTO goods_display_names (goods_code, korean_name, english_name) VALUES
('P-CP7R-04', '피렐리 친투라토 P7 245/45R18 100Y *MOE RFT', 'Pirelli CINTURATO P7 245/45R18 100Y *MOE RFT'),
('P-SCOR-18', '피렐리 스콜피온 MS 235/55R19 105V XL', 'Pirelli SCORPION MS 235/55R19 105V XL')
ON DUPLICATE KEY UPDATE
    korean_name = VALUES(korean_name),
    english_name = VALUES(english_name);
```

### 1.2 성능표기 시스템 테이블 생성
```sql
-- 성능표기 카테고리 테이블
CREATE TABLE IF NOT EXISTS performance_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL COMMENT '카테고리명',
    display_name VARCHAR(50) NOT NULL COMMENT '표시명',
    `order` INT DEFAULT 0 COMMENT '정렬순서',
    is_active TINYINT(1) DEFAULT 1 COMMENT '활성화',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 성능표기 태그 테이블
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

-- 상품별 성능표기 배정 테이블
CREATE TABLE IF NOT EXISTS goods_performance_tags (
    id INT AUTO_INCREMENT PRIMARY KEY,
    goods_code VARCHAR(20) NOT NULL COMMENT '상품코드',
    tag_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tag_id) REFERENCES performance_tags(id) ON DELETE CASCADE,
    UNIQUE KEY uk_goods_tag (goods_code, tag_id),
    INDEX idx_goods_code (goods_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 1.3 성능표기 카테고리 및 태그 데이터 추가
```sql
-- 기존 데이터 삭제 (재실행 시)
DELETE FROM goods_performance_tags;
DELETE FROM performance_tags;
DELETE FROM performance_categories;

-- 카테고리 생성 (4개: 승차감, 핸들링, 연비, 소음)
INSERT INTO performance_categories (name, display_name, `order`) VALUES
('comfort', '승차감', 1),
('handling', '핸들링', 2),
('fuel', '연비', 3),
('noise', '소음', 4);

-- 승차감 태그 (탁월, 우수, 양호)
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
```

### 1.4 피렐리 상품 성능표기 추가
```sql
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
```

### 1.5 데이터 확인
```sql
-- 성능표기 확인
SELECT
    gpt.goods_code as '상품코드',
    pc.display_name as '카테고리',
    pt.name as '태그'
FROM goods_performance_tags gpt
JOIN performance_tags pt ON gpt.tag_id = pt.id
JOIN performance_categories pc ON pt.category_id = pc.id
ORDER BY gpt.goods_code, pc.`order`;

-- 한글/영문명 확인
SELECT * FROM goods_display_names WHERE goods_code IN ('P-CP7R-04', 'P-SCOR-18');
```

예상 결과:
```
+----------+----------+------+
| 상품코드  | 카테고리  | 태그  |
+----------+----------+------+
| P-CP7R-04| 승차감    | 탁월  |
| P-CP7R-04| 핸들링    | 탁월  |
| P-CP7R-04| 연비      | 우수  |
| P-CP7R-04| 소음      | 탁월  |
| P-SCOR-18| 승차감    | 우수  |
| P-SCOR-18| 핸들링    | 우수  |
| P-SCOR-18| 연비      | 양호  |
| P-SCOR-18| 소음      | 우수  |
+----------+----------+------+
```

## 2단계: 코드 배포

### Bash Console에서
```bash
cd ~/tirepass
git pull origin main
```

## 3단계: 웹앱 Reload

https://www.pythonanywhere.com/user/tirepass/webapps/
→ **Reload tirepass.pythonanywhere.com** 버튼 클릭

## 4단계: 확인

### 모바일 화면 확인
https://tirepass.pythonanywhere.com/mobile/products/?search=pirelli

확인사항:
1. ✅ P-CP7R-04: 성능표기 4개 (승차감:탁월, 핸들링:탁월, 연비:우수, 소음:탁월) 2x2 그리드 표시
2. ✅ P-SCOR-18: 성능표기 4개 (승차감:우수, 핸들링:우수, 연비:양호, 소음:우수) 2x2 그리드 표시
3. ✅ 한글명 + 영문명 정상 표시
4. ✅ 가격 정보 (공장도가, 할인율, 공급가) 정상 표시

### Admin 확인
- 성능표기 카테고리: https://tirepass.pythonanywhere.com/admin/tire_data/performancecategory/
- 성능표기 태그: https://tirepass.pythonanywhere.com/admin/tire_data/performancetag/
- 상품 성능표기: https://tirepass.pythonanywhere.com/admin/tire_data/goodsperformancetag/
- 상품 표시명: https://tirepass.pythonanywhere.com/admin/tire_data/goodsdisplayname/

## 5단계: 추가 상품 성능표기 등록 방법

### Admin에서 직접 등록
1. https://tirepass.pythonanywhere.com/admin/tire_data/goodsperformancetag/
2. "상품 성능표기 추가+" 클릭
3. 상품코드 입력 (예: K-ENZA-01)
4. 성능표기 선택 (예: 승차감 - 탁월)
5. 저장
6. 같은 상품에 4개의 성능표기 추가 반복

### MySQL로 일괄 등록
```sql
-- 예: 금호 엔자라 상품 등록
INSERT INTO goods_performance_tags (goods_code, tag_id) VALUES
('K-ENZA-01', (SELECT pt.id FROM performance_tags pt JOIN performance_categories pc ON pt.category_id=pc.id WHERE pc.name='comfort' AND pt.name='우수')),
('K-ENZA-01', (SELECT pt.id FROM performance_tags pt JOIN performance_categories pc ON pt.category_id=pc.id WHERE pc.name='handling' AND pt.name='양호')),
('K-ENZA-01', (SELECT pt.id FROM performance_tags pt JOIN performance_categories pc ON pt.category_id=pc.id WHERE pc.name='fuel' AND pt.name='탁월')),
('K-ENZA-01', (SELECT pt.id FROM performance_tags pt JOIN performance_categories pc ON pt.category_id=pc.id WHERE pc.name='noise' AND pt.name='우수'));
```

## 브랜드별 추천 성능표기

### 프리미엄 세단용 (예: 피렐리 Cinturato, 미쉐린 Primacy)
- 승차감: 탁월 | 핸들링: 탁월 | 연비: 우수 | 소음: 탁월

### SUV용 (예: 피렐리 Scorpion, 미쉐린 Latitude)
- 승차감: 우수 | 핸들링: 우수 | 연비: 양호 | 소음: 우수

### 경제형 (예: 금호 엔자라, 넥센 엔페라)
- 승차감: 우수 | 핸들링: 양호 | 연비: 탁월 | 소음: 우수

### 고성능 (예: 미쉐린 PS4, 피렐리 P Zero)
- 승차감: 우수 | 핸들링: 탁월 | 연비: 양호 | 소음: 우수

## 완료!

모든 단계 완료 후:
- ✅ 모바일 상품 카드에 성능표기 4개 2x2 그리드 표시
- ✅ 한글명/영문명 정상 표시
- ✅ Admin에서 성능표기 관리 가능
- ✅ 브랜드별, 상품별 맞춤 성능표기
