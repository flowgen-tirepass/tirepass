# TirePASS B2B 초기 론칭 가이드

B2B 서비스 초기 론칭 시 기존 고객 일괄 등록 및 초기 비밀번호 설정 가이드입니다.

---

## 📋 목차
1. [초기 계정 정책](#초기-계정-정책)
2. [일괄 등록 프로세스](#일괄-등록-프로세스)
3. [고객 안내 사항](#고객-안내-사항)
4. [기술 사양](#기술-사양)
5. [문제 해결](#문제-해결)

---

## 초기 계정 정책

### 🔐 계정 정보
- **아이디(로그인ID)**: 사업자등록번호 10자리
- **초기 비밀번호**: 사업자등록번호 뒤 5자리
- **비밀번호 변경**: 최초 로그인 시 **필수**

### 📝 예시
```
사업자등록번호: 123-45-67890

→ 아이디: 1234567890
→ 초기 비밀번호: 67890
→ 최초 로그인 후 새 비밀번호로 변경 필수 (최소 4자)
```

### ⚙️ 작동 방식
1. 고객이 초기 비밀번호로 로그인
2. 시스템이 `must_change_password` 플래그 확인
3. 플래그가 `true`인 경우 비밀번호 변경 페이지로 자동 리다이렉트
4. 비밀번호 변경 완료 후 정상 서비스 이용 가능

---

## 일괄 등록 프로세스

### Step 1: 환경 준비

#### 필수 패키지 설치
```bash
pip install fdb mysql-connector-python
```

#### ERP 서버 연결 확인
- **호스트**: ITIRE2.iptime.org
- **데이터베이스**: C:\Program Files\PsimCarS\Data\ITIRE.GDB
- **테이블**: CUSTOMS

### Step 2: 일괄 등록 스크립트 실행

```bash
python scripts/register_initial_customers.py
```

#### 스크립트 동작
1. ERP CUSTOMS 테이블에서 사업자등록번호가 있는 고객 조회
2. 각 고객의 사업자번호 뒤 5자리를 초기 비밀번호로 설정
3. Django `make_password()`로 비밀번호 해시화
4. `customers_simple` 테이블에 등록
   - `code`: 고객 코드
   - `name`: 상호
   - `enno`: 사업자등록번호 (10자리)
   - `password`: 해시화된 초기 비밀번호
   - `signup_source`: 'erp_initial'
   - `is_registered`: 1 (등록 완료)
   - `must_change_password`: 1 (변경 필수)

#### 실행 결과 예시
```
=================================================
TirePASS B2B 초기 고객 일괄 등록
=================================================

📋 작업 내용:
  - ERP에서 사업자등록번호가 있는 고객 가져오기
  - 사업자번호 뒤 5자리를 초기 비밀번호로 설정
  - customers_simple 테이블에 등록
  - 최초 로그인 시 비밀번호 변경 강제

계속 진행하시겠습니까? (y/n): y

=== ERP Firebird 서버 연결 중... ===
총 150명의 고객 데이터를 가져왔습니다.

=== MySQL 데이터베이스에 등록 중... ===

✅ 등록: C001 - (주)ABC타이어 (초기 비밀번호: 67890)
✅ 등록: C002 - (주)XYZ모터스 (초기 비밀번호: 12345)
...

============================================================
=== 등록 완료 ===
============================================================
✅ 신규 등록: 150명
ℹ️  이미 등록됨: 0명
⚠️  건너뜀: 5명 (사업자번호 오류)
❌ 에러: 0명
============================================================

🎉 총 150명의 고객이 신규 등록되었습니다.
```

### Step 3: 등록 결과 확인

#### MySQL 확인
```bash
mysql -uroot -ptirepass itire_db -e "
SELECT code, name, enno, is_registered, must_change_password, signup_source
FROM customers_simple
WHERE signup_source='erp_initial'
LIMIT 10;
"
```

#### 예상 결과
```
+------+--------------------+------------+---------------+----------------------+---------------+
| code | name               | enno       | is_registered | must_change_password | signup_source |
+------+--------------------+------------+---------------+----------------------+---------------+
| C001 | (주)ABC타이어      | 1234567890 |             1 |                    1 | erp_initial   |
| C002 | (주)XYZ모터스      | 9876543210 |             1 |                    1 | erp_initial   |
+------+--------------------+------------+---------------+----------------------+---------------+
```

### Step 4: 테스트

#### 로그인 테스트
1. `/mobile/login/` 접속
2. 사업자등록번호 입력 (예: `1234567890`)
3. 초기 비밀번호 입력 (예: `67890`)
4. 로그인 클릭
5. "최초 로그인입니다. 보안을 위해 비밀번호를 변경해주세요." 메시지 확인
6. 비밀번호 변경 페이지로 자동 이동
7. 새 비밀번호 입력 (최소 4자)
8. 변경 완료 후 홈 화면 접속

---

## 고객 안내 사항

### 📧 고객에게 전달할 안내문 (예시)

```
[TirePASS] B2B 온라인 주문 시스템 오픈 안내

안녕하세요, TirePASS입니다.

B2B 온라인 주문 시스템이 오픈되었습니다.
귀사의 로그인 정보를 안내드립니다.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📱 접속 주소
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
https://yourdomain.com/mobile/login/

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔐 로그인 정보
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 아이디: 귀사의 사업자등록번호 10자리
• 초기 비밀번호: 사업자번호 뒤 5자리

예시)
사업자등록번호: 123-45-67890
→ 아이디: 1234567890
→ 비밀번호: 67890

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ 중요 안내
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
최초 로그인 시 보안을 위해 반드시
비밀번호를 변경해주시기 바랍니다.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📞 문의
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Tel: 02-1234-5678
Email: support@tirepass.com

감사합니다.
```

### 🎯 FAQ

**Q1. 사업자등록번호를 입력할 때 하이픈(-)을 넣어야 하나요?**
A. 하이픈은 자동으로 제거되므로 있어도 없어도 됩니다.
   - `123-45-67890` ✅
   - `1234567890` ✅

**Q2. 초기 비밀번호를 잊어버렸어요.**
A. 사업자등록번호 뒤 5자리가 초기 비밀번호입니다.
   예: 123-45-67890 → 67890

**Q3. 비밀번호를 변경했는데 다시 로그인이 안돼요.**
A. 변경한 새 비밀번호로 로그인하셔야 합니다.
   초기 비밀번호는 1회만 사용 가능합니다.

**Q4. 비밀번호 길이 제한은?**
A. 최소 4자 이상이면 됩니다. (숫자, 영문, 특수문자 모두 가능)

**Q5. 사업자등록번호가 없는 고객은 어떻게 하나요?**
A. 관리자에게 문의하여 별도 계정을 발급받으셔야 합니다.

---

## 기술 사양

### 데이터베이스 스키마

#### customers_simple 테이블
```sql
CREATE TABLE customers_simple (
    code VARCHAR(10) PRIMARY KEY,           -- 고객 코드
    name VARCHAR(50),                       -- 상호
    rep VARCHAR(20),                        -- 대표자
    tel1 VARCHAR(20),                       -- 전화번호
    tel3 VARCHAR(20),                       -- 휴대전화
    enno VARCHAR(20),                       -- 사업자등록번호
    password VARCHAR(255),                  -- 해시화된 비밀번호
    signup_source VARCHAR(20),              -- 가입 경로
    is_registered TINYINT(1) DEFAULT 0,     -- 등록 여부
    must_change_password TINYINT(1) DEFAULT 1  -- 비밀번호 변경 필수
);
```

### API 엔드포인트

#### 로그인 API
```
POST /api/mobile/auth/login/

Request:
{
  "customer_code": "1234567890",
  "password": "67890"
}

Response (초기 비밀번호):
{
  "success": true,
  "message": "로그인 성공",
  "data": {
    "customer_code": "C001",
    "name": "(주)ABC타이어",
    "must_change_password": true  ← 비밀번호 변경 필요
  }
}
```

#### 비밀번호 변경 API
```
POST /api/mobile/auth/change-password/

Request:
{
  "customer_code": "C001",
  "current_password": "67890",
  "new_password": "newpass1234",
  "confirm_password": "newpass1234"
}

Response:
{
  "success": true,
  "message": "비밀번호가 변경되었습니다."
}

→ must_change_password가 자동으로 false로 업데이트됨
```

### 프론트엔드 흐름

```javascript
// mobile/login.html (lines 71-75)
if (data.data.must_change_password) {
    showAlert('최초 로그인입니다. 보안을 위해 비밀번호를 변경해주세요.', 'info');
    setTimeout(() => {
        location.href = '/mobile/profile/?change_password=true';
    }, 2000);
}
```

```javascript
// mobile/profile.html (lines 248-255)
const urlParams = new URLSearchParams(window.location.search);
if (urlParams.get('change_password') === 'true') {
    setTimeout(() => {
        showChangePassword();
        showAlert('보안을 위해 비밀번호를 변경해주세요', 'info');
    }, 500);
}
```

---

## 문제 해결

### 1. ERP 연결 실패
```
에러: ERP 연결 에러: Unable to complete network request
```

**원인**: ERP 서버에 연결할 수 없음
**해결**:
1. ERP 서버가 실행 중인지 확인
2. 네트워크 연결 확인
3. 방화벽 설정 확인 (포트 3050)
4. FIREBIRD_CONFIG 설정 확인

### 2. MySQL 연결 실패
```
에러: MySQL 연결 에러: Access denied for user 'root'@'localhost'
```

**원인**: MySQL 인증 실패
**해결**:
1. MySQL 서버 실행 확인
   ```bash
   net start MariaDB
   ```
2. 비밀번호 확인
3. MYSQL_CONFIG 설정 확인

### 3. 사업자번호 형식 오류
```
⚠️ 건너뜀: C001 - (주)ABC (사업자번호 형식 오류: 12345)
```

**원인**: 사업자등록번호가 10자리가 아님
**해결**: ERP CUSTOMS 테이블의 ENNO 값 확인 및 수정

### 4. 중복 등록 시도
```
ℹ️ 이미 등록됨: 50명
```

**원인**: 이미 등록된 고객은 자동으로 건너뜀 (정상)
**해결**: 필요 없음 (의도된 동작)

### 5. 로그인 실패
```
"사업자등록번호 또는 비밀번호가 올바르지 않습니다."
```

**원인**:
- 사업자번호가 잘못 입력됨
- 초기 비밀번호가 아닌 다른 값 입력
- 이미 비밀번호를 변경한 경우

**해결**:
1. 사업자번호 10자리 확인
2. 초기 비밀번호 = 사업자번호 뒤 5자리
3. 이미 변경한 경우 새 비밀번호 사용

### 6. 비밀번호 변경 페이지가 나타나지 않음
```
로그인 후 홈으로 바로 이동됨
```

**원인**: must_change_password가 이미 false
**해결**:
1. DB 확인
   ```sql
   SELECT code, must_change_password FROM customers_simple WHERE code='C001';
   ```
2. 필요시 수동으로 재설정
   ```sql
   UPDATE customers_simple SET must_change_password=1 WHERE code='C001';
   ```

---

## 보안 고려사항

### ✅ 구현된 보안 기능
1. **비밀번호 해시화**: Django의 `make_password()` 사용 (PBKDF2)
2. **초기 비밀번호 강제 변경**: `must_change_password` 플래그
3. **비밀번호 최소 길이**: 4자 이상
4. **입력 값 검증**: 사업자번호 10자리 숫자 검증

### ⚠️ 추가 권장사항
1. **HTTPS 사용**: 프로덕션 환경에서 SSL 인증서 필수
2. **비밀번호 정책 강화**: 최소 8자, 영문+숫자+특수문자 조합
3. **로그인 시도 제한**: Brute force 공격 방지
4. **세션 타임아웃**: 일정 시간 후 자동 로그아웃
5. **2단계 인증**: SMS 또는 OTP 추가 (선택사항)

---

## 체크리스트

### 론칭 전
- [ ] ERP 서버 연결 테스트
- [ ] MySQL 데이터베이스 백업
- [ ] 스크립트 테스트 실행 (소수 고객)
- [ ] 로그인 기능 테스트
- [ ] 비밀번호 변경 기능 테스트
- [ ] 고객 안내문 준비
- [ ] 고객 지원 체계 준비

### 론칭 후
- [ ] 전체 고객 일괄 등록
- [ ] 등록 결과 확인
- [ ] 샘플 계정 로그인 테스트
- [ ] 고객에게 안내문 발송
- [ ] 고객 문의 모니터링
- [ ] 로그인 통계 확인

---

## 관련 파일

### 스크립트
- `scripts/register_initial_customers.py` - 일괄 등록 스크립트

### 백엔드 API
- `tire_data/api_views.py`
  - `api_auth_login()` (lines 1121-1191)
  - `api_auth_change_password()` (lines 1252-1311)

### 프론트엔드
- `tire_data/templates/mobile/login.html` (lines 71-75)
- `tire_data/templates/mobile/profile.html` (lines 10-29, 248-255)

### 데이터베이스
- `customers_simple` 테이블
  - `must_change_password` 컬럼 (TINYINT, default: 1)

---

**마지막 업데이트**: 2025-01-13
**작성자**: TirePASS 개발팀
**문의**: support@tirepass.com
