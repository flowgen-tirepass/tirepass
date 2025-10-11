# ERP API 서버 설정 가이드

## ✅ 완료된 작업

### 1. FastAPI 서버 설치 및 실행
- 파일: `C:\Users\jmyang\Dropbox\1.0_tirepass\erp_api_server.py`
- 상태: ✅ 정상 작동 확인
- ERP 연결: ✅ 6525개 상품 조회 확인
- 로컬 테스트: http://localhost:8000/health

### 2. 서버 실행 명령어
```cmd
cd C:\Users\jmyang\Dropbox\1.0_tirepass
.\venv\Scripts\python.exe erp_api_server.py
```

## 📋 화성 사무실에서 할 작업

### 단계 1: 화성 로컬 PC IP 확인

명령 프롬프트에서:
```cmd
ipconfig
```

**IPv4 주소**를 확인하세요. (예: 192.168.0.100)

### 단계 2: iptime 공유기 설정

#### 2-1. iptime 관리자 페이지 접속
- 브라우저에서 http://192.168.0.1 또는 http://192.168.219.1
- 관리자 계정으로 로그인

#### 2-2. 포트포워드 설정
1. **고급 설정** 메뉴 클릭
2. **NAT/라우터 관리** → **포트포워드 설정** 클릭
3. **새 규칙 추가** 버튼 클릭
4. 다음 정보 입력:

| 항목 | 값 |
|------|-----|
| 규칙 이름 | `ERP_API_SERVER` |
| 외부 포트 | `8000` |
| 내부 IP 주소 | `192.168.0.XXX` (단계 1에서 확인한 IP) |
| 내부 포트 | `8000` |
| 프로토콜 | `TCP` |

5. **적용** 버튼 클릭

#### 2-3. DDNS 확인
- 기존 DDNS: `itire2.iptime.org`
- 포트포워딩 후 외부 접근 URL: `http://itire2.iptime.org:8000`

### 단계 3: 방화벽 설정 (Windows 방화벽)

#### 3-1. Windows Defender 방화벽 설정
1. **제어판** → **Windows Defender 방화벽**
2. 왼쪽 메뉴에서 **고급 설정** 클릭
3. **인바운드 규칙** 클릭 → **새 규칙** 클릭
4. 규칙 유형: **포트** 선택
5. 프로토콜 및 포트:
   - **TCP** 선택
   - 특정 로컬 포트: **8000** 입력
6. 작업: **연결 허용** 선택
7. 프로필: 모두 선택 (도메인, 개인, 공용)
8. 이름: `ERP API Server Port 8000`

### 단계 4: 외부 접근 테스트

#### 4-1. 로컬에서 FastAPI 서버 실행
```cmd
cd C:\Users\jmyang\Dropbox\1.0_tirepass
.\venv\Scripts\python.exe erp_api_server.py
```

#### 4-2. 외부에서 접근 테스트

다른 네트워크(예: 스마트폰 4G)에서 테스트:
```
http://itire2.iptime.org:8000/health
```

**예상 응답**:
```json
{
  "status": "healthy",
  "database": "connected",
  "total_goods": 6525
}
```

#### 4-3. API 문서 확인
```
http://itire2.iptime.org:8000/docs
```

### 단계 5: API 테스트 (API Key 필요)

API Key: `tirepass-erp-secret-2024`

**상품 개수 조회**:
```
http://itire2.iptime.org:8000/api/goods/count?api_key=tirepass-erp-secret-2024
```

**상품 목록 조회**:
```
http://itire2.iptime.org:8000/api/goods?api_key=tirepass-erp-secret-2024&limit=10
```

## 🔧 서버를 항상 실행 상태로 유지

### 방법 1: 백그라운드 실행 (임시)
```cmd
start /B .\venv\Scripts\python.exe erp_api_server.py
```

### 방법 2: Windows 서비스로 등록 (영구)
나중에 설정 가이드 추가 예정

### 방법 3: 작업 스케줄러 (재부팅 시 자동 실행)
1. **작업 스케줄러** 열기
2. **기본 작업 만들기** 클릭
3. 이름: `ERP API Server`
4. 트리거: **컴퓨터를 시작할 때**
5. 작업: **프로그램 시작**
6. 프로그램: `C:\Users\jmyang\Dropbox\1.0_tirepass\venv\Scripts\python.exe`
7. 인수: `C:\Users\jmyang\Dropbox\1.0_tirepass\erp_api_server.py`
8. 시작 위치: `C:\Users\jmyang\Dropbox\1.0_tirepass`

## 📝 다음 단계 (pythonanywhere 설정)

포트포워딩이 완료되면:

1. Django `settings.py`에 ERP API URL 추가:
   ```python
   ERP_API_URL = 'http://itire2.iptime.org:8000'
   ERP_API_KEY = 'tirepass-erp-secret-2024'
   ```

2. `mobile_views.py`에서 로컬 API 호출
3. `api_views.py`에서 실시간 재고 조회

## 🆘 트러블슈팅

### 문제 1: 외부에서 접근 안 됨
- iptime 포트포워딩 설정 재확인
- Windows 방화벽 규칙 확인
- FastAPI 서버가 실행 중인지 확인

### 문제 2: ERP 연결 실패
- ERP 서버(ITIRE2.iptime.org) 상태 확인
- Firebird 서비스 실행 여부 확인

### 문제 3: 서버가 자꾸 종료됨
- 명령 프롬프트 창을 닫지 않기
- 작업 스케줄러로 자동 실행 설정

## 📞 문의
- 문제 발생 시 로그 확인: FastAPI 서버 실행 창의 에러 메시지
