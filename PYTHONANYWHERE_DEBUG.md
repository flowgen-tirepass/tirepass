# PythonAnywhere 디버깅 가이드

## 1. 전체 에러 로그 확인
```bash
cd ~/itire
tail -100 /var/log/tirepass.pythonanywhere.com.error.log
```

## 2. ERP API 연결 테스트
```bash
cd ~/itire
source ~/.virtualenvs/itire-venv/bin/activate
python3 << EOF
from tire_data.erp_api_client import ERPAPIClient

# API 연결 테스트
print("=== ERP API 연결 테스트 ===")
try:
    count = ERPAPIClient.get_goods_count()
    print(f"✓ 상품 개수: {count}")
except Exception as e:
    print(f"✗ 오류: {e}")

# 검색 테스트
print("\n=== 검색 테스트 (205) ===")
try:
    results = ERPAPIClient.get_goods_list(offset=0, limit=5, search="205")
    print(f"✓ 검색 결과: {len(results)} 개")
    for item in results[:3]:
        print(f"  - {item['code']}: {item['name']}")
except Exception as e:
    print(f"✗ 오류: {e}")
EOF
```

## 3. Django 설정 확인
```bash
cd ~/itire
python3 << EOF
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itire.settings')
django.setup()

from tire_data.models import Goods
from tire_data.admin import GoodsAdmin
from django.contrib import admin

print("=== Django Admin 설정 확인 ===")
admin_instance = GoodsAdmin(Goods, admin.site)
print(f"search_fields: {admin_instance.search_fields}")
print(f"list_display: {admin_instance.list_display}")
print(f"change_list_template: {admin_instance.change_list_template}")
EOF
```

## 4. ERP API 서버 상태 확인 (노트북에서)
```powershell
powershell -Command "Invoke-RestMethod -Uri 'http://ITIRE2.iptime.org:8000/health' | ConvertTo-Json"
```

## 5. PythonAnywhere에서 ERP API 접근 테스트
```bash
curl -s "http://ITIRE2.iptime.org:8000/health"
curl -s "http://ITIRE2.iptime.org:8000/api/goods/count?api_key=tirepass-erp-secret-2024"
curl -s "http://ITIRE2.iptime.org:8000/api/goods?api_key=tirepass-erp-secret-2024&offset=0&limit=3&search=205"
```

## 예상 결과

### 정상 작동 시:
```json
{"status":"healthy","database":"connected","total_goods":6528}
{"count":6528}
[{"code":"...","name":"205/55R16 ..."}]
```

### 오류 발생 시:
- Connection refused → TgenAI 서버 중지
- Timeout → 방화벽/네트워크 문제
- 401 Unauthorized → API 키 불일치
- 500 Internal Server Error → Firebird 연결 문제

## 6. 웹 앱 재시작
```bash
touch /var/www/tirepass_pythonanywhere_com_wsgi.py
```

## 7. 실시간 로그 모니터링

### 에러 로그 (ERROR 레벨)
```bash
tail -f /var/log/tirepass.pythonanywhere.com.error.log
```

### Info 로그 (INFO 레벨 - 디버깅용)
```bash
cd ~/itire
tail -f info.log
```

이 상태에서 브라우저에서 검색을 시도하면 실시간 로그 확인 가능

## 8. 로그 확인 가이드

검색 후 다음 로그를 확인:
```bash
cd ~/itire
echo "=== 최근 검색 로그 ==="
tail -50 info.log | grep "검색어"

echo "=== ERP API 요청 ==="
tail -50 info.log | grep "ERP API"

echo "=== 필터 적용 ==="
tail -50 info.log | grep "필터"
```

## 9. 문제 해결 체크리스트

### ✅ 검색이 작동하지 않는 경우
1. ERP API 서버 상태 확인
   ```bash
   curl -s http://ITIRE2.iptime.org:8000/health
   ```
2. info.log에서 "검색어" 키워드 확인
3. ERP API 응답 확인

### ✅ 필터가 작동하지 않는 경우
1. info.log에서 "필터 적용" 확인
2. 타이어 패턴 매칭 로그 확인
3. 필터 전후 개수 비교
