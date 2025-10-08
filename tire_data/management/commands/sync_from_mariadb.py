import pymysql
from django.core.management.base import BaseCommand
from tire_data.models import (
    Goods, Customers, BrandGroup, BrandGroupPattern, CustomerDiscount,
    CustomerProductDiscount
)
from django.db import transaction

MARIADB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "tirepass",
    "database": "itire_db",
    "charset": "utf8mb4"
}

class Command(BaseCommand):
    help = "MariaDB에서 데이터를 가져와서 SQLite에 동기화"

    def handle(self, *args, **options):
        try:
            # MariaDB 연결
            self.stdout.write("MariaDB 연결 중...")
            conn = pymysql.connect(**MARIADB_CONFIG)
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            
            # Goods 테이블 동기화
            self.stdout.write("\nGoods 테이블 동기화 중...")
            cursor.execute("SELECT * FROM goods")
            goods_data = cursor.fetchall()
            
            with transaction.atomic():
                for row in goods_data:
                    Goods.objects.update_or_create(
                        code=row["CODE"],
                        defaults={
                            "name": row["NAME"],
                            "bun1": row.get("BUN1"),
                            "brand": row.get("brand"),
                            "is_tire": row.get("is_tire", False),
                            "jaego": row.get("JAEGO", 0),
                            "fixp": row.get("FIXP", 0),
                            "discount_rate": row.get("discount_rate", 0.00),
                        }
                    )
            
            self.stdout.write(self.style.SUCCESS(f"✓ Goods {len(goods_data)}개 동기화 완료"))
            
            # Customers 테이블 동기화
            self.stdout.write("\nCustomers 테이블 동기화 중...")
            cursor.execute("SELECT * FROM customers_simple")
            customers_data = cursor.fetchall()
            
            with transaction.atomic():
                for row in customers_data:
                    Customers.objects.update_or_create(
                        code=row["code"],
                        defaults={
                            "name": row.get("name"),
                            "rep": row.get("rep"),
                            "tel1": row.get("tel1"),
                            "tel3": row.get("tel3"),
                            "enno": row.get("enno"),
                            "is_registered": row.get("is_registered", False),
                            "user_id": row.get("user_id"),
                            "must_change_password": row.get("must_change_password", True),
                        }
                    )
            
            self.stdout.write(self.style.SUCCESS(f"✓ Customers {len(customers_data)}개 동기화 완료"))

            # BrandGroup 테이블 동기화
            self.stdout.write("\nBrandGroup 테이블 동기화 중...")
            cursor.execute("SELECT * FROM brand_groups")
            brandgroup_data = cursor.fetchall()

            with transaction.atomic():
                for row in brandgroup_data:
                    BrandGroup.objects.update_or_create(
                        id=row["id"],
                        defaults={
                            "brand": row["brand"],
                            "group_name": row["group_name"],
                            "group_order": row.get("group_order", 0),
                            "description": row.get("description"),
                            "is_active": row.get("is_active", True),
                        }
                    )

            self.stdout.write(self.style.SUCCESS(f"✓ BrandGroup {len(brandgroup_data)}개 동기화 완료"))

            # BrandGroupPattern 테이블 동기화
            self.stdout.write("\nBrandGroupPattern 테이블 동기화 중...")
            cursor.execute("SELECT * FROM brand_group_patterns")
            pattern_data = cursor.fetchall()

            with transaction.atomic():
                for row in pattern_data:
                    BrandGroupPattern.objects.update_or_create(
                        id=row["id"],
                        defaults={
                            "group_id": row["group_id"],
                            "pattern": row["pattern"],
                        }
                    )

            self.stdout.write(self.style.SUCCESS(f"✓ BrandGroupPattern {len(pattern_data)}개 동기화 완료"))

            # CustomerDiscount 테이블 동기화
            self.stdout.write("\nCustomerDiscount 테이블 동기화 중...")
            cursor.execute("SELECT * FROM customer_discounts")
            discount_data = cursor.fetchall()

            with transaction.atomic():
                for row in discount_data:
                    CustomerDiscount.objects.update_or_create(
                        id=row["id"],
                        defaults={
                            "customer_code": row["customer_code"],
                            "brand": row["brand"],
                            "group_id": row.get("group_id"),
                            "discount_rate": row.get("discount_rate", 0.00),
                            "priority": row.get("priority", 0),
                            "start_date": row.get("start_date"),
                            "end_date": row.get("end_date"),
                            "memo": row.get("memo"),
                            "is_active": row.get("is_active", True),
                            "created_by": row.get("created_by"),
                            "updated_by": row.get("updated_by"),
                        }
                    )

            self.stdout.write(self.style.SUCCESS(f"✓ CustomerDiscount {len(discount_data)}개 동기화 완료"))

            # CustomerProductDiscount 테이블 동기화
            self.stdout.write("\nCustomerProductDiscount 테이블 동기화 중...")
            cursor.execute("SELECT * FROM customer_product_discounts")
            product_discount_data = cursor.fetchall()

            with transaction.atomic():
                for row in product_discount_data:
                    CustomerProductDiscount.objects.update_or_create(
                        id=row["id"],
                        defaults={
                            "customer_code": row["customer_code"],
                            "product_code": row["product_code"],
                            "brand": row.get("brand"),
                            "additional_discount_rate": row.get("additional_discount_rate", 0.00),
                            "start_date": row.get("start_date"),
                            "end_date": row.get("end_date"),
                            "memo": row.get("memo"),
                            "is_active": row.get("is_active", True),
                            "priority": row.get("priority", 0),
                            "created_by": row.get("created_by"),
                            "updated_by": row.get("updated_by"),
                        }
                    )

            self.stdout.write(self.style.SUCCESS(f"✓ CustomerProductDiscount {len(product_discount_data)}개 동기화 완료"))

            cursor.close()
            conn.close()

            self.stdout.write(self.style.SUCCESS("\n=== 동기화 완료 ==="))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"동기화 실패: {e}"))
