# 🚀 포인트 조정 기능 배포 가이드

## ✅ 완료된 단계

1. ✅ 코드 수정 완료 (tire_data/admin.py, views.py, urls.py, middleware.py)
2. ✅ GitHub에 커밋 및 푸시 완료
3. ✅ PythonAnywhere에서 `git pull origin main` 실행 완료

## 📌 다음 단계: 웹앱 재시작

### 방법 1: 웹 인터페이스 (가장 간단!)

1. **브라우저에서 접속**: https://www.pythonanywhere.com/user/tirepass/webapps/
2. **tirepass.pythonanywhere.com** 찾기
3. 초록색 **"Reload tirepass.pythonanywhere.com"** 버튼 클릭
4. "✓ Reloaded" 메시지 확인

### 방법 2: Bash 콘솔에서 실행

PythonAnywhere Bash 콘솔에서:

```bash
# 방법 A: touch 명령어
touch /var/www/tirepass_pythonanywhere_com_wsgi.py

# 방법 B: pa_reload_webapp.py 스크립트
pa_reload_webapp.py tirepass.pythonanywhere.com
```

## 🧪 테스트 방법

### 1단계: 페이지 접속

1. 브라우저 **캐시 삭제** (Ctrl+Shift+Delete)
2. 테스트 페이지 접속: https://tirepass.pythonanywhere.com/admin/tire_data/customers/0-1-0002/change/
3. **강력 새로고침** (Ctrl+F5 또는 Shift+F5)

### 2단계: UI 확인

다음 요소들이 보여야 합니다:

```
포인트 정보
├─ 보유 포인트: 0P
└─ 포인트 지급/차감
   ├─ [포인트 금액 (숫자만 입력)]  ← 높이가 충분히 큰 입력박스
   ├─ [➕ 포인트 지급 ▼]           ← 드롭다운 (텍스트 잘림 없음)
   ├─ [사유 (필수)]
   └─ [포인트 적용] 버튼
```

### 3단계: 포인트 지급 테스트

1. **포인트 금액**: `1000` 입력
2. **유형**: "➕ 포인트 지급" 선택 (기본값)
3. **사유**: `배포 테스트` 입력
4. **"포인트 적용"** 버튼 클릭

**예상 결과:**
```
✅ [고객명]님에게 1,000P를 지급했습니다. (현재 잔액: 1,000P)
```

### 4단계: 포인트 차감 테스트

1. **포인트 금액**: `500` 입력
2. **유형**: "➖ 포인트 차감" 선택
3. **사유**: `테스트 차감` 입력
4. **"포인트 적용"** 버튼 클릭

**예상 결과:**
```
✅ [고객명]님의 포인트 500P를 차감했습니다. (현재 잔액: 500P)
```

## 🔍 문제 해결

### CSRF 403 에러가 발생하면?

1. **미들웨어 확인**:
   ```bash
   cd ~/tirepass
   grep -n "AdminPointsCSRFExemptMiddleware" itire/settings.py
   ```
   → Line 71에 있어야 함

2. **에러 로그 확인**:
   ```bash
   tail -50 /var/log/tirepass.pythonanywhere.com.error.log
   ```

3. **웹앱 재시작 재시도**:
   ```bash
   touch /var/www/tirepass_pythonanywhere_com_wsgi.py
   ```

### 폼이 안 보이면?

1. **브라우저 캐시 완전 삭제**
2. **시크릿 모드**로 접속 시도
3. **에러 로그** 확인:
   ```bash
   tail -50 /var/log/tirepass.pythonanywhere.com.error.log
   ```

## 📝 변경된 파일 목록

```
tire_data/admin.py        → mark_safe() 사용, 레이아웃 개선
tire_data/middleware.py   → AdminPointsCSRFExemptMiddleware 추가
tire_data/urls.py         → /admin/adjust-points/<customer_id>/ 추가
tire_data/views.py        → adjust_customer_points_view() 추가
itire/settings.py         → 미들웨어 등록
```

## 🎯 핵심 기능

### 1. CSRF 검증 우회
- **미들웨어**: `AdminPointsCSRFExemptMiddleware`
- **적용 URL**: `/admin/adjust-points/`로 시작하는 모든 URL
- **보안**: Admin 로그인 + Staff 권한 필수

### 2. 포인트 조정
- **지급**: `CustomerPoint.add_points(amount, 'EARN_ADMIN', description)`
- **차감**: `CustomerPoint.use_points(amount, description)`
- **트랜잭션 기록**: `PointTransaction` 모델에 자동 저장

### 3. UI 개선
- 입력박스 높이: 44px (1.5배 증가)
- 드롭다운 텍스트: 전체 표시 (잘림 없음)
- 레이아웃: 수직 배치 (가독성 향상)

## ✅ 성공 확인 체크리스트

- [ ] 웹앱 Reload 완료
- [ ] 브라우저 캐시 삭제
- [ ] 폼이 화면에 표시됨
- [ ] 드롭다운 텍스트가 잘 보임 (잘림 없음)
- [ ] 입력박스 높이가 충분함
- [ ] 1,000P 지급 테스트 성공
- [ ] 500P 차감 테스트 성공
- [ ] 성공 메시지 표시됨
- [ ] CSRF 403 에러 없음

## 🆘 도움이 필요하면?

에러가 발생하면 다음 정보를 제공해주세요:

1. **에러 메시지** (화면에 표시된 메시지)
2. **에러 로그**:
   ```bash
   tail -100 /var/log/tirepass.pythonanywhere.com.error.log | grep -A 5 "adjust-points"
   ```
3. **스크린샷** (폼 화면 또는 에러 화면)

---

**마지막 업데이트**: 2025-11-18
**작성자**: Claude Code
