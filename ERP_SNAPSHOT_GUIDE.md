# ERP 스냅샷 시스템 사용 가이드

## 📊 개요

ERP 상품 수를 **매시간 자동 기록**하여 과거 특정 시점의 데이터를 조회할 수 있는 시스템입니다.

---

## 🎯 현재 상황 (2025-10-14 기준)

### Django DB (pythonanywhere)
- **상품 수**: 6,519개
- **마지막 동기화**: 2025-10-07 08:01:01 (7일 전)
- **문제**: Django DB 동기화가 중단됨

### ERP 실시간 (itire2.iptime.org:8000)
- **상품 수**: 6,530개
- **상태**: 정상 작동 중
- **차이**: +11개 (Django보다 많음)

### 해결 방법
✅ **시간별 스냅샷 기록** 시스템 구축 완료!
- 매시간 ERP 상태 기록
- 과거 시점 데이터 조회 가능
- 30일 자동 백업

---

## 🚀 사용 방법

### 1. 수동으로 스냅샷 기록

```bash
# 현재 시점 기록 (강제 실행)
python manage.py record_erp_snapshot --force

# 결과 예시:
# 🔍 ERP 상태 확인 중...
# ✅ 스냅샷 저장 완료: 2025-10-14 07:38:00 | 상품: 6,530개 | 응답: 121.1ms
```

### 2. 특정 시점 데이터 조회

```bash
# Django Shell에서
python manage.py shell

# Python 코드:
from tire_data.models import ERPSnapshot
from django.utils import timezone
from datetime import datetime

# 오늘 09시 상품 수 조회
count_9am = ERPSnapshot.get_today_9am_count()
if count_9am:
    print(f'오늘 09시 상품 수: {count_9am:,}개')
else:
    print('데이터 없음')

# 특정 시간 조회
target_time = timezone.make_aware(datetime(2025, 10, 14, 9, 0, 0))
count = ERPSnapshot.get_count_at_time(target_time)
print(f'상품 수: {count:,}개')

# 최근 24시간 통계
stats = ERPSnapshot.get_hourly_stats(hours=24)
print(f"평균 응답 시간: {stats['avg_response_time']:.2f}ms")
print(f"총 체크 횟수: {stats['total_checks']}회")
print(f"연결 성공: {stats['connected_count']}회")
```

### 3. 관리자 페이지에서 확인

```
http://tirepass.pythonanywhere.com/admin/tire_data/erpsnapshot/

# 목록 화면:
2025-10-14 07:38 | connected | 6,530개
2025-10-14 08:00 | connected | 6,532개
2025-10-14 09:00 | connected | 6,535개
...
```

---

## ⏰ 자동 실행 설정 (PythonAnywhere)

### 크론탭 설정

PythonAnywhere > **Tasks** 탭:

```bash
# 매시간 정각에 실행
0 * * * * /home/tirepass/.virtualenvs/tirepass-venv/bin/python /home/tirepass/tirepass/manage.py record_erp_snapshot

# 또는 매일 특정 시간에만:
0 9,12,15,18 * * * /home/tirepass/.virtualenvs/tirepass-venv/bin/python /home/tirepass/tirepass/manage.py record_erp_snapshot
```

### 크론탭 의미
- `0 * * * *`: 매시간 0분 (예: 09:00, 10:00, 11:00...)
- `0 9,12,15,18 * * *`: 09시, 12시, 15시, 18시에만

---

## 📈 데이터 분석 예시

### 1. 일일 상품 증가량

```python
from tire_data.models import ERPSnapshot
from django.utils import timezone
from datetime import timedelta

# 오늘 09시
today_9am = ERPSnapshot.get_today_9am_count()

# 어제 09시
yesterday = timezone.now() - timedelta(days=1)
yesterday_9am = ERPSnapshot.get_count_at_time(
    timezone.make_aware(datetime.combine(yesterday.date(), datetime.min.time().replace(hour=9)))
)

if today_9am and yesterday_9am:
    diff = today_9am - yesterday_9am
    print(f'어제 대비 증가: {diff:+}개')
```

### 2. 시간대별 상품 수 변화

```python
from tire_data.models import ERPSnapshot
from django.utils import timezone
from datetime import datetime, timedelta

# 오늘 하루 데이터
today = timezone.now().date()
snapshots = ERPSnapshot.objects.filter(
    timestamp__date=today,
    status='connected'
).order_by('timestamp')

print('시간대별 상품 수:')
for snap in snapshots:
    print(f'{snap.timestamp.strftime("%H:%M")} - {snap.erp_goods_count:,}개')
```

### 3. 응답 시간 모니터링

```python
from tire_data.models import ERPSnapshot
from django.db.models import Avg

# 최근 24시간 평균 응답 시간
stats = ERPSnapshot.get_hourly_stats(hours=24)
print(f"평균 응답 시간: {stats['avg_response_time']:.2f}ms")
print(f"최대 응답 시간: {stats['max_response_time']:.2f}ms")
print(f"최소 응답 시간: {stats['min_response_time']:.2f}ms")

# 느린 응답 찾기
slow_responses = ERPSnapshot.objects.filter(
    response_time_ms__gt=500  # 500ms 이상
).order_by('-response_time_ms')[:10]

print('\n가장 느린 응답 10건:')
for snap in slow_responses:
    print(f'{snap.timestamp} - {snap.response_time_ms:.2f}ms')
```

### 4. 연결 안정성 분석

```python
from tire_data.models import ERPSnapshot
from django.utils import timezone
from datetime import timedelta

# 최근 7일 데이터
week_ago = timezone.now() - timedelta(days=7)
snapshots = ERPSnapshot.objects.filter(timestamp__gte=week_ago)

total = snapshots.count()
connected = snapshots.filter(status='connected').count()
success_rate = (connected / total * 100) if total > 0 else 0

print(f'연결 성공률: {success_rate:.2f}% ({connected}/{total})')
```

---

## 🔍 질문에 대한 답변

### Q: "오늘 09시에는 몇 개 상품으로 업무가 시작되었나요?"

**A: 지금부터는 확인 가능합니다!**

```python
from tire_data.models import ERPSnapshot

# 오늘 09시 상품 수
count = ERPSnapshot.get_today_9am_count()

if count:
    print(f'✅ 오늘 09시: {count:,}개')
else:
    print('❌ 아직 09시 데이터가 기록되지 않았습니다.')
    print('   (크론탭 설정 후 내일부터 자동 기록)')
```

**현재 상황 (2025-10-14 07:38 기준):**
- 아직 09시 전이므로 데이터 없음
- 크론탭 설정 후 **오늘 09:00부터 자동 기록 시작**
- 내일부터는 "오늘 09시 상품 수" 조회 가능

---

## 📊 대시보드 위젯 연동

### 위젯에 시간별 추이 표시

```javascript
// tire_data/templates/admin/base_site.html에 추가 가능

async function fetchSnapshotStats() {
    const response = await fetch('/api/admin/erp/snapshot-stats/');
    const data = await response.json();

    // 예시:
    // {
    //   "today_9am": 6530,
    //   "current": 6535,
    //   "diff": +5,
    //   "hourly_trend": [6530, 6532, 6535]
    // }

    document.getElementById('today-9am-count').textContent =
        `오늘 09시: ${data.today_9am.toLocaleString()}개`;
    document.getElementById('current-diff').textContent =
        `(+${data.diff}개)`;
}
```

---

## 💾 데이터 보관 정책

### 자동 삭제
- **30일 이상** 오래된 스냅샷 자동 삭제
- 디스크 공간 절약
- record_erp_snapshot 명령 실행 시 자동 처리

### 백업 권장
```bash
# 중요 데이터 백업
python manage.py dumpdata tire_data.ERPSnapshot > erp_snapshots_backup.json

# 복원
python manage.py loaddata erp_snapshots_backup.json
```

---

## 🎓 활용 시나리오

### 1. 일일 업무 시작 상품 수 추적
- 매일 09시 상품 수 자동 기록
- 전일 대비 증감 확인
- 주간/월간 추이 분석

### 2. 장애 발생 시점 추적
- 응답 시간 급증 시점 확인
- 연결 끊김 기록 조회
- 원인 분석 데이터 제공

### 3. 성능 모니터링
- 시간대별 응답 시간 분석
- 느린 시간대 파악
- 시스템 최적화 근거

### 4. 비즈니스 인사이트
- 상품 증가 추이 분석
- 입고/판매 패턴 파악
- 재고 변동 모니터링

---

## 🐛 트러블슈팅

### 문제 1: 스냅샷이 기록되지 않음

**원인**: 크론탭 설정 안 됨 또는 ERP 서버 연결 실패

**해결**:
```bash
# 수동 실행 테스트
python manage.py record_erp_snapshot --force

# 크론탭 확인 (PythonAnywhere)
# Tasks 탭에서 설정 확인
```

### 문제 2: 09시 데이터가 None

**원인**: 09시 이전이거나, 09시 스냅샷이 아직 기록되지 않음

**해결**:
```python
# 가장 가까운 시간의 데이터 조회
from tire_data.models import ERPSnapshot
latest = ERPSnapshot.objects.filter(status='connected').first()
if latest:
    print(f'가장 최근: {latest.timestamp} - {latest.erp_goods_count:,}개')
```

### 문제 3: 오래된 데이터 삭제 안 됨

**원인**: record_erp_snapshot 명령이 실행되지 않음

**해결**:
```bash
# 수동 정리
python manage.py shell

from tire_data.models import ERPSnapshot
from django.utils import timezone
from datetime import timedelta

cutoff = timezone.now() - timedelta(days=30)
deleted = ERPSnapshot.objects.filter(timestamp__lt=cutoff).delete()
print(f'{deleted[0]}개 삭제')
```

---

## 📈 향후 개선 계획

### Phase 1 (완료) ✅
- [x] 스냅샷 모델 생성
- [x] 기록 명령어 구현
- [x] 조회 메서드 구현
- [x] 크론탭 설정 가이드

### Phase 2 (계획 중)
- [ ] API 엔드포인트 추가 (`/api/admin/erp/snapshots/`)
- [ ] 위젯에 시간별 그래프 추가
- [ ] 이메일 알림 (급격한 변화 감지 시)
- [ ] 엑셀 리포트 생성

### Phase 3 (장기 계획)
- [ ] 머신러닝 기반 예측 (내일 09시 예상 상품 수)
- [ ] 이상 패턴 자동 감지
- [ ] 슬랙/텔레그램 알림 연동

---

## 📞 문의

**기술 문서**: `TGENAI_AGENT_PLAN.md` 참조
**깃허브**: https://github.com/flowgen-tirepass/tirepass

---

**마지막 업데이트**: 2025-10-14 07:38
**작성자**: Claude Code
**버전**: 1.0.0
