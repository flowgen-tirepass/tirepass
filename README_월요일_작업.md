# 📅 월요일 작업 가이드 - ERP 휴대폰 번호 동기화

> **작성일:** 2025-11-08 (토요일)
> **작업일:** 2025-11-11 (월요일)
> **소요 시간:** 약 30분
> **난이도:** 쉬움

---

## 🎯 작업 목표

광주 화성 ERP의 고객 휴대폰 번호(TEL4 필드)를 Django DB로 동기화하여 모바일 앱에서 사용 가능하게 만들기

---

## 📂 준비된 파일 목록

모든 파일은 `C:\Users\jmyang\Dropbox\1.0_tirepass\` 폴더에 있습니다:

| 파일명 | 용도 | 사용 대상 |
|--------|------|-----------|
| `월요일_간단_프롬프트.txt` ⭐ | Claude에게 전달할 빠른 시작 프롬프트 | 양정민님 |
| `월요일_연속성_프롬프트.txt` | Claude에게 전달할 상세 프롬프트 | 양정민님 |
| `월요일_작업_체크리스트.txt` | 단계별 작업 체크리스트 | 양정민님 |
| `광주_담당자용_간단_수정_가이드.txt` ⭐ | FastAPI 서버 수정 가이드 | 광주 담당자 |
| `TEAMVIEWER_GUIDE.md` | TeamViewer 접속 및 수정 상세 가이드 | 참고용 |
| `erp_api_server.py` | 수정된 FastAPI 서버 코드 | TgenAI PC에 복사 |
| `sync_mobile_phones.py` | 휴대폰 번호 동기화 스크립트 | PythonAnywhere에서 실행 |
| `check_erp_tel4.py` | TEL4 필드 확인 스크립트 | PythonAnywhere에서 실행 |

⭐ = 필수 파일

---

## 🚀 빠른 시작 (3단계)

### 1️⃣ Claude Code에 프롬프트 전달

**간단 버전 (추천):**
```
C:\Users\jmyang\Dropbox\1.0_tirepass\월요일_간단_프롬프트.txt
```
→ 파일 내용 복사 후 Claude에게 붙여넣기

**상세 버전 (전체 이해 필요시):**
```
C:\Users\jmyang\Dropbox\1.0_tirepass\월요일_연속성_프롬프트.txt
```

### 2️⃣ 광주 담당자에게 카톡/문자

```
안녕하세요,

월요일 출근하시면 FastAPI 서버 파일 수정 부탁드립니다.
(5분이면 완료됩니다)

📁 가이드 파일:
C:\Users\jmyang\Dropbox\1.0_tirepass\광주_담당자용_간단_수정_가이드.txt

작업 내용:
1. stop_server.bat 실행
2. erp_api_server.py 파일 교체
3. start_server.bat 실행

완료 후 알려주시면 감사하겠습니다!
```

### 3️⃣ Claude와 함께 작업 진행

담당자 작업 완료 후:
1. TEL4 필드 확인
2. 동기화 실행
3. 결과 검증

---

## 📋 상세 작업 흐름

### Phase 1: 광주 담당자 작업 (5분)

**담당자가 할 일:**
1. TgenAI PC 슬립 모드 해제
2. FastAPI 서버 중지
3. `erp_api_server.py` 파일 교체
4. FastAPI 서버 재시작
5. 양정민님께 완료 알림

**가이드 파일:**
- `광주_담당자용_간단_수정_가이드.txt` (3단계만 따라하면 됨)

---

### Phase 2: TEL4 필드 확인 (2분)

**PythonAnywhere에서 실행:**
```bash
cd ~/1.0_tirepass
python check_erp_tel4.py
```

**성공 시:**
```
✅ TEL4 필드 있음!
TEL4 샘플 데이터:
  [1] 0-1-0001      거라지21           010-1234-5678 ✅
```

**실패 시:**
```
❌ TEL4 필드 없음!
→ 광주 담당자에게 재확인 요청
```

---

### Phase 3: 휴대폰 번호 동기화 (5분)

**PythonAnywhere에서 실행:**
```bash
python sync_mobile_phones.py
```

**예상 결과:**
```
2️⃣ 휴대폰 필드명 확인
✅ 휴대폰 필드명: 'tel4' (광주 ERP TEL4 필드)

4️⃣ 휴대폰 번호 통계
전체: 1,754명
010으로 시작: 500+명 ✅

5️⃣ Django DB 업데이트
✅ 업데이트 완료!
   업데이트: 500명
```

---

### Phase 4: 결과 검증 (3분)

**Django Admin 확인:**
1. https://tirepass.pythonanywhere.com/admin/ 접속
2. Customers 목록 열기
3. "휴대전화" 컬럼에 010 번호 확인
4. 여러 고객 샘플 확인

**성공 조건:**
- ✅ 010으로 시작하는 번호가 tel3 필드에 저장됨
- ✅ 500명 이상 업데이트됨
- ✅ Django Admin에서 확인됨

---

## ⚠️ 문제 해결

### 문제 1: "tel4 필드가 없습니다!"

**원인:**
- FastAPI 서버 코드 미수정
- 서버 재시작 안 됨

**해결:**
1. 광주 담당자에게 확인 요청
2. `광주_담당자용_간단_수정_가이드.txt` 다시 확인
3. 서버 완전히 종료 후 재시작

---

### 문제 2: 동기화 후에도 빈 값

**원인:**
- ERP에 TEL4 데이터가 실제로 없음

**확인:**
```bash
python check_erp_tel4.py
```
→ 출력에서 TEL4 샘플 데이터 확인

**대안:**
- TEL2, TEL3 등 다른 필드 사용 검토
- 광주 ERP 프로그램에서 고객 관리 확인

---

### 문제 3: FastAPI 연결 실패

**확인:**
```bash
curl http://ITIRE2.iptime.org:8000/health
```

**원인:**
- TgenAI PC 슬립 모드
- 서버 중단
- 네트워크 문제

**해결:**
- 광주 담당자에게 PC 상태 확인 요청

---

## 📊 작업 전후 비교

### Before (토요일)
```
FastAPI 응답:
{
  "code": "0-1-0001",
  "name": "거라지21",
  "tel1": "062-123-4567",
  "tel3": "",  // 빈 값
  "enno": "410-14-48232"
}

Django DB:
Customers.tel3 = NULL (대부분)
```

### After (월요일 목표)
```
FastAPI 응답:
{
  "code": "0-1-0001",
  "name": "거라지21",
  "tel1": "062-123-4567",
  "tel3": "",
  "tel4": "010-1234-5678",  // ← 추가됨
  "enno": "410-14-48232"
}

Django DB:
Customers.tel3 = "010-1234-5678" (500+명)
```

---

## ✅ 완료 체크리스트

- [ ] Claude에게 연속성 프롬프트 전달
- [ ] 광주 담당자에게 작업 요청
- [ ] 담당자 작업 완료 확인
- [ ] TEL4 필드 확인 성공
- [ ] 동기화 스크립트 실행
- [ ] 500+명 업데이트 확인
- [ ] Django Admin에서 검증
- [ ] ✨ 작업 완료!

---

## 📞 연락처

**광주 담당자:**
- 작업 요청: 가이드 파일 위치 전달
- 완료 확인: 카톡/문자로 알림 받기

**문제 발생 시:**
- Claude Code에게 에러 메시지와 함께 문의
- 즉시 해결 가능

---

## 💡 참고사항

### 시스템 구조
```
ERP Firebird (광주)
  ↓ TEL4 필드 (휴대폰)
FastAPI (TgenAI PC)
  ↓ HTTP API
Django (PythonAnywhere)
  ↓ Customers.tel3
모바일 앱
```

### 기술 스택
- **ERP:** Firebird Database (CUSTOMS 테이블)
- **FastAPI:** Python 3.x + fdb (Firebird driver)
- **Django:** 4.2 + MySQL
- **배포:** PythonAnywhere

### 중요 개념
- **TEL4 → tel3 매핑**: ERP의 TEL4를 Django의 tel3에 저장
- **010 필터링**: 010으로 시작하는 번호만 동기화
- **초기화 후 업데이트**: 기존 tel3 전체 삭제 후 ERP 데이터로 채움

---

**작성자:** Claude Code & 양정민
**버전:** 1.0
**최종 수정:** 2025-11-08

---

Good luck! 🚀
