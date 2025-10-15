# Generated manually - Add order_source and related fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tire_data', '0006_erpsnapshot'),
    ]

    operations = [
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
