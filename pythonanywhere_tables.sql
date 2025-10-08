-- ============================================
-- PythonAnywhere MySQL 테이블 생성 스크립트
-- ============================================
-- 작성일: 2025-10-08
-- 용도: Django 관리 테이블들을 pythonanywhere MySQL에 생성
-- 주의: goods, customers_simple 테이블은 ERP 서버 트리거가 생성/관리함
-- ============================================

-- 데이터베이스 선택 (pythonanywhere에서 실행 시 DB명 변경 필요)
-- USE yourusername$itire_db;

-- ============================================
-- 1. 쇼핑/주문 관련 테이블
-- ============================================

-- 1.1 장바구니 테이블
CREATE TABLE IF NOT EXISTS shopping_cart (
  id BIGINT NOT NULL AUTO_INCREMENT,
  customer_code VARCHAR(10) NOT NULL COMMENT '고객 코드',
  product_code VARCHAR(20) NOT NULL COMMENT '상품 코드',
  quantity INT DEFAULT 1 COMMENT '수량',
  selected_year INT DEFAULT NULL COMMENT '선택 제조년도(DOT)',
  unit_price BIGINT NOT NULL COMMENT '단가',
  discount_rate DECIMAL(5,2) DEFAULT 0.00 COMMENT '적용 할인율(%)',
  final_price BIGINT NOT NULL COMMENT '최종가격',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '생성일시',
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '수정일시',
  PRIMARY KEY (id),
  UNIQUE KEY unique_cart_item (customer_code, product_code, selected_year)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 1.2 주문 테이블
CREATE TABLE IF NOT EXISTS orders (
  id BIGINT NOT NULL AUTO_INCREMENT,
  order_number VARCHAR(50) NOT NULL COMMENT '주문번호',
  customer_code VARCHAR(10) NOT NULL COMMENT '고객 코드',
  customer_name VARCHAR(50) DEFAULT NULL COMMENT '고객명',
  total_amount BIGINT DEFAULT 0 COMMENT '총 주문금액',
  total_discount BIGINT DEFAULT 0 COMMENT '총 할인금액',
  final_amount BIGINT DEFAULT 0 COMMENT '최종 결제금액',
  order_status VARCHAR(20) DEFAULT 'pending' COMMENT '주문상태',
  payment_status VARCHAR(20) DEFAULT 'unpaid' COMMENT '결제상태',
  payment_method VARCHAR(20) DEFAULT NULL COMMENT '결제방법',
  shipping_address TEXT DEFAULT NULL COMMENT '배송지 주소',
  shipping_memo TEXT DEFAULT NULL COMMENT '배송 메모',
  order_date DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '주문일시',
  confirmed_date DATETIME DEFAULT NULL COMMENT '주문확인일시',
  shipped_date DATETIME DEFAULT NULL COMMENT '출고일시',
  delivered_date DATETIME DEFAULT NULL COMMENT '배송완료일시',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '생성일시',
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '수정일시',
  PRIMARY KEY (id),
  UNIQUE KEY order_number (order_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 1.3 주문 아이템 테이블
CREATE TABLE IF NOT EXISTS order_items (
  id BIGINT NOT NULL AUTO_INCREMENT,
  order_id BIGINT NOT NULL COMMENT '주문ID',
  product_code VARCHAR(20) NOT NULL COMMENT '상품 코드',
  product_name VARCHAR(100) NOT NULL COMMENT '상품명',
  brand VARCHAR(50) DEFAULT NULL COMMENT '브랜드',
  quantity INT DEFAULT 1 COMMENT '수량',
  selected_year INT DEFAULT NULL COMMENT '선택 제조년도(DOT)',
  unit_price BIGINT NOT NULL COMMENT '단가',
  basic_discount_rate DECIMAL(5,2) DEFAULT 0.00 COMMENT '기본 할인율(%)',
  customer_discount_rate DECIMAL(5,2) DEFAULT 0.00 COMMENT '고객 할인율(%)',
  additional_discount_rate DECIMAL(5,2) DEFAULT 0.00 COMMENT '추가 할인율(%)',
  dot_discount_rate DECIMAL(5,2) DEFAULT 0.00 COMMENT 'DOT 할인율(%)',
  total_discount_rate DECIMAL(5,2) DEFAULT 0.00 COMMENT '총 할인율(%)',
  discounted_price BIGINT NOT NULL COMMENT '할인가격',
  final_price BIGINT NOT NULL COMMENT '최종가격(수량포함)',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '생성일시',
  PRIMARY KEY (id),
  KEY order_id (order_id),
  CONSTRAINT order_items_ibfk_1 FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 1.4 결제 테이블
CREATE TABLE IF NOT EXISTS payments (
  id BIGINT NOT NULL AUTO_INCREMENT,
  order_id BIGINT NOT NULL COMMENT '주문ID',
  payment_method VARCHAR(20) NOT NULL COMMENT '결제방법',
  payment_amount BIGINT NOT NULL COMMENT '결제금액',
  payment_status VARCHAR(20) DEFAULT 'pending' COMMENT '결제상태',
  transaction_id VARCHAR(100) DEFAULT NULL COMMENT '거래번호(PG사)',
  payment_key VARCHAR(200) DEFAULT NULL COMMENT '토스 결제 키',
  order_id_toss VARCHAR(100) DEFAULT NULL COMMENT '토스 주문 ID',
  pg_name VARCHAR(50) DEFAULT NULL COMMENT 'PG사명',
  payment_date DATETIME DEFAULT NULL COMMENT '결제일시',
  cancelled_date DATETIME DEFAULT NULL COMMENT '취소일시',
  memo TEXT DEFAULT NULL COMMENT '메모',
  raw_response TEXT DEFAULT NULL COMMENT '결제 원본 응답',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '생성일시',
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '수정일시',
  PRIMARY KEY (id),
  KEY order_id (order_id),
  KEY idx_payment_key (payment_key),
  CONSTRAINT payments_ibfk_1 FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ============================================
-- 2. 할인 관리 테이블
-- ============================================

-- 2.1 브랜드 그룹 테이블
CREATE TABLE IF NOT EXISTS brand_groups (
  id BIGINT NOT NULL AUTO_INCREMENT,
  brand VARCHAR(50) NOT NULL COMMENT '브랜드명',
  group_name VARCHAR(100) NOT NULL COMMENT '그룹명',
  group_order INT DEFAULT 0 COMMENT '그룹 순서',
  description TEXT DEFAULT NULL COMMENT '그룹 설명',
  is_active TINYINT(1) DEFAULT 1 COMMENT '활성화 여부',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '생성일시',
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '수정일시',
  PRIMARY KEY (id),
  UNIQUE KEY unique_brand_group (brand, group_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2.2 브랜드 그룹 패턴 테이블
CREATE TABLE IF NOT EXISTS brand_group_patterns (
  id BIGINT NOT NULL AUTO_INCREMENT,
  group_id BIGINT NOT NULL COMMENT '그룹ID',
  pattern VARCHAR(100) NOT NULL COMMENT '패턴명',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '생성일시',
  PRIMARY KEY (id),
  UNIQUE KEY unique_group_pattern (group_id, pattern),
  CONSTRAINT brand_group_patterns_ibfk_1 FOREIGN KEY (group_id) REFERENCES brand_groups (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2.3 고객 할인 테이블
CREATE TABLE IF NOT EXISTS customer_discounts (
  id BIGINT NOT NULL AUTO_INCREMENT,
  customer_code VARCHAR(10) NOT NULL COMMENT '고객 코드',
  brand VARCHAR(50) NOT NULL COMMENT '브랜드명',
  group_id BIGINT DEFAULT NULL COMMENT '그룹ID',
  discount_rate DECIMAL(5,2) DEFAULT 0.00 COMMENT '할인율(%)',
  priority INT DEFAULT 0 COMMENT '우선순위',
  start_date DATE DEFAULT NULL COMMENT '시작일',
  end_date DATE DEFAULT NULL COMMENT '종료일',
  memo TEXT DEFAULT NULL COMMENT '메모',
  is_active TINYINT(1) DEFAULT 1 COMMENT '활성화 여부',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '생성일시',
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '수정일시',
  created_by VARCHAR(50) DEFAULT NULL COMMENT '생성자',
  updated_by VARCHAR(50) DEFAULT NULL COMMENT '수정자',
  PRIMARY KEY (id),
  UNIQUE KEY unique_customer_brand_group (customer_code, brand, group_id),
  KEY group_id (group_id),
  CONSTRAINT customer_discounts_ibfk_1 FOREIGN KEY (group_id) REFERENCES brand_groups (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2.4 고객별 상품 할인 테이블
CREATE TABLE IF NOT EXISTS customer_product_discounts (
  id BIGINT NOT NULL AUTO_INCREMENT,
  customer_code VARCHAR(10) NOT NULL,
  product_code VARCHAR(20) NOT NULL,
  additional_discount_rate DECIMAL(5,2) NOT NULL,
  start_date DATE DEFAULT NULL,
  end_date DATE DEFAULT NULL,
  memo LONGTEXT DEFAULT NULL,
  is_active TINYINT(1) NOT NULL,
  priority INT NOT NULL,
  created_at DATETIME(6) NOT NULL,
  updated_at DATETIME(6) NOT NULL,
  created_by VARCHAR(50) DEFAULT NULL,
  updated_by VARCHAR(50) DEFAULT NULL,
  brand VARCHAR(100) DEFAULT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY customer_product_discoun_customer_code_product_co_6fd29911_uniq (customer_code, product_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2.5 할인 이력 테이블
CREATE TABLE IF NOT EXISTS discount_history (
  id BIGINT NOT NULL AUTO_INCREMENT,
  customer_code VARCHAR(10) NOT NULL COMMENT '고객 코드',
  product_code VARCHAR(50) NOT NULL COMMENT '상품 코드',
  brand VARCHAR(50) DEFAULT NULL COMMENT '브랜드',
  group_id BIGINT DEFAULT NULL COMMENT '그룹ID',
  basic_discount DECIMAL(5,2) DEFAULT NULL COMMENT '기본 할인율',
  customer_discount DECIMAL(5,2) DEFAULT NULL COMMENT '고객 할인율',
  applied_discount DECIMAL(5,2) DEFAULT NULL COMMENT '적용 할인율',
  original_price DECIMAL(10,2) DEFAULT NULL COMMENT '원가',
  final_price DECIMAL(10,2) DEFAULT NULL COMMENT '최종가격',
  transaction_date DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '거래일시',
  PRIMARY KEY (id),
  KEY group_id (group_id),
  CONSTRAINT discount_history_ibfk_1 FOREIGN KEY (group_id) REFERENCES brand_groups (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2.6 제조년도별 재고 할당 테이블
CREATE TABLE IF NOT EXISTS year_allocations (
  id BIGINT NOT NULL AUTO_INCREMENT,
  goods_code VARCHAR(20) NOT NULL,
  year_2025 INT NOT NULL,
  year_2024 INT NOT NULL,
  year_2023 INT NOT NULL,
  year_2022 INT NOT NULL,
  year_2021_before INT NOT NULL,
  year_2024_discount DECIMAL(5,2) DEFAULT 0.00 COMMENT '2024년 할인율(%)',
  year_2023_discount DECIMAL(5,2) DEFAULT 0.00 COMMENT '2023년 할인율(%)',
  year_2022_discount DECIMAL(5,2) DEFAULT 0.00 COMMENT '2022년 할인율(%)',
  year_2021_before_discount DECIMAL(5,2) DEFAULT 0.00 COMMENT '2021년 이전 할인율(%)',
  last_updated DATETIME(6) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY year_allocations_goods_code_81a5f7ce_uniq (goods_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ============================================
-- 3. 인덱스 추가 (성능 최적화)
-- ============================================

-- 주문 테이블 인덱스
CREATE INDEX IF NOT EXISTS idx_orders_customer_code ON orders(customer_code);
CREATE INDEX IF NOT EXISTS idx_orders_order_status ON orders(order_status);
CREATE INDEX IF NOT EXISTS idx_orders_payment_status ON orders(payment_status);
CREATE INDEX IF NOT EXISTS idx_orders_order_date ON orders(order_date);

-- 주문 아이템 테이블 인덱스
CREATE INDEX IF NOT EXISTS idx_order_items_product_code ON order_items(product_code);

-- 장바구니 테이블 인덱스
CREATE INDEX IF NOT EXISTS idx_shopping_cart_customer_code ON shopping_cart(customer_code);
CREATE INDEX IF NOT EXISTS idx_shopping_cart_product_code ON shopping_cart(product_code);

-- 결제 테이블 인덱스
CREATE INDEX IF NOT EXISTS idx_payments_payment_status ON payments(payment_status);
CREATE INDEX IF NOT EXISTS idx_payments_transaction_id ON payments(transaction_id);

-- 할인 테이블 인덱스
CREATE INDEX IF NOT EXISTS idx_customer_discounts_customer_code ON customer_discounts(customer_code);
CREATE INDEX IF NOT EXISTS idx_customer_discounts_brand ON customer_discounts(brand);
CREATE INDEX IF NOT EXISTS idx_customer_product_discounts_customer_code ON customer_product_discounts(customer_code);
CREATE INDEX IF NOT EXISTS idx_customer_product_discounts_product_code ON customer_product_discounts(product_code);


-- ============================================
-- 4. 초기 데이터 (선택사항)
-- ============================================
-- 필요 시 초기 브랜드 그룹 데이터 등을 여기에 추가


-- ============================================
-- 완료 메시지
-- ============================================
SELECT 'pythonanywhere MySQL 테이블 생성 완료!' AS status;
