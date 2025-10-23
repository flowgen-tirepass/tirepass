# Generated manually - Add order_source and related fields

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tire_data', '0006_erpsnapshot'),
    ]

    operations = [
        # Create Order model first
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_number', models.CharField(max_length=50, unique=True, verbose_name='주문번호')),
                ('customer_code', models.CharField(max_length=10, verbose_name='고객 코드')),
                ('customer_name', models.CharField(blank=True, max_length=50, null=True, verbose_name='고객명')),
                ('total_amount', models.BigIntegerField(default=0, verbose_name='총 주문금액')),
                ('total_discount', models.BigIntegerField(default=0, verbose_name='총 할인금액')),
                ('final_amount', models.BigIntegerField(default=0, verbose_name='최종 결제금액')),
                ('order_status', models.CharField(default='pending', max_length=20, verbose_name='주문상태')),
                ('payment_status', models.CharField(choices=[('unpaid', '미결제'), ('paid', '결제완료'), ('refunded', '환불완료')], default='unpaid', max_length=20, verbose_name='결제상태')),
                ('payment_method', models.CharField(blank=True, max_length=20, null=True, verbose_name='결제방법')),
                ('shipping_address', models.TextField(blank=True, null=True, verbose_name='배송지 주소')),
                ('shipping_memo', models.TextField(blank=True, null=True, verbose_name='배송 메모')),
                ('order_date', models.DateTimeField(auto_now_add=True, verbose_name='주문일시')),
                ('confirmed_date', models.DateTimeField(blank=True, null=True, verbose_name='주문확인일시')),
                ('shipped_date', models.DateTimeField(blank=True, null=True, verbose_name='출고일시')),
                ('delivered_date', models.DateTimeField(blank=True, null=True, verbose_name='배송완료일시')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='생성일시')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='수정일시')),
            ],
            options={
                'verbose_name': '주문',
                'verbose_name_plural': 'A. 📊 판매 | 03. 주문',
                'db_table': 'orders',
                'ordering': ['-order_date'],
                'managed': True,
            },
        ),
        # Create OrderItem model
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_code', models.CharField(max_length=20, verbose_name='상품 코드')),
                ('product_name', models.CharField(max_length=100, verbose_name='상품명')),
                ('brand', models.CharField(blank=True, max_length=50, null=True, verbose_name='브랜드')),
                ('quantity', models.IntegerField(default=1, verbose_name='수량')),
                ('selected_year', models.CharField(blank=True, max_length=10, null=True, verbose_name='선택 제조년도(DOT)')),
                ('unit_price', models.BigIntegerField(default=0, verbose_name='단가')),
                ('basic_discount_rate', models.DecimalField(decimal_places=2, default=0.0, max_digits=5, verbose_name='기본 할인율(%)')),
                ('customer_discount_rate', models.DecimalField(decimal_places=2, default=0.0, max_digits=5, verbose_name='고객 할인율(%)')),
                ('additional_discount_rate', models.DecimalField(decimal_places=2, default=0.0, max_digits=5, verbose_name='추가 할인율(%)')),
                ('dot_discount_rate', models.DecimalField(decimal_places=2, default=0.0, max_digits=5, verbose_name='DOT 할인율(%)')),
                ('total_discount_rate', models.DecimalField(decimal_places=2, default=0.0, max_digits=5, verbose_name='총 할인율(%)')),
                ('discounted_price', models.BigIntegerField(default=0, verbose_name='할인가격')),
                ('final_price', models.BigIntegerField(default=0, verbose_name='최종가격(수량포함)')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='생성일시')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='tire_data.order', verbose_name='주문')),
            ],
            options={
                'verbose_name': '주문 상세',
                'verbose_name_plural': 'A. 📊 판매 | 03-1. 주문 상세',
                'db_table': 'order_items',
                'ordering': ['order', 'id'],
                'managed': True,
            },
        ),
        # Create ShoppingCart model
        migrations.CreateModel(
            name='ShoppingCart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_code', models.CharField(max_length=10, verbose_name='고객 코드')),
                ('product_code', models.CharField(max_length=20, verbose_name='상품 코드')),
                ('quantity', models.IntegerField(default=1, verbose_name='수량')),
                ('selected_year', models.CharField(blank=True, max_length=10, null=True, verbose_name='선택 제조년도(DOT)')),
                ('unit_price', models.BigIntegerField(default=0, verbose_name='단가')),
                ('discount_rate', models.DecimalField(decimal_places=2, default=0.0, max_digits=5, verbose_name='적용 할인율(%)')),
                ('final_price', models.BigIntegerField(default=0, verbose_name='최종가격')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='생성일시')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='수정일시')),
            ],
            options={
                'verbose_name': '장바구니',
                'verbose_name_plural': 'A. 📊 판매 | 04. 장바구니',
                'db_table': 'shopping_cart',
                'ordering': ['-created_at'],
                'managed': True,
                'unique_together': {('customer_code', 'product_code', 'selected_year')},
            },
        ),
        # Create Payment model
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_method', models.CharField(choices=[('card', '카드결제'), ('transfer', '계좌이체'), ('cash', '현금결제')], max_length=20, verbose_name='결제방법')),
                ('payment_amount', models.BigIntegerField(verbose_name='결제금액')),
                ('payment_status', models.CharField(choices=[('pending', '결제대기'), ('completed', '결제완료'), ('failed', '결제실패'), ('cancelled', '결제취소')], default='pending', max_length=20, verbose_name='결제상태')),
                ('transaction_id', models.CharField(blank=True, db_column='transaction_id', max_length=100, null=True, verbose_name='거래번호(PG사)')),
                ('payment_key', models.CharField(blank=True, db_column='payment_key', max_length=200, null=True, verbose_name='토스 결제 키')),
                ('order_id_toss', models.CharField(blank=True, db_column='order_id_toss', max_length=100, null=True, verbose_name='토스 주문 ID')),
                ('pg_name', models.CharField(blank=True, max_length=50, null=True, verbose_name='PG사명')),
                ('payment_date', models.DateTimeField(blank=True, null=True, verbose_name='결제일시')),
                ('cancelled_date', models.DateTimeField(blank=True, null=True, verbose_name='취소일시')),
                ('memo', models.TextField(blank=True, null=True, verbose_name='메모')),
                ('raw_response', models.TextField(blank=True, db_column='raw_response', null=True, verbose_name='결제 원본 응답')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='생성일시')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='수정일시')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='tire_data.order', verbose_name='주문')),
            ],
            options={
                'verbose_name': '결제',
                'verbose_name_plural': 'A. 📊 판매 | 05. 결제',
                'db_table': 'payments',
                'ordering': ['-created_at'],
                'managed': True,
            },
        ),
        # Create ShippingAddress model
        migrations.CreateModel(
            name='ShippingAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_code', models.CharField(max_length=10, verbose_name='고객 코드')),
                ('recipient_name', models.CharField(max_length=50, verbose_name='수령인')),
                ('phone_number', models.CharField(max_length=20, verbose_name='전화번호')),
                ('postal_code', models.CharField(blank=True, max_length=10, null=True, verbose_name='우편번호')),
                ('address', models.CharField(max_length=200, verbose_name='주소')),
                ('address_detail', models.CharField(blank=True, max_length=200, null=True, verbose_name='상세주소')),
                ('is_default', models.BooleanField(default=False, verbose_name='기본배송지')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='생성일시')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='수정일시')),
            ],
            options={
                'verbose_name': '배송지 주소',
                'verbose_name_plural': 'A. 📊 판매 | 06. 배송지',
                'db_table': 'shipping_addresses',
                'ordering': ['-is_default', '-created_at'],
                'managed': True,
            },
        ),
        migrations.AddField(
            model_name='order',
            name='cancelled_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='취소일시'),
        ),
        migrations.AddField(
            model_name='order',
            name='cancelled_reason',
            field=models.TextField(blank=True, null=True, verbose_name='취소사유'),
        ),
        migrations.AddField(
            model_name='order',
            name='returned_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='반품일시'),
        ),
        migrations.AddField(
            model_name='order',
            name='returned_reason',
            field=models.TextField(blank=True, null=True, verbose_name='반품사유'),
        ),
        migrations.AddField(
            model_name='order',
            name='order_source',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('mobile', '모바일 주문'),
                    ('erp_phone', 'ERP 전화주문'),
                    ('erp_import', 'ERP 수동입력'),
                ],
                default='mobile',
                verbose_name='주문 출처'
            ),
        ),
        migrations.AddField(
            model_name='order',
            name='erp_order_number',
            field=models.CharField(max_length=50, blank=True, null=True, verbose_name='ERP 주문번호'),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('pending', '주문대기'),
                    ('confirmed', '주문확인'),
                    ('preparing', '출고준비'),
                    ('shipped', '배송중'),
                    ('delivered', '배송완료'),
                    ('cancelled', '주문취소'),
                    ('returned', '반품완료'),
                ],
                default='pending',
                verbose_name='주문상태'
            ),
        ),
    ]
