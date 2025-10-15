# 실시간 재고 변화 추적 시스템 - 최종 설정 가이드

## 완료된 작업

✅ **1. 데이터베이스 테이블 생성**
- `goods_realtime_snapshots` 테이블 생성 완료
- 인덱스 설정 (code, snapshot_time)

✅ **2. Django 모델 추가**
- `GoodsRealtimeSnapshot` 모델 생성
- 헬퍼 메서드 추가:
  - `get_recent_changes()`: 최근 변화가 많은 상품 조회
  - `get_hourly_data()`: 특정 상품의 시간별 데이터

✅ **3. Migration 생성 및 적용**
- `0012_goodsrealtimesnapshot.py` migration 생성
- PythonAnywhere 데이터베이스에 적용 완료

✅ **4. 스냅샷 수집 명령어 작성**
- `collect_realtime_snapshots` management command
- 재고 상위 5개 상품 자동 추적
- 이전 스냅샷과 비교하여 변화량 계산
- 30일 이상 된 스냅샷 자동 정리

✅ **5. Admin 위젯 추가**
- `GoodsRealtimeSnapshotAdmin` 생성
- 시각화 기능:
  - 🟢 재고 증가 (녹색)
  - 🔴 재고 감소 (빨강)
  - ⚪ 변화 없음 (회색)
- 날짜별 필터링 지원

✅ **6. Git 커밋 및 푸시**
- 모든 변경사항 커밋 완료
- GitHub 저장소에 푸시 완료

---

## 남은 작업 (약 10분)

### 1단계: PythonAnywhere 코드 업데이트 (3분)

SSH 터미널 접속:

```bash
cd ~/tirepass
git pull origin main
```

예상 출력:
```
remote: Enumerating objects: 25, done.
remote: Counting objects: 100% (25/25), done.
remote: Compressing objects: 100% (20/20), done.
remote: Total 23 (delta 3), reused 23 (delta 3), pack-reused 0
Unpacking objects: 100% (23/23), done.
From https://github.com/flowgen-tirepass/tirepass
   d083cdc..db23c58  main       -> origin/main
Updating d083cdc..db23c58
Fast-forward
 tire_data/admin.py                              | 120 +++++++++++++++++++
 TgenAI_INSTALL/pythonanywhere_scheduled_task_guide.md | 150 +++++++++++++++++++++++
 ... (20 files changed)
```

### 2단계: 웹앱 재시작 (1분)

PythonAnywhere 대시보드:
1. **Web** 탭 클릭
2. **Reload tirepass.pythonanywhere.com** 버튼 클릭
3. 상태 확인: `Running` 표시

또는 SSH에서:
```bash
touch /var/www/tirepass_pythonanywhere_com_wsgi.py
```

### 3단계: 스냅샷 수집 테스트 (1분)

SSH 터미널에서 수동 실행:

```bash
cd ~/tirepass
source ~/.virtualenvs/itire-venv/bin/activate
python manage.py collect_realtime_snapshots
```

예상 출력:
```
=== 실시간 재고 스냅샷 수집 (2025-10-15 14:30:00) ===

ERP API에서 상품 데이터 조회 중...
수집 대상: 5개 상품

  ANNAITE-AN-16 | 195/70R15 8P AN900 (ANNAITE)   |   55개 ( +0) ⚪
  ANNAITE-AN-02 | 205/55R16 AN600 (ANNAITE)      |   31개 ( +0) ⚪
  ANNAITE-AN-15 | 195R15 8P AN900 (ANNAITE)      |   31개 ( +0) ⚪
  ANNAITE-AN-14 | 235/55R19 AN616 (ANNAITE)      |   30개 ( +0) ⚪
  ANNAITE-AN-07 | 245/45R19 AN606 (ANNAITE)      |   22개 ( +0) ⚪

✅ 스냅샷 수집 완료: 5개
```

### 4단계: Admin에서 확인 (1분)

브라우저에서:
1. https://tirepass.pythonanywhere.com/admin/ 접속
2. 로그인
3. **C. ⚙️ 설정 | 07. 실시간 재고 추적** 클릭

확인 사항:
- 방금 수집한 스냅샷 5개 표시됨
- 스냅샷 시간이 최신임
- 변화량 표시 (처음이라 모두 0)

### 5단계: 자동 스냅샷 수집 설정 (5분)

PythonAnywhere 대시보드:
1. **Tasks** 탭 클릭
2. **Create a new scheduled task** 섹션

설정:
```
Frequency: Hourly
Hour: * (every hour)
Minute: 0
Command: /home/tirepass/.virtualenvs/itire-venv/bin/python /home/tirepass/tirepass/manage.py collect_realtime_snapshots
```

3. **Create** 버튼 클릭

확인:
```
Scheduled tasks:
  Hourly at 0 minutes past: collect_realtime_snapshots
  Next run: 2025-10-15 15:00 (in 30 minutes)
```

---

## 실시간성 증명 전략

### 24시간 후부터

스냅샷이 24회 수집되면:
- 시간별 재고 변화 그래프 생성 가능
- 실제 판매/입고 변화 확인 가능
- 관리자에게 "실시간 데이터" 증명 가능

### 예상 시나리오

**관리자:** "이 데이터가 정말 실시간인가요?"

**답변:**
1. Admin → **C. ⚙️ 설정 | 07. 실시간 재고 추적** 클릭
2. 특정 상품 코드 선택 (예: M-CC2SUV-07)
3. 최근 24시간 스냅샷 표시:
   ```
   10-15 14:00 | M-CC2SUV-07 | 125개 (🟢 +10)  입고 발생
   10-15 13:00 | M-CC2SUV-07 | 115개 (🔴 -5)   판매 발생
   10-15 12:00 | M-CC2SUV-07 | 120개 (⚪ 0)
   ...
   ```

4. **설명:** "ERP 시스템과 매시간 동기화되며, 실제 판매/입고 시점의 재고 변화가 기록됩니다."

---

## 데이터 활용

### 1. 인기 상품 분석

```python
# 최근 24시간 가장 많이 팔린 상품
GoodsRealtimeSnapshot.get_recent_changes(hours=24, limit=10)
```

### 2. 재고 알람

변화량이 -50 이하인 경우 알람:
```python
critical_changes = GoodsRealtimeSnapshot.objects.filter(
    change_from_prev__lte=-50
).order_by('-snapshot_time')[:10]
```

### 3. 시간대별 판매 패턴

```python
# 특정 상품의 시간별 재고 데이터
hourly_data = GoodsRealtimeSnapshot.get_hourly_data('M-CC2SUV-07', hours=24)
```

---

## 문제 해결

### Q1: 스냅샷이 수집되지 않는 경우

**확인:**
```bash
cd ~/tirepass
python manage.py collect_realtime_snapshots
```

**오류 예시:**
```
❌ 스냅샷 수집 실패: Connection refused
```

**해결:**
- TgenAI PC가 켜져 있는지 확인
- ERP API 접근 가능한지 확인: `curl http://itire2.iptime.org:8002/health`

### Q2: 변화량이 항상 0인 경우

**원인:**
- 실제 재고 변화가 없음
- 또는 추적 대상 상품이 거래가 적은 상품

**해결:**
- 추적 대상 변경: 재고가 많은 상품 대신 회전율이 높은 상품 추적
- `collect_realtime_snapshots.py`의 정렬 기준 변경:
  ```python
  # 재고 많은 순 → 최근 변화 많은 순으로 변경
  ```

### Q3: PythonAnywhere 무료 플랜 제한

**알림:**
- 무료 플랜은 scheduled task가 3개월마다 만료됨
- **Extend** 버튼 클릭하여 연장 필요

**확인 주기:** 매 3개월

---

## 다음 단계 (선택사항)

### 1. 대시보드 위젯 추가

Admin 인덱스 페이지에 위젯 추가:
- 최근 1시간 변화량 TOP 5
- 24시간 트렌드 차트 (Chart.js)

### 2. API 엔드포인트 추가

모바일 앱에서 실시간 재고 변화 조회:
```
GET /api/goods/{code}/realtime-history/
```

### 3. 알람 시스템

재고 급감 시 이메일/SMS 알람:
- 변화량 -30 이상: 경고
- 변화량 -50 이상: 긴급

---

**작성일:** 2025-10-15
**소요 시간:** 10분 (자동화 설정 후 24시간 데이터 수집)
**다음 확인:** 24시간 후 (2025-10-16 오후)

## 성공 기준

✅ 매시간 스냅샷 자동 수집
✅ Admin에서 시간별 변화 확인 가능
✅ 🟢🔴⚪ 변화량 시각화
✅ 관리자에게 실시간성 증명 가능
