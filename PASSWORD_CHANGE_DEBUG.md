# 비밀번호 변경 문제 디버깅 가이드

## 문제 증상
1. 비밀번호 변경 후 새 비밀번호로 로그인 안 됨
2. 이전 비밀번호로도 로그인 안 됨
3. 비밀번호가 저장되지 않는 것으로 추정

## 수정 완료된 항목

### 1. 네비게이션 문제 수정
- ✅ 프로필 페이지에 "홈으로 가기" 버튼 추가
- ✅ 비밀번호 변경 성공 후 자동으로 홈으로 이동

### 2. API 수정
- ✅ `api_auth_profile`: signup_source 필드 제거 (존재하지 않는 필드)
- ✅ `profile.html`: signup_source 표시 제거

## 확인이 필요한 사항

### 1. MySQL 테이블 구조 확인

**로컬에서 실행:**
```bash
mysql -uroot -ptirepass itire_db < check_customers_table.sql
```

또는 MySQL 콘솔에서:
```sql
USE itire_db;
DESCRIBE customers_simple;
```

**확인할 컬럼:**
- `password` VARCHAR(255)
- `must_change_password` TINYINT(1) 또는 BOOLEAN
- `is_registered` TINYINT(1) 또는 BOOLEAN

### 2. 비밀번호 해시 확인

**Python Shell에서:**
```python
python manage.py shell

from tire_data.models import Customers
from django.contrib.auth.hashers import make_password, check_password

# 테스트 고객 조회
customer = Customers.objects.filter(is_registered=True).first()
print(f"고객: {customer.code} - {customer.name}")
print(f"비밀번호 해시: {customer.password}")
print(f"must_change_password: {customer.must_change_password}")

# 초기 비밀번호로 테스트
initial_password = customer.enno[-5:]
print(f"\n초기 비밀번호: {initial_password}")
print(f"로그인 가능: {check_password(initial_password, customer.password)}")
```

## 디버깅 단계

### 단계 1: 로그 추가

**tire_data/api_views.py** 파일의 `api_auth_change_password` 함수에 로그 추가:

```python
import logging
logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
def api_auth_change_password(request):
    """비밀번호 변경 API"""
    try:
        body_unicode = request.body.decode('utf-8')
        data = json.loads(body_unicode)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        return JsonResponse({
            'success': False,
            'message': f'잘못된 요청입니다: {str(e)}'
        }, status=400)

    customer_code = request.session.get('customer_code') or data.get('customer_code')
    current_password = data.get('current_password', '').strip()
    new_password = data.get('new_password', '').strip()
    confirm_password = data.get('confirm_password', '').strip()

    logger.info(f"비밀번호 변경 요청: customer_code={customer_code}")

    # ... 중간 코드 ...

    try:
        customer = Customers.objects.get(code=customer_code)

        logger.info(f"현재 비밀번호 해시: {customer.password[:20]}...")

        # 현재 비밀번호 확인
        if not check_password(current_password, customer.password):
            logger.warning(f"현재 비밀번호 불일치: {customer_code}")
            return JsonResponse({
                'success': False,
                'message': '현재 비밀번호가 일치하지 않습니다.'
            }, status=401)

        # 새 비밀번호로 변경
        old_hash = customer.password
        customer.password = make_password(new_password)
        customer.must_change_password = False
        customer.save()

        # 저장 확인
        customer.refresh_from_db()
        logger.info(f"비밀번호 변경 완료:")
        logger.info(f"  이전 해시: {old_hash[:20]}...")
        logger.info(f"  새 해시: {customer.password[:20]}...")
        logger.info(f"  must_change_password: {customer.must_change_password}")

        return JsonResponse({
            'success': True,
            'message': '비밀번호가 변경되었습니다.'
        })

    except Customers.DoesNotExist:
        logger.error(f"고객 정보 없음: {customer_code}")
        return JsonResponse({
            'success': False,
            'message': '고객 정보를 찾을 수 없습니다.'
        }, status=404)
    except Exception as e:
        logger.exception(f"비밀번호 변경 오류: {customer_code}")
        return JsonResponse({
            'success': False,
            'message': f'비밀번호 변경 중 오류가 발생했습니다: {str(e)}'
        }, status=500)
```

### 단계 2: PythonAnywhere 에러 로그 확인

1. https://www.pythonanywhere.com 로그인
2. **Web** 탭 클릭
3. **Log files** 섹션
4. **Error log** 클릭
5. 비밀번호 변경 시도 후 로그 확인

### 단계 3: 데이터베이스 직접 확인

**PythonAnywhere Bash 콘솔:**
```bash
mysql -u tirepass -p
USE tirepass$itire_db;

-- 테스트 고객 조회
SELECT code, name, enno, password, must_change_password
FROM customers_simple
WHERE is_registered = 1
LIMIT 1;

-- 비밀번호 변경 후 다시 조회하여 해시가 변경되었는지 확인
```

## 가능한 원인과 해결방법

### 원인 1: customers_simple 테이블에 컬럼이 없음

**증상:**
- `must_change_password` 컬럼이 존재하지 않음

**해결:**
```sql
ALTER TABLE customers_simple
ADD COLUMN must_change_password TINYINT(1) DEFAULT 1
COMMENT '비밀번호변경필요';
```

### 원인 2: 트랜잭션 자동 커밋 문제

**증상:**
- save() 호출 후 실제 DB에 저장 안 됨

**해결:**
```python
# api_views.py
from django.db import transaction

@transaction.atomic
def api_auth_change_password(request):
    # ... 코드 ...
    customer.save()
    # transaction.atomic으로 자동 커밋 보장
```

### 원인 3: 읽기 전용 테이블

**증상:**
- models.py에서 `managed = False`로 설정됨

**확인:**
```python
# tire_data/models.py
class Customers(models.Model):
    class Meta:
        db_table = 'customers_simple'
        managed = True  # False면 True로 변경
```

### 원인 4: 세션 문제

**증상:**
- customer_code가 세션에서 제대로 전달 안 됨

**해결:**
```javascript
// profile.html
body: JSON.stringify({
    customer_code: getCustomerCode(),  // 이 함수가 제대로 작동하는지 확인
    current_password: currentPassword,
    new_password: newPassword,
    confirm_password: confirmPassword
})
```

## 즉시 테스트 방법

### 1. 브라우저 개발자 도구 확인

1. Chrome 개발자 도구 열기 (F12)
2. **Network** 탭 선택
3. 비밀번호 변경 시도
4. `/api/mobile/auth/change-password/` 요청 확인
5. **Request Payload** 확인:
   ```json
   {
       "customer_code": "고객코드",
       "current_password": "현재비번",
       "new_password": "새비번",
       "confirm_password": "새비번"
   }
   ```
6. **Response** 확인:
   ```json
   {
       "success": true,
       "message": "비밀번호가 변경되었습니다."
   }
   ```

### 2. 수동 API 테스트 (Postman 또는 curl)

```bash
curl -X POST https://tirepass.pythonanywhere.com/api/mobile/auth/change-password/ \
  -H "Content-Type: application/json" \
  -d '{
    "customer_code": "테스트고객코드",
    "current_password": "현재비번",
    "new_password": "새비번",
    "confirm_password": "새비번"
  }'
```

## 체크리스트

- [ ] MySQL customers_simple 테이블에 must_change_password 컬럼 존재 확인
- [ ] models.py에서 Customers 모델의 managed = True 확인
- [ ] 비밀번호 변경 API 로그 확인
- [ ] 브라우저 개발자 도구로 Request/Response 확인
- [ ] MySQL에서 직접 password 컬럼 변경 여부 확인
- [ ] PythonAnywhere Error log 확인

## 다음 단계

위 단계를 순서대로 진행하면서 문제를 찾아야 합니다. 가장 먼저:

1. **MySQL 테이블 구조 확인** - must_change_password 컬럼 존재 여부
2. **브라우저 개발자 도구** - API 응답 확인
3. **PythonAnywhere Error Log** - 서버 에러 확인

문제를 찾으면 해당 섹션의 해결방법을 적용하세요.
