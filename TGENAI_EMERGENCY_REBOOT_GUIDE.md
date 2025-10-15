# TgenAI 긴급 재부팅 및 복구 가이드

## 🚨 현재 상황

**문제**: TeamViewer 접속 불가
**위치**: 광주광역시 (주)아이타이어 본사 사무실
**영향**: ERP 게이트웨이 모니터링 중단 가능성

---

## ⚡ 즉시 조치 사항 (현장 재부팅 필요)

### 1단계: 물리적 재부팅 (현장 담당자)

광주 본사에 계신 분께 요청하여 다음 절차를 진행하세요:

```
1. TgenAI PC 찾기
   - 컴퓨터명: ITIRE2 또는 TgenAI
   - 위치: 광주 본사 사무실

2. 재부팅
   방법 1 (정상):
   - 시작 메뉴 → 전원 → 다시 시작

   방법 2 (응답 없는 경우):
   - Ctrl + Alt + Delete → 전원 → 다시 시작

   방법 3 (완전 멈춤):
   - 전원 버튼 길게 누르기 (5초)
   - 10초 대기
   - 전원 버튼 다시 누르기

3. 재부팅 후 확인
   - Windows 로그인 완료 대기
   - 네트워크 연결 확인 (우측 하단 아이콘)
   - TeamViewer 실행 확인 (작업 표시줄)
```

### 2단계: 재부팅 후 자동 시작 확인

재부팅 후 다음 항목들이 자동으로 시작되어야 합니다:

- ✅ **TeamViewer** (원격 접속용)
- ✅ **ERP API 서버** (erp_api_server.py)
- ✅ **TgenAI 게이트웨이 모니터** (작업 스케줄러)

---

## 🔧 근본 원인 분석

### TeamViewer 접속 불가 원인

1. **TgenAI PC 전원 꺼짐**
   - 정전, 전원 케이블 분리
   - 하드웨어 오류

2. **네트워크 문제**
   - 인터넷 연결 끊김
   - 공유기 재부팅 필요
   - IP 주소 변경

3. **TeamViewer 프로세스 종료**
   - 프로그램 충돌
   - Windows 업데이트 후 미실행

4. **Windows 응답 없음**
   - 시스템 과부하
   - 프로세스 데드락

---

## 🌐 Wake-on-LAN 설정 (향후 원격 재시작)

다음 섹션을 참고하여 Wake-on-LAN을 설정하면,
**PC가 꺼져 있어도 원격에서 전원을 켤 수 있습니다!**

이후 별도 가이드 파일 참조:
- `WAKE_ON_LAN_SETUP_GUIDE.md`

---

## 🤖 자동 복구 시스템 (재부팅 후 설정)

재부팅 후 다음 스크립트들을 실행하여 자동 복구 시스템을 구축하세요:

### 1. TeamViewer 자동 시작 및 감시
- 파일: `teamviewer_watchdog.bat`
- 위치: 시작 프로그램 폴더

### 2. ERP 게이트웨이 모니터
- 파일: `tgenai_erp_gateway_monitor.py`
- 실행: 작업 스케줄러 자동 실행

### 3. 네트워크 감시 및 재연결
- 파일: `network_watchdog.bat`
- 실행: 작업 스케줄러 자동 실행

---

## 📞 비상 연락 절차

### 광주 본사 담당자에게 요청할 사항

**전화로 전달할 내용**:

```
안녕하세요. 긴급 상황입니다.

광주 본사에 있는 TgenAI 컴퓨터를 재부팅해 주셔야 합니다.

1. 컴퓨터 위치: [위치 정보]
2. 재부팅 방법: 전원 버튼 누르기 또는 시작 메뉴 → 다시 시작
3. 재부팅 후 확인: TeamViewer가 자동으로 실행되는지 확인

감사합니다!
```

---

## 🔍 재부팅 후 점검 체크리스트

재부팅이 완료되면 다음 항목들을 순서대로 확인하세요:

### 네트워크 연결
- [ ] 인터넷 연결 확인 (우측 하단 네트워크 아이콘)
- [ ] 공인 IP 확인: http://checkip.amazonaws.com
- [ ] itire2.iptime.org 도메인 확인

### TeamViewer
- [ ] TeamViewer 실행 중 (작업 표시줄 아이콘)
- [ ] TeamViewer ID 확인
- [ ] 원격 접속 테스트

### ERP 시스템
- [ ] ERP API 서버 실행 중 (포트 8000)
- [ ] Firebird DB 연결 확인
- [ ] 헬스체크: http://localhost:8000/health

### 게이트웨이 모니터
- [ ] 작업 스케줄러에서 실행 중 확인
- [ ] 로그 파일 생성 확인: `tgenai_gateway_monitor.log`
- [ ] 최근 로그 확인 (30분 이내)

---

## 📋 점검 명령어 (PowerShell)

재부팅 후 TgenAI에서 다음 명령어를 실행하여 상태를 확인하세요:

```powershell
# 네트워크 연결 확인
Test-Connection -ComputerName google.com -Count 2

# ERP API 서버 확인
Invoke-WebRequest -Uri "http://localhost:8000/health" | Select-Object -ExpandProperty Content

# TeamViewer 프로세스 확인
Get-Process TeamViewer* | Select-Object Name, Id, StartTime

# 작업 스케줄러 확인
schtasks /query /tn "TgenAI_ERP_Gateway_Monitor"

# 로그 파일 확인 (최근 20줄)
Get-Content C:\Users\jmyang\Dropbox\1.0_tirepass\tgenai_gateway_monitor.log -Tail 20
```

---

## 🎯 재발 방지 대책

### 1. Wake-on-LAN 설정 (최우선)
→ `WAKE_ON_LAN_SETUP_GUIDE.md` 참조

### 2. TeamViewer 자동 복구 시스템
→ `teamviewer_watchdog.bat` 설치

### 3. UPS (무정전 전원 공급 장치) 설치 권장
- 정전 시 PC 안전하게 종료
- 순간 정전 방지

### 4. 원격 모니터링 강화
- 주기적인 상태 확인
- 장애 발생 시 알림

---

**작성일**: 2025-10-15
**긴급 상황**: 광주 본사 현장 재부팅 필요
