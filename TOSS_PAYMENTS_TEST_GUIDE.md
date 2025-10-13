# 토스페이먼츠 테스트 결제 가이드

TirePASS 프로젝트의 토스페이먼츠 테스트 결제를 위한 가이드입니다.

## 📋 목차
1. [테스트 환경 설정](#테스트-환경-설정)
2. [테스트 카드 정보](#테스트-카드-정보)
3. [테스트 계좌 정보](#테스트-계좌-정보)
4. [API 키 정보](#api-키-정보)
5. [결제 테스트 시나리오](#결제-테스트-시나리오)
6. [주의사항](#주의사항)

---

## 테스트 환경 설정

### 현재 설정 (itire/settings.py)
```python
TOSS_PAYMENTS_CLIENT_KEY = 'test_ck_EP59LybZ8BlBZd2LBbAQV6GYo7pR'
TOSS_PAYMENTS_SECRET_KEY = 'test_ck_EP59LybZ8BlBZd2LBbAQV6GYo7pR'
TOSS_PAYMENTS_SECURITY_KEY = '1f1e0fecdf0102c9bd1d27391d29dd1fc4ee3fa5737c560f5e9bb4f37c2200a7'
TOSS_PAYMENTS_API_URL = 'https://api.tosspayments.com/v1'
```

### 테스트 모드 확인
- 테스트 키는 `test_ck_` 또는 `test_sk_`로 시작합니다
- 실제 결제가 발생하지 않습니다
- 테스트 모드에서는 실제 은행/카드사와 연동되지 않습니다

---

## 테스트 카드 정보

토스페이먼츠에서 제공하는 테스트용 가상 카드 정보입니다.

### 1. 일반 승인 카드 (정상 결제)

| 카드사 | 카드번호 | 유효기간 | CVC | 비밀번호 |
|--------|----------|----------|-----|----------|
| 신한카드 | 5514-1234-5678-9012 | 12/25 | 123 | 12 |
| 국민카드 | 4567-1234-5678-9012 | 01/26 | 456 | 34 |
| 하나카드 | 5211-1234-5678-9012 | 03/27 | 789 | 56 |
| 삼성카드 | 4910-1234-5678-9012 | 06/28 | 012 | 78 |
| 현대카드 | 5523-1234-5678-9012 | 09/29 | 345 | 90 |
| 롯데카드 | 5488-1234-5678-9012 | 11/30 | 678 | 11 |

**공통 정보:**
- 생년월일: 881201
- 통신사: SKT
- 전화번호: 01012345678

### 2. 특수 테스트 카드

#### 승인 거부 테스트
```
카드번호: 5514-0000-0000-0001
유효기간: 12/30
CVC: 123
→ 잔액 부족 오류 발생
```

#### 취소 불가 테스트
```
카드번호: 5514-0000-0000-0002
유효기간: 12/30
CVC: 123
→ 결제는 성공하지만 취소 불가
```

#### 승인 지연 테스트
```
카드번호: 5514-0000-0000-0003
유효기간: 12/30
CVC: 123
→ 승인 처리가 5초 지연됨
```

---

## 테스트 계좌 정보

가상계좌 및 계좌이체 테스트를 위한 정보입니다.

### 가상계좌 발급 테스트
```
은행: 모든 은행 가능
예금주: 아무 이름이나 입력
→ 테스트 환경에서 즉시 가상계좌 발급됨
```

### 가상계좌 입금 테스트 (자동 입금 처리)
1. 가상계좌 발급 후 반환된 계좌번호 확인
2. 토스페이먼츠 개발자센터에서 "입금 처리" 버튼 클릭
3. 또는 API를 통해 가상 입금 처리:
```bash
curl -X POST https://api.tosspayments.com/v1/virtual-accounts/{계좌번호}/deposit \
  -H "Authorization: Basic {인코딩된_시크릿키}" \
  -H "Content-Type: application/json"
```

### 계좌이체 테스트
```
은행: 신한은행
계좌번호: 110-123-456789
예금주: 홍길동
비밀번호: 1234
→ 모든 금액 결제 승인됨
```

---

## API 키 정보

### 테스트 키 발급 방법
1. [토스페이먼츠 개발자센터](https://developers.tosspayments.com/) 접속
2. 회원가입 및 로그인
3. "내 애플리케이션" 메뉴에서 새 애플리케이션 생성
4. "개발" 탭에서 테스트 키 확인

### 키 종류
```
클라이언트 키 (Client Key): test_ck_XXXXXXXX
- 프론트엔드에서 결제창 호출 시 사용
- 공개되어도 무방

시크릿 키 (Secret Key): test_sk_XXXXXXXX
- 백엔드 API 호출 시 사용
- 절대 노출되면 안 됨
- Base64 인코딩 후 Authorization 헤더에 포함
```

### 시크릿 키 인코딩 예제
```python
import base64

secret_key = "test_sk_XXXXXXXX:"  # 끝에 콜론(:) 추가
encoded = base64.b64encode(secret_key.encode()).decode()
# Authorization: Basic {encoded}
```

---

## 결제 테스트 시나리오

### 1. 정상 결제 플로우
```
1. 사용자가 장바구니에서 "주문하기" 클릭
2. 배송지 선택 모달에서 배송지 선택
3. 결제 수단 선택 (카드/계좌이체)
4. 토스페이먼츠 결제창에서 테스트 카드 정보 입력
5. 결제 승인
6. 콜백 URL로 리다이렉트
7. 서버에서 결제 승인 API 호출
8. 주문 완료 처리
```

### 2. 결제 실패 테스트
```
1-4. 위와 동일
5. 승인 거부 카드(5514-0000-0000-0001) 사용
6. 결제 실패 메시지 표시
7. 주문 상태: 'cancelled'
8. 재고 복구 처리
```

### 3. 결제 취소 테스트
```
1. 정상 결제 완료 후
2. 관리자 페이지 또는 API에서 결제 취소 요청
3. 토스페이먼츠 취소 API 호출
4. 취소 승인
5. 주문 상태: 'cancelled'
6. 결제 상태: 'refunded'
7. 재고 복구 처리
```

---

## 주의사항

### ⚠️ 중요 사항

1. **테스트 키는 절대 프로덕션 환경에서 사용 금지**
   - 실제 결제가 발생하지 않아 수익 손실 발생
   - 보안 취약점 발생 가능

2. **시크릿 키 관리**
   - 환경변수로 관리 권장
   - GitHub 등 공개 저장소에 커밋 금지
   - `.env` 파일을 `.gitignore`에 추가

3. **테스트 환경 분리**
   ```python
   # settings.py
   if DEBUG:
       TOSS_PAYMENTS_CLIENT_KEY = os.environ.get('TOSS_TEST_CLIENT_KEY')
       TOSS_PAYMENTS_SECRET_KEY = os.environ.get('TOSS_TEST_SECRET_KEY')
   else:
       TOSS_PAYMENTS_CLIENT_KEY = os.environ.get('TOSS_LIVE_CLIENT_KEY')
       TOSS_PAYMENTS_SECRET_KEY = os.environ.get('TOSS_LIVE_SECRET_KEY')
   ```

4. **Webhook 설정**
   - 로컬 개발: ngrok 등을 사용하여 로컬 서버 노출
   - 테스트 서버: HTTPS 필수
   - Webhook URL: `https://your-domain.com/api/mobile/payment/webhook/`

5. **결제 금액 제한**
   - 테스트 모드에서는 모든 금액 결제 가능
   - 실제 환경에서는 최소/최대 금액 제한 확인

### 💡 팁

1. **빠른 테스트를 위한 카드 번호 기억법**
   - 신한카드: 5514로 시작
   - 나머지는 모두 1234-5678-9012

2. **결제 로그 확인**
   - 토스페이먼츠 개발자센터 > 결제 내역
   - Django 관리자 페이지 > Payments
   - `debug.log` 파일

3. **문제 해결**
   ```python
   # 결제 API 응답 전체 로깅
   logger.info(f"Toss Payments Response: {response_data}")
   ```

---

## 참고 자료

- [토스페이먼츠 공식 문서](https://docs.tosspayments.com/)
- [테스트 카드 목록](https://docs.tosspayments.com/reference/test-card)
- [API 레퍼런스](https://docs.tosspayments.com/reference)
- [결제창 연동 가이드](https://docs.tosspayments.com/guides/payment-widget/integration)

---

## 문의

- 토스페이먼츠 고객센터: 1544-7772
- 이메일: support@tosspayments.com
- 개발자 커뮤니티: https://community.tosspayments.com/

---

**마지막 업데이트:** 2025-01-13
**작성자:** TirePASS 개발팀
