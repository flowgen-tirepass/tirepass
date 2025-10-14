# Admin 메뉴 구조 개선 계획

## 🎯 목표

Django Admin 사이드바를 다음과 같이 그룹화:

```
📊 판매 관리
  ├─ 01. 상품 (타이어)
  ├─ 02. 고객
  ├─ 03. 주문
  ├─ 04. 장바구니
  ├─ 05. 결제
  └─ 06. 배송지

💰 할인 관리
  ├─ 01. 브랜드 그룹
  ├─ 02. 그룹 패턴
  ├─ 03. 고객별 할인
  ├─ 04. 상품별 할인
  └─ 05. 할인 이력

⚙️ 설정
  ├─ 01. 상품 성능표기 (주)
  ├─ 02. 성능표기 카테고리
  ├─ 03. 성능표기 태그
  ├─ 04. 상품 표시명
  ├─ 05. 연식 할인율
  ├─ 06. ERP 스냅샷
  └─ 07. ERP 고객 (읽기전용)
```

## 📋 구현 방법

### 방법 1: verbose_name_plural 변경 (✅ 선택)

**장점**:
- 빠르고 간단
- 추가 패키지 불필요
- PythonAnywhere에서 바로 작동

**구현**:
```python
class Meta:
    verbose_name_plural = '📊 판매 | 01. 상품'
```

알파벳/숫자 순으로 자동 정렬되어 그룹화됩니다.

### 방법 2: 커스텀 AdminSite (향후)

**장점**:
- 완전한 제어
- 드래그 앤 드롭 가능 (django-admin-tools)
- 대시보드 커스터마이징

**단점**:
- 복잡한 구현
- 추가 패키지 필요
- 마이그레이션 필요

## 🔧 실행 계획

### 1단계: models.py 수정

```python
# tire_data/models.py

class Goods(models.Model):
    class Meta:
        verbose_name_plural = '📊 판매 | 01. 상품'

class Customers(models.Model):
    class Meta:
        verbose_name_plural = '📊 판매 | 02. 고객'

class Order(models.Model):
    class Meta:
        verbose_name_plural = '📊 판매 | 03. 주문'

class OrderItem(models.Model):
    class Meta:
        verbose_name_plural = '📊 판매 | 03-1. 주문 항목'

class ShoppingCart(models.Model):
    class Meta:
        verbose_name_plural = '📊 판매 | 04. 장바구니'

class Payment(models.Model):
    class Meta:
        verbose_name_plural = '📊 판매 | 05. 결제'

class ShippingAddress(models.Model):
    class Meta:
        verbose_name_plural = '📊 판매 | 06. 배송지'

# 할인 관리
class BrandGroup(models.Model):
    class Meta:
        verbose_name_plural = '💰 할인 | 01. 브랜드 그룹'

class BrandGroupPattern(models.Model):
    class Meta:
        verbose_name_plural = '💰 할인 | 02. 그룹 패턴'

class CustomerDiscount(models.Model):
    class Meta:
        verbose_name_plural = '💰 할인 | 03. 고객별 할인'

class CustomerProductDiscount(models.Model):
    class Meta:
        verbose_name_plural = '💰 할인 | 04. 상품별 할인'

class DiscountHistory(models.Model):
    class Meta:
        verbose_name_plural = '💰 할인 | 05. 할인 이력'

# 설정
class GoodsPerformanceTag(models.Model):
    class Meta:
        verbose_name_plural = '⚙️ 설정 | 01. 상품 성능표기'

class PerformanceCategory(models.Model):
    class Meta:
        verbose_name_plural = '⚙️ 설정 | 02. 성능표기 카테고리'

class PerformanceTag(models.Model):
    class Meta:
        verbose_name_plural = '⚙️ 설정 | 03. 성능표기 태그'

class GoodsDisplayName(models.Model):
    class Meta:
        verbose_name_plural = '⚙️ 설정 | 04. 상품 표시명'

class YearAllocation(models.Model):
    class Meta:
        verbose_name_plural = '⚙️ 설정 | 05. 연식 할인율'

class ERPSnapshot(models.Model):
    class Meta:
        verbose_name_plural = '⚙️ 설정 | 06. ERP 스냅샷'

class CustomersFull(models.Model):
    class Meta:
        verbose_name_plural = '⚙️ 설정 | 07. ERP 고객 (읽기전용)'
```

### 2단계: CustomersFull 복구

```python
# tire_data/admin.py

@admin.register(CustomersFull)
class CustomersFullAdmin(admin.ModelAdmin):
    """ERP 전체 고객 목록 (읽기 전용)"""
    list_display = ['code', 'name', 'rep', 'tel1', 'tel3', 'enno', 'last_sync']
    search_fields = ['code', 'name', 'rep', 'enno']
    readonly_fields = [field.name for field in CustomersFull._meta.fields]
    ordering = ['code']
    list_per_page = 50

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
```

## 📊 예상 결과

### Before (현재):
```
Django administration
├─ 상품목록
├─ 고객 목록
├─ 주문
├─ 장바구니
├─ 결제
├─ 배송지
├─ 브랜드 그룹
├─ 그룹 패턴
├─ 고객별 할인
├─ 상품별 할인
├─ 할인 이력
├─ 상품 성능표기
├─ 성능표기 카테고리
├─ 성능표기 태그
├─ 상품 표시명
├─ 연식 할인율
└─ ERP 스냅샷 기록
```
❌ 20개+ 메뉴가 평면적으로 나열

### After (개선):
```
📊 판매 관리
  ├─ 01. 상품
  ├─ 02. 고객
  ├─ 03. 주문
  │   └─ 03-1. 주문 항목
  ├─ 04. 장바구니
  ├─ 05. 결제
  └─ 06. 배송지

💰 할인 관리
  ├─ 01. 브랜드 그룹
  ├─ 02. 그룹 패턴
  ├─ 03. 고객별 할인
  ├─ 04. 상품별 할인
  └─ 05. 할인 이력

⚙️ 설정
  ├─ 01. 상품 성능표기
  ├─ 02. 성능표기 카테고리
  ├─ 03. 성능표기 태그
  ├─ 04. 상품 표시명
  ├─ 05. 연식 할인율
  ├─ 06. ERP 스냅샷
  └─ 07. ERP 고객 (읽기전용)

인증 및 권한
  ├─ 사용자
  └─ 그룹
```
✅ 3개 주요 그룹으로 명확하게 구분

## ⚠️ 주의사항

1. **기존 북마크**: URL은 변경되지 않으나 메뉴 이름이 변경됨
2. **검색**: Admin 검색은 정상 작동
3. **권한**: 기존 권한 유지
4. **모바일**: 모바일 화면도 동일하게 적용

## 🚀 배포 순서

1. 로컬에서 models.py 수정
2. 마이그레이션 (필요시)
3. 테스트
4. Git commit & push
5. PythonAnywhere에서 pull
6. Web app reload
7. Admin 페이지 확인

## 📝 향후 개선 (Phase 2)

- [ ] django-admin-tools 도입
- [ ] 대시보드 위젯 추가
- [ ] 드래그 앤 드롭 메뉴 정렬
- [ ] 메뉴 접기/펼치기 기능
- [ ] 사용자별 메뉴 커스터마이징

---

**작성일**: 2025-10-14
**작성자**: Claude Code
**상태**: 계획 단계
