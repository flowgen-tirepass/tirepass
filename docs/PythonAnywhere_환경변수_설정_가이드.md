# PythonAnywhere 환경변수 설정 가이드

**작성일**: 2025년 11월 22일

---

## 📋 설정해야 할 환경변수 목록

아래 환경변수들을 PythonAnywhere에 설정해야 합니다.

### 필수 환경변수

```bash
DEBUG=False
DJANGO_SECRET_KEY=<새로운-강력한-시크릿-키>
TOSS_PAYMENTS_CLIENT_KEY=<토스페이먼츠-라이브-클라이언트-키>
TOSS_PAYMENTS_SECRET_KEY=<토스페이먼츠-라이브-시크릿-키>
TOSS_PAYMENTS_SECURITY_KEY=<토스페이먼츠-보안-키>
ERP_SYNC_API_KEY=<ERP-API-키>
```

### 선택적 환경변수 (기본값 사용 가능)

```bash
ALLOWED_HOSTS=tirepass.pythonanywhere.com,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=https://tirepass.pythonanywhere.com
DB_PASSWORD=<데이터베이스-비밀번호>
```

---

## 🔧 PythonAnywhere 환경변수 설정 방법

### 1단계: PythonAnywhere 로그인

1. https://www.pythonanywhere.com/ 접속
2. 계정으로 로그인

### 2단계: Web 탭으로 이동

1. 상단 메뉴에서 **"Web"** 클릭
2. 현재 실행 중인 웹 앱 확인 (tirepass.pythonanywhere.com)

### 3단계: 환경변수 섹션 찾기

1. Web 탭 페이지를 아래로 스크롤
2. **"Environment variables"** 섹션 찾기
   - "Code:" 섹션 아래에 위치
   - "WSGI configuration file:" 위에 위치

### 4단계: 환경변수 추가

각 환경변수를 하나씩 추가합니다:

#### DEBUG 설정
```
Name:  DEBUG
Value: False
```
→ **"Add new variable"** 버튼 클릭

#### DJANGO_SECRET_KEY 설정

**먼저 새로운 시크릿 키를 생성해야 합니다:**

```python
# 로컬에서 Python 실행
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
# 출력된 키를 복사
```

또는 온라인에서 생성:
- https://djecrety.ir/ 접속
- "Generate" 클릭
- 생성된 키 복사

```
Name:  DJANGO_SECRET_KEY
Value: <생성된-시크릿-키-붙여넣기>
```
→ **"Add new variable"** 버튼 클릭

#### TOSS_PAYMENTS_CLIENT_KEY 설정

```
Name:  TOSS_PAYMENTS_CLIENT_KEY
Value: <토스페이먼츠에서 발급받은 라이브 클라이언트 키>
```
→ **"Add new variable"** 버튼 클릭

**토스페이먼츠 키 확인 방법:**
1. https://developers.tosspayments.com/ 로그인
2. 내 개발정보 → API 키 메뉴
3. **라이브 환경** 탭 선택
4. "클라이언트 키" 복사 (live_ck_로 시작)

#### TOSS_PAYMENTS_SECRET_KEY 설정

```
Name:  TOSS_PAYMENTS_SECRET_KEY
Value: <토스페이먼츠에서 발급받은 라이브 시크릿 키>
```
→ **"Add new variable"** 버튼 클릭

**토스페이먼츠 시크릿 키 확인:**
1. 같은 페이지에서 "시크릿 키" 복사 (live_sk_로 시작)

#### TOSS_PAYMENTS_SECURITY_KEY 설정

```
Name:  TOSS_PAYMENTS_SECURITY_KEY
Value: <토스페이먼츠 보안 키>
```
→ **"Add new variable"** 버튼 클릭

#### ERP_SYNC_API_KEY 설정

```
Name:  ERP_SYNC_API_KEY
Value: <광주 ERP 서버와 약속한 API 키>
```
→ **"Add new variable"** 버튼 클릭

**참고**: 이 키는 광주 ERP 서버에서 데이터를 전송할 때 인증에 사용됩니다.

#### ALLOWED_HOSTS 설정 (선택)

```
Name:  ALLOWED_HOSTS
Value: tirepass.pythonanywhere.com,localhost,127.0.0.1
```
→ **"Add new variable"** 버튼 클릭

**참고**: 설정하지 않으면 기본값이 사용됩니다.

#### CSRF_TRUSTED_ORIGINS 설정 (선택)

```
Name:  CSRF_TRUSTED_ORIGINS
Value: https://tirepass.pythonanywhere.com
```
→ **"Add new variable"** 버튼 클릭

---

## ✅ 환경변수 설정 확인

모든 환경변수를 추가한 후:

1. **"Reload"** 버튼 클릭 (페이지 상단 초록색 버튼)
   - 웹 앱을 재시작하여 환경변수를 적용합니다.

2. **설정 확인**:
   - PythonAnywhere 콘솔에서 확인:
   ```bash
   # Bash console 열기
   cd ~/tirepass
   echo $DEBUG
   echo $DJANGO_SECRET_KEY
   # 등등...
   ```

3. **Django에서 확인**:
   ```bash
   python manage.py shell
   ```
   ```python
   from django.conf import settings
   print(settings.DEBUG)  # False가 출력되어야 함
   print(settings.SECRET_KEY)  # 설정한 시크릿 키가 출력되어야 함
   print(settings.TOSS_PAYMENTS_CLIENT_KEY)  # live_ck_로 시작하는 키
   print(settings.TOSS_PAYMENTS_SECRET_KEY)  # live_sk_로 시작하는 키
   exit()
   ```

---

## 📸 스크린샷 가이드

### Environment variables 섹션 위치:

```
┌─────────────────────────────────────────────────────────┐
│ Web                                                      │
├─────────────────────────────────────────────────────────┤
│ Configuration for tirepass.pythonanywhere.com           │
│                                                          │
│ Code:                                                    │
│   Source code: /home/tirepass/tirepass                  │
│   Working directory: /home/tirepass/tirepass            │
│   WSGI configuration file: /var/www/...                 │
│                                                          │
│ Environment variables:                   ← 여기!        │
│   ┌────────────────────────────────────┐                │
│   │ Name: [____________]               │                │
│   │ Value: [____________]              │                │
│   │ [Add new variable]                 │                │
│   └────────────────────────────────────┘                │
│                                                          │
│   Existing variables:                                   │
│   • DEBUG = False                      [Remove]         │
│   • DJANGO_SECRET_KEY = django-ins... [Remove]         │
│   • TOSS_PAYMENTS_CLIENT_KEY = liv... [Remove]         │
│   ...                                                   │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## ⚠️ 주의 사항

### 1. 시크릿 키 보안

- **절대로** GitHub에 커밋하지 마세요
- **절대로** 다른 사람과 공유하지 마세요
- 시크릿 키가 노출되면 즉시 재생성하세요

### 2. DEBUG=False 확인

- 운영 환경에서는 **반드시** `DEBUG=False`
- `DEBUG=True`는 보안 취약점을 노출시킵니다

### 3. HTTPS 사용

- PythonAnywhere는 자동으로 HTTPS를 제공합니다
- 설정에서 HTTPS가 강제됩니다 (`SECURE_SSL_REDIRECT=True`)

### 4. 토스페이먼츠 키

- **라이브 환경** 키를 사용하세요 (live_ck_, live_sk_로 시작)
- 테스트 키 (test_ck_, test_sk_)는 운영 환경에서 작동하지 않습니다

---

## 🔄 환경변수 변경 시

환경변수를 변경한 후에는:

1. **"Reload" 버튼 클릭** (웹 앱 재시작)
2. 또는 Web 탭에서:
   ```
   [Reload tirepass.pythonanywhere.com] ← 이 버튼 클릭
   ```

---

## 📝 체크리스트

설정 완료 후 확인:

- [ ] DEBUG=False 설정됨
- [ ] DJANGO_SECRET_KEY 설정됨 (새로 생성한 키)
- [ ] TOSS_PAYMENTS_CLIENT_KEY 설정됨 (live_ck_로 시작)
- [ ] TOSS_PAYMENTS_SECRET_KEY 설정됨 (live_sk_로 시작)
- [ ] ERP_SYNC_API_KEY 설정됨
- [ ] 웹 앱 Reload 완료
- [ ] Django shell에서 확인 완료

---

## 🆘 문제 해결

### 환경변수가 적용되지 않는 경우:

1. **웹 앱 Reload**: 반드시 Reload 버튼을 클릭해야 합니다
2. **오타 확인**: 환경변수 이름에 오타가 없는지 확인
3. **공백 확인**: 값 앞뒤에 공백이 없는지 확인
4. **로그 확인**: Error log 탭에서 오류 메시지 확인

### Django 시작 실패 시:

Error log 확인:
```
Web 탭 → Error log → 최근 로그 확인
```

일반적인 오류:
- `TOSS_PAYMENTS_CLIENT_KEY는 환경변수로 설정해야 합니다!`
  → 환경변수를 설정하고 Reload
- `SECRET_KEY must not be empty`
  → DJANGO_SECRET_KEY 설정 확인

---

**설정 완료!** 환경변수가 모두 설정되면 시스템이 안전하게 운영됩니다.
