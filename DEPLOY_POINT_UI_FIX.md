# 포인트 관리 UI 수정사항 배포 가이드

## 📋 수정 내용
고객 관리자 페이지에서 "포인트 정보" 섹션과 포인트 조정 폼이 표시되지 않던 문제를 해결했습니다.

### 변경 사항
**커밋 1 (2b0cf36)**: fieldsets 수정
- `tire_data/admin.py` 파일의 `CustomersAdmin` 클래스 수정
- fieldsets에 누락된 `password`, `user_id` 필드 추가
- Django가 자동으로 필드를 재배치하는 문제 해결

**커밋 2 (3e3755e)**: 포인트 조정 폼 mark_safe 적용 ⭐ 핵심 수정
- `adjust_points_form()` 메서드에서 `format_html()` → `mark_safe()`로 변경
- Django Admin의 readonly_fields에서 HTML 렌더링 문제 해결
- short_description 추가

**커밋 3 (dffa445)**: 배송지 목록도 mark_safe 적용
- `shipping_addresses_display()` 메서드도 동일하게 수정
- 배송지 테이블이 제대로 렌더링되도록 개선

## 🚀 PythonAnywhere 배포 절차

### 1. SSH 접속
```bash
ssh jmyang@ssh.pythonanywhere.com
```

### 2. 프로젝트 디렉토리로 이동
```bash
cd ~/tirepass
```

### 3. Git Pull (최신 코드 가져오기)
```bash
git pull origin main
```

예상 출력:
```
remote: Enumerating objects: X, done.
remote: Counting objects: 100% (X/X), done.
remote: Compressing objects: 100% (X/X), done.
From https://github.com/flowgen-tirepass/tirepass
   2b0cf36..dffa445  main       -> origin/main
Updating 2b0cf36..dffa445
Fast-forward
 tire_data/admin.py | 6 +++---
 1 file changed, 3 insertions(+), 3 deletions(-)
```

### 4. 웹앱 재시작 (중요!)

#### 방법 1: 웹 콘솔 사용 (권장)
1. https://www.pythonanywhere.com/user/jmyang/webapps/ 접속
2. **tirepass.pythonanywhere.com** 웹앱 찾기
3. **"Reload" 버튼** 클릭 (초록색 버튼)

#### 방법 2: 명령어 사용
```bash
touch /var/www/jmyang_pythonanywhere_com_wsgi.py
```

또는

```bash
pa_reload_webapp.py tirepass.pythonanywhere.com
```

## ✅ 배포 확인

### 1. 관리자 페이지 접속
https://tirepass.pythonanywhere.com/admin/tire_data/customers/0-1-0002/change/

### 2. 확인할 내용
페이지를 새로고침하면 다음 섹션들이 순서대로 표시되어야 합니다:

```
✅ 기본 정보
   - 고객코드, 상호, 대표자, 전화1, 휴대전화, 사업자번호, 비밀번호

✅ 계정 상태
   - 회원가입여부, 사용자ID, 비밀번호변경필요

✅ 멤버십 등급
   - 회원등급, 등급갱신일

✅ 포인트 정보 ⭐ (새로 표시되는 섹션)
   ┌─────────────────────────────────────┐
   │ 고객의 포인트 잔액입니다.            │
   │ 아래 폼에서 포인트를 지급하거나       │
   │ 차감할 수 있습니다.                  │
   ├─────────────────────────────────────┤
   │ 보유 포인트: 0P                      │
   ├─────────────────────────────────────┤
   │ 현재 잔액: 0P                        │
   │                                     │
   │ [포인트 금액 입력]  [유형 선택]      │
   │                                     │
   │ [사유 입력]                          │
   │                                     │
   │ [포인트 적용] 버튼                   │
   │                                     │
   │ 📋 이 고객의 포인트 거래 내역 보기 → │
   └─────────────────────────────────────┘

✅ 등록된 배송지
   (접힌 상태로 표시)
```

### 3. 포인트 지급 테스트
1. **포인트 금액**: 1000 입력
2. **유형**: "➕ 포인트 지급" 선택
3. **사유**: "배포 테스트" 입력
4. **포인트 적용** 버튼 클릭

예상 결과:
```
✅ [고객명]님에게 1,000P를 지급했습니다. (현재 잔액: 1,000P)
```

## 🔍 문제 해결

### 포인트 정보 섹션이 여전히 안 보이는 경우

1. **브라우저 캐시 삭제**
   - Chrome: Ctrl+Shift+Delete
   - 강력 새로고침: Ctrl+F5 (Windows) / Cmd+Shift+R (Mac)

2. **웹앱 재시작 확인**
   ```bash
   # PythonAnywhere 웹 콘솔에서 Reload 버튼을 다시 클릭
   ```

3. **로그 확인**
   ```bash
   tail -n 50 /var/log/jmyang.pythonanywhere.com.error.log
   tail -n 50 /var/log/jmyang.pythonanywhere.com.server.log
   ```

4. **Python 프로세스 강제 재시작**
   - PythonAnywhere 웹 콘솔에서 "Force Reload" 또는
   - Kill all python processes 후 웹앱 재시작

### 에러가 발생하는 경우

```bash
# 에러 로그 확인
tail -n 100 /var/log/jmyang.pythonanywhere.com.error.log

# Python 문법 오류 체크
python3 -m py_compile ~/tirepass/tire_data/admin.py
```

## 📝 커밋 정보
- **커밋 1**: 2b0cf36 - Fix: 고객 관리 페이지에 포인트 정보 섹션이 표시되도록 수정
- **커밋 2**: 3e3755e - Fix: 포인트 조정 폼이 화면에 표시되지 않는 문제 해결 ⭐
- **커밋 3**: dffa445 - Fix: 배송지 목록 표시도 mark_safe로 수정
- **변경 파일**: tire_data/admin.py (총 3개 커밋)

## 🔍 기술 상세 (개발자용)

### 문제의 근본 원인
Django Admin의 `readonly_fields`에서 HTML을 반환하는 메서드를 작성할 때:

❌ **잘못된 방법**: `format_html()` 사용
```python
def my_field(self, obj):
    html = '<div>Some HTML</div>'
    return format_html(html)  # ← 작동하지 않음!
```

✅ **올바른 방법**: `mark_safe()` 사용
```python
def my_field(self, obj):
    from django.utils.safestring import mark_safe
    html = '<div>Some HTML</div>'
    return mark_safe(html)  # ← 정상 작동!
```

### 왜 이런 차이가 발생하나?
- `format_html()`: 전달된 문자열을 **이스케이프 처리**한 후 안전하게 표시 (HTML 태그가 문자 그대로 표시됨)
- `mark_safe()`: 문자열을 **신뢰할 수 있는 HTML**로 표시 (태그가 렌더링됨)

### 유사한 문제 발생 시 체크리스트
1. readonly_fields에 메서드가 포함되어 있는가?
2. 메서드가 HTML 문자열을 반환하는가?
3. `mark_safe()` 대신 `format_html()`을 사용했는가?
4. → Yes라면 `mark_safe()`로 변경 필요!

## 💡 참고사항
- 이 수정사항은 기존 데이터에 영향을 주지 않습니다
- 데이터베이스 마이그레이션 불필요
- 정적 파일 재수집 불필요
- 웹앱 재시작만으로 즉시 적용 가능
