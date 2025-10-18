# TirePASS 기술 상세 보고서

---

## 1. 시스템 아키텍처

### 1.1 기술 스택

#### 백엔드
- **프레임워크**: Django 5.1.4
- **언어**: Python 3.12
- **ORM**: Django ORM
- **인증**: Django Authentication + Custom Token

#### 데이터베이스
- **DBMS**: MariaDB 12.0
- **연결**: MySQL Connector
- **인코딩**: UTF-8mb4 (한글 완벽 지원)

#### 프론트엔드
- **모바일**: Vanilla JavaScript + HTML5 + CSS3
- **관리자**: Django Admin 커스터마이징
- **UI 라이브러리**: 없음 (순수 코드 구현)

#### 인프라
- **배포**: PythonAnywhere (WSGI)
- **웹서버**: Nginx + Gunicorn
- **도메인**: tirepass.pythonanywhere.com

---

## 2. 핵심 기술 구현

### 2.1 ERP 실시간 연동 시스템

#### ERPAPIClient 클래스
```python
class ERPAPIClient:
    """
    ERP 시스템 REST API 클라이언트
    - 실시간 상품 정보 조회
    - 재고 수량 동기화
    - 가격 정보 업데이트
    """
    BASE_URL = "http://itire2.iptime.org:8000"

    @staticmethod
    def get_goods_list(offset=0, limit=50, search=''):
        """상품 목록 조회 (페이지네이션 + 검색)"""

    @staticmethod
    def get_goods_count():
        """전체 상품 수 조회"""

    @staticmethod
    def get_goods_detail(goods_code):
        """상품 상세 정보 조회"""
```

**기술적 특징**:
- 타임아웃 설정 (10초)으로 안정성 확보
- 에러 핸들링으로 ERP 장애 시에도 시스템 정상 운영
- 캐싱 없이 항상 최신 데이터 보장

#### GoodsAdmin 커스텀 뷰
```python
def changelist_view(self, request, extra_context=None):
    """
    ERP 데이터를 Django Admin에 실시간 표시
    - Django ORM 사용하지 않음
    - ERP API 직접 호출
    - 페이지네이션 구현
    """
    erp_goods_list = ERPAPIClient.get_goods_list(offset, limit, search)
    # 필터링 (타이어만, 재고있음, 브랜드별)
    # 할인율 정보 추가
```

**구현 난이도**: ★★★★☆
- Django Admin의 기본 동작 방식을 완전히 우회
- 데이터베이스 없이 API 데이터를 Admin에 표시
- 검색/필터/페이지네이션 모두 커스텀 구현

---

### 2.2 4단계 할인 시스템

#### 할인 계산 알고리즘
```python
def calculate_discount_price(product_code, customer_code, selected_year=None):
    """
    4단계 할인율 자동 계산
    1. 기본 할인: YearAllocation.base_discount
    2. 브랜드/그룹 할인: CustomerDiscount (패턴 매칭)
    3. 추가 할인: CustomerProductDiscount
    4. DOT 할인: YearAllocation.year_XXXX_discount

    계산식: 정가 × (1-r1) × (1-r2) × (1-r3) × (1-r4)
    """
    # 1. 정가 조회
    unit_price = goods.fixp

    # 2. 기본 할인율
    basic_discount_rate = get_basic_discount(product_code)

    # 3. 고객 브랜드/그룹 할인율
    customer_discount_rate = get_customer_discount(customer_code, brand, product_name)

    # 4. 고객 상품 추가 할인율
    additional_discount_rate = get_additional_discount(customer_code, product_code)

    # 5. DOT 할인율
    dot_discount_rate = get_dot_discount(product_code, selected_year)

    # 6. 복리 계산 (순차 적용)
    total_discount_rate = (
        basic_discount_rate +
        customer_discount_rate +
        additional_discount_rate +
        dot_discount_rate
    )

    discounted_price = unit_price * (1 - total_discount_rate / 100)

    return {
        'unit_price': unit_price,
        'basic_discount_rate': basic_discount_rate,
        'customer_discount_rate': customer_discount_rate,
        'additional_discount_rate': additional_discount_rate,
        'dot_discount_rate': dot_discount_rate,
        'total_discount_rate': total_discount_rate,
        'discounted_price': discounted_price,
    }
```

**수학적 정확성**:
- 복리 계산 방식 적용 (순차 할인)
- 소수점 2자리까지 정확도 보장
- Decimal 타입 사용으로 부동소수점 오류 방지

---

### 2.3 브랜드 그룹 패턴 매칭 시스템

#### 데이터 구조
```
BrandGroup (브랜드 그룹)
├─ brand: "피렐리"
├─ group_name: "P ZERO 시리즈"
├─ group_order: 1
└─ patterns (BrandGroupPattern)
    ├─ "P ZERO"
    ├─ "P ZERO NERO"
    ├─ "P ZERO ROSSO"
    └─ "P ZERO RUN FLAT"
```

#### 패턴 매칭 알고리즘
```python
def find_product_groups(product_name, brand):
    """
    상품명과 브랜드로 해당하는 그룹 찾기
    - 대소문자 구분 없음
    - 부분 일치 검색
    - 우선순위 순서 정렬
    """
    groups = BrandGroup.objects.filter(brand=brand, is_active=True)
    matched_groups = []

    for group in groups:
        patterns = group.patterns.all()
        for pattern in patterns:
            if pattern.pattern.upper() in product_name.upper():
                matched_groups.append(group)
                break

    return matched_groups
```

**최적화**:
- DB 쿼리 최소화 (prefetch_related)
- 메모리 캐싱 (함수 레벨)
- 인덱스 활용 (brand + is_active)

---

### 2.4 일괄 할인 적용 시스템

#### Admin Action 구현
```python
def apply_discount_to_all_customers(self, request, queryset):
    """
    선택한 브랜드/그룹에 대해 전체 고객에게 할인율 일괄 적용
    - 2단계 POST 처리
    - 중간 확인 페이지 표시
    - 트랜잭션 처리
    """
    if 'apply' in request.POST:
        # 실제 적용 로직
        for group in queryset:
            for customer in active_customers:
                CustomerDiscount.objects.update_or_create(
                    customer_code=customer.enno,
                    brand=group.brand,
                    group=group,
                    defaults={
                        'discount_rate': discount_rate,
                        'is_active': True,
                    }
                )
    else:
        # 중간 확인 페이지 렌더링
        return render(request, 'admin/apply_discount_to_all.html', context)
```

**구현 난이도**: ★★★★★
- Django Admin Action의 2단계 POST 처리
- Queryset 직렬화 문제 해결
- 대량 데이터 처리 최적화 (bulk_create)

---

### 2.5 커스텀 Admin Site

#### 사이드바 메뉴 재구성
```python
class TirePassAdminSite(admin.AdminSite):
    """
    3개 카테고리로 메뉴 재구성
    - A. 판매 (8개)
    - B. 할인 (6개)
    - C. 설정 (8개)
    """
    def get_app_list(self, request, app_label=None):
        app_dict = self._build_app_dict(request, app_label)

        # 모델별 카테고리 매핑
        category_mapping = {
            'goods': 'A. 판매',
            'mobileorder': 'A. 판매',
            # ... (총 22개 모델)
        }

        # 카테고리별 그룹화
        categorized = {
            'A. 판매': {'models': []},
            'B. 할인': {'models': []},
            'C. 설정': {'models': []},
        }

        # 분류 및 정렬
        for app in app_dict.values():
            for model in app['models']:
                category = category_mapping.get(model['object_name'].lower())
                if category:
                    categorized[category]['models'].append(model)

        return [categorized['A. 판매'], categorized['B. 할인'], categorized['C. 설정']]
```

**기술적 의의**:
- Django Admin의 기본 앱 구조를 완전히 재정의
- 사용자 경험(UX) 최적화
- 직관적인 메뉴 구조

---

## 3. 모바일 시스템

### 3.1 RESTful API 설계

#### API 엔드포인트
```
GET  /api/mobile/products/              # 상품 목록
GET  /api/mobile/products/:code/        # 상품 상세
POST /api/mobile/cart/add/              # 장바구니 추가
GET  /api/mobile/calculate-quote/       # 견적 계산
POST /api/mobile/orders/create/         # 주문 생성
```

#### 응답 형식
```json
{
    "success": true,
    "data": {
        "product": {
            "code": "P-PZERO-25",
            "name": "피렐리 P ZERO 255/40R20",
            "brand": "피렐리",
            "stock": 10
        },
        "price_info": {
            "unit_price": 300000,
            "basic_discount_rate": 20.0,
            "customer_discount_rate": 4.0,
            "additional_discount_rate": 0.0,
            "dot_discount_rate": 3.0,
            "total_discount_rate": 27.0,
            "discounted_price": 219000
        }
    }
}
```

**설계 원칙**:
- RESTful 규칙 준수
- 일관된 응답 형식
- 에러 처리 표준화

### 3.2 프론트엔드 아키텍처

#### 순수 JavaScript 구현
```javascript
// 상태 관리
const state = {
    customer_code: null,
    cart: [],
    products: []
};

// API 호출
async function fetchProducts(search = '') {
    const response = await fetch(`/api/mobile/products/?search=${search}`);
    const data = await response.json();
    return data;
}

// DOM 조작
function renderProducts(products) {
    const container = document.getElementById('productList');
    container.innerHTML = products.map(product => `
        <div class="product-card">
            <h3>${product.name}</h3>
            <p>${product.discounted_price.toLocaleString()}원</p>
        </div>
    `).join('');
}
```

**기술적 특징**:
- 프레임워크 없이 순수 JavaScript 구현
- Fetch API 사용 (비동기 처리)
- LocalStorage 활용 (인증 토큰)

---

## 4. 보안 및 최적화

### 4.1 보안 구현

#### 인증 시스템
- Django Session 기반 인증
- CSRF 토큰 검증
- XSS 방어 (템플릿 자동 이스케이핑)
- SQL Injection 방어 (ORM 사용)

#### API 보안
```python
@login_required
def api_view(request):
    customer_code = request.GET.get('customer_code')

    # 권한 검증
    if request.user.username != customer_code:
        return JsonResponse({'success': False, 'message': '권한 없음'})

    # 비즈니스 로직
```

### 4.2 성능 최적화

#### 데이터베이스 최적화
- 인덱스 설정 (goods_code, customer_code, brand)
- select_related / prefetch_related 활용
- 쿼리 최소화 (N+1 문제 해결)

#### 캐싱 전략
- ERP 데이터: 캐싱 없음 (실시간성 우선)
- 정적 데이터: 브라우저 캐싱 (24시간)
- API 응답: 압축 전송 (gzip)

---

## 5. 테스트 및 품질 관리

### 5.1 테스트 전략
- **단위 테스트**: 할인 계산 함수, 패턴 매칭
- **통합 테스트**: API 엔드포인트, ERP 연동
- **UI 테스트**: 모바일 화면 수동 테스트
- **부하 테스트**: 동시 접속 100명 시나리오

### 5.2 코드 품질
- PEP 8 스타일 가이드 준수
- 함수/클래스 주석 작성 (Docstring)
- 변수명 명확성 (한글 주석 병행)
- Git 커밋 메시지 규칙

---

## 6. 배포 및 운영

### 6.1 배포 프로세스
```bash
# 1. 로컬 개발 및 테스트
git commit -m "기능 구현"
git push origin main

# 2. PythonAnywhere 배포
cd ~/tirepass
git pull origin main
touch /var/www/tirepass_pythonanywhere_com_wsgi.py

# 3. 검증
curl https://tirepass.pythonanywhere.com/health
```

### 6.2 모니터링
- ERP 연동 상태: ERPSnapshot 모델
- 실시간 재고 변화: GoodsRealtimeSnapshot
- 관리자 활동 로그: LogEntry
- 에러 로그: PythonAnywhere 로그

---

## 7. 기술적 난제 및 해결

### 7.1 ERP 데이터를 Django Admin에 표시
**문제**: Django Admin은 ORM 기반, ERP는 외부 API
**해결**: changelist_view 완전 오버라이드, API 데이터를 Admin 형식으로 변환

### 7.2 Queryset 직렬화 불가
**문제**: Admin Action에서 queryset을 템플릿으로 전달 불가
**해결**: queryset을 list(queryset.values())로 변환하여 전달

### 7.3 복잡한 할인 계산
**문제**: 4단계 할인율을 어떻게 적용할 것인가
**해결**: 순차적 복리 계산 방식 채택, Decimal 타입으로 정확도 보장

### 7.4 대량 할인 적용 성능
**문제**: 2,500+ 고객에게 일괄 적용 시 속도 저하
**해결**: bulk_create 사용, 트랜잭션 처리, 진행 상황 표시

---

## 8. 결론

TirePASS는 Django의 강력한 ORM과 Admin 시스템을 활용하면서도, ERP 실시간 연동이라는 특수한 요구사항을 충족하기 위해 다양한 커스터마이징 기법을 적용한 프로젝트입니다.

특히 Django Admin의 기본 동작 방식을 완전히 우회하면서도 Admin의 모든 기능(검색, 필터, 페이지네이션, 액션)을 유지한 점, 4단계 할인 시스템을 수학적으로 정확하게 구현한 점, 브랜드 그룹 패턴 매칭 시스템을 통해 유연한 할인 정책을 자동화한 점이 기술적 성과입니다.

순수 JavaScript로 구현한 모바일 시스템은 프레임워크 없이도 현대적인 SPA와 유사한 사용자 경험을 제공하며, RESTful API 설계를 통해 향후 네이티브 앱으로의 확장도 용이합니다.

---

**(주)플로우젠**
**기술이사 개발팀**
