# TeamViewer 접속 및 FastAPI 서버 TEL4 필드 추가 가이드

## 📋 준비 사항

**TeamViewer 정보:**
- ID: 547 995 053
- Password: (이전에 받은 비밀번호)
- 대상 PC: TgenAI (광주 화성 ERP 서버)

**계정 정보:**
- TeamViewer 계정: jmyangkr@gmail.com
- Password: sinc9569yjm*

---

## 1️⃣ TeamViewer 접속

1. TeamViewer 실행
2. "파트너 ID" 입력: `547 995 053`
3. "연결" 클릭
4. 비밀번호 입력
5. 연결 완료 후 Windows 바탕화면 확인

---

## 2️⃣ FastAPI 서버 코드 수정

### 파일 위치
```
C:\TgenAI\erp_api_server.py
```

### 수정 방법 A: 메모장으로 직접 수정

1. `C:\TgenAI` 폴더 열기
2. `erp_api_server.py` 파일 우클릭 → "편집" (메모장 열림)
3. 아래 5군데 수정

---

### 수정 1: CustomerResponse 모델 (약 53-61번째 줄)

**기존:**
```python
class CustomerResponse(BaseModel):
    """고객 정보 응답 모델"""
    code: str
    name: str
    rep: Optional[str] = None
    tel1: Optional[str] = None
    tel3: Optional[str] = None
    enno: Optional[str] = None
```

**수정 후:**
```python
class CustomerResponse(BaseModel):
    """고객 정보 응답 모델"""
    code: str
    name: str
    rep: Optional[str] = None
    tel1: Optional[str] = None
    tel3: Optional[str] = None
    tel4: Optional[str] = None  # ← 이 줄 추가
    enno: Optional[str] = None
```

---

### 수정 2: get_customers_list - search 쿼리 (약 271-279번째 줄)

**기존:**
```python
            query = """
                SELECT CODE, NAME, REP, TEL1, TEL3, ENNO
                FROM CUSTOMS
                WHERE NAME LIKE ? OR CODE LIKE ?
                ORDER BY CODE
                ROWS ? TO ?
            """
```

**수정 후:**
```python
            query = """
                SELECT CODE, NAME, REP, TEL1, TEL3, TEL4, ENNO
                FROM CUSTOMS
                WHERE NAME LIKE ? OR CODE LIKE ?
                ORDER BY CODE
                ROWS ? TO ?
            """
```

---

### 수정 3: get_customers_list - 기본 쿼리 (약 281-287번째 줄)

**기존:**
```python
            query = """
                SELECT CODE, NAME, REP, TEL1, TEL3, ENNO
                FROM CUSTOMS
                ORDER BY CODE
                ROWS ? TO ?
            """
```

**수정 후:**
```python
            query = """
                SELECT CODE, NAME, REP, TEL1, TEL3, TEL4, ENNO
                FROM CUSTOMS
                ORDER BY CODE
                ROWS ? TO ?
            """
```

---

### 수정 4: get_customers_list - 응답 생성 (약 290-300번째 줄)

**기존:**
```python
        customers_list = []
        for row in cursor.fetchall():
            code, name, rep, tel1, tel3, enno = row
            customers_list.append(CustomerResponse(
                code=code if code else "",
                name=name if name else "",
                rep=rep,
                tel1=tel1,
                tel3=tel3,
                enno=enno
            ))
```

**수정 후:**
```python
        customers_list = []
        for row in cursor.fetchall():
            code, name, rep, tel1, tel3, tel4, enno = row  # ← tel4 추가
            customers_list.append(CustomerResponse(
                code=code if code else "",
                name=name if name else "",
                rep=rep,
                tel1=tel1,
                tel3=tel3,
                tel4=tel4,  # ← 이 줄 추가
                enno=enno
            ))
```

---

### 수정 5: get_customer_detail - 쿼리 (약 320-325번째 줄)

**기존:**
```python
        query = """
            SELECT CODE, NAME, REP, TEL1, TEL3, ENNO
            FROM CUSTOMS
            WHERE CODE = ?
        """
```

**수정 후:**
```python
        query = """
            SELECT CODE, NAME, REP, TEL1, TEL3, TEL4, ENNO
            FROM CUSTOMS
            WHERE CODE = ?
        """
```

---

### 수정 6: get_customer_detail - 응답 생성 (약 333-342번째 줄)

**기존:**
```python
        code, name, rep, tel1, tel3, enno = row
        customer = CustomerResponse(
            code=code if code else "",
            name=name if name else "",
            rep=rep,
            tel1=tel1,
            tel3=tel3,
            enno=enno
        )
```

**수정 후:**
```python
        code, name, rep, tel1, tel3, tel4, enno = row  # ← tel4 추가
        customer = CustomerResponse(
            code=code if code else "",
            name=name if name else "",
            rep=rep,
            tel1=tel1,
            tel3=tel3,
            tel4=tel4,  # ← 이 줄 추가
            enno=enno
        )
```

---

### 수정 방법 B: 파일 통째로 교체 (더 빠름)

**Dropbox 파일:**
```
C:\Users\jmyang\Dropbox\1.0_tirepass\erp_api_server.py
```

**복사 방법:**
1. TeamViewer로 TgenAI에 접속
2. Dropbox 파일 열기: `C:\Users\jmyang\Dropbox\1.0_tirepass\erp_api_server.py`
3. 전체 선택 (Ctrl+A) → 복사 (Ctrl+C)
4. TgenAI 파일 열기: `C:\TgenAI\erp_api_server.py`
5. 전체 선택 (Ctrl+A) → 붙여넣기 (Ctrl+V)
6. 저장 (Ctrl+S)

---

## 3️⃣ FastAPI 서버 재시작

### 방법 1: 배치 파일 사용 (권장)

**서버 종료:**
```
C:\TgenAI\stop_server.bat
```

**서버 시작:**
```
C:\TgenAI\start_server.bat
```

### 방법 2: 수동 재시작

**1. 서버 종료:**
- 작업 관리자 (Ctrl+Shift+Esc)
- "Python" 프로세스 찾기
- "작업 끝내기"

**2. 서버 시작:**
- 명령 프롬프트 (cmd) 열기
- 아래 명령 실행:
```cmd
cd C:\TgenAI
python erp_api_server.py
```

---

## 4️⃣ 테스트

### API 테스트 (브라우저)

**1. 서버 상태 확인:**
```
http://localhost:8000/health
```

**2. API 문서 확인:**
```
http://localhost:8000/docs
```

**3. 고객 데이터 확인:**
```
http://localhost:8000/api/customers?api_key=tirepass-erp-secret-2024&offset=0&limit=5
```

**확인 사항:**
- `tel4` 필드가 응답에 포함되어 있는지 확인
- 값이 "010"으로 시작하는지 확인

---

## 5️⃣ Django 휴대폰 동기화 실행

TgenAI 서버 수정 완료 후, PythonAnywhere에서 동기화 스크립트 실행:

```bash
cd ~/1.0_tirepass
python sync_mobile_phones.py
```

**예상 결과:**
```
================================================================================
ERP 휴대폰 번호 → Django 휴대전화 동기화
================================================================================

1️⃣ ERP 고객 데이터 구조 확인
--------------------------------------------------------------------------------
...

2️⃣ 휴대폰 필드명 확인
--------------------------------------------------------------------------------
✅ 휴대폰 필드명: 'tel4' (광주 ERP TEL4 필드)

3️⃣ ERP 전체 고객 데이터 가져오기 (필드: tel4)
--------------------------------------------------------------------------------
...
```

---

## 🔍 트러블슈팅

### 문제 1: "tel4 필드가 없습니다!" 에러

**원인:** FastAPI 서버 코드 수정이 반영되지 않음
**해결:** 서버를 완전히 종료하고 다시 시작

### 문제 2: 서버 시작 안 됨

**원인:** Python 문법 오류 또는 들여쓰기 오류
**해결:**
1. 오류 메시지 확인
2. 파일 통째로 교체 (방법 B 사용)

### 문제 3: TEL4 값이 모두 빈 값

**원인:** ERP Firebird DB에 TEL4 컬럼이 실제로 없거나 다른 이름
**해결:**
1. ERP 프로그램 열어서 고객 관리 확인
2. "휴대폰" 필드가 어느 컬럼에 저장되는지 확인
3. 필요시 TEL2, FAX 등 다른 필드로 변경

---

## ✅ 완료 확인

- [ ] TeamViewer로 TgenAI 접속 성공
- [ ] erp_api_server.py 6군데 수정 완료
- [ ] 파일 저장 완료
- [ ] FastAPI 서버 재시작 완료
- [ ] http://localhost:8000/api/customers 테스트 → tel4 필드 확인
- [ ] sync_mobile_phones.py 실행 → 010 번호 동기화 성공

---

**작성일:** 2025-11-08
**목적:** ERP TEL4 필드(휴대폰) 데이터를 Django DB tel3 필드로 동기화
