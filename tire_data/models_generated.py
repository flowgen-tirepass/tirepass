# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class CustomersSimple(models.Model):
    code = models.CharField(primary_key=True, max_length=10)
    name = models.CharField(max_length=50, blank=True, null=True)
    rep = models.CharField(max_length=20, blank=True, null=True)
    tel1 = models.CharField(max_length=20, blank=True, null=True)
    tel3 = models.CharField(max_length=20, blank=True, null=True)
    enno = models.CharField(max_length=20, blank=True, null=True)
    is_registered = models.IntegerField(blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)
    must_change_password = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'customers_simple'


class BrandGroups(models.Model):
    brand = models.CharField(max_length=50, db_comment='브랜드명')
    group_name = models.CharField(max_length=100, db_comment='그룹명')
    group_order = models.IntegerField(blank=True, null=True, db_comment='그룹 표시 순서')
    description = models.TextField(blank=True, null=True, db_comment='그룹 설명')
    is_active = models.IntegerField(blank=True, null=True, db_comment='활성화 여부')
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'brand_groups'
        unique_together = (('brand', 'group_name'),)
        db_table_comment = '브랜드별 그룹 관리'


class BrandGroupPatterns(models.Model):
    group = models.ForeignKey(BrandGroups, models.DO_NOTHING, db_comment='그룹 ID')
    pattern = models.CharField(max_length=100, db_comment='패턴명')
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'brand_group_patterns'
        unique_together = (('group', 'pattern'),)
        db_table_comment = '그룹별 패턴 매핑'


class Goods(models.Model):
    code = models.CharField(db_column='CODE', primary_key=True, max_length=20)  # Field name made lowercase.
    name = models.CharField(db_column='NAME', max_length=100, blank=True, null=True)  # Field name made lowercase.
    bun1 = models.CharField(db_column='BUN1', max_length=50, blank=True, null=True)  # Field name made lowercase.
    jaego = models.IntegerField(db_column='JAEGO', blank=True, null=True)  # Field name made lowercase.
    fixp = models.BigIntegerField(db_column='FIXP', blank=True, null=True)  # Field name made lowercase.
    last_sync = models.DateTimeField(db_column='LAST_SYNC', blank=True, null=True)  # Field name made lowercase.
    brand = models.CharField(max_length=50, blank=True, null=True)
    discount_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, db_comment='할인율(%)')
    is_tire = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'goods'
