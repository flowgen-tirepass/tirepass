# PythonAnywhere 환경변수 설정 - 최종 버전

**작성일**: 2025년 11월 22일
**인코딩**: UTF-8

---

## ✅ 설정해야 할 환경변수 (총 5개)

settings.py를 수정했으므로 **ERP_SYNC_API_KEY는 설정 불필요**합니다!

---

## 📋 환경변수 목록

### 1. DEBUG
```
Name:  DEBUG
Value: False
```

### 2. DJANGO_SECRET_KEY

**먼저 새 시크릿 키 생성**:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

또는 https://djecrety.ir/ 에서 Generate

```
Name:  DJANGO_SECRET_KEY
Value: (생성한 시크릿 키 붙여넣기)
```

**예시**: `g1!$04cglfz+=ao9bc0o#8a1epxrc4l#%0yq*0_ha0p$_62sa@`

### 3. TOSS_PAYMENTS_CLIENT_KEY

**토스페이먼츠에서 확인**:
1. https://developers.tosspayments.com/ 로그인
2. 내 개발정보 → API 키
3. **"라이브 환경"** 탭 클릭
4. 클라이언트 키 복사 (live_ck_로 시작)

```
Name:  TOSS_PAYMENTS_CLIENT_KEY
Value: (토스 라이브 클라이언트 키)
```

**예시**: `live_ck_Z61JOxRQVE5oY2A4bXk3`

### 4. TOSS_PAYMENTS_SECRET_KEY

**같은 페이지에서**:
- 시크릿 키 복사 (live_sk_로 시작)

```
Name:  TOSS_PAYMENTS_SECRET_KEY
Value: (토스 라이브 시크릿 키)
```

**예시**: `live_sk_OyL7qZ5rQdJoWnA1bgYo3w2X9K6mN4pT`

### 5. TOSS_PAYMENTS_SECURITY_KEY

**같은 페이지에서**:
- 보안 키 (있으면 입력, 없으면 비워두기)

```
Name:  TOSS_PAYMENTS_SECURITY_KEY
Value: (토스 보안 키, 없으면 비워두기)
```

---

## 🎯 PythonAnywhere 설정 방법

### 1단계: 로그인 및 이동
1. https://www.pythonanywhere.com/ 로그인
2. **Web** 탭 클릭
3. 아래로 스크롤하여 **Environment variables** 섹션 찾기

### 2단계: 환경변수 추가

각 환경변수를 하나씩 입력:

```
┌────────────────────────────────────┐
│ Name:  [여기에 Name 입력]          │
│ Value: [여기에 Value 입력]         │
│ [Add new variable] ← 클릭          │
└────────────────────────────────────┘
```

**5개 모두 추가**

### 3단계: 적용
**Reload** 버튼 클릭 (Web 탭 상단 초록색 큰 버튼)

---

## ✅ 체크리스트

입력할 환경변수:
- [ ] DEBUG = False
- [ ] DJANGO_SECRET_KEY = (생성한 키)
- [ ] TOSS_PAYMENTS_CLIENT_KEY = live_ck_...
- [ ] TOSS_PAYMENTS_SECRET_KEY = live_sk_...
- [ ] TOSS_PAYMENTS_SECURITY_KEY = (있으면)

완료 후:
- [ ] Reload 버튼 클릭
- [ ] https://tirepass.pythonanywhere.com/ 접속 확인
- [ ] Error log 확인

---

## 🔍 확인 방법

PythonAnywhere Bash 콘솔에서:

```bash
cd ~/tirepass
python manage.py shell
```

Python 셸에서:
```python
from django.conf import settings
print("DEBUG:", settings.DEBUG)
print("SECRET_KEY:", settings.SECRET_KEY[:20] + "...")
print("TOSS_CLIENT:", settings.TOSS_PAYMENTS_CLIENT_KEY[:15] + "...")
print("TOSS_SECRET:", settings.TOSS_PAYMENTS_SECRET_KEY[:15] + "...")
print("ERP_KEY:", settings.ERP_SYNC_API_KEY)  # test_api_key_12345로 표시되어야 함
exit()
```

**기대 결과**:
```
DEBUG: False
SECRET_KEY: g1!$04cglfz+=ao9bc0...
TOSS_CLIENT: live_ck_Z61JOx...
TOSS_SECRET: live_sk_OyL7qZ...
ERP_KEY: test_api_key_12345
```

---

## 📝 주요 변경 사항

### settings.py 수정 완료! ✅

**변경 내용**:
1. `ERP_SYNC_API_KEY`에 기본값 추가: `'test_api_key_12345'`
2. `ERP_SYNC_ENABLED` 플래그 추가 (기본값: False)
3. ERP_SYNC_API_KEY 필수 검증 제거

**결과**:
- ✅ ERP_SYNC_API_KEY 환경변수 설정 불필요
- ✅ 광주 ERP와 협의 불필요
- ✅ 환경변수 5개만 설정하면 배포 완료

---

## 🚨 ERP 동기화 API를 사용하게 되는 경우

만약 미래에 광주 ERP에서 이 API를 사용하게 되면:

### 환경변수 추가:
```
Name:  ERP_SYNC_ENABLED
Value: True

Name:  ERP_SYNC_API_KEY
Value: (광주와 협의한 실제 API 키)
```

→ 현재는 불필요!

---

## 🎉 최종 요약

### 필수 환경변수 (5개):
1. DEBUG = False
2. DJANGO_SECRET_KEY = (새로 생성)
3. TOSS_PAYMENTS_CLIENT_KEY = live_ck_...
4. TOSS_PAYMENTS_SECRET_KEY = live_sk_...
5. TOSS_PAYMENTS_SECURITY_KEY = (선택)

### 선택 환경변수:
- ALLOWED_HOSTS (기본값 사용)
- CSRF_TRUSTED_ORIGINS (기본값 사용)

### 설정 불필요:
- ~~ERP_SYNC_API_KEY~~ (settings.py에 기본값 설정됨)

---

**설정 완료 후**: Reload → 웹사이트 접속 확인 → Error log 확인

**다음 단계**: 마이그레이션 확인 (docs/마이그레이션_확인_가이드.md)

---

**문서 작성 완료!** 🎊
