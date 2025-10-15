# Wake-on-LAN (WOL) 완벽 설정 가이드

## 📖 목차
1. [Wake-on-LAN이란?](#wake-on-lan이란)
2. [BIOS 설정](#bios-설정)
3. [Windows 설정](#windows-설정)
4. [공유기 설정](#공유기-설정)
5. [MAC 주소 확인](#mac-주소-확인)
6. [WOL 전송 방법](#wol-전송-방법)
7. [문제 해결](#문제-해결)

---

## Wake-on-LAN이란?

**Wake-on-LAN (WOL)**은 꺼져 있는 컴퓨터를 네트워크를 통해 원격으로 켤 수 있는 기술입니다.

### 작동 원리
```
[원격 PC] → Magic Packet 전송 → [네트워크] → [TgenAI PC 전원 ON]
```

### 필요 조건
- ✅ 메인보드 WOL 지원 (대부분 지원)
- ✅ 유선 LAN 연결 (무선은 불안정)
- ✅ BIOS에서 WOL 활성화
- ✅ Windows에서 WOL 활성화
- ✅ 전원 케이블 연결 (콘센트에 꽂혀 있어야 함)

---

## BIOS 설정

### 1단계: BIOS 진입

1. **PC 재부팅**
2. **부팅 중 키 연타**:
   - Dell/HP: `F2` 또는 `F12`
   - ASUS/MSI: `Del` 또는 `F2`
   - Lenovo: `F1` 또는 `F2`

### 2단계: WOL 옵션 찾기

BIOS 메뉴 위치 (제조사별):

**일반적인 위치**:
```
Power Management (전원 관리)
  └─ Wake on LAN (LAN으로 깨우기)
  └─ Power On by PCI-E/PCI (PCI-E로 전원 켜기)
  └─ Resume by PCI-E Device (PCI-E 장치로 재시작)
```

**ASUS**:
```
Advanced (고급)
  └─ APM Configuration
      └─ Power On By PCI-E/PCI: [Enabled]
```

**Dell**:
```
Power Management
  └─ Wake on LAN/WLAN: [LAN Only]
  └─ Block Sleep: [Disabled]
```

**HP**:
```
Advanced
  └─ Built-in Device Options
      └─ Network Boot: [Enabled]
      └─ Wake on LAN: [Boot to Network]
```

### 3단계: 설정 활성화

다음 옵션들을 **Enabled** 또는 **ON**으로 설정:

- ✅ **Wake on LAN**: Enabled
- ✅ **Power On by PCI-E Device**: Enabled
- ✅ **Resume by PCI-E Device**: Enabled
- ✅ **Deep Sleep Control**: Disabled (있는 경우)

### 4단계: 저장 및 재부팅

- `F10` 키 눌러 저장
- `Yes` 선택하여 재부팅

---

## Windows 설정

### 1단계: 네트워크 어댑터 설정

#### 방법 1: 제어판 (권장)

1. **제어판 열기**:
   - `Win + R` → `ncpa.cpl` 입력 → Enter

2. **네트워크 어댑터 찾기**:
   - "이더넷" 또는 "로컬 영역 연결" 우클릭
   - **속성** 선택

3. **구성 버튼 클릭**

4. **전원 관리 탭**:
   - ✅ "컴퓨터가 이 장치를 끌 수 있도록 허용" 체크
   - ✅ "이 장치를 사용하여 컴퓨터의 대기 모드 종료 허용" 체크
   - ✅ "Magic Packet만 컴퓨터의 대기 모드를 종료할 수 있음" 체크

5. **고급 탭**:
   - **Wake on Magic Packet**: Enabled
   - **Wake on Pattern Match**: Enabled (있는 경우)
   - **Energy Efficient Ethernet**: Disabled (있는 경우)
   - **Green Ethernet**: Disabled (있는 경우)

6. **확인** 클릭

#### 방법 2: PowerShell (자동화)

관리자 권한 PowerShell에서 실행:

```powershell
# 네트워크 어댑터 확인
Get-NetAdapter

# WOL 활성화 (어댑터 이름을 "이더넷"으로 가정)
Enable-NetAdapterPowerManagement -Name "이더넷" -WakeOnMagicPacket
Enable-NetAdapterPowerManagement -Name "이더넷" -WakeOnPattern

# 확인
Get-NetAdapterPowerManagement -Name "이더넷"
```

### 2단계: 전원 옵션 설정

1. **제어판 → 전원 옵션**
2. **현재 사용 중인 계획 옆 "계획 설정 변경"** 클릭
3. **고급 전원 관리 옵션 설정 변경** 클릭
4. **USB 설정 → USB 선택적 일시 중단 설정**: **사용 안 함**
5. **PCI Express → 링크 상태 전원 관리**: **해제**
6. **적용** 및 **확인**

### 3단계: 빠른 시작 비활성화 (중요!)

Windows 10/11의 빠른 시작 기능은 WOL을 방해할 수 있습니다.

1. **제어판 → 전원 옵션**
2. **전원 단추 작동 설정** (왼쪽 메뉴)
3. **현재 사용할 수 없는 설정 변경** 클릭
4. **빠른 시작 켜기(권장)** 체크 해제 ❌
5. **변경 내용 저장**

---

## 공유기 설정 (포트 포워딩)

인터넷을 통해 외부에서 WOL을 사용하려면 공유기 설정이 필요합니다.

### 1단계: 공유기 관리 페이지 접속

```
일반적인 주소:
- http://192.168.0.1
- http://192.168.1.1
- http://192.168.219.1 (KT)
```

### 2단계: 포트 포워딩 설정

**ipTIME 공유기**:
```
1. 관리도구 → 고급 설정 → NAT/라우터 관리 → 포트포워드 설정
2. 규칙 추가:
   - 규칙 이름: WOL
   - 내부 IP: 192.168.x.x (TgenAI PC 고정 IP)
   - 외부 포트: 9 (UDP)
   - 내부 포트: 9 (UDP)
   - 프로토콜: UDP
3. 적용
```

**일반 공유기**:
```
Port Forwarding (포트 포워딩)
  - External Port: 9
  - Internal Port: 9
  - Internal IP: [TgenAI PC의 로컬 IP]
  - Protocol: UDP
```

### 3단계: DHCP 예약 (고정 IP)

TgenAI PC의 IP 주소가 변경되지 않도록 고정:

```
1. DHCP 서버 설정 → 수동 IP 할당
2. TgenAI PC의 MAC 주소 입력
3. 고정 IP 할당 (예: 192.168.0.100)
4. 저장
```

---

## MAC 주소 확인

### 방법 1: 명령 프롬프트

```batch
ipconfig /all
```

출력 예시:
```
이더넷 어댑터 이더넷:
   물리적 주소 . . . . . . . . : 00-1A-2B-3C-4D-5E
```

### 방법 2: PowerShell

```powershell
Get-NetAdapter | Select-Object Name, MacAddress
```

### 방법 3: Windows 설정

```
설정 → 네트워크 및 인터넷 → 이더넷 → 속성
→ 아래로 스크롤하여 "물리적 주소(MAC)" 확인
```

**MAC 주소 형식**:
- Windows: `00-1A-2B-3C-4D-5E`
- Linux/Mac: `00:1a:2b:3c:4d:5e`

---

## WOL 전송 방법

### 1. 로컬 네트워크에서 (광주 본사 내)

다른 PC에서 실행:

#### Python 스크립트 사용
→ `wake_tgenai.py` 참조 (별도 파일)

#### PowerShell 사용
```powershell
# WOL 전송 함수
function Send-WOL {
    param(
        [Parameter(Mandatory=$true)]
        [string]$MacAddress
    )

    $Mac = $MacAddress -replace '[:-]',''
    $Target = [byte[]](0xFF * 6)
    $Target += [byte[]](($Mac -split '(..)' | Where-Object {$_}) | ForEach-Object {[convert]::ToByte($_, 16)}) * 16

    $UdpClient = New-Object System.Net.Sockets.UdpClient
    $UdpClient.Connect(([System.Net.IPAddress]::Broadcast), 9)
    [void]$UdpClient.Send($Target, $Target.Length)
    $UdpClient.Close()

    Write-Host "Magic Packet 전송 완료: $MacAddress"
}

# TgenAI MAC 주소 입력 후 실행
Send-WOL -MacAddress "00-1A-2B-3C-4D-5E"
```

### 2. 외부 인터넷에서

#### 방법 1: WOL 웹 서비스 (권장)
- https://www.depicus.com/wake-on-lan/woli
- MAC 주소와 공인 IP 입력

#### 방법 2: Python 스크립트
→ `wake_tgenai_remote.py` 참조 (별도 파일)

#### 방법 3: 모바일 앱
- **Android**: Wake on LAN
- **iOS**: Wake On Lan

---

## 문제 해결

### 1. WOL이 작동하지 않음

#### 체크리스트

- [ ] BIOS에서 WOL 활성화 확인
- [ ] Windows 네트워크 어댑터 설정 확인
- [ ] 빠른 시작 비활성화 확인
- [ ] 유선 LAN 케이블 연결 확인 (무선 안 됨!)
- [ ] 전원 케이블 콘센트에 연결 확인
- [ ] MAC 주소 정확한지 확인
- [ ] 공유기 포트 포워딩 설정 확인 (외부 접속 시)

### 2. 로컬에서는 되는데 외부에서 안 됨

**원인**: 공유기 설정 문제

**해결책**:
1. 공유기 포트 포워딩 재확인 (UDP 포트 9)
2. TgenAI PC 고정 IP 확인
3. 공인 IP 변경 확인 (DDNS 사용 권장)

### 3. Magic Packet 전송 후에도 켜지지 않음

**시도할 방법**:

1. **완전 종료 (권장)**:
   ```
   시작 메뉴 → 전원 → Shift 키 누른 채로 "종료" 클릭
   ```
   (빠른 시작 무시하고 완전 종료)

2. **BIOS에서 추가 설정 확인**:
   - Deep Sleep: Disabled
   - ErP Support: Disabled
   - AC Recovery: Power On

3. **네트워크 어댑터 드라이버 업데이트**:
   - 장치 관리자 → 네트워크 어댑터 → 드라이버 업데이트

### 4. 종료 후 몇 시간 뒤에 WOL 실패

**원인**: 전원 관리 기능이 LAN 카드 전원 차단

**해결책**:
1. BIOS에서 "ErP Support" 또는 "Deep Sleep" 비활성화
2. 전원 옵션 → USB 선택적 일시 중단: 사용 안 함

---

## 테스트 절차

### 1단계: 로컬 네트워크 테스트

1. TgenAI PC를 정상 종료 (Shift + 종료)
2. 같은 네트워크의 다른 PC에서 WOL 전송
3. TgenAI PC 전원 켜지는지 확인 (LED 점등)
4. 30초 대기 후 TeamViewer 접속 시도

### 2단계: 외부 네트워크 테스트

1. TgenAI PC를 정상 종료
2. 모바일 데이터 또는 다른 네트워크에서 WOL 전송
3. 1-2분 대기 후 TeamViewer 접속 시도

---

## 추천 설정 요약

### BIOS 설정
```
✅ Wake on LAN: Enabled
✅ Power On by PCI-E: Enabled
❌ Deep Sleep: Disabled
❌ ErP Support: Disabled
```

### Windows 설정
```
✅ Magic Packet으로 깨우기: Enabled
✅ 패턴 일치로 깨우기: Enabled
❌ 빠른 시작: Disabled
❌ USB 선택적 일시 중단: Disabled
```

### 공유기 설정
```
✅ 포트 포워딩: UDP 9번 포트
✅ DHCP 예약: TgenAI 고정 IP
✅ DDNS 설정 (선택)
```

---

## 다음 단계

1. **WOL 설정 완료** (이 가이드)
2. **WOL 전송 스크립트 설치** → `wake_tgenai.py`
3. **자동 복구 시스템 구축** → `TGENAI_EMERGENCY_REBOOT_GUIDE.md`
4. **TeamViewer 감시 스크립트** → `teamviewer_watchdog.bat`

---

**작성일**: 2025-10-15
**목적**: TgenAI PC 원격 전원 제어
