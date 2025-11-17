from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ("tire_data", "0026_merge_20251117_1843"),
    ]

    operations = [
        migrations.RunSQL(
            # Forward SQL
            sql="""
            -- Create point_policies table
            CREATE TABLE `point_policies` (
                `id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
                `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL UNIQUE,
                `earn_rate` decimal(5, 2) NOT NULL,
                `min_order_amount` integer NOT NULL,
                `signup_bonus` integer NOT NULL,
                `point_validity_days` integer NOT NULL,
                `min_use_amount` integer NOT NULL,
                `max_use_rate` decimal(5, 2) NOT NULL,
                `is_active` bool NOT NULL,
                `created_at` datetime(6) NOT NULL,
                `updated_at` datetime(6) NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

            -- Create customer_points table
            CREATE TABLE `customer_points` (
                `id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
                `balance` integer NOT NULL,
                `total_earned` integer NOT NULL,
                `total_used` integer NOT NULL,
                `updated_at` datetime(6) NOT NULL,
                `customer_id` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL UNIQUE,
                CONSTRAINT `customer_points_customer_id_fk`
                    FOREIGN KEY (`customer_id`) REFERENCES `customers_simple` (`code`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

            -- Create point_transactions table
            CREATE TABLE `point_transactions` (
                `id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
                `transaction_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
                `amount` integer NOT NULL,
                `balance_after` integer NOT NULL,
                `description` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
                `order_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
                `created_at` datetime(6) NOT NULL,
                `expires_at` date NULL,
                `customer_id` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
                CONSTRAINT `point_transactions_customer_id_fk`
                    FOREIGN KEY (`customer_id`) REFERENCES `customers_simple` (`code`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

            -- Create indexes
            CREATE INDEX `point_trans_custome_idx` ON `point_transactions` (`customer_id`, `created_at` DESC);
            CREATE INDEX `point_trans_order_idx` ON `point_transactions` (`order_code`);
            """,
            # Reverse SQL
            reverse_sql="""
            DROP TABLE IF EXISTS `point_transactions`;
            DROP TABLE IF EXISTS `customer_points`;
            DROP TABLE IF EXISTS `point_policies`;
            """
        ),
    ]
