# Claude Code 인수인계 프롬프트

> 새로운 Claude Code 세션을 시작할 때 이 프롬프트를 복사하여 붙여넣으세요.
> Claude가 즉시 프로젝트 컨텍스트를 이해하고 작업을 시작할 수 있습니다.

---

## 📋 빠른 인수인계 프롬프트

아래 텍스트를 복사하여 새 Claude Code 세션에 붙여넣으세요:

```
안녕하세요! TirePASS 프로젝트 작업을 계속하겠습니다.

프로젝트 컨텍스트:
- 프로젝트: TirePASS (타이어 판매 및 재고 관리 시스템)
- 기술 스택: Django + FastAPI + PythonAnywhere
- 위치: C:\Users\jmyang\Dropbox\1.0_tirepass\

먼저 다음 파일들을 읽어주세요:
1. SYSTEM_INFO.md - 전체 시스템 정보
2. .claude/project-context.md - 프로젝트 컨텍스트

시스템 상태:
- 광주 TgenAI PC: FastAPI 서버 24/7 가동 중 (C:\TgenAI\, 포트 8000)
- PythonAnywhere: Django 웹앱 운영 중 (tirepass.pythonanywhere.com)
- ERP 연동: Firebird DB → FastAPI → Django
- Git: main 브랜치 사용

준비되면 현재 작업할 내용을 알려주시면 시작하겠습니다.
```

---

## 📖 상세 인수인계 프롬프트 (더 많은 컨텍스트가 필요할 때)

```
안녕하세요! TirePASS 프로젝트의 지속적인 개발을 위해 인수인계합니다.

## 프로젝트 개요
TirePASS는 타이어 판매 및 재고 관리 통합 시스템입니다.
- Django 기반 웹앱 (모바일 최적화)
- FastAPI를 통한 ERP 실시간 연동
- PythonAnywhere 클라우드 호스팅

## 시스템 구조
```
광주 ERP 서버 (Firebird DB)
    ↕ 내부 네트워크
광주 TgenAI PC (FastAPI Gateway :8000) - 24/7 가동 중
    ↕ 인터넷
PythonAnywhere (Django 웹앱)
```

## 중요 파일 및 문서
프로젝트 루트: C:\Users\jmyang\Dropbox\1.0_tirepass\

필수 읽기 문서:
1. **SYSTEM_INFO.md** - 전체 시스템 정보 (하드웨어, 네트워크, DB, 서비스)
2. **.claude/project-context.md** - 프로젝트 컨텍스트 (자주 사용하는 명령, 워크플로우)
3. **TgenAI_INSTALL/README.txt** - TgenAI 설치 및 관리 가이드

주요 코드:
- tire_data/ - Django 메인 앱
- tire_data/models.py - 데이터 모델
- tire_data/admin.py - 관리자 인터페이스
- tire_data/views.py - API 뷰

TgenAI 시스템:
- 광주 TgenAI PC: C:\TgenAI\
- erp_api_server.py - FastAPI 서버
- tgenai_erp_gateway_monitor.py - 24/7 모니터링

## 주요 데이터베이스
1. Firebird (ERP 원본): itire2.iptime.org:3050, SYSDBA/masterkey
2. MariaDB (ERP 서버): itire2.iptime.org:3306, root/tirepass, DB: itire_db
3. MySQL (PythonAnywhere): tirepass.mysql.pythonanywhere-services.com, DB: tirepass$default

## 현재 시스템 상태
✅ 광주 TgenAI PC: FastAPI 서버 24/7 안정 가동 중
   - 포트: 8000
   - 헬스체크: http://itire2.iptime.org:8000/health
   - 상품 수: 6,530개 (Firebird DB)
   - 로그: C:\TgenAI\*.log

✅ PythonAnywhere: Django 웹앱 운영 중
   - URL: https://tirepass.pythonanywhere.com
   - Admin: /admin/
   - 매시간 ERP 스냅샷 자동 생성

✅ Git 저장소: https://github.com/flowgen-tirepass/tirepass
   - 브랜치: main
   - 최근 커밋: 관리자 보안 강화, Goodyear 로고 수정

## 자주 사용하는 작업

### Django 개발 (로컬)
```bash
.\venv\Scripts\python.exe manage.py runserver
.\venv\Scripts\python.exe manage.py makemigrations
.\venv\Scripts\python.exe manage.py migrate
```

### PythonAnywhere 배포
```bash
ssh tirepass@ssh.pythonanywhere.com
cd ~/tirepass
git pull origin main
source ~/.virtualenvs/tirepass-venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
# 대시보드에서 Reload
```

### TgenAI 관리 (광주 PC, TeamViewer)
```batch
C:\TgenAI\check_status.bat
C:\TgenAI\stop_server.bat
C:\TgenAI\start_server.bat
```

### MariaDB 쿼리
```bash
"C:\Program Files\MariaDB 12.0\bin\mysql.exe" -uroot -ptirepass itire_db -e "SELECT COUNT(*) FROM goods;"
```

## 최근 작업 내역
- 2025-10-16: TgenAI 광주 PC 설치 완료, 24/7 가동 시작
- 2025-10-16: Goodyear 로고 크기 수정 (160×61)
- 2025-10-15: TgenAI 설치 패키지 생성
- 2025-10-14: 주문 취소/반품 기능 추가

## 주의사항
1. **정적 파일 변경 시**: 반드시 collectstatic 실행 후 PythonAnywhere Reload
2. **이미지 변경 시**: 브랜드 로고는 160px 너비 기준, 비율 유지
3. **DB 마이그레이션**: 로컬 테스트 후 PythonAnywhere 배포
4. **TgenAI 서버**: 광주 TgenAI PC는 24/7 가동 필수, 건드리지 않음
5. **Git 커밋**: 중요한 변경 사항은 즉시 커밋 및 푸시

## 문제 해결
- Django 오류: PythonAnywhere Error log 확인
- 정적 파일 미반영: collectstatic --clear 후 브라우저 캐시 삭제
- ERP 동기화 실패: TgenAI Gateway 상태 확인 (http://itire2.iptime.org:8000/health)

## 다음 단계
위 내용을 확인하셨으면, 현재 작업하실 내용을 알려주세요.
예시:
- "상품 상세 페이지에 새로운 필드 추가해줘"
- "고객 검색 기능 개선이 필요해"
- "ERP 스냅샷 통계 확인해줘"
- "Nexen 로고 크기 조정해줘"

준비되었습니다! 무엇을 도와드릴까요?
```

---

## 💡 사용 팁

### 빠른 시작 (일반 작업)
간단한 작업의 경우 "📋 빠른 인수인계 프롬프트"만 사용하세요.

### 복잡한 작업 시작
다음의 경우 "📖 상세 인수인계 프롬프트" 사용:
- 새로운 기능 개발
- 시스템 구조 변경
- 문제 해결 및 디버깅
- 데이터베이스 스키마 변경

### 특정 영역 작업
특정 영역만 작업할 경우 프롬프트를 커스터마이즈하세요:

**예시: 프론트엔드 작업**
```
안녕하세요! TirePASS 프론트엔드 작업을 하려고 합니다.

읽어주세요: .claude/project-context.md

작업 영역:
- tire_data/templates/ - HTML 템플릿
- tire_data/static/ - CSS, JavaScript, 이미지

현재 작업: [구체적인 작업 내용]
```

**예시: 데이터베이스 작업**
```
안녕하세요! TirePASS 데이터베이스 작업을 하려고 합니다.

읽어주세요: SYSTEM_INFO.md (데이터베이스 섹션)

DB 정보:
- MariaDB: itire2.iptime.org:3306, DB: itire_db, root/tirepass
- MySQL (PythonAnywhere): tirepass$default

현재 작업: [구체적인 작업 내용]
```

**예시: TgenAI 관리**
```
안녕하세요! TgenAI 시스템 관리 작업입니다.

읽어주세요: TgenAI_INSTALL/README.txt

시스템 위치: 광주 TgenAI PC, C:\TgenAI\
현재 상태: 24/7 가동 중

현재 작업: [구체적인 작업 내용]
```

---

## 🔧 Claude Code 세션 자동화

### 방법 1: .claude/project-context.md 활용
Claude Code는 `.claude/` 폴더의 파일을 자동으로 인식합니다.
프로젝트 루트에 `.claude/project-context.md`가 있으면 자동 로드됩니다.

### 방법 2: 빠른 프롬프트 저장
자주 사용하는 프롬프트를 텍스트 파일로 저장해두세요:
```
C:\Users\jmyang\Dropbox\quick_prompts\
├── tirepass_handoff.txt
├── tirepass_frontend.txt
├── tirepass_database.txt
└── tirepass_tgenai.txt
```

### 방법 3: AI 어시스턴트 활용 (개발 중)
향후 개발될 AI 어시스턴트를 통해 자동으로 세션을 초기화할 수 있습니다.

---

## 📝 인수인계 체크리스트

새 세션 시작 전 확인:

- [ ] SYSTEM_INFO.md 최신 버전인가?
- [ ] .claude/project-context.md 업데이트되었나?
- [ ] Git 저장소 최신 상태인가? (git pull)
- [ ] TgenAI Gateway 정상 가동 중인가? (http://itire2.iptime.org:8000/health)
- [ ] PythonAnywhere 웹앱 정상 동작 중인가?
- [ ] 최근 작업 내역 확인했나?

---

**문서 버전**: 1.0
**작성일**: 2025-10-16
**마지막 검증**: 2025-10-16 by Claude Code
