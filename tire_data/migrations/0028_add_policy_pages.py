# Generated manually for PolicyPage model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tire_data', '0027_add_point_system'),
    ]

    operations = [
        migrations.CreateModel(
            name='PolicyPage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(unique=True, verbose_name='URL 슬러그')),
                ('title', models.CharField(max_length=100, verbose_name='제목')),
                ('policy_type', models.CharField(
                    choices=[
                        ('terms', '이용약관'),
                        ('privacy', '개인정보처리방침'),
                        ('refund', '환불정책'),
                        ('shipping', '배송정책'),
                        ('other', '기타')
                    ],
                    default='other',
                    max_length=20,
                    verbose_name='정책 유형'
                )),
                ('content', models.TextField(verbose_name='내용')),
                ('is_active', models.BooleanField(default=True, verbose_name='활성화')),
                ('show_in_footer', models.BooleanField(default=True, verbose_name='푸터에 표시')),
                ('display_order', models.IntegerField(default=0, verbose_name='표시 순서')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='생성일시')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='수정일시')),
            ],
            options={
                'verbose_name': '정책 페이지',
                'verbose_name_plural': 'C. ⚙️ 설정 | 02. 정책 페이지 관리',
                'db_table': 'policy_pages',
                'ordering': ['display_order', 'title'],
                'managed': True,
            },
        ),
    ]
