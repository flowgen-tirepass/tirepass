# 토스페이먼츠 연동 가이드

## 📌 개요

타이어패스 모바일 쇼핑몰에 토스페이먼츠를 연동하여 신용카드 및 계좌이체 결제를 구현합니다.

## 🔑 API 키 설정

### 테스트 키 (개발용)
- 클라이언트 키: `test_ck_XXX...`
- 시크릿 키: `test_sk_XXX...`

### 라이브 키 (실제 운영)
- 클라이언트 키: `live_ck_XXX...` (토스 가입 후 발급)
- 시크릿 키: `live_sk_XXX...` (토스 가입 후 발급)

**설정 파일**: `itire/settings.py`
```python
# Toss Payments 설정
TOSS_CLIENT_KEY = os.getenv('TOSS_CLIENT_KEY', 'test_ck_...')
TOSS_SECRET_KEY = os.getenv('TOSS_SECRET_KEY', 'test_sk_...')
TOSS_API_URL = 'https://api.tosspayments.com/v1/payments'
```

---

## 🔄 결제 흐름

### 1단계: 주문서 생성
```
사용자가 "구매하기" 클릭
→ 장바구니 데이터 검증
→ 임시 주문(Order) 생성 (status: pending, payment_status: unpaid)
→ 주문번호 생성 (예: TP20250123001)
```

### 2단계: 결제 페이지
```html
<!-- mobile/templates/mobile/checkout.html -->
<script src="https://js.tosspayments.com/v1/payment-widget"></script>
<script>
  const clientKey = "{{ toss_client_key }}";
  const paymentWidget = PaymentWidget(clientKey, customerKey);

  paymentWidget.renderPaymentMethods("#payment-method");

  // 결제하기 버튼
  async function requestPayment() {
    await paymentWidget.requestPayment({
      orderId: "{{ order.order_number }}",
      orderName: "타이어 {{ order.items.count }}건",
      successUrl: "{{ request.scheme }}://{{ request.get_host }}/mobile/payment/success",
      failUrl: "{{ request.scheme }}://{{ request.get_host }}/mobile/payment/fail",
      customerEmail: "{{ customer.email }}",
      customerName: "{{ customer.name }}",
    });
  }
</script>
```

### 3단계: 결제 승인 (백엔드)
**URL**: `/mobile/payment/success?paymentKey=xxx&orderId=xxx&amount=xxx`

```python
# mobile/views.py
def payment_success(request):
    payment_key = request.GET.get('paymentKey')
    order_id = request.GET.get('orderId')
    amount = request.GET.get('amount')

    # 1. 주문 조회
    order = Order.objects.get(order_number=order_id)

    # 2. 금액 검증
    if int(amount) != order.final_amount:
        return redirect('payment_fail')

    # 3. 토스 승인 API 호출
    import requests
    import base64

    secret_key = settings.TOSS_SECRET_KEY
    encoded = base64.b64encode(f"{secret_key}:".encode()).decode()

    response = requests.post(
        f"{settings.TOSS_API_URL}/{payment_key}",
        headers={
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/json"
        },
        json={
            "orderId": order_id,
            "amount": amount
        }
    )

    if response.status_code == 200:
        # 4. 승인 성공 - 주문 처리
        payment_data = response.json()

        # Payment 레코드 생성
        Payment.objects.create(
            order=order,
            payment_method=payment_data['method'],
            payment_amount=payment_data['totalAmount'],
            payment_status='completed',
            payment_key=payment_key,
            order_id_toss=order_id,
            transaction_id=payment_data.get('transactionKey'),
            pg_name='토스페이먼츠',
            payment_date=timezone.now(),
            raw_response=json.dumps(payment_data)
        )

        # 주문 상태 변경
        order.order_status = 'confirmed'
        order.payment_status = 'paid'
        order.confirmed_date = timezone.now()
        order.save()

        # 🔥 재고 감소
        decrease_inventory(order)

        return redirect('payment_complete', order_id=order.id)
    else:
        # 승인 실패
        return redirect('payment_fail')
```

---

## 📦 재고 감소 로직

```python
def decrease_inventory(order):
    """주문 완료 시 재고 감소"""
    from tire_data.models import Goods, YearAllocation

    for item in order.items.all():
        # 1. Goods 재고 감소
        goods = Goods.objects.get(code=item.product_code)
        goods.jaego -= item.quantity
        goods.save()

        # 2. DOT 재고 감소 (YearAllocation)
        if item.selected_year:
            try:
                allocation = YearAllocation.objects.get(goods_code=item.product_code)
                year_field = f'year_{item.selected_year}'

                if hasattr(allocation, year_field):
                    current_qty = getattr(allocation, year_field)
                    setattr(allocation, year_field, current_qty - item.quantity)
                    allocation.save()
            except YearAllocation.DoesNotExist:
                pass
```

---

## 🛠️ 구현 체크리스트

### Backend (Django)
- [ ] `itire/settings.py`에 토스 키 설정 추가
- [ ] `mobile/views.py`에 결제 관련 뷰 추가:
  - [ ] `checkout_view` - 결제 페이지
  - [ ] `payment_success_view` - 승인 처리
  - [ ] `payment_fail_view` - 실패 처리
  - [ ] `payment_complete_view` - 완료 페이지
- [ ] `mobile/urls.py`에 URL 패턴 추가
- [ ] 재고 감소 함수 구현
- [ ] Order Admin 추가

### Frontend (Mobile)
- [ ] `checkout.html` - 결제 페이지 템플릿
- [ ] `payment_complete.html` - 완료 페이지
- [ ] `payment_fail.html` - 실패 페이지
- [ ] 장바구니 페이지 (`cart.html`)
- [ ] 주문 내역 페이지 (`orders.html`)

### API Endpoints
```
POST   /mobile/api/cart/add              장바구니 담기
GET    /mobile/api/cart                  장바구니 조회
DELETE /mobile/api/cart/<id>             장바구니 삭제
POST   /mobile/api/order/create          주문 생성
GET    /mobile/payment/checkout/<id>     결제 페이지
GET    /mobile/payment/success           결제 승인 (토스 콜백)
GET    /mobile/payment/fail              결제 실패 (토스 콜백)
GET    /mobile/payment/complete/<id>     결제 완료 페이지
```

---

## 🧪 테스트 시나리오

### 1. 테스트 카드 정보
```
카드번호: 5570-0000-0000-0001
유효기간: 12/30
CVC: 123
```

### 2. 테스트 계좌이체
- 은행: 아무거나 선택
- 계좌번호: 1234567890

### 3. 테스트 절차
1. ✅ 상품 검색
2. ✅ 장바구니 담기
3. ✅ 주문서 작성
4. ✅ 결제 진행 (테스트 카드)
5. ✅ 결제 완료 확인
6. ✅ 재고 감소 확인 (Goods, YearAllocation)
7. ✅ 관리자 페이지에서 주문 확인

---

## 📚 참고 문서

- [토스페이먼츠 공식 문서](https://docs.tosspayments.com/)
- [결제위젯 연동 가이드](https://docs.tosspayments.com/guides/payment-widget/integration)
- [승인 API 문서](https://docs.tosspayments.com/reference#payment-승인)

---

## ⚠️ 주의사항

1. **시크릿 키 보안**
   - 절대 프론트엔드에 노출 금지
   - 환경변수로 관리 (`.env` 파일)
   - Git에 커밋 금지

2. **금액 검증**
   - 클라이언트에서 전달된 금액 무조건 재검증
   - 주문서 금액과 승인 금액 일치 확인

3. **재고 부족 처리**
   - 주문 생성 전 재고 확인
   - 동시 주문 시 경쟁 상태(Race Condition) 고려

4. **에러 처리**
   - 승인 실패 시 주문 취소
   - 네트워크 에러 시 재시도 로직
   - 사용자에게 명확한 에러 메시지

---

**작성일**: 2025-01-23
**작성자**: Claude Code
**버전**: 1.0
