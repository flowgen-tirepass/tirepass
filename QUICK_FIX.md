# 검색 기능 빠른 수정 가이드

## 1. 로그 파일 생성 및 권한 설정

```bash
cd ~/itire

# 로그 파일 생성
touch info.log error.log

# 권한 설정 (읽기/쓰기 가능)
chmod 666 info.log error.log

# 파일 확인
ls -la *.log
```

## 2. 웹 앱 강제 재시작

```bash
touch /var/www/tirepass_pythonanywhere_com_wsgi.py

# 잠시 대기
sleep 3
```

## 3. 테스트 - 브라우저에서 검색

1. https://tirepass.pythonanywhere.com/admin/tire_data/goods/ 접속
2. 검색창에 "205" 입력
3. 검색 버튼 클릭

## 4. 로그 확인

```bash
cd ~/itire

# 로그 파일이 생성되었는지 확인
ls -lh info.log

# 최근 로그 확인
tail -30 info.log

# 실시간 모니터링
tail -f info.log
```

## 5. 로그가 여전히 비어있다면

### 5-1. Django 에러 로그 확인
```bash
tail -50 /var/log/tirepass.pythonanywhere.com.error.log
```

### 5-2. Python 인터프리터에서 직접 테스트
```bash
cd ~/itire
source ~/.virtualenvs/itire-venv/bin/activate
python3 << 'EOF'
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itire.settings_production')
django.setup()

from tire_data.erp_api_client import ERPAPIClient

# 검색 테스트
print("=== 검색 테스트: 205 ===")
results = ERPAPIClient.get_goods_list(search="205", offset=0, limit=5)
print(f"결과: {len(results)} 개")
for item in results[:3]:
    print(f"  - {item['code']}: {item['name']}")
EOF
```

### 5-3. 템플릿 검색 폼 확인
```bash
cd ~/itire
grep -A 5 'form method="get"' tire_data/templates/admin/goods_changelist.html | head -20
```

## 6. 검색이 작동하지 않는 원인 파악

### 원인 1: Django admin 기본 검색과 충돌
템플릿에서 커스텀 검색 폼을 만들었지만, Django admin의 기본 검색 기능과 충돌할 수 있음.

### 원인 2: 검색 파라미터 전달 문제
검색 폼이 올바른 URL 파라미터를 생성하지 못할 수 있음.

### 원인 3: changelist_view가 호출되지 않음
Django admin의 다른 뷰가 먼저 처리될 수 있음.

## 7. 긴급 수정 (검색 URL 직접 테스트)

브라우저에서 직접 URL 입력:
```
https://tirepass.pythonanywhere.com/admin/tire_data/goods/?q=205
```

이 URL이 작동하면 → 검색 폼 문제
작동하지 않으면 → changelist_view 로직 문제

## 8. 로그 레벨 임시 상승

info.log가 생성되지 않으면 콘솔 로그로 확인:
```bash
cd ~/itire
python3 manage.py shell << 'EOF'
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('tire_data')
logger.info("테스트 로그")
EOF
```

## 9. 웹 앱 설정 확인

PythonAnywhere Web 탭에서:
1. "Reload" 버튼이 초록색인지 확인
2. "Error log" 클릭하여 최근 에러 확인
3. Python 버전이 3.10 이상인지 확인

## 10. 최종 확인 사항

```bash
cd ~/itire
echo "=== Git 상태 ==="
git log -1 --oneline

echo "=== Python 패키지 ==="
source ~/.virtualenvs/itire-venv/bin/activate
pip list | grep requests

echo "=== Django 설정 ==="
python3 manage.py check

echo "=== 로그 파일 권한 ==="
ls -la *.log
```
