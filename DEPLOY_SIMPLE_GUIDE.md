# 🚀 간단 배포 가이드 (웹 콘솔 사용)

SSH 접속 없이 PythonAnywhere 웹 콘솔에서 직접 배포하는 방법입니다.

## 📌 1단계: Bash 콘솔 열기

1. https://www.pythonanywhere.com/user/jmyang/consoles/ 접속
2. **"Bash"** 콘솔 클릭 (또는 새 Bash 콘솔 생성)

## 📌 2단계: 코드 업데이트

Bash 콘솔에서 다음 명령어를 **순서대로** 입력:

```bash
# 프로젝트 디렉토리로 이동
cd ~/tirepass

# 최신 코드 가져오기
git pull origin main
```

**예상 출력:**
```
From https://github.com/flowgen-tirepass/tirepass
   2b0cf36..9056995  main       -> origin/main
Updating 2b0cf36..9056995
Fast-forward
 tire_data/admin.py           | 6 +++---
 DEPLOY_POINT_UI_FIX.md       | 194 +++++++++++++++++++
 2 files changed, 197 insertions(+), 3 deletions(-)
```

## 📌 3단계: 웹앱 재시작

### 방법 A: 웹 인터페이스 사용 (가장 간단!)

1. https://www.pythonanywhere.com/user/jmyang/webapps/ 접속
2. **tirepass.pythonanywhere.com** 찾기
3. 초록색 **"Reload tirepass.pythonanywhere.com"** 버튼 클릭
4. "✓ Reloaded" 메시지 확인

### 방법 B: 콘솔에서 재시작

Bash 콘솔에서 다음 명령어 실행:

```bash
# 웹앱 재시작
touch /var/www/jmyang_pythonanywhere_com_wsgi.py
```

또는

```bash
# PythonAnywhere 헬퍼 스크립트 사용
pa_reload_webapp.py tirepass.pythonanywhere.com
```

## 📌 4단계: 배포 확인

1. 브라우저에서 Ctrl+Shift+Delete로 **캐시 삭제**
2. https://tirepass.pythonanywhere.com/admin/tire_data/customers/0-1-0002/change/ 접속
3. **F5** 또는 **Ctrl+F5**로 강력 새로고침
4. "포인트 정보" 섹션 확인:

```
포인트 정보
├─ 보유 포인트: 0P ✅
└─ 포인트 지급/차감 폼: ✅ (이제 보여야 함!)
   ├─ [포인트 금액 입력]
   ├─ [유형 선택: ➕ 지급 / ➖ 차감]
   ├─ [사유 입력]
   └─ [포인트 적용] 버튼
```

## 🔧 SSH 비밀번호 문제 해결 (선택사항)

SSH 접속이 필요한 경우:

### 옵션 1: SSH 비밀번호 재설정

1. https://www.pythonanywhere.com/user/jmyang/account/ 접속
2. "SSH password" 섹션 찾기
3. 새 비밀번호 설정

### 옵션 2: SSH 키 등록 (추천)

1. 로컬에서 SSH 키 생성 (이미 있다면 스킵):
   ```bash
   ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
   ```

2. 공개키 복사:
   ```bash
   cat ~/.ssh/id_rsa.pub
   ```

3. PythonAnywhere에 등록:
   - https://www.pythonanywhere.com/user/jmyang/ssh/ 접속
   - 공개키 붙여넣기
   - Save 클릭

4. 다음부터는 비밀번호 없이 접속:
   ```bash
   ssh jmyang@ssh.pythonanywhere.com
   ```

## 💡 참고사항

- **웹 콘솔 방법**이 가장 간단하고 확실합니다
- 배포 후 반드시 **브라우저 캐시를 삭제**하세요
- 웹앱 재시작은 **필수**입니다 (안 하면 변경사항이 적용되지 않음!)
- 문제가 있으면 에러 로그 확인:
  ```bash
  tail -50 /var/log/jmyang.pythonanywhere.com.error.log
  ```

## ✅ 성공 확인

배포가 성공했다면:
- ✅ 포인트 조정 폼이 화면에 표시됨
- ✅ 배송지 테이블도 정상 표시됨
- ✅ 테스트 포인트 지급 가능

테스트 방법:
1. 포인트 금액: `1000` 입력
2. 유형: "➕ 포인트 지급" 선택
3. 사유: "배포 테스트" 입력
4. "포인트 적용" 클릭
5. "✅ [고객명]님에게 1,000P를 지급했습니다" 메시지 확인
