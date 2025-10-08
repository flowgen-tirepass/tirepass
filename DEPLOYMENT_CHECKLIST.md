# PythonAnywhere 배포 체크리스트

## 1. 업로드할 파일/폴더

### 핵심 Django 프로젝트 파일
- ✅ `manage.py` - Django 관리 스크립트
- ✅ `requirements.txt` - 패키지 의존성
- ✅ `pythonanywhere_wsgi.py` - WSGI 설정
- ✅ `pythonanywhere_tables.sql` - 테이블 생성 SQL 스크립트

### itire/ (프로젝트 설정)
- ✅ `itire/__init__.py`
- ✅ `itire/settings.py` - Django 설정
- ✅ `itire/settings_production.py` - 프로덕션 설정 (있을 경우)
- ✅ `itire/urls.py` - URL 라우팅
- ✅ `itire/wsgi.py` - WSGI 진입점
- ✅ `itire/asgi.py` - ASGI 진입점
- ✅ `itire/middleware.py` - 커스텀 미들웨어

### tire_data/ (메인 앱)
- ✅ `tire_data/__init__.py`
- ✅ `tire_data/models.py` - 데이터 모델
- ✅ `tire_data/models_shopping.py` - 쇼핑/주문 모델
- ✅ `tire_data/models_generated.py` - 생성된 모델
- ✅ `tire_data/views.py` - 관리자 뷰
- ✅ `tire_data/mobile_views.py` - 모바일 뷰
- ✅ `tire_data/api_views.py` - API 뷰
- ✅ `tire_data/urls.py` - URL 매핑
- ✅ `tire_data/admin.py` - 관리자 페이지 설정
- ✅ `tire_data/apps.py` - 앱 설정
- ✅ `tire_data/utils.py` - 유틸리티 함수
- ✅ `tire_data/templatetags/` - 템플릿 태그
- ✅ `tire_data/management/commands/` - 커스텀 관리 명령어

### templates/ (템플릿 파일)
- ✅ `templates/` - 전체 템플릿 폴더

### static/ (정적 파일)
- ✅ `static/` - 전체 정적 파일 폴더

## 2. 업로드하지 않을 파일/폴더
- ❌ `venv/` - 가상환경 (pythonanywhere에서 새로 생성)
- ❌ `db_dumps/` - 로컬 DB 덤프
- ❌ `__pycache__/` - 파이썬 캐시
- ❌ `*.pyc` - 컴파일된 파이썬 파일
- ❌ `debug.log` - 로컬 로그 파일
- ❌ `debug (HWASUNG의 충돌된 사본 2025-10-08).log` - 충돌 파일
- ❌ `mobile/` - 이전 모바일 앱 (사용 안 함)
- ❌ `work/` - 작업 임시 폴더
- ❌ `data/` - 로컬 데이터 폴더
- ❌ `staticfiles/` - collectstatic 결과 (서버에서 재생성)
- ❌ `tirepass.db` - SQLite DB (사용 안 함)
- ❌ `node_modules/` - Node.js 패키지
- ❌ `.claude/` - Claude 설정
- ❌ `*.md` 파일들 (문서) - DEPLOYMENT 관련 제외
- ❌ 충돌된 사본 파일들

## 3. pythonanywhere MySQL 테이블 생성 SQL

### 3.1 ERP 서버에서 받을 테이블 (managed=False)
이 테이블들은 ERP 서버 트리거가 생성/관리:
- `goods` - 상품 정보
- `customers_simple` - 고객 정보

### 3.2 Django가 관리하는 테이블 (managed=True)
**✅ `pythonanywhere_tables.sql` 파일을 pythonanywhere MySQL에서 실행**

이 SQL 스크립트는 다음 테이블들을 생성합니다:
- 쇼핑/주문: `shopping_cart`, `orders`, `order_items`, `payments`
- 할인 관리: `brand_groups`, `brand_group_patterns`, `customer_discounts`, `customer_product_discounts`, `discount_history`, `year_allocations`
- 인덱스: 성능 최적화를 위한 각종 인덱스

## 4. pythonanywhere 환경 변수 설정
```python
# settings.py에서 사용
DEBUG = False
ALLOWED_HOSTS = ['yourusername.pythonanywhere.com']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'yourusername$itire_db',
        'USER': 'yourusername',
        'PASSWORD': 'your_mysql_password',
        'HOST': 'yourusername.mysql.pythonanywhere-services.com',
    }
}
```

## 5. 배포 순서
1. ✅ pythonanywhere MySQL에 Django 관리 테이블 생성
2. ✅ 코드 업로드 (Git 또는 Files 탭)
3. ✅ 가상환경 생성 및 패키지 설치
4. ✅ static 파일 collect
5. ✅ WSGI 설정 파일 업데이트
6. ✅ Web app 재시작
7. ✅ 테스트 (관리자 로그인, 모바일 페이지)
8. ✅ ERP 트리거 연동 테스트
9. ✅ 로컬 테스트 데이터 삭제

## 6. 데이터 새로고침 확인사항
- API 응답에 Cache-Control 헤더 추가 필요
- 상품/고객 목록 API는 항상 최신 데이터 반환
- 브라우저 캐싱 방지

## 7. 주의사항
⚠️ **ERP 서버 트리거가 이미 설정되어 있어야 함:**
- 상품(goods) 테이블 실시간 동기화
- 고객(customers_simple) 테이블 실시간 동기화
- 트리거 동작 확인 필요

⚠️ **배포 후 즉시:**
- 로컬 itire_db의 모든 테스트 데이터 삭제
- C001, C002 등 테스트 고객 삭제
- 테스트 상품 데이터 삭제
