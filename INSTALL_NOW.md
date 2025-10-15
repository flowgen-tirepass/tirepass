# TgenAI 자동 복구 시스템 - 즉시 설치 가이드

## ✅ TeamViewer 접속 완료!

이제 다음 5단계를 순서대로 진행하세요.

---

## 1️⃣ Python 패키지 설치 (1분)

### 명령 프롬프트 또는 PowerShell 열기

**방법 1**: 시작 메뉴 → "cmd" 또는 "PowerShell" 검색

**방법 2**: `Win + R` → `cmd` 입력 → Enter

### 명령어 실행

```bash
cd C:\Users\jmyang\Dropbox\1.0_tirepass

venv\Scripts\activate

pip install psutil requests
```

### 예상 출력

```
Collecting psutil
  Downloading psutil-...
Successfully installed psutil-... requests-...
```

✅ **확인**: "Successfully installed" 메시지 확인

---

## 2️⃣ 전체 감시 시스템 설치 (1분)

### 관리자 권한으로 실행

1. 파일 탐색기에서 다음 경로 열기:
   ```
   C:\Users\jmyang\Dropbox\1.0_tirepass
   ```

2. **`install_all_watchdogs.bat`** 파일 찾기

3. **우클릭** → **"관리자 권한으로 실행"** 선택

### 설치 진행

다음 메시지가 순서대로 출력됩니다:

```
========================================
TgenAI 전체 감시 시스템 설치
========================================

[1/3] ERP 게이트웨이 모니터 등록
[SUCCESS] ERP 게이트웨이 모니터 등록 완료

[2/3] TeamViewer 감시견 등록
[SUCCESS] TeamViewer 감시견 등록 완료

[3/3] 네트워크 감시견 등록
[SUCCESS] 네트워크 감시견 등록 완료

========================================
설치 완료!
========================================
```

### 작업 스케줄러 확인 (선택)

"작업 스케줄러를 열어서 확인하시겠습니까? (Y/N)"
→ **Y** 입력

다음 3개 작업이 "준비됨" 상태인지 확인:
- ✅ TgenAI_ERP_Gateway_Monitor
- ✅ TgenAI_TeamViewer_Watchdog
- ✅ TgenAI_Network_Watchdog

---

## 3️⃣ MAC 주소 확인 (1분)

Wake-on-LAN 설정을 위해 TgenAI PC의 MAC 주소를 확인합니다.

### 명령어 실행

```bash
ipconfig /all
```

### MAC 주소 찾기

출력에서 다음 내용 찾기:

```
이더넷 어댑터 이더넷:

   물리적 주소 . . . . . . . . : 00-1A-2B-3C-4D-5E
                                  ^^^^^^^^^^^^^^^^^^
```

**중요**: "물리적 주소"를 기록하세요!

예시: `00-1A-2B-3C-4D-5E`

---

## 4️⃣ Wake-on-LAN 설정 (2분)

### wake_tgenai.py 파일 수정

1. 파일 열기:
   ```
   C:\Users\jmyang\Dropbox\1.0_tirepass\wake_tgenai.py
   ```

2. 메모장 또는 편집기로 열기

3. **19번째 줄** 찾기:
   ```python
   TGENAI_MAC = "00-00-00-00-00-00"  # ⚠️ 실제 MAC 주소로 변경 필요!
   ```

4. 3단계에서 확인한 MAC 주소로 변경:
   ```python
   TGENAI_MAC = "00-1A-2B-3C-4D-5E"  # ← 실제 MAC 주소 입력
   ```

5. **저장** (Ctrl + S)

### WOL 테스트 (선택)

다른 PC에서 테스트:

```bash
python wake_tgenai.py
```

---

## 5️⃣ 시스템 재부팅 및 확인 (3분)

### 재부팅

```
시작 메뉴 → 전원 → 다시 시작
```

### 재부팅 후 자동 시작 확인

1. **로그 파일 생성 확인** (2-3분 대기):
   ```
   C:\Users\jmyang\Dropbox\1.0_tirepass\tgenai_gateway_monitor.log
   C:\Users\jmyang\Dropbox\1.0_tirepass\teamviewer_watchdog.log
   C:\Users\jmyang\Dropbox\1.0_tirepass\network_watchdog.log
   ```

2. **로그 내용 확인**:
   - 파일 열어서 최근 시간(몇 분 전) 로그가 있는지 확인
   - "시작" 또는 "정상" 메시지 확인

3. **ERP API 서버 확인**:
   - 브라우저에서 접속: http://localhost:8000/health
   - 출력:
     ```json
     {"status":"healthy","database":"connected","total_goods":6530}
     ```

---

## ✅ 설치 완료 체크리스트

완료 후 다음 항목들을 확인하세요:

### 소프트웨어
- [ ] Python 패키지 설치 완료 (psutil, requests)
- [ ] 작업 스케줄러에 3개 작업 등록 완료

### 자동 시작
- [ ] 재부팅 후 3개 로그 파일 생성 확인
- [ ] 로그 내용에 최근 시간 기록 확인
- [ ] ERP API 서버 헬스체크 정상 확인

### Wake-on-LAN (선택)
- [ ] MAC 주소 확인 완료
- [ ] wake_tgenai.py에 MAC 주소 입력 완료

---

## 🎯 다음 단계 (선택)

### A. Wake-on-LAN BIOS 설정

자세한 내용: `WAKE_ON_LAN_SETUP_GUIDE.md` 참조

간단 요약:
1. 재부팅 → F2 또는 Del 키
2. Power Management → Wake on LAN: Enabled
3. 저장 후 재부팅

### B. 공유기 포트 포워딩

외부에서 WOL 사용하려면:
1. 공유기 관리 페이지 (http://192.168.0.1)
2. 포트포워드 설정
3. UDP 포트 9 → TgenAI PC IP

---

## 🚨 문제 발생 시

### 패키지 설치 실패

```bash
# pip 업그레이드
python -m pip install --upgrade pip

# 다시 설치
pip install psutil requests
```

### 작업 스케줄러 등록 실패

- 관리자 권한으로 실행했는지 확인
- Windows 작업 스케줄러 서비스 실행 확인

### 로그 파일이 생성 안 됨

- 작업 스케줄러 열기 (taskschd.msc)
- 작업 우클릭 → "실행"으로 수동 시작
- 오류 메시지 확인

---

## 📞 지원

더 자세한 내용:
- `COMPLETE_SETUP_GUIDE.md` (70페이지 종합 가이드)
- `WAKE_ON_LAN_SETUP_GUIDE.md` (40페이지 WOL 가이드)

---

**예상 총 소요 시간**: 약 8-10분
**난이도**: 쉬움 (복사-붙여넣기만)
