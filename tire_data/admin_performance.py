"""
성능 표기 Admin 설정
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import PerformanceCategory, PerformanceTag, GoodsPerformanceTag, Goods


class PerformanceTagInline(admin.TabularInline):
    """카테고리별 태그 인라인"""
    model = PerformanceTag
    extra = 1
    fields = ['name', 'order', 'is_active']
    ordering = ['order', 'name']


# Z. 미사용 - 구 성능표기 시스템 (BrandPatternPerformance로 대체)
# @admin.register(PerformanceCategory)
class PerformanceCategoryAdmin(admin.ModelAdmin):
    """성능 표기 카테고리 관리"""
    list_display = ['display_name', 'name', 'order', 'tag_count', 'is_active', 'created_at']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'display_name']
    ordering = ['order', 'name']
    inlines = [PerformanceTagInline]

    def tag_count(self, obj):
        """태그 개수"""
        count = obj.tags.count()
        return format_html(f'<span>{count}개</span>')
    tag_count.short_description = '태그 개수'


# Z. 미사용 - 구 성능표기 시스템 (BrandPatternPerformance로 대체)
# @admin.register(PerformanceTag)
class PerformanceTagAdmin(admin.ModelAdmin):
    """성능 표기 태그 관리"""
    list_display = ['name', 'category', 'order', 'goods_count', 'is_active', 'created_at']
    list_editable = ['order', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'category__display_name']
    ordering = ['category__order', 'order', 'name']

    def goods_count(self, obj):
        """적용된 상품 개수"""
        count = obj.goods_tags.count()
        return format_html(f'<span>{count}개</span>')
    goods_count.short_description = '적용 상품'


class GoodsPerformanceTagInline(admin.TabularInline):
    """상품별 성능 표기 인라인"""
    model = GoodsPerformanceTag
    extra = 1
    fields = ['tag', 'created_at']
    readonly_fields = ['created_at']
    ordering = ['tag__category__order', 'tag__order']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """태그 선택 시 활성화된 태그만 표시"""
        if db_field.name == "tag":
            kwargs["queryset"] = PerformanceTag.objects.filter(
                is_active=True
            ).select_related('category').order_by('category__order', 'order')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# Z. 미사용 - 구 성능표기 시스템 (BrandPatternPerformance로 대체)
# @admin.register(GoodsPerformanceTag)
class GoodsPerformanceTagAdmin(admin.ModelAdmin):
    """상품 성능 표기 관리"""
    list_display = ['goods_code', 'goods_name_display', 'tag', 'category_display', 'created_at']
    list_filter = ['tag__category', 'tag']
    search_fields = ['goods_code', 'tag__name']
    ordering = ['goods_code', 'tag__category__order', 'tag__order']
    autocomplete_fields = []  # Goods는 managed=False라 autocomplete 불가

    def goods_name_display(self, obj):
        """상품명 표시"""
        try:
            goods = Goods.objects.get(code=obj.goods_code)
            return goods.name[:50]
        except Goods.DoesNotExist:
            return format_html('<span style="color: red;">상품 없음</span>')
    goods_name_display.short_description = '상품명'

    def category_display(self, obj):
        """카테고리 표시"""
        return obj.tag.category.display_name
    category_display.short_description = '카테고리'
    category_display.admin_order_field = 'tag__category__display_name'
