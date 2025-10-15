# PythonAnywhere 스케줄 작업 설정 가이드

## 실시간 재고 스냅샷 자동 수집 설정

### 1. PythonAnywhere 대시보드 접속

1. https://www.pythonanywhere.com 로그인
2. **Tasks** 탭 클릭

### 2. Scheduled Task 추가

#### 설정 정보:

```
Frequency: Hourly
Hour: * (every hour)
Minute: 0
Command: /home/tirepass/.virtualenvs/itire-venv/bin/python /home/tirepass/tirepass/manage.py collect_realtime_snapshots
```

#### 단계별 설정:

1. **Tasks** 페이지에서 **Create a new scheduled task** 섹션 찾기
2. **Frequency** 드롭다운에서 `Hourly` 선택
3. **Hour** 필드에 `*` 입력 (모든 시간)
4. **Minute** 필드에 `0` 입력 (정시)
5. **Command** 필드에 다음 입력:
   ```bash
   /home/tirepass/.virtualenvs/itire-venv/bin/python /home/tirepass/tirepass/manage.py collect_realtime_snapshots
   ```
6. **Create** 버튼 클릭

### 3. 작업 확인

설정 완료 후 **Scheduled tasks** 목록에 새 작업이 표시됨:

```
Hourly at 0 minutes past: collect_realtime_snapshots
Next run: [다음 정시]
```

### 4. 수동 테스트 (선택사항)

설정 후 바로 테스트하려면 SSH 터미널에서:

```bash
cd ~/tirepass
source ~/.virtualenvs/itire-venv/bin/activate
python manage.py collect_realtime_snapshots
```

### 5. 로그 확인

몇 시간 후 데이터베이스에서 스냅샷 확인:

```sql
SELECT
    code,
    name,
    jaego,
    change_from_prev,
    snapshot_time
FROM goods_realtime_snapshots
ORDER BY snapshot_time DESC
LIMIT 20;
```

### 6. 예상 결과

- **첫 1시간**: 모든 상품 변화량 0 (기준 스냅샷)
- **2시간 후부터**: 실제 재고 변화량 표시
  - 🟢 증가 (출고 취소, 입고)
  - 🔴 감소 (판매, 출고)
  - ⚪ 변화 없음

### 7. 데이터 활용

24시간 후부터:
- Admin 위젯에서 실시간 변화 그래프 표시
- 관리자에게 "실시간 데이터" 증명 가능
- 인기 상품 분석 가능

---

## 문제 해결

### Task가 실행되지 않는 경우:

1. **Tasks** 탭에서 **Expiry** 컬럼 확인
   - PythonAnywhere 무료 플랜은 scheduled task가 3개월마다 만료됨
   - **Extend** 버튼 클릭하여 연장

2. 명령어 경로 확인:
   ```bash
   which python  # virtualenv 활성화 후
   pwd  # manage.py 위치 확인
   ```

3. 로그 확인:
   - PythonAnywhere는 scheduled task 실행 로그를 **Files** 탭의 `/var/log/` 디렉토리에 저장
   - 또는 **Tasks** 페이지에서 작업 옆의 **Log** 링크 클릭

### 실행 시간 변경:

- 트래픽이 적은 시간대로 조정하려면 `Minute` 필드를 변경
  - 예: `15` → 매시 15분에 실행 (00:15, 01:15, 02:15...)

---

**작성일**: 2025-10-15
**작업 소요 시간**: 약 5분
**다음 단계**: Admin 위젯 추가
