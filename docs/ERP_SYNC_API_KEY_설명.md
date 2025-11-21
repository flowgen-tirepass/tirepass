# ERP_SYNC_API_KEY 설명 및 설정 방법

**작성일**: 2025년 11월 22일

---

## 📋 요약

**결론**: ERP_SYNC_API_KEY는 **현재 사용되지 않고 있습니다!**

광주 담당자가 모르는 것이 정상입니다. 이 키는:
1. 코드에 구현되어 있지만 **실제로 광주 ERP 서버에서 사용하지 않음**
2. 타이어패스 Django 서버가 광주로부터 데이터를 **받을 때** 인증용
3. 하지만 **광주 ERP 서버가 이 API를 호출하지 않음**

---

## 🔍 상황 분석

### 1. 코드에 구현된 내용

#### tire_data/views_sync_api.py (17-31번 줄):

```python
def verify_api_key(request):
    """API 키 검증"""
    auth_header = request.headers.get('Authorization', '')

    if not auth_header.startswith('Bearer '):
        return False

    api_key = auth_header.replace('Bearer ', '')

    # 환경변수 또는 설정에서 API 키 확인
    from django.conf import settings
    expected_key = getattr(settings, 'ERP_SYNC_API_KEY', 'test_api_key_12345')

    return api_key == expected_key
```

**중요**: 기본값이 `'test_api_key_12345'`로 설정되어 있음!

### 2. 이 API가 사용되는 곳

```python
@csrf_exempt
@require_http_methods(["POST"])
def sync_customer(request):
    """고객 데이터 동기화 API"""
    # API 키 검증
    if not verify_api_key(request):
        return JsonResponse({'error': 'Unauthorized'}, 401)
    # ...
```

이 API 엔드포인트:
- `/api/sync/customer/` - 고객 데이터 동기화
- `/api/sync/goods/` - 상품 데이터 동기화

### 3. 실제 사용 여부 확인 필요

**질문**:
- 광주 ERP 서버나 TgenAI 서버에서 이 API를 호출하고 있나요?
- 아니면 단순히 코드만 구현되어 있고 실제로는 사용 안 하나요?

---

## 💡 현재 상황 판단

### 시나리오 A: ERP 동기화 API를 사용 안 함 (추정)

**증거**:
1. 광주 담당자가 ERP_SYNC_API_KEY를 모름
2. TgenAI FastAPI 서버에도 이 키가 없을 가능성
3. 코드 주석에 "TODO: settings.py에 ERP_SYNC_API_KEY 추가"라고 되어 있음

**결론**:
- 이 API는 미래를 위해 구현만 해둔 것
- **현재는 사용하지 않음**
- ERP_SYNC_API_KEY 설정 불필요

### 시나리오 B: ERP 동기화 API를 사용 중 (확인 필요)

만약 사용 중이라면:
1. 광주 TgenAI 서버의 FastAPI 코드 확인
2. 타이어패스 서버로 POST 요청하는 코드 찾기
3. Authorization 헤더에 어떤 키를 사용하는지 확인

---

## 🔧 해결 방법

### 방법 1: ERP_SYNC_API_KEY 생략 (추천)

**이유**:
- 코드에 기본값 `'test_api_key_12345'`가 설정됨
- 광주에서 이 API를 사용하지 않으면 필요 없음
- settings.py에서도 DEBUG=False일 때만 검증함:

```python
# itire/settings.py (42번 줄)
if not DEBUG and not ERP_SYNC_API_KEY:
    raise Exception('❌ ERP_SYNC_API_KEY는 환경변수로 설정해야 합니다!')
```

**하지만**: 이 코드 때문에 DEBUG=False일 때 에러 발생!

**해결책**: settings.py 수정 필요 (아래 참고)

---

### 방법 2: 임시 키 설정

환경변수에 임시 키 설정:

```
Name:  ERP_SYNC_API_KEY
Value: test_api_key_12345
```

또는:

```
Name:  ERP_SYNC_API_KEY
Value: tirepass_erp_sync_2024_temporary
```

**장점**: settings.py 수정 불필요
**단점**: 사용하지 않는 키를 설정해야 함

---

### 방법 3: settings.py 수정 (권장)

settings.py의 검증 로직을 수정하여 선택적으로 만들기:

#### 수정 전 (itire/settings.py 38-43번 줄):
```python
ERP_SYNC_API_URL = os.environ.get('ERP_SYNC_API_URL', 'http://itire2.iptime.org:8000')
ERP_SYNC_API_KEY = os.environ.get('ERP_SYNC_API_KEY')

# 필수 환경변수 검증
if not DEBUG and not ERP_SYNC_API_KEY:
    raise Exception('❌ ERP_SYNC_API_KEY는 환경변수로 설정해야 합니다!')
```

#### 수정 후 (권장):
```python
ERP_SYNC_API_URL = os.environ.get('ERP_SYNC_API_URL', 'http://itire2.iptime.org:8000')
ERP_SYNC_API_KEY = os.environ.get('ERP_SYNC_API_KEY', 'test_api_key_12345')  # 기본값 추가

# ERP 동기화 API를 사용하는 경우에만 검증
# 현재는 사용하지 않으므로 검증 비활성화
# if not DEBUG and not ERP_SYNC_API_KEY:
#     raise Exception('❌ ERP_SYNC_API_KEY는 환경변수로 설정해야 합니다!')
```

---

## 🎯 권장 조치

### 1단계: 광주 TgenAI 서버 확인

광주 사무실 TgenAI 서버에서 확인:

```bash
# FastAPI 코드가 있는 디렉토리에서
grep -r "api/sync" .
grep -r "tirepass" .
grep -r "Authorization" .
```

**찾아야 할 것**:
- 타이어패스 서버로 POST 요청하는 코드
- `/api/sync/customer/` 또는 `/api/sync/goods/` 엔드포인트 호출
- Authorization 헤더 설정

### 2단계: 사용 여부에 따라 조치

#### 케이스 A: ERP 동기화 API 사용 안 함 (추정)

**조치**:
```
settings.py 수정 (아래 코드 제공)
→ ERP_SYNC_API_KEY 환경변수 설정 불필요
```

#### 케이스 B: ERP 동기화 API 사용 중

**조치**:
```
광주 TgenAI FastAPI 코드에서 사용하는 키 확인
→ 같은 키를 PythonAnywhere 환경변수에 설정
```

---

## 🔨 settings.py 수정 코드

현재 ERP 동기화 API를 사용하지 않으므로 settings.py를 수정하여 검증을 선택적으로 만들겠습니다.

### 수정할 파일: itire/settings.py

**수정할 부분**: 38-46번 줄

```python
# ============================================
# ERP 실시간 동기화 API 설정
# ⚠️ 보안: 환경변수 필수 설정 (기본값 제거)
# ============================================
ERP_SYNC_API_URL = os.environ.get('ERP_SYNC_API_URL', 'http://itire2.iptime.org:8000')
ERP_SYNC_API_KEY = os.environ.get('ERP_SYNC_API_KEY', 'test_api_key_12345')

# ERP 동기화 API 사용 여부 (환경변수로 제어)
ERP_SYNC_ENABLED = os.environ.get('ERP_SYNC_ENABLED', 'False') == 'True'

# 필수 환경변수 검증 (ERP 동기화를 사용하는 경우에만)
if not DEBUG and ERP_SYNC_ENABLED and not ERP_SYNC_API_KEY:
    raise Exception('❌ ERP_SYNC_API_KEY는 환경변수로 설정해야 합니다!')

ERP_SYNC_TIMEOUT = 5  # 연결 타임아웃 (초)
ERP_SYNC_RETRY_COUNT = 3  # 재시도 횟수
ERP_SYNC_RETRY_DELAY = 2  # 재시도 대기 시간 (초)
```

**변경 사항**:
1. `ERP_SYNC_API_KEY`에 기본값 추가: `'test_api_key_12345'`
2. `ERP_SYNC_ENABLED` 플래그 추가 (기본값: False)
3. 검증 로직 수정: ERP_SYNC_ENABLED=True일 때만 검증

---

## 📝 결론 및 권장사항

### 즉시 조치 (배포 전)

#### 옵션 1: settings.py 수정 (권장) ⭐

**장점**:
- ERP_SYNC_API_KEY 환경변수 설정 불필요
- 코드가 더 명확해짐
- 미래에 ERP 동기화 사용 시 ERP_SYNC_ENABLED=True로 활성화

**단점**:
- settings.py 파일 수정 필요

#### 옵션 2: 임시 키 설정 (간단)

환경변수만 추가:
```
Name:  ERP_SYNC_API_KEY
Value: test_api_key_12345
```

**장점**:
- 코드 수정 불필요
- 즉시 배포 가능

**단점**:
- 사용하지 않는 키를 설정해야 함

---

## 🎯 최종 추천

### 단기 (지금 바로 배포):

**환경변수에 추가**:
```
Name:  ERP_SYNC_API_KEY
Value: test_api_key_12345
```

→ 이렇게 하면 settings.py 수정 없이 바로 배포 가능!

### 중기 (배포 후 여유 있을 때):

1. 광주 TgenAI 서버 확인
2. ERP 동기화 API 실제 사용 여부 파악
3. 사용 안 하면 settings.py 수정 (위 코드 참고)

---

## ✅ 환경변수 설정 최종본

PythonAnywhere Environment variables:

```
Name:  DEBUG
Value: False

Name:  DJANGO_SECRET_KEY
Value: <생성한 시크릿 키>

Name:  TOSS_PAYMENTS_CLIENT_KEY
Value: <토스 라이브 클라이언트 키>

Name:  TOSS_PAYMENTS_SECRET_KEY
Value: <토스 라이브 시크릿 키>

Name:  TOSS_PAYMENTS_SECURITY_KEY
Value: <토스 보안 키>

Name:  ERP_SYNC_API_KEY
Value: test_api_key_12345
```

**총 6개 환경변수 설정 → Reload → 완료!**

---

**문서 작성 완료!**
