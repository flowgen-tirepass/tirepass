# PythonAnywhere 환경변수 설정 가이드

## 🔐 보안 업데이트 안내

2025년 1월 보안 패치 이후, 민감한 정보(토스페이먼츠 키, ERP API 키 등)가 소스코드에서 제거되었습니다.
**반드시 PythonAnywhere 환경변수로 설정해야 시스템이 정상 작동합니다.**

---

## 📋 설정 방법

### 1. PythonAnywhere 대시보드 접속
1. https://www.pythonanywhere.com 로그인
2. **Web** 탭 클릭
3. `tirepass.pythonanywhere.com` 선택

### 2. Environment variables 설정
**Web 탭 하단의 "Environment variables" 섹션으로 스크롤**

아래 변수들을 **하나씩** 추가:

```
이름(Name)                          값(Value)
──────────────────────────────────────────────────────────────
DEBUG                                False
TOSS_PAYMENTS_CLIENT_KEY             live_ck_jExPeJWYVQ1zDYG7N7PEV49R5gvN
TOSS_PAYMENTS_SECRET_KEY             live_sk_ex6BJGQOVDxgWD1LEMnaVW4w2zNb
TOSS_PAYMENTS_SECURITY_KEY           bddf753aff5f8aadb8aec10a1da97cae1cf5b06494ae82d18683e9a339e56971
ERP_SYNC_API_KEY                     [광주 본사에 문의하여 확인]
```

### 3. Web App Reload
환경변수 설정 후:
1. Web 탭 상단의 **"Reload tirepass.pythonanywhere.com"** 버튼 클릭
2. 1-2분 대기

---

## ✅ 설정 확인

### 방법 1: 웹사이트 접속
```
https://tirepass.pythonanywhere.com/mobile/login/
```
- 로그인 페이지가 정상적으로 로드되면 성공

### 방법 2: 에러 로그 확인
```
Web 탭 → Log files → Error log
```
- `❌ TOSS_PAYMENTS_CLIENT_KEY와 TOSS_PAYMENTS_SECRET_KEY는 환경변수로 설정해야 합니다!` 메시지가 **없으면** 성공

---

## 🔧 문제 해결

### 문제: "환경변수를 설정해야 합니다" 오류
**원인**: 환경변수가 설정되지 않았거나 오타

**해결책**:
1. Environment variables 섹션에서 변수명 철자 확인
2. 값에 공백이나 따옴표가 없는지 확인
3. Reload 버튼을 누른 후 1-2분 대기

### 문제: 500 Internal Server Error
**원인**: Python 코드 오류 또는 데이터베이스 연결 문제

**해결책**:
1. Error log 확인
2. 데이터베이스 비밀번호 확인 (DB_PASSWORD 환경변수)
3. Bash 콘솔에서 직접 확인:
```bash
cd /home/tirepass/1.0_tirepass
python3 manage.py check
```

### 문제: 토스페이먼츠 결제 실패
**원인**: TOSS_PAYMENTS_SECRET_KEY 오류

**해결책**:
1. 토스페이먼츠 대시보드에서 실제 Secret Key 재확인
2. 환경변수 값 복사/붙여넣기 시 공백 주의

---

## 📝 환경변수 목록 (전체)

| 변수명 | 필수 | 기본값 | 설명 |
|--------|------|--------|------|
| `DEBUG` | 선택 | False | 디버그 모드 (운영: False) |
| `DJANGO_SECRET_KEY` | 선택 | (자동 생성) | Django 암호화 키 |
| `ALLOWED_HOSTS` | 선택 | tirepass.pythonanywhere.com | 허용 호스트 |
| `TOSS_PAYMENTS_CLIENT_KEY` | **필수** | - | 토스 클라이언트 키 |
| `TOSS_PAYMENTS_SECRET_KEY` | **필수** | - | 토스 시크릿 키 |
| `TOSS_PAYMENTS_SECURITY_KEY` | 선택 | - | 토스 보안 키 |
| `ERP_SYNC_API_KEY` | **필수** | - | ERP API 인증 키 |
| `ERP_SYNC_API_URL` | 선택 | http://itire2.iptime.org:8000 | ERP API 주소 |
| `DB_PASSWORD` | 선택 | (자동 설정) | 데이터베이스 비밀번호 |
| `CSRF_TRUSTED_ORIGINS` | 선택 | https://tirepass.pythonanywhere.com | CSRF 신뢰 도메인 |

---

## 🔒 보안 주의사항

1. **절대 Git에 커밋하지 마세요**
   - `.env` 파일에 실제 키를 저장하지 마세요
   - `.env.example`은 템플릿이므로 괜찮습니다

2. **키 유출 시 조치**
   - 토스페이먼츠 대시보드에서 즉시 키 재발급
   - PythonAnywhere 환경변수 업데이트
   - Reload

3. **백업**
   - 환경변수 값을 안전한 장소(광주 본사 서버 등)에 백업
   - PythonAnywhere 계정 비밀번호도 안전하게 관리

---

## 📞 문의

- **광주 본사 IT 담당자**: [전화번호]
- **PythonAnywhere 지원**: help@pythonanywhere.com

**마지막 업데이트**: 2025년 1월
**작성자**: 타이어패스 개발팀
