# Generated manually - Add ExcludedGoods model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tire_data', '0007_add_order_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExcludedGoods',
            fields=[
                ('code', models.CharField(max_length=20, primary_key=True, serialize=False, verbose_name='상품코드')),
                ('reason', models.CharField(max_length=200, verbose_name='제외 사유')),
                ('excluded_at', models.DateTimeField(auto_now_add=True, verbose_name='제외일시')),
                ('excluded_by', models.CharField(default='admin', max_length=50, verbose_name='제외자')),
            ],
            options={
                'verbose_name': '제외 상품',
                'verbose_name_plural': 'C. ⚙️ 설정 | 05. ERP 동기화 제외 상품',
                'db_table': 'excluded_goods',
                'managed': True,
            },
        ),
    ]
