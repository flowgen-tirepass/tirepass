# Generated manually for ERPSnapshot model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tire_data', '0005_auto_20251002_1917'),
    ]

    operations = [
        migrations.CreateModel(
            name='ERPSnapshot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(db_index=True, verbose_name='기록 시간')),
                ('status', models.CharField(choices=[('connected', '연결됨'), ('disconnected', '연결 끊김'), ('timeout', '타임아웃'), ('connection_error', '연결 오류')], db_index=True, max_length=20, verbose_name='상태')),
                ('response_time_ms', models.FloatField(blank=True, null=True, verbose_name='응답 시간(ms)')),
                ('erp_goods_count', models.IntegerField(default=0, verbose_name='ERP 상품 수')),
                ('database_status', models.CharField(default='unknown', max_length=20, verbose_name='DB 상태')),
                ('api_url', models.CharField(max_length=200, verbose_name='API URL')),
                ('error_message', models.TextField(blank=True, null=True, verbose_name='오류 메시지')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='레코드 생성일시')),
            ],
            options={
                'verbose_name': 'ERP 스냅샷',
                'verbose_name_plural': 'ERP 스냅샷 기록',
                'db_table': 'erp_snapshots',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.AddIndex(
            model_name='erpsnapshot',
            index=models.Index(fields=['-timestamp'], name='erp_snapsho_timesta_04a836_idx'),
        ),
        migrations.AddIndex(
            model_name='erpsnapshot',
            index=models.Index(fields=['status', '-timestamp'], name='erp_snapsho_status_9b3f52_idx'),
        ),
    ]
