# 성능표시 기능 통합 배포 가이드

## 변경 사항 요약

### 문제점
- BrandPatternPerformance 모델이 Admin 메뉴에 표시되지 않는 문제 발생
- 별도의 메뉴로 관리하는 것이 비효율적

### 해결 방안
- **BrandPatternPerformance 모델 삭제**
- **BrandPattern 모델에 성능표시 필드 통합**
- 기존 "B. 💰 할인 | 02. 브랜드 패턴" 메뉴에서 모든 것을 관리

## 변경된 파일 목록

### 1. 모델 변경
- `tire_data/models.py`
  - ✅ BrandPattern 모델에 성능표시 필드 추가 (classification, grade, performance, season, road_type, logo_filename)
  - ✅ BrandPatternPerformance 모델 삭제
  - ✅ get_performance_boxes() 메서드 BrandPattern에 추가

### 2. Admin 변경
- `tire_data/admin.py`
  - ✅ BrandPatternAdmin에 성능표시 필드 추가
  - ✅ performance_display 컬럼 추가 (성능표시 요약)
  - ✅ BrandPatternPerformance import 제거
  - ✅ BrandPatternPerformanceAdmin 클래스 삭제
  - ✅ custom_admin_site 등록에서 BrandPatternPerformance 제거

### 3. Forms 변경
- `tire_data/forms.py`
  - ✅ BrandPatternPerformance import 제거
  - ✅ BrandPatternPerformanceForm 클래스 삭제

### 4. API 변경
- `tire_data/api_views.py`
  - ✅ BrandPatternPerformance import 제거
  - ✅ BrandPattern 기반으로 성능표시 데이터 조회 변경
  - ✅ brand_performance_map 로직 수정 (default 제거, patterns만 사용)

### 5. 마이그레이션
- `tire_data/migrations/0021_add_performance_fields_to_brandpattern.py`
  - BrandPattern에 6개 필드 추가
- `tire_data/migrations/0022_remove_brandpatternperformance_add_performance_to_brandpattern.py`
  - BrandPatternPerformance 모델 삭제

## 배포 절차

### 1단계: 로컬에서 Git Commit & Push
```bash
cd C:\Users\jmyang\Dropbox\1.0_tirepass

# 변경사항 확인
git status

# 변경된 파일 추가
git add tire_data/models.py
git add tire_data/admin.py
git add tire_data/forms.py
git add tire_data/api_views.py
git add tire_data/migrations/0021_add_performance_fields_to_brandpattern.py
git add tire_data/migrations/0022_remove_brandpatternperformance_add_performance_to_brandpattern.py

# 커밋
git commit -m "Refactor: BrandPatternPerformance를 BrandPattern에 통합

- BrandPattern 모델에 성능표시 필드 추가 (classification, grade, performance, season, road_type, logo_filename)
- BrandPatternPerformance 모델 삭제
- BrandPatternAdmin에 성능표시 관리 기능 추가
- API에서 BrandPattern 기반으로 성능표시 데이터 조회
- 관리자 메뉴 간소화: B.02 브랜드 패턴에서 모든 것 관리"

# 서버로 푸시
git push origin main
```

### 2단계: PythonAnywhere에서 Pull
```bash
# PythonAnywhere Bash 콘솔
cd /home/tirepass/tirepass

# 최신 코드 가져오기
git pull origin main
```

### 3단계: 마이그레이션 적용
```bash
# 마이그레이션 상태 확인
python manage.py showmigrations tire_data | tail -5

# 0021, 0022 마이그레이션 적용
python manage.py migrate tire_data

# 결과 확인 - 아래와 같이 표시되어야 함:
# [X] 0021_add_performance_fields_to_brandpattern
# [X] 0022_remove_brandpatternperformance_add_performance_to_brandpattern
```

**예상 출력:**
```
Running migrations:
  Applying tire_data.0021_add_performance_fields_to_brandpattern... OK
  Applying tire_data.0022_remove_brandpatternperformance_add_performance_to_brandpattern... OK
```

### 4단계: 데이터베이스 확인
```bash
# MySQL 콘솔에서 확인
python manage.py dbshell
```

```sql
-- BrandPattern 테이블에 새 필드 추가 확인
DESCRIBE brand_patterns;

-- classification, grade, performance, season, road_type, logo_filename 컬럼이 있어야 함

-- BrandPatternPerformance 테이블 삭제 확인
SHOW TABLES LIKE 'brand_pattern_performance';
-- Empty set (0.00 sec) 이어야 함

exit;
```

### 5단계: Python 캐시 삭제
```bash
cd /home/tirepass/tirepass

# Python 캐시 완전 삭제
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
```

### 6단계: 웹 앱 재시작
1. PythonAnywhere 웹 페이지 접속
2. **Web** 탭 클릭
3. **Reload** 버튼 (초록색) 클릭
4. 재시작 완료 메시지 확인

### 7단계: 관리자 페이지 확인
1. **새 시크릿 모드 창** 열기
2. https://tirepass.pythonanywhere.com/admin/ 접속
3. 로그인
4. **B. 💰 할인** 섹션 확인
5. **02. 브랜드 패턴** 클릭
6. 패턴 하나를 선택하여 편집
7. **성능 표시 (모바일 상품카드용)** 섹션이 보이는지 확인
   - 분류1
   - 상품등급
   - 상품성능
   - 계절
   - 로드타입
   - 브랜드 로고 파일명

## 새로운 사용 방법

### 관리자에서 성능표시 설정하기
1. **B. 💰 할인 | 02. 브랜드 패턴** 메뉴 접속
2. 브랜드와 패턴 선택 또는 새로 추가
3. **성능 표시 (모바일 상품카드용)** 섹션에서 설정
   - **분류1**: 전체, 승용세단, 승용SUV/RV, 트럭/밴, 스포츠카
   - **상품등급**: 전체, 가성비, 고급형, 최고급형, OE용타이어, 전기차
   - **상품성능**: 정숙성, 주행안정성, 젖은노면제동력, 연비, 구름저항, 마일리지
   - **계절**: 사계절, 겨울용, 여름용
   - **로드타입**: ON로드, OFF로드
   - **브랜드 로고 파일명**: 예) michelin.png
4. 저장

### 목록에서 확인하기
- 브랜드 패턴 목록에서 **성능표시** 컬럼에 설정된 내용 요약 표시
- 파란색 텍스트: 설정됨
- 회색 "미설정": 아직 설정 안됨

## 데이터 마이그레이션 (필요시)

만약 기존 BrandPatternPerformance에 데이터가 있었다면, 마이그레이션 전에 데이터를 BrandPattern으로 복사해야 합니다.

**데이터 마이그레이션 스크립트** (마이그레이션 적용 전 실행):
```python
# Python shell에서 실행
python manage.py shell

from tire_data.models import BrandPattern, BrandPatternPerformance

# BrandPatternPerformance 데이터를 BrandPattern으로 복사
for bp_perf in BrandPatternPerformance.objects.all():
    if bp_perf.pattern:
        try:
            bp = BrandPattern.objects.get(
                brand=bp_perf.brand,
                pattern_name=bp_perf.pattern.pattern_name
            )
            bp.classification = bp_perf.classification
            bp.grade = bp_perf.grade
            bp.performance = bp_perf.performance
            bp.season = bp_perf.season
            bp.road_type = bp_perf.road_type
            bp.logo_filename = bp_perf.logo_filename
            bp.save()
            print(f"✓ {bp}")
        except BrandPattern.DoesNotExist:
            print(f"✗ Pattern not found: {bp_perf.brand.name} - {bp_perf.pattern.pattern_name}")
```

## 테스트 체크리스트

- [ ] Git push 완료
- [ ] PythonAnywhere에서 git pull 완료
- [ ] 마이그레이션 0021, 0022 적용 완료
- [ ] brand_patterns 테이블에 새 컬럼 추가 확인
- [ ] brand_pattern_performance 테이블 삭제 확인
- [ ] Python 캐시 삭제 완료
- [ ] 웹 앱 재시작 완료
- [ ] 관리자 페이지 접속 확인
- [ ] B.02 브랜드 패턴 메뉴에서 성능표시 필드 표시 확인
- [ ] 성능표시 데이터 저장 테스트
- [ ] 모바일 API에서 성능표시 데이터 조회 확인
- [ ] 모바일 페이지에서 성능 박스 표시 확인

## 롤백 방법 (문제 발생 시)

문제가 발생하면 이전 마이그레이션으로 되돌릴 수 있습니다:

```bash
# 0020 마이그레이션으로 롤백 (BrandPatternPerformance 복원)
python manage.py migrate tire_data 0020

# 이전 코드로 되돌리기
git log --oneline -5  # 커밋 해시 확인
git reset --hard <이전_커밋_해시>
git push origin main --force  # 주의: 강제 푸시

# 웹 앱 재시작
```

## 문의사항
문제가 발생하면 로그를 확인하세요:
- PythonAnywhere 웹 탭 > **Log files**
- **Error log** 확인
- **Server log** 확인
