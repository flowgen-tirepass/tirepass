# TirePASS 프로젝트 컨텍스트

> Claude Code 자동 로드용 프로젝트 컨텍스트
> 새 세션 시작 시 이 파일이 자동으로 읽힙니다.

## 프로젝트 개요

**TirePASS**: 타이어 판매 및 재고 관리 통합 시스템
- **웹 플랫폼**: Django 기반 모바일 최적화 웹앱
- **ERP 연동**: FastAPI Gateway를 통한 실시간 데이터 연동
- **배포**: PythonAnywhere 클라우드 호스팅

## 핵심 시스템 구조

```
광주 ERP 서버 (Firebird DB)
    ↕
광주 TgenAI PC (FastAPI Gateway :8000)
    ↕
PythonAnywhere (Django 웹앱)
```

## 주요 기술 스택

- **Backend**: Django 4.x, Django REST Framework
- **Frontend**: HTML5/CSS3, JavaScript (모바일 최적화)
- **ERP Gateway**: FastAPI, Firebird (fdb), MariaDB (pymysql)
- **Hosting**: PythonAnywhere
- **Database**: Firebird (ERP), MariaDB (로컬), MySQL (PythonAnywhere)
- **Version Control**: Git/GitHub

## 중요 위치

### 로컬 개발 환경
```
C:\Users\jmyang\Dropbox\1.0_tirepass\
├── manage.py
├── tire_data/ - 메인 Django 앱
├── TgenAI_INSTALL/ - TgenAI 설치 패키지
├── SYSTEM_INFO.md - 전체 시스템 정보
└── .claude/ - Claude Code 설정
```

### 광주 TgenAI PC
```
C:\TgenAI\
├── erp_api_server.py - FastAPI 서버 (포트 8000)
├── tgenai_erp_gateway_monitor.py - 24/7 모니터링
└── *.bat - 관리 스크립트
```

### PythonAnywhere
```
/home/tirepass/tirepass/
├── Django 프로젝트 루트
├── staticfiles/ - 정적 파일
└── media/ - 미디어 파일
```

## 주요 데이터베이스

### Firebird (ERP 원본)
```
Host: itire2.iptime.org:3050
Database: C:\Program Files\PsimCarS\Data\ITIRE.GDB
User: SYSDBA / Password: masterkey
접근: TgenAI PC를 통한 읽기 전용
```

### MariaDB (ERP 서버)
```
Host: itire2.iptime.org:3306
Database: itire_db
User: root / Password: tirepass
용도: Django 개발/테스트, ERP 동기화
```

### MySQL (PythonAnywhere)
```
Host: tirepass.mysql.pythonanywhere-services.com
Database: tirepass$default
User: tirepass
용도: 프로덕션 Django 데이터베이스
```

## 자주 사용하는 명령

### 로컬 개발

**Django 서버 실행**
```bash
.\venv\Scripts\python.exe manage.py runserver
```

**마이그레이션**
```bash
.\venv\Scripts\python.exe manage.py makemigrations
.\venv\Scripts\python.exe manage.py migrate
```

**정적 파일 수집**
```bash
.\venv\Scripts\python.exe manage.py collectstatic
```

**MariaDB 직접 쿼리**
```bash
"C:\Program Files\MariaDB 12.0\bin\mysql.exe" -uroot -ptirepass itire_db -e "쿼리"
```

### PythonAnywhere 배포

**SSH 접속**
```bash
ssh tirepass@ssh.pythonanywhere.com
```

**배포 프로세스**
```bash
cd ~/tirepass
git pull origin main
source ~/.virtualenvs/tirepass-venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
# 대시보드에서 "Reload" 버튼 클릭
```

### TgenAI 관리

**상태 확인**
```bash
curl -s http://itire2.iptime.org:8000/health
```

**광주 TgenAI PC에서 (TeamViewer 접속)**
```batch
C:\TgenAI\check_status.bat
C:\TgenAI\stop_server.bat
C:\TgenAI\start_server.bat
```

## Git 워크플로우

**현재 브랜치**: main

**커밋 프로세스**
```bash
git add .
git commit -m "설명"
git push origin main
```

**최근 커밋 확인**
```bash
git log --oneline -5
```

## 주요 모델 (tire_data/models.py)

- **Goods**: 타이어 상품 정보
- **CustomersSimple**: 고객 정보
- **YearAllocation**: 연식별 할인 정보
- **Order**: 주문 정보
- **OrderItem**: 주문 상세
- **ShippingAddress**: 배송지 정보
- **ERPSnapshot**: ERP 스냅샷 메타데이터
- **GoodsRealtimeSnapshot**: 실시간 재고 추적

## 관리자 인터페이스

**URL**: https://tirepass.pythonanywhere.com/admin/

**주요 기능**:
- 상품 관리 (ERP 동기화 데이터)
- 고객 관리
- 주문 관리 (취소/반품 포함)
- 재고 추적
- ERP 스냅샷 조회

## 네트워크 구성

**내부 네트워크 (광주 사무실)**
- 192.168.0.225 - ERP 서버
- 192.168.0.113 - TgenAI PC

**외부 접속**
- itire2.iptime.org - DDNS
- 포트 8000 - FastAPI Gateway
- 포트 3306 - MariaDB

**클라우드**
- tirepass.pythonanywhere.com - Django 웹앱

## 프로젝트 특이사항

### 이미지 관리
- 브랜드 로고: `tire_data/static/mobile/img/brands/`
- 크기 표준: 160px 너비 기준
- Goodyear 로고: 160×61 (최근 수정됨)

### ERP 동기화
- TgenAI PC에서 24/7 FastAPI 서버 운영
- PythonAnywhere에서 매시간 스냅샷 생성
- Firebird DB → FastAPI → Django ORM

### 주문 시스템
- 모바일 주문 (order_source='mobile')
- 전화 주문 (order_source='erp_phone')
- 취소/반품 필드 포함

## 문제 해결 체크리스트

### Django 앱이 동작하지 않을 때
1. PythonAnywhere Error log 확인
2. 마이그레이션 상태 확인
3. 정적 파일 재수집
4. 웹앱 Reload

### 정적 파일이 업데이트되지 않을 때
1. `python manage.py collectstatic --noinput --clear`
2. PythonAnywhere 웹앱 Reload
3. 브라우저 캐시 삭제 (Ctrl+F5)

### ERP 데이터가 동기화되지 않을 때
1. TgenAI Gateway 상태 확인 (http://itire2.iptime.org:8000/health)
2. 광주 TgenAI PC 로그 확인 (C:\TgenAI\*.log)
3. ERP 서버 연결 확인

## 주요 문서

- **SYSTEM_INFO.md**: 전체 시스템 정보 (상세)
- **HANDOFF_PROMPT.md**: 세션 인수인계용 프롬프트
- **TgenAI_INSTALL/README.txt**: TgenAI 설치 가이드
- **집PC_설치가이드.md**: TgenAI 상세 설치 가이드

## 연락처 및 지원

- **GitHub**: https://github.com/flowgen-tirepass/tirepass
- **PythonAnywhere**: tirepass 계정

---

**빠른 참조**: 더 상세한 정보는 SYSTEM_INFO.md 참조
**마지막 업데이트**: 2025-10-16
