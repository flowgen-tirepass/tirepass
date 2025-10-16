# TirePASS 시스템 정보

> 마지막 업데이트: 2025-10-16
>
> 이 문서는 TirePASS 프로젝트의 모든 시스템 정보를 포함합니다.
> Claude Code 세션 간 정보 지속성을 위해 작성되었습니다.

## 목차
1. [시스템 아키텍처](#시스템-아키텍처)
2. [하드웨어 인벤토리](#하드웨어-인벤토리)
3. [소프트웨어 스택](#소프트웨어-스택)
4. [네트워크 토폴로지](#네트워크-토폴로지)
5. [데이터베이스](#데이터베이스)
6. [서비스 및 포트](#서비스-및-포트)
7. [인증 정보](#인증-정보)
8. [배포 환경](#배포-환경)
9. [모니터링](#모니터링)
10. [백업 및 복구](#백업-및-복구)

---

## 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────────┐
│                         인터넷                                    │
└─────────────────────────────────────────────────────────────────┘
           ▲                    ▲                    ▲
           │                    │                    │
    ┌──────┴────────┐    ┌──────┴────────┐    ┌─────┴──────┐
    │  광주 ERP     │    │  광주 TgenAI  │    │ Python     │
    │  서버         │◄───┤  PC           │───►│ Anywhere   │
    │               │    │               │    │            │
    │ 192.168.0.225 │    │ 192.168.0.113 │    │ 클라우드    │
    │               │    │               │    │            │
    │ Firebird DB   │    │ FastAPI       │    │ Django     │
    │ MariaDB       │    │ Gateway       │    │ 웹앱        │
    │               │    │ :8000 포트    │    │            │
    └───────────────┘    └───────────────┘    └────────────┘
         ▲                     ▲
         │                     │
         └─────────────────────┘
            내부 네트워크 (192.168.0.x)

    외부 접속: itire2.iptime.org (DDNS)
```

### 시스템 흐름

1. **ERP 데이터 읽기**
   - 광주 TgenAI PC → 광주 ERP 서버 (Firebird DB)
   - 내부 네트워크를 통한 직접 연결
   - 6,530개 상품 데이터

2. **API 제공**
   - FastAPI 서버 (포트 8000)
   - RESTful API 엔드포인트
   - 실시간 재고, 고객, 상품 정보

3. **웹 서비스**
   - PythonAnywhere Django 앱
   - 시간별 스냅샷 자동 생성
   - 모바일 최적화 인터페이스

---

## 하드웨어 인벤토리

### 1. 광주 ERP 서버
- **호스트명**: 미확인
- **내부 IP**: 192.168.0.225
- **외부 DDNS**: itire2.iptime.org
- **OS**: Windows (버전 미확인)
- **용도**: ERP 시스템 운영
- **주요 서비스**:
  - Firebird Database Server
  - MariaDB Server
- **접근 제한**: 직접 접근 불가, TgenAI PC를 통한 간접 접근만 가능

### 2. 광주 TgenAI PC
- **호스트명**: TirePASS-TEST
- **내부 IP**: 192.168.0.113
- **OS**: Windows (최신 버전)
- **Python**: 3.13.7
- **설치 위치**: C:\TgenAI\
- **용도**: ERP Gateway & 24/7 모니터링
- **TeamViewer**: 원격 접속 가능
- **주요 서비스**:
  - FastAPI ERP Gateway (포트 8000)
  - 24/7 모니터링 스크립트
  - Windows Task Scheduler 자동 시작

### 3. 개발 노트북 (현재 장치)
- **위치**: C:\Users\jmyang\Dropbox\1.0_tirepass\
- **OS**: Windows (win32)
- **용도**: 개발, 테스트, 배포
- **Git**: 활성화됨
- **Python**: 가상환경 (venv)

### 4. 집 PC
- **외부 IP**: 119.197.67.203 (변동 가능)
- **상태**: TeamViewer 연결 가능
- **제약**: 광주 내부 네트워크 접근 불가
- **참고**: TgenAI 설치 시도했으나 네트워크 이슈로 광주 TgenAI PC 사용으로 변경

---

## 소프트웨어 스택

### 백엔드 (Django)
```
Python 3.x
Django 4.x+
djangorestframework
django-cors-headers
pymysql
cryptography
```

### ERP Gateway (FastAPI)
```
Python 3.13.7
fastapi==0.115.4
uvicorn[standard]==0.32.0
fdb==2.0.4 (Firebird driver)
firebird-driver==2.0.2
pymysql==1.1.1
requests==2.32.3
psutil==6.1.0
orjson==3.10.10
```

### 프론트엔드
```
HTML5/CSS3
JavaScript (Vanilla)
모바일 최적화 반응형 디자인
```

### 이미지 처리
```
Pillow (PIL)
```

### 데이터베이스 클라이언트
```
MariaDB 12.0 (mysql.exe)
- 위치: C:\Program Files\MariaDB 12.0\bin\mysql.exe
```

---

## 네트워크 토폴로지

### 내부 네트워크 (광주 사무실)
```
네트워크: 192.168.0.x/24
게이트웨이: 192.168.0.1 (추정)

장비:
- 192.168.0.225 (ERP 서버)
  - Firebird: 3050 포트
  - MariaDB: 3306 포트

- 192.168.0.113 (TgenAI PC)
  - FastAPI: 8000 포트
```

### 외부 접속
```
DDNS: itire2.iptime.org
포트 포워딩:
  - TCP 8000 → 192.168.0.113:8000 (FastAPI)
  - TCP 3306 → 192.168.0.225:3306 (MariaDB)
```

### 클라우드
```
PythonAnywhere
- 도메인: tirepass.pythonanywhere.com
- SSH: ssh.pythonanywhere.com
- MySQL: tirepass.mysql.pythonanywhere-services.com
```

---

## 데이터베이스

### 1. Firebird Database (ERP 원본)
```
호스트: 192.168.0.225 (내부) / itire2.iptime.org (외부)
포트: 3050
경로: C:\Program Files\PsimCarS\Data\ITIRE.GDB
사용자: SYSDBA
비밀번호: masterkey
문자셋: NONE
용도: ERP 시스템 메인 데이터베이스
접근: TgenAI PC를 통한 읽기 전용
```

**주요 테이블**:
- 상품 정보
- 재고 관리
- 고객 정보
- 주문 데이터

**데이터 규모**: 약 6,530개 상품

### 2. MariaDB (ERP 서버)
```
호스트: itire2.iptime.org
포트: 3306
데이터베이스: itire_db
사용자: root
비밀번호: tirepass
문자셋: utf8mb4
```

**주요 테이블**:
- `goods` - 상품 정보 (타이어)
- `customers_simple` - 고객 정보
- `orders` - 주문 데이터
- `order_items` - 주문 상세
- `year_allocations` - 연식별 할인
- `shipping_addresses` - 배송지
- `erp_snapshots` - ERP 스냅샷 메타데이터

**최근 확인** (2025-10-16):
- 총 상품 수: 6,530개
- 최신 동기화: LAST_SYNC 필드 업데이트됨

### 3. MySQL (PythonAnywhere)
```
호스트: tirepass.mysql.pythonanywhere-services.com
데이터베이스: tirepass$default
사용자: tirepass
비밀번호: [PythonAnywhere 대시보드 참조]
```

**Django 앱 데이터베이스**:
- Django 모델과 동기화
- 정적 파일: /home/tirepass/tirepass/staticfiles/
- 미디어 파일: /home/tirepass/tirepass/media/

---

## 서비스 및 포트

### 광주 TgenAI PC (192.168.0.113)

#### FastAPI ERP Gateway
```
포트: 8000
프로세스: python.exe erp_api_server.py
작업 위치: C:\TgenAI\
가상환경: C:\TgenAI\venv\
로그: C:\TgenAI\erp_api_server.log

주요 엔드포인트:
- GET /health - 헬스체크
- GET /goods - 상품 목록
- GET /goods/{code} - 상품 상세
- GET /customers - 고객 목록

응답 포맷: JSON (orjson)
상태: 24/7 가동 중 (2025-10-15부터 16+ 시간 안정 운영 확인)
```

#### 24/7 모니터링
```
스크립트: tgenai_erp_gateway_monitor.py
로그: C:\TgenAI\tgenai_gateway_monitor.log
체크 주기: 60초
재시작 조건: 3회 연속 실패
Windows Task: TgenAI_ERP_Gateway
자동 시작: 부팅 시 (1분 지연)
```

### PythonAnywhere (tirepass)

#### Django 웹앱
```
URL: https://tirepass.pythonanywhere.com
워커 타입: Web
WSGI 설정: /var/www/tirepass_pythonanywhere_com_wsgi.py
소스 코드: /home/tirepass/tirepass/
가상환경: /home/tirepass/.virtualenvs/tirepass-venv/

정적 파일:
- URL: /static/
- 경로: /home/tirepass/tirepass/staticfiles/

미디어 파일:
- URL: /media/
- 경로: /home/tirepass/tirepass/media/
```

#### 정기 작업 (Scheduled Tasks)
```
스냅샷 생성: 매시간 0분
실행 명령: python /home/tirepass/tirepass/manage.py create_snapshot
```

---

## 인증 정보

### 데이터베이스 접근

**Firebird (ERP)**
```
Host: itire2.iptime.org
Port: 3050
Database: C:\Program Files\PsimCarS\Data\ITIRE.GDB
User: SYSDBA
Password: masterkey
```

**MariaDB (ERP)**
```
Host: itire2.iptime.org
Port: 3306
Database: itire_db
User: root
Password: tirepass
```

**MySQL (PythonAnywhere)**
```
Host: tirepass.mysql.pythonanywhere-services.com
Database: tirepass$default
User: tirepass
Password: [PythonAnywhere 대시보드에서 확인]
```

### 클라우드 서비스

**PythonAnywhere**
```
계정: tirepass
API Token: [PythonAnywhere 계정 설정에서 생성]
SSH: ssh tirepass@ssh.pythonanywhere.com
```

### Git Repository

**GitHub**
```
저장소: https://github.com/flowgen-tirepass/tirepass
브랜치: main
최근 커밋:
- 8ac875a: 관리자 로그인 사업자등록번호 입력 차단
- e778c38: 메뉴 순서 수정 및 Goodyear 로고 크기 변경
- e48bc0d: Admin 메뉴 그룹화 및 주문 취소/반품 기능 추가
```

---

## 배포 환경

### 개발 환경 (로컬)
```
위치: C:\Users\jmyang\Dropbox\1.0_tirepass\
Git: 활성화
Python: venv 가상환경
브랜치: main
```

### 스테이징 환경
```
없음 (프로덕션으로 직접 배포)
```

### 프로덕션 환경 (PythonAnywhere)
```
앱 이름: tirepass
도메인: tirepass.pythonanywhere.com
Python: 3.x
Django: 4.x+
웹 워커: 1개 (무료 플랜)
```

### 배포 프로세스

1. **로컬 개발**
   ```bash
   # 코드 수정
   git add .
   git commit -m "메시지"
   git push origin main
   ```

2. **PythonAnywhere 배포**
   ```bash
   # SSH 접속
   ssh tirepass@ssh.pythonanywhere.com

   # 코드 업데이트
   cd ~/tirepass
   git pull origin main

   # 의존성 설치
   source ~/.virtualenvs/tirepass-venv/bin/activate
   pip install -r requirements.txt

   # 마이그레이션
   python manage.py migrate

   # 정적 파일 수집
   python manage.py collectstatic --noinput

   # 웹앱 재시작
   # PythonAnywhere 대시보드에서 "Reload" 버튼 클릭
   ```

---

## 모니터링

### TgenAI Gateway 상태

**자동 모니터링**
```
스크립트: tgenai_erp_gateway_monitor.py
로그 위치: C:\TgenAI\tgenai_gateway_monitor.log
모니터링 항목:
- FastAPI 서버 헬스 체크 (60초마다)
- 프로세스 상태 확인
- PythonAnywhere 연결 테스트
- 자동 재시작 (3회 연속 실패 시)
```

**수동 확인**
```batch
# TgenAI PC에서 실행
C:\TgenAI\check_status.bat

확인 항목:
1. Python 프로세스 실행 여부
2. 8000 포트 사용 여부
3. /health 엔드포인트 응답
4. 최근 로그 (마지막 10줄)
```

**헬스체크 엔드포인트**
```
URL: http://itire2.iptime.org:8000/health
정상 응답:
{
  "status": "healthy",
  "database": "connected",
  "total_goods": 6530
}
```

### PythonAnywhere 모니터링

**액세스 로그**
```
위치: PythonAnywhere 대시보드 → Web → Log files
- Server log
- Error log
- Access log
```

**스냅샷 생성 확인**
```
URL: https://tirepass.pythonanywhere.com/admin/tire_data/erpsnapshot/
확인 사항:
- 매시간 0분에 스냅샷 생성되는지
- 상품 수 변화 추적
- 오류 발생 여부
```

### 데이터베이스 모니터링

**MariaDB 상태 확인**
```bash
"C:\Program Files\MariaDB 12.0\bin\mysql.exe" -uroot -ptirepass itire_db -e "
SELECT COUNT(*) as total_goods,
       MIN(LAST_SYNC) as earliest_sync,
       MAX(LAST_SYNC) as latest_sync
FROM goods;"
```

---

## 백업 및 복구

### 코드 백업

**Git Repository**
```
원격 저장소: GitHub (flowgen-tirepass/tirepass)
자동 백업: Dropbox 동기화 (C:\Users\jmyang\Dropbox\1.0_tirepass\)
백업 주기: 코드 변경 시마다 (git push)
```

### 데이터베이스 백업

**Firebird (ERP)**
```
백업 담당: 광주 ERP 서버 관리자
TirePASS 팀 역할: 읽기 전용 접근만
```

**MariaDB (ERP 서버)**
```
백업 방법: 미설정 (ERP 서버 관리자 확인 필요)
```

**MySQL (PythonAnywhere)**
```
백업 방법: PythonAnywhere 자동 백업 (유료 플랜 기능)
수동 백업:
  mysqldump -h tirepass.mysql.pythonanywhere-services.com \
            -u tirepass -p tirepass$default > backup.sql
```

### TgenAI 설치 패키지

**백업 위치**
```
1. Dropbox: C:\Users\jmyang\Dropbox\1.0_tirepass\TgenAI_INSTALL\
2. GitHub: https://github.com/flowgen-tirepass/tirepass
   - Commit 4aa745c: 핵심 파일 및 문서
   - Commit a50ff72: 설치 스크립트
```

**복구 절차**
```
1. TgenAI_INSTALL 폴더를 C:\TgenAI\로 복사
2. install.bat 실행 (자동 설치)
3. register_autostart.bat 실행 (관리자 권한)
4. check_status.bat으로 확인
```

### 정적 파일 백업

**브랜드 로고**
```
위치: tire_data/static/mobile/img/brands/
파일 형식: PNG
중요 파일:
- goodyear.png (160×61, 최근 수정됨)
- kumho.png, hankook.png, nexen.png, etc.

백업: Git 저장소에 포함됨
```

---

## 주요 파일 위치

### Django 프로젝트 (로컬)
```
C:\Users\jmyang\Dropbox\1.0_tirepass\
├── manage.py
├── requirements.txt
├── tire_data/
│   ├── models.py - 데이터 모델
│   ├── views.py - API 뷰
│   ├── admin.py - 관리자 인터페이스
│   ├── static/
│   │   └── mobile/
│   │       └── img/
│   │           └── brands/ - 브랜드 로고
│   └── templates/ - HTML 템플릿
└── TgenAI_INSTALL/ - TgenAI 설치 패키지
```

### TgenAI (광주 PC)
```
C:\TgenAI\
├── erp_api_server.py - FastAPI 서버
├── tgenai_erp_gateway_monitor.py - 모니터링
├── requirements.txt
├── venv/ - Python 가상환경
├── install.bat - 설치 스크립트
├── register_autostart.bat - 자동 시작 등록
├── start_server.bat - 수동 시작
├── stop_server.bat - 중지
├── check_status.bat - 상태 확인
├── erp_api_server.log - 서버 로그
└── tgenai_gateway_monitor.log - 모니터링 로그
```

### PythonAnywhere
```
/home/tirepass/
├── tirepass/ - Django 프로젝트
│   ├── manage.py
│   ├── tire_data/
│   ├── staticfiles/ - 수집된 정적 파일
│   └── media/
└── .virtualenvs/
    └── tirepass-venv/ - Python 가상환경
```

---

## 문제 해결 가이드

### FastAPI 서버가 시작되지 않을 때

**증상**: curl http://localhost:8000/health 실패

**확인 사항**:
1. Python 프로세스 확인
   ```batch
   tasklist /FI "IMAGENAME eq python.exe"
   ```

2. 포트 8000 사용 여부
   ```batch
   netstat -ano | findstr :8000
   ```

3. 로그 확인
   ```batch
   type C:\TgenAI\erp_api_server.log
   type C:\TgenAI\tgenai_gateway_monitor.log
   ```

**해결 방법**:
- 서버 재시작: `C:\TgenAI\stop_server.bat` → `C:\TgenAI\start_server.bat`
- 모니터링 재시작: Windows Task Scheduler에서 "TgenAI_ERP_Gateway" 작업 실행

### ERP DB 연결 실패

**증상**: FastAPI 서버 로그에 "Connection refused" 오류

**확인 사항**:
1. 네트워크 연결
   ```batch
   ping itire2.iptime.org
   ```

2. Firebird 서비스 상태 (ERP 서버에서 확인 필요)

3. 방화벽 설정 (포트 3050, 3306)

**해결 방법**:
- 광주 ERP 서버 관리자에게 문의
- TgenAI PC가 내부 네트워크에 연결되어 있는지 확인

### PythonAnywhere 배포 실패

**증상**: 코드 업데이트 후 웹사이트 오류

**확인 사항**:
1. Error log 확인 (PythonAnywhere 대시보드)
2. Python 버전 호환성
3. 패키지 의존성

**해결 방법**:
```bash
ssh tirepass@ssh.pythonanywhere.com
cd ~/tirepass
source ~/.virtualenvs/tirepass-venv/bin/activate
pip install -r requirements.txt --upgrade
python manage.py collectstatic --noinput
# 대시보드에서 Reload
```

### 정적 파일 업데이트가 반영되지 않을 때

**증상**: 브랜드 로고 등이 업데이트되지 않음

**해결 방법**:
```bash
# PythonAnywhere SSH에서
cd ~/tirepass
python manage.py collectstatic --noinput --clear
# 대시보드에서 Reload
# 브라우저 캐시 삭제 (Ctrl+F5)
```

---

## 최근 변경 이력

### 2025-10-16
- TgenAI 광주 PC 설치 완료 (C:\TgenAI\)
- FastAPI 서버 24/7 가동 시작
- Windows Task Scheduler 자동 시작 등록
- Firebird 드라이버 (fdb) 추가
- 16+ 시간 안정 운영 확인
- Goodyear 로고 크기 수정 (160×61)

### 2025-10-15
- TgenAI 설치 패키지 생성 (TgenAI_INSTALL/)
- install.bat, register_autostart.bat 스크립트 작성
- tgenai_erp_gateway_monitor.py 모니터링 시스템 구축

### 2025-10-14
- Orders 테이블에 취소/반품 필드 추가
- Admin 메뉴 그룹화
- ERP 시간별 스냅샷 시스템 구축

---

## 연락처 및 지원

### 기술 지원
- **Claude Code**: AI 어시스턴트 (이 세션)
- **GitHub Issues**: https://github.com/flowgen-tirepass/tirepass/issues

### 서비스 제공자
- **PythonAnywhere**: https://www.pythonanywhere.com/support/
- **GitHub**: https://support.github.com/

---

## 라이선스

이 프로젝트는 비공개 프로젝트입니다.

---

**문서 끝**

> 이 문서는 자동으로 생성되었으며, 시스템 변경 시 업데이트가 필요합니다.
> 마지막 검증: 2025-10-16 by Claude Code
