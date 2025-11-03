#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itire.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.db import connection

def create_discount_tables():
    """할인 시스템 테이블 생성"""

    with connection.cursor() as cursor:
        print("=== 고객 할인 시스템 테이블 생성 시작 ===\n")

        try:
            # 1. brand_groups 테이블
            print("1. brand_groups 테이블 생성...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS brand_groups (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    brand VARCHAR(50) NOT NULL COMMENT '브랜드명',
                    group_name VARCHAR(100) NOT NULL COMMENT '그룹명',
                    group_order INT DEFAULT 0 COMMENT '그룹 표시 순서',
                    description TEXT COMMENT '그룹 설명',
                    is_active BOOLEAN DEFAULT TRUE COMMENT '활성화 여부',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    UNIQUE KEY uk_brand_group (brand, group_name),
                    INDEX idx_brand (brand),
                    INDEX idx_active (is_active)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='브랜드별 그룹 관리'
            """)
            print("   [OK] brand_groups 테이블 생성 완료")

        except Exception as e:
            print(f"   [INFO] brand_groups: {e}")

        try:
            # 2. brand_group_patterns 테이블
            print("\n2. brand_group_patterns 테이블 생성...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS brand_group_patterns (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    group_id INT NOT NULL COMMENT '그룹 ID',
                    pattern VARCHAR(100) NOT NULL COMMENT '패턴명',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (group_id) REFERENCES brand_groups(id) ON DELETE CASCADE,
                    UNIQUE KEY uk_group_pattern (group_id, pattern),
                    INDEX idx_pattern (pattern)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='그룹별 패턴 매핑'
            """)
            print("   [OK] brand_group_patterns 테이블 생성 완료")

        except Exception as e:
            print(f"   [INFO] brand_group_patterns: {e}")

        try:
            # 3. customer_discounts 테이블
            print("\n3. customer_discounts 테이블 생성...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS customer_discounts (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    customer_code VARCHAR(10) NOT NULL COMMENT '고객 코드',
                    brand VARCHAR(50) NOT NULL COMMENT '브랜드명',
                    group_id INT COMMENT '그룹 ID',
                    discount_rate DECIMAL(5,2) DEFAULT 0 COMMENT '할인율',
                    priority INT DEFAULT 0 COMMENT '우선순위',
                    start_date DATE COMMENT '할인 시작일',
                    end_date DATE COMMENT '할인 종료일',
                    memo TEXT COMMENT '메모',
                    is_active BOOLEAN DEFAULT TRUE COMMENT '활성화 여부',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    created_by VARCHAR(50) COMMENT '생성자',
                    updated_by VARCHAR(50) COMMENT '수정자',
                    INDEX fk_customer_code (customer_code),
                    FOREIGN KEY fk_group_id (group_id) REFERENCES brand_groups(id) ON DELETE SET NULL,
                    UNIQUE KEY uk_customer_brand_group (customer_code, brand, group_id),
                    INDEX idx_customer (customer_code),
                    INDEX idx_brand (brand),
                    INDEX idx_group (group_id),
                    INDEX idx_active_date (is_active, start_date, end_date)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='고객별 할인율 설정'
            """)
            print("   [OK] customer_discounts 테이블 생성 완료")

        except Exception as e:
            print(f"   [INFO] customer_discounts: {e}")

        try:
            # 4. discount_history 테이블
            print("\n4. discount_history 테이블 생성...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS discount_history (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    customer_code VARCHAR(10) NOT NULL COMMENT '고객 코드',
                    product_code VARCHAR(50) NOT NULL COMMENT '상품 코드',
                    brand VARCHAR(50) COMMENT '브랜드',
                    group_id INT COMMENT '적용된 그룹 ID',
                    basic_discount DECIMAL(5,2) COMMENT '기본 할인율',
                    customer_discount DECIMAL(5,2) COMMENT '고객 할인율',
                    applied_discount DECIMAL(5,2) COMMENT '최종 적용 할인율',
                    original_price DECIMAL(10,2) COMMENT '원가',
                    final_price DECIMAL(10,2) COMMENT '최종 가격',
                    transaction_date DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '거래 일시',
                    INDEX idx_customer_date (customer_code, transaction_date),
                    INDEX idx_product (product_code)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='할인 적용 이력'
            """)
            print("   [OK] discount_history 테이블 생성 완료")

        except Exception as e:
            print(f"   [INFO] discount_history: {e}")

        # 테이블 확인
        print("\n=== 생성된 테이블 확인 ===")
        cursor.execute("""
            SELECT TABLE_NAME, TABLE_COMMENT
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME IN ('brand_groups', 'brand_group_patterns',
                              'customer_discounts', 'discount_history')
        """)

        tables = cursor.fetchall()
        for table_name, comment in tables:
            print(f"   - {table_name}: {comment}")

        print("\n=== 테이블 생성 완료 ===")

def insert_sample_data():
    """샘플 데이터 삽입"""

    with connection.cursor() as cursor:
        print("\n=== 샘플 데이터 삽입 시작 ===\n")

        # 1. 브랜드 그룹 생성
        print("1. 브랜드 그룹 생성...")

        # 기존 10개 브랜드에 대한 그룹 생성
        brands = ['MICHELIN', 'HANKOOK', 'KUMHO', 'BRIDGESTONE', 'CONTINENTAL',
                  'DUNLOP', 'GOODYEAR', 'NEXEN', 'PIRELLI', 'YOKOHAMA']

        for brand in brands:
            try:
                cursor.execute("""
                    INSERT INTO brand_groups (brand, group_name, group_order, description)
                    VALUES
                    (%s, 'Premium', 1, 'Premium line products'),
                    (%s, 'Standard', 2, 'Standard line products'),
                    (%s, 'Economy', 3, 'Economy line products')
                """, (brand, brand, brand))
                print(f"   [OK] {brand} 그룹 생성")
            except Exception as e:
                print(f"   [SKIP] {brand}: {e}")

        # 2. TEST001 고객 할인 설정
        print("\n2. TEST001 고객 샘플 할인 설정...")

        # 몇 개 브랜드에 대해 샘플 할인 설정
        try:
            cursor.execute("""
                INSERT INTO customer_discounts
                (customer_code, brand, group_id, discount_rate, memo)
                SELECT 'TEST001', bg.brand, bg.id,
                       CASE bg.group_name
                           WHEN 'Premium' THEN 15.0
                           WHEN 'Standard' THEN 10.0
                           WHEN 'Economy' THEN 5.0
                       END,
                       CONCAT(bg.brand, ' ', bg.group_name, ' discount')
                FROM brand_groups bg
                WHERE bg.brand IN ('MICHELIN', 'HANKOOK', 'KUMHO')
                ON DUPLICATE KEY UPDATE
                discount_rate = VALUES(discount_rate)
            """)
            print("   [OK] TEST001 고객 할인 설정 완료")
        except Exception as e:
            print(f"   [ERROR] 고객 할인 설정: {e}")

        print("\n=== 샘플 데이터 삽입 완료 ===")

if __name__ == '__main__':
    print("\n" + "="*50)
    print("Django를 통한 할인 테이블 생성")
    print("="*50 + "\n")

    create_discount_tables()

    # 자동으로 샘플 데이터 삽입
    insert_sample_data()

    print("\n완료되었습니다.")