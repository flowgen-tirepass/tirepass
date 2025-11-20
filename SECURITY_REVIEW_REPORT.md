# 타이어패스 보안 검토 보고서

**검토 일자**: 2025년 1월
**검토 범위**: 전체 시스템 (관리자 + 모바일 주문 시스템)
**검토자**: Claude Code AI

---

## 📊 요약

| 항목 | 개수 | 위험도 |
|------|------|--------|
| 치명적 취약점 | 3개 | ⛔️ 매우 높음 |
| 중간 위험 | 2개 | ⚠️ 중간 |
| 낮은 위험 | 1개 | ⚡ 낮음 |
| 양호 | 2개 | ✅ 양호 |

---

## ⛔️ 치명적 취약점 (즉시 수정 필요)

### 1. CSRF 보호 비활성화 (@csrf_exempt 남용)

**파일**: `tire_data/api_views_mobile.py`

**취약한 API 목록**:
```python
Line 512: @csrf_exempt api_cart_add_simple()        # 장바구니 추가
Line 568: @csrf_exempt api_payment_prepare_toss()   # 결제 준비
Line 601: @csrf_exempt api_payment_confirm_toss()   # 결제 확인
Line 680: @csrf_exempt api_payment_method_delete()  # 결제수단 삭제
Line 721: @csrf_exempt api_payment_method_update_nickname() # 결제수단 수정
Line 775: @csrf_exempt api_payment_method_billing_auth()    # 빌링키 발급
Line 898: @csrf_exempt api_payment_method_add()     # 결제수단 등록
Line 1145: @csrf_exempt api_customer_info()         # 고객정보 조회
```

**공격 시나리오**:
1. 공격자가 악성 사이트에 다음 코드 삽입:
```html
<form action="https://tirepass.pythonanywhere.com/api/mobile/cart/add" method="POST">
  <input type="hidden" name="customer_code" value="피해자코드">
  <input type="hidden" name="product_code" value="비싼타이어">
  <input type="hidden" name="quantity" value="100">
</form>
<script>document.forms[0].submit();</script>
```
2. 로그인한 사용자가 악성 사이트 방문
3. 사용자 모르게 장바구니에 상품 추가됨
4. 결제수단 조작 또는 무단 결제 가능

**해결 방법**:
```python
# ❌ 현재 (위험)
@csrf_exempt
@require_http_methods(["POST"])
def api_cart_add_simple(request):
    data = json.loads(request.body)
    customer_code = data.get('customer_code')
    # ...

# ✅ 수정 후 (안전)
@require_http_methods(["POST"])
def api_cart_add_simple(request):
    # 세션에서 customer_code 가져오기 (신뢰할 수 있는 출처)
    customer_code = request.session.get('customer_code')
    if not customer_code:
        return JsonResponse({'success': False, 'error': '로그인이 필요합니다.'}, status=401)

    data = json.loads(request.body)
    # CSRF 토큰은 Django 미들웨어가 자동 검증
    # ...
```

**긴급도**: 🔴 **최우선 수정**

---

### 2. 인증 없는 API 접근 (Session Authentication 누락)

**파일**: `tire_data/api_views_mobile.py`

**문제**:
- 모든 API가 `customer_code`를 클라이언트에서 받음
- 세션 기반 인증 없음
- 공격자가 다른 사용자의 `customer_code`를 알면 그 사용자로 행동 가능

**공격 시나리오**:
```python
# 공격자가 다른 고객 코드로 주문 조회
import requests
response = requests.get(
    'https://tirepass.pythonanywhere.com/api/mobile/customer/info/',
    json={'customer_code': '다른고객코드'}  # 다른 사람 코드
)
# 다른 고객의 개인정보, 주문내역 조회 가능
```

**영향받는 API**:
- `api_customer_info()` - 고객 정보 조회
- `api_cart_add_simple()` - 장바구니 조작
- `api_payment_method_*()` - 결제수단 조작
- 모든 주문 관련 API

**해결 방법**:
```python
# 모든 API에 적용할 데코레이터 생성
from functools import wraps
from django.http import JsonResponse

def mobile_login_required(view_func):
    """모바일 API 로그인 필수 데코레이터"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        customer_code = request.session.get('customer_code')
        if not customer_code:
            return JsonResponse({
                'success': False,
                'error': '로그인이 필요합니다.'
            }, status=401)
        return view_func(request, *args, **kwargs)
    return wrapper

# 적용
@mobile_login_required
@require_http_methods(["POST"])
def api_cart_add_simple(request):
    # customer_code는 세션에서만 가져옴 (클라이언트 입력 무시)
    customer_code = request.session.get('customer_code')
    # ...
```

**긴급도**: 🔴 **최우선 수정**

---

### 3. 민감 정보 하드코딩 (프로덕션 키 노출)

**파일**: `itire/settings.py`

**노출된 정보**:
```python
Line 23: TOSS_PAYMENTS_CLIENT_KEY = '...live_ck_jExPeJWYVQ1zDYG7N7PEV49R5gvN'
Line 24: TOSS_PAYMENTS_SECRET_KEY = '...live_sk_ex6BJGQOVDxgWD1LEMnaVW4w2zNb'
Line 25: TOSS_PAYMENTS_SECURITY_KEY = 'bddf753aff5f8aadb8aec10a1da97cae...'
Line 32: ERP_SYNC_API_KEY = 'tirepass_erp_sync_key_2024_change_in_production'
```

**위험**:
- GitHub에 업로드 시 전 세계 공개
- 공격자가 토스페이먼츠 키로 무단 결제 가능
- ERP 시스템 무단 접근 가능

**해결 방법**:
1. **PythonAnywhere 환경변수 설정**:
```bash
# PythonAnywhere Web 탭 → Environment variables
TOSS_PAYMENTS_CLIENT_KEY = live_ck_xxxxx
TOSS_PAYMENTS_SECRET_KEY = live_sk_xxxxx
TOSS_PAYMENTS_SECURITY_KEY = xxxxxxx
ERP_SYNC_API_KEY = real_secret_key
```

2. **settings.py 수정**:
```python
# ❌ 현재 (위험)
TOSS_PAYMENTS_SECRET_KEY = 'live_sk_ex6BJGQOVDxgWD1LEMnaVW4w2zNb'

# ✅ 수정 후 (안전)
TOSS_PAYMENTS_SECRET_KEY = os.environ.get('TOSS_PAYMENTS_SECRET_KEY')
if not TOSS_PAYMENTS_SECRET_KEY:
    raise ImproperlyConfigured('TOSS_PAYMENTS_SECRET_KEY must be set in environment variables')
```

3. **.gitignore에 추가**:
```
.env
*.env
local_settings.py
```

**긴급도**: 🔴 **최우선 수정**

---

## ⚠️ 중간 위험

### 4. 에러 메시지에 민감 정보 노출

**파일**: `tire_data/api_views_mobile.py`

**문제 위치**:
```python
Line 308: return JsonResponse({'success': False, 'error': str(e)}, status=500)
Line 560: return JsonResponse({'success': False, 'error': str(e)}, status=500)
Line 594: return JsonResponse({'success': False, 'error': str(e)}, status=500)
# 총 15개 이상의 예외 처리에서 동일한 패턴
```

**노출 가능한 정보**:
- 데이터베이스 테이블/컬럼명
- SQL 쿼리 구조
- 파일 경로
- 라이브러리 버전

**해결 방법**:
```python
# ❌ 현재
except Exception as e:
    logger.error(f"장바구니 추가 오류: {str(e)}")
    return JsonResponse({
        'success': False,
        'error': str(e)  # 위험: 내부 정보 노출
    }, status=500)

# ✅ 수정 후
except Exception as e:
    logger.error(f"장바구니 추가 오류: {str(e)}", exc_info=True)  # 로그에는 상세 기록
    return JsonResponse({
        'success': False,
        'error': '요청 처리 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.'  # 일반적인 메시지
    }, status=500)
```

**긴급도**: 🟡 **1주일 내 수정**

---

### 5. DEBUG=True 프로덕션 위험

**파일**: `itire/settings.py` Line 16

**문제**:
```python
DEBUG = os.environ.get('DEBUG', 'True') == 'True'  # 기본값이 True
```

**위험**:
- PythonAnywhere에서 환경변수 설정 안 하면 DEBUG 모드 활성화
- 에러 페이지에 전체 소스코드, 설정 노출
- SQL 쿼리 노출

**해결 방법**:
```python
# ✅ 수정 후
DEBUG = os.environ.get('DEBUG', 'False') == 'True'  # 기본값 False로 변경
```

**긴급도**: 🟡 **1주일 내 수정**

---

## ⚡ 낮은 위험

### 6. ALLOWED_HOSTS = '*' (와일드카드)

**파일**: `itire/settings.py` Line 18

**문제**:
```python
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*,localhost,127.0.0.1').split(',')
```

**위험**:
- Host 헤더 인젝션 공격 가능성 (낮음)

**해결 방법**:
```python
ALLOWED_HOSTS = os.environ.get(
    'ALLOWED_HOSTS',
    'tirepass.pythonanywhere.com,localhost,127.0.0.1'
).split(',')
```

**긴급도**: 🟢 **2주일 내 수정**

---

## ✅ 양호한 부분

### 7. SQL Injection 방어 (양호)
- Django ORM 사용으로 SQL Injection 위험 거의 없음
- 원시 SQL 쿼리 사용 없음

### 8. 비밀번호 해싱 (양호)
- `django.contrib.auth.hashers.make_password()` 사용 (Line 1105)
- PBKDF2 알고리즘으로 안전하게 해싱

---

## 📋 추가 개선 사항

### 9. 누락된 모바일 페이지

**현재 MOBILE_USER_MANUAL.md에만 언급, 실제 페이지 없음**:
- `/mobile/terms/` - 이용약관 상세
- `/mobile/privacy/` - 개인정보처리방침 상세
- `/mobile/refund/` - 반품/환불 정책
- `/mobile/faq/` - 자주 묻는 질문
- `/mobile/support/` - 고객지원 (연락처)

**법적 요구사항**:
- 전자상거래법: 이용약관, 환불정책 필수
- 개인정보보호법: 개인정보처리방침 필수

---

## 🔧 수정 우선순위

### Phase 1: 긴급 수정 (오늘 완료)
1. ✅ CSRF 보호 복원 (모든 @csrf_exempt 제거)
2. ✅ 세션 기반 인증 추가 (mobile_login_required 데코레이터)
3. ✅ settings.py 민감 정보 환경변수 이동

### Phase 2: 중요 수정 (1주일 내)
4. ⚠️ 에러 메시지 일반화 (내부 정보 숨김)
5. ⚠️ DEBUG=False 기본값 변경
6. ⚠️ 누락된 페이지 추가 (이용약관, 환불정책 등)

### Phase 3: 개선 (2주일 내)
7. 🟢 ALLOWED_HOSTS 명시적 설정
8. 🟢 보안 헤더 추가 (CSP, X-Content-Type-Options 등)
9. 🟢 Rate Limiting 추가 (무차별 대입 공격 방지)

---

## 📝 수정 체크리스트

- [ ] `@csrf_exempt` 제거 (8개 API)
- [ ] `mobile_login_required` 데코레이터 생성 및 적용
- [ ] 세션에서 customer_code 가져오도록 수정
- [ ] settings.py 민감 정보 환경변수 이동
- [ ] PythonAnywhere 환경변수 설정
- [ ] .gitignore에 .env 추가
- [ ] 에러 메시지 일반화 (15개 위치)
- [ ] DEBUG 기본값 False로 변경
- [ ] 이용약관 페이지 생성
- [ ] 개인정보처리방침 페이지 생성
- [ ] 반품/환불 정책 페이지 생성
- [ ] FAQ 페이지 생성
- [ ] 고객지원 페이지 생성

---

## 📞 긴급 문의

보안 취약점 발견 시:
- 광주 본사 IT 담당자에게 즉시 연락
- 시스템 일시 중단 검토

**최종 업데이트**: 2025년 1월
**다음 검토 예정**: 2025년 2월
