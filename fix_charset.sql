-- 데이터베이스 charset/collation 수정
-- PythonAnywhere MySQL console에서 실행할 SQL

-- 1. 데이터베이스 기본 charset 변경
ALTER DATABASE `tirepass$itire_db` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 2. customers_simple 테이블 변경
ALTER TABLE `customers_simple` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 3. orders 테이블 변경
ALTER TABLE `orders` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 4. order_items 테이블 변경
ALTER TABLE `order_items` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 5. shopping_cart 테이블 변경
ALTER TABLE `shopping_cart` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 6. payments 테이블 변경
ALTER TABLE `payments` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 7. shipping_addresses 테이블 변경
ALTER TABLE `shipping_addresses` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 8. year_allocations 테이블 변경
ALTER TABLE `year_allocations` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 9. brand_groups 테이블 변경
ALTER TABLE `brand_groups` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 10. brand_group_patterns 테이블 변경
ALTER TABLE `brand_group_patterns` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 11. customer_discounts 테이블 변경
ALTER TABLE `customer_discounts` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 12. customer_product_discounts 테이블 변경
ALTER TABLE `customer_product_discounts` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 13. discount_history 테이블 변경
ALTER TABLE `discount_history` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 14. goods_display_names 테이블 변경
ALTER TABLE `goods_display_names` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 테이블 정보 확인
SELECT
    TABLE_NAME,
    TABLE_COLLATION
FROM
    information_schema.TABLES
WHERE
    TABLE_SCHEMA = 'tirepass$itire_db'
    AND TABLE_NAME IN (
        'customers_simple',
        'orders',
        'order_items',
        'shopping_cart',
        'payments',
        'shipping_addresses',
        'year_allocations',
        'brand_groups',
        'brand_group_patterns',
        'customer_discounts',
        'customer_product_discounts',
        'discount_history',
        'goods_display_names'
    );
