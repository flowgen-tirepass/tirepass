# 📸 카드 OCR 기능 기술 문서

**작성일:** 2025년 11월 1일
**담당:** 개발팀
**목적:** 카드 자동 인식 기능 구현 방안

---

## 1️⃣ 카드 OCR이란?

**OCR (Optical Character Recognition):** 이미지에서 문자를 자동으로 인식하는 기술

### 작동 방식
```
[스마트폰 카메라]
       ↓
[카드 이미지 촬영]
       ↓
[AI가 카드번호, 유효기간, 이름 인식]
       ↓
[자동으로 입력 폼에 채워짐]
```

---

## 2️⃣ 구현 옵션 비교

### 옵션 1: 토스페이먼츠 Payment Widget ⭐ **추천**

| 항목 | 내용 |
|------|------|
| **비용** | 무료 (결제 수수료에 포함) |
| **정확도** | 95% 이상 |
| **지원 카드** | 국내 모든 카드사 |
| **설치** | JavaScript SDK 포함만 하면 됨 |
| **보안** | 토스페이먼츠가 직접 처리 (PCI DSS 인증) |
| **유지보수** | 토스가 자동 업데이트 |

**장점:**
- ✅ 추가 개발 거의 불필요
- ✅ 결제 위젯과 완벽 통합
- ✅ 카드 유효성 검증 자동
- ✅ 빌링키 발급까지 한 번에

**단점:**
- ❌ 디자인 커스터마이징 제한

**구현 코드 예시:**
```javascript
// 토스페이먼츠 위젯 초기화
const paymentWidget = PaymentWidget(clientKey, customerKey);

// 카드 등록 UI (자동으로 스캔 버튼 포함)
paymentWidget.renderPaymentMethods('#payment-widget', {
  value: 0, // 빌링키 발급 시 0원
  currency: 'KRW',
  cardScanEnabled: true  // 카드 스캔 활성화 ✅
});

// 빌링키 발급
const billingKey = await paymentWidget.requestBillingKey();
```

---

### 옵션 2: NAVER CLOVA OCR

| 항목 | 내용 |
|------|------|
| **비용** | 월 1,000건 무료, 이후 건당 10원 |
| **정확도** | 90% 이상 |
| **지원 카드** | 국내/해외 카드 모두 |
| **설치** | REST API 연동 필요 |
| **보안** | 직접 구현 필요 |

**장점:**
- ✅ 한국어 최적화
- ✅ 다양한 카드 형태 인식
- ✅ 여권, 신분증 등 다른 문서도 인식 가능

**단점:**
- ❌ 별도 비용 발생
- ❌ 직접 구현 필요
- ❌ 결제 시스템과 별도 운영

**구현 코드 예시:**
```python
import requests

# CLOVA OCR API 호출
def scan_card(image_base64):
    url = "https://naveropenapi.apigw.ntruss.com/vision/v1/creditcard"

    headers = {
        "X-NCP-APIGW-API-KEY-ID": "YOUR_CLIENT_ID",
        "X-NCP-APIGW-API-KEY": "YOUR_CLIENT_SECRET",
        "Content-Type": "application/json"
    }

    data = {
        "version": "V2",
        "requestId": "unique-request-id",
        "timestamp": 0,
        "images": [{"format": "jpg", "data": image_base64, "name": "card"}]
    }

    response = requests.post(url, json=data, headers=headers)
    result = response.json()

    # 카드번호, 유효기간 추출
    card_number = result['images'][0]['creditCard']['result']['number']
    expiry_date = result['images'][0]['creditCard']['result']['validThru']

    return {
        'card_number': card_number,
        'expiry_date': expiry_date
    }
```

---

### 옵션 3: 서드파티 라이브러리 (Card.io, Scanbot)

| 항목 | 내용 |
|------|------|
| **비용** | 무료 또는 월 $99~ |
| **정확도** | 80-90% |
| **지원 카드** | 해외 카드 위주 |
| **설치** | 모바일 앱 SDK 필요 |

**장점:**
- ✅ 오프라인에서도 작동 (디바이스에서 인식)

**단점:**
- ❌ 한국 카드 인식률 낮음
- ❌ 추가 라이브러리 필요
- ❌ iOS/Android 각각 구현

---

## 3️⃣ 최종 추천: 토스페이먼츠 Payment Widget

### 선정 이유

1. **비용 효율성**
   - 추가 비용 없음
   - 이미 토스페이먼츠 사용 중

2. **개발 편의성**
   - 10줄 이내 코드로 구현
   - 테스트 완료된 안정적인 시스템

3. **보안**
   - 카드 정보가 TirePASS 서버를 거치지 않음
   - 토스 서버에서 직접 처리

4. **사용자 경험**
   - 익숙한 UI (토스 앱과 동일)
   - 빠른 인식 속도 (1-2초)

---

## 4️⃣ 구현 계획

### Phase 1: 기본 빌링키 등록 (1주)
- [ ] PaymentMethod 모델 생성
- [ ] 토스 Payment Widget 연동
- [ ] 카드 등록 UI 구현
- [ ] 빌링키 저장 API

### Phase 2: 카드 스캔 활성화 (3일)
- [ ] Widget 옵션에 `cardScanEnabled: true` 추가
- [ ] 모바일 카메라 권한 요청
- [ ] 스캔 실패 시 수동 입력 전환

### Phase 3: 테스트 (2일)
- [ ] 다양한 카드사 테스트
- [ ] 조명 조건별 테스트
- [ ] 오류 처리 테스트

---

## 5️⃣ 사용자 시나리오

```
┌─────────────────────────────────────┐
│  1. [카드 등록] 버튼 클릭           │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  2. 토스 위젯 팝업 표시              │
│     "카드를 스캔하거나 직접 입력"   │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  3. [📸 카드 스캔] 버튼 클릭        │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  4. 카메라 권한 요청                 │
│     "카메라 접근을 허용하시겠습니까?"│
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  5. 카드를 카메라에 비춤             │
│     [카드 인식 가이드라인 표시]     │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  6. 자동 인식 (1-2초)               │
│     ✅ 카드번호: 자동 입력          │
│     ✅ 유효기간: 자동 입력          │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  7. CVC, 비밀번호 수동 입력         │
│     (보안상 자동 입력 불가)         │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  8. [등록] 버튼 클릭                │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  9. 빌링키 발급 및 저장 완료        │
│     "카드가 등록되었습니다"         │
└─────────────────────────────────────┘
```

---

## 6️⃣ 기술 스펙

### 지원 환경
- **모바일 웹:** iOS Safari 12+, Android Chrome 80+
- **카메라 API:** getUserMedia() 사용
- **이미지 형식:** JPEG, PNG
- **해상도:** 최소 720p 권장

### 인식 가능한 정보
✅ **자동 인식:**
- 카드번호 (16자리)
- 유효기간 (MM/YY)
- 카드 소유자 이름 (영문)

❌ **수동 입력 필요:**
- CVC/CVV (3-4자리)
- 카드 비밀번호 앞 2자리

### 에러 처리
```javascript
try {
  const billingKey = await paymentWidget.requestBillingKey();
} catch (error) {
  if (error.code === 'CAMERA_NOT_SUPPORTED') {
    // 카메라 미지원 → 수동 입력으로 전환
    showManualInput();
  } else if (error.code === 'SCAN_FAILED') {
    // 스캔 실패 → 재시도 또는 수동 입력
    showRetryOrManualInput();
  } else if (error.code === 'USER_CANCEL') {
    // 사용자가 취소
    closeBillingKeyModal();
  }
}
```

---

## 7️⃣ 비용 분석

### 토스페이먼츠 결제 수수료 (카드 OCR 포함)

| 카드사 | 수수료율 | OCR 추가 비용 |
|--------|----------|--------------|
| 국내 신용카드 | 2.9% | 0원 |
| 국내 체크카드 | 2.9% | 0원 |
| 해외카드 | 3.6% | 0원 |

**예시:**
- 100,000원 주문 시 → 수수료 2,900원
- OCR 기능 사용해도 수수료 동일 ✅

---

## 8️⃣ FAQ (개발팀용)

### Q1. 빌링키 발급 시 실제 결제가 되나요?
**A.** 아니요. 빌링키 발급은 0원 결제로 카드 유효성만 확인합니다.

### Q2. 카드 스캔 실패율은?
**A.** 토스페이먼츠 공식 자료: 약 5% (조명 불량, 카드 손상 등)

### Q3. 법인카드도 스캔 가능한가요?
**A.** 네, 개인/법인 구분 없이 모두 가능합니다.

### Q4. 해외카드는?
**A.** VISA, MasterCard, AMEX 등 국제 브랜드 카드 가능.

### Q5. 오프라인에서도 작동하나요?
**A.** 아니요. 토스 서버와 통신이 필요하므로 인터넷 연결 필수.

---

## 9️⃣ 참고 자료

- [토스페이먼츠 빌링키 API 문서](https://docs.tosspayments.com/reference/billing-key)
- [Payment Widget SDK](https://docs.tosspayments.com/reference/widget-sdk)
- [카드 스캔 가이드](https://docs.tosspayments.com/guides/card-scan)

---

**결론: 토스페이먼츠 Payment Widget으로 구현 진행! 🚀**
