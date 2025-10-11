# TgenAI PC FastAPI 서버 설치 가이드

## 📋 설치 전 준비사항

- [x] TgenAI PC 정리 완료
- [x] Python 3.13.7 설치 확인
- [x] venv 가상환경 존재 확인
- [x] C:\TgenAI\erp_api 폴더 생성 완료

---

## 🚀 설치 단계

### 1단계: FastAPI 서버 파일 복사

**방법 A: 직접 복사 (권장)**

1. Dropbox 폴더에서 `erp_api_server.py` 파일을 찾습니다
   - 경로: `C:\Users\jmyang\Dropbox\1.0_tirepass\erp_api_server.py`

2. TgenAI PC에 복사:
   - TeamViewer 파일 전송 기능 사용
   - 대상: `C:\TgenAI\erp_api\erp_api_server.py`

**방법 B: 명령어로 복사 (TgenAI PC에서 실행)**

```cmd
copy "\\DESKTOP-XXXXXX\Users\jmyang\Dropbox\1.0_tirepass\erp_api_server.py" "C:\TgenAI\erp_api\"
```

---

### 2단계: Python 패키지 설치

TgenAI PC에서 명령 프롬프트 실행:

```cmd
cd C:\TgenAI
venv\Scripts\pip install fastapi uvicorn fdb pydantic
```

**예상 소요 시간:** 2-3분

**설치되는 패키지:**
- `fastapi` - 웹 API 프레임워크
- `uvicorn` - ASGI 웹 서버
- `fdb` - Firebird 데이터베이스 드라이버
- `pydantic` - 데이터 검증 라이브러리

---

### 3단계: 서버 시작 스크립트 생성

TgenAI PC에서 메모장으로 새 파일 생성:

**파일명:** `C:\TgenAI\start_erp_api.bat`

**내용:**
```batch
@echo off
chcp 65001 >nul
echo ====================================
echo ERP API Server 시작
echo ====================================
echo.
cd C:\TgenAI
venv\Scripts\python.exe erp_api\erp_api_server.py
pause
```

---

### 4단계: 서버 실행 테스트

1. `C:\TgenAI\start_erp_api.bat` 더블클릭 실행

2. 다음 메시지가 나타나는지 확인:
   ```
   ============================================================
   ERP API Server 시작
   ============================================================
   ERP Host: ITIRE2.iptime.org
   API URL: http://localhost:8000
   Docs: http://localhost:8000/docs
   ============================================================
   INFO:     Started server process [xxxxx]
   INFO:     Waiting for application startup.
   INFO:     Application startup complete.
   INFO:     Uvicorn running on http://0.0.0.0:8000
   ```

3. 웹 브라우저에서 테스트:
   - 기본 상태: http://localhost:8000
   - 헬스 체크: http://localhost:8000/health
   - API 문서: http://localhost:8000/docs

---

### 5단계: 연결 테스트

**헬스 체크 테스트:**

브라우저에서 `http://localhost:8000/health` 접속

**예상 응답:**
```json
{
  "status": "healthy",
  "database": "connected",
  "total_goods": 6525
}
```

**상품 개수 조회 테스트:**

```
http://localhost:8000/api/goods/count?api_key=tirepass-erp-secret-2024
```

**예상 응답:**
```json
{
  "count": 6525
}
```

---

## 🔧 문제 해결

### 에러 1: "fdb 모듈을 찾을 수 없음"

```cmd
cd C:\TgenAI
venv\Scripts\pip install fdb
```

### 에러 2: "fbclient.dll을 찾을 수 없음"

1. `C:\TgenAI\fbclient.dll` 파일 존재 확인
2. 환경 변수 PATH에 `C:\TgenAI` 추가

### 에러 3: "ITIRE2.iptime.org에 연결할 수 없음"

```cmd
ping ITIRE2.iptime.org
```

- 정상: `Reply from xxx.xxx.xxx.xxx: time=2ms`
- 실패: 네트워크 설정 확인 필요

### 에러 4: "포트 8000이 이미 사용 중"

다른 포트 사용 (예: 8001):

`erp_api_server.py` 파일의 마지막 줄 수정:
```python
uvicorn.run(app, host="0.0.0.0", port=8001)
```

---

## 📊 다음 단계

설치 완료 후:

1. [ ] 외부 접속을 위한 포트 포워딩 설정
2. [ ] Windows 방화벽 설정
3. [ ] pythonanywhere Django 연동 테스트
4. [ ] Windows 서비스 등록 (자동 시작)

---

## 💡 참고 정보

**서버 중지:**
- Ctrl + C (명령 프롬프트에서)

**로그 확인:**
- 콘솔 출력에서 실시간 확인

**API 문서:**
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

**보안:**
- API Key: `tirepass-erp-secret-2024`
- 모든 API 호출 시 `api_key` 파라미터 필요
- 읽기 전용 (SELECT only) - ERP 데이터 변경 없음
