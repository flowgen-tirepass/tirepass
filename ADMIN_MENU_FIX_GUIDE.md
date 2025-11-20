# BrandPatternPerformance 관리자 메뉴 표시 문제 해결 가이드

## 문제 상황
- BrandPatternPerformance 모델이 Django에 정상 등록되어 있음
- 데이터베이스 테이블도 존재함
- **하지만 관리자 페이지에 "B. 💰 할인 | 06. 브랜드/패턴 성능표시" 메뉴가 보이지 않음**

## 원인 분석
여러 번 `verbose_name_plural`을 변경하고 마이그레이션을 생성하면서 PythonAnywhere 서버에서 다음 문제가 발생할 수 있습니다:

1. **Python 모듈 캐싱**: 웹 앱 재시작만으로는 변경된 models.py가 완전히 reload되지 않을 수 있음
2. **마이그레이션 미적용**: 최신 마이그레이션(0020)이 서버에 적용되지 않았을 수 있음
3. **Git 동기화 문제**: 로컬의 최신 변경사항이 서버에 push되지 않았을 수 있음

## 해결 방법

### 1단계: 로컬에서 Git Push
```bash
# 로컬 PC (Windows)에서 실행
cd C:\Users\jmyang\Dropbox\1.0_tirepass

# 현재 상태 확인
git status

# 변경사항 커밋 (아직 커밋하지 않았다면)
git add tire_data/models.py tire_data/migrations/0020_alter_brandpatternperformance_options.py
git commit -m "Fix: BrandPatternPerformance verbose_name_plural을 B.06으로 설정"

# 서버로 푸시
git push origin main
```

### 2단계: PythonAnywhere에서 Pull 및 마이그레이션 적용
```bash
# PythonAnywhere Bash 콘솔에서 실행
cd /home/tirepass/tirepass

# 최신 코드 가져오기
git pull origin main

# 마이그레이션 상태 확인
python manage.py showmigrations tire_data | tail -20

# 0020 마이그레이션이 [ ] (미적용) 상태라면 적용
python manage.py migrate tire_data

# 마이그레이션이 이미 [X] (적용됨) 상태라면 다음 명령으로 강제 재적용
python manage.py migrate tire_data 0019  # 이전 버전으로 되돌림
python manage.py migrate tire_data 0020  # 다시 적용
```

### 3단계: Python 캐시 완전 삭제 및 웹 앱 재시작
```bash
# PythonAnywhere Bash 콘솔에서 실행
cd /home/tirepass/tirepass

# Python 캐시 파일 모두 삭제
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

# uWSGI 캐시도 삭제 (있다면)
rm -rf /tmp/*.sock 2>/dev/null || true
```

이제 PythonAnywhere 웹 앱 페이지에서:
1. **Reload** 버튼 클릭 (초록색 버튼)
2. **웹 앱 재시작 완료** 메시지 확인

### 4단계: 관리자 페이지 확인
1. **완전히 새로운 시크릿 모드 창** 열기
2. 관리자 페이지 로그인
3. **"B. 💰 할인"** 섹션 확인
4. **"06. 브랜드/패턴 성능표시"** 메뉴가 보이는지 확인

## 추가 확인 사항

### 서버에서 현재 설정 확인
```bash
# PythonAnywhere Bash 콘솔에서 실행
python manage.py shell << 'EOF'
from tire_data.models import BrandPatternPerformance
from tire_data.admin import custom_admin_site

# 모델의 verbose_name_plural 확인
print(f"verbose_name_plural: {BrandPatternPerformance._meta.verbose_name_plural}")

# custom_admin_site 등록 확인
print(f"\nRegistered: {BrandPatternPerformance in custom_admin_site._registry}")

# 등록된 Admin 클래스 확인
if BrandPatternPerformance in custom_admin_site._registry:
    admin_class = custom_admin_site._registry[BrandPatternPerformance]
    print(f"Admin class: {admin_class.__class__.__name__}")

# 모든 B 섹션 모델 출력
print("\n=== B. 할인 섹션 모든 모델 ===")
for model in custom_admin_site._registry:
    vn = model._meta.verbose_name_plural
    if vn.startswith('B.'):
        print(f"  {vn}")
EOF
```

예상 결과:
```
verbose_name_plural: B. 💰 할인 | 06. 브랜드/패턴 성능표시
Registered: True
Admin class: BrandPatternPerformanceAdmin

=== B. 할인 섹션 모든 모델 ===
  B. 💰 할인 | 01. 브랜드
  B. 💰 할인 | 02. 브랜드 패턴
  B. 💰 할인 | 03. 고객사별 브랜드 할인
  B. 💰 할인 | 04. DOT 수입일 할인
  B. 💰 할인 | 05. 상품별 추가 할인
  B. 💰 할인 | 06. 브랜드/패턴 성능표시
```

## 만약 여전히 보이지 않는다면

### 최종 해결책: 새로운 마이그레이션 생성
기존 마이그레이션에 문제가 있을 수 있으므로 새로운 마이그레이션을 생성합니다.

```bash
# 로컬 PC에서 실행
cd C:\Users\jmyang\Dropbox\1.0_tirepass

# 새 마이그레이션 생성
python manage.py makemigrations tire_data --name "fix_brandpatternperformance_menu"

# Git에 커밋 및 푸시
git add tire_data/migrations/
git commit -m "Fix: BrandPatternPerformance 메뉴 표시 수정"
git push origin main
```

```bash
# PythonAnywhere에서 실행
cd /home/tirepass/tirepass
git pull origin main
python manage.py migrate tire_data

# 캐시 삭제
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# 웹 앱 재시작 (PythonAnywhere 웹 페이지에서 Reload 버튼 클릭)
```

## 체크리스트

- [ ] 로컬에서 git push 완료
- [ ] PythonAnywhere에서 git pull 완료
- [ ] 마이그레이션 0020 적용 확인
- [ ] Python 캐시 파일 삭제 완료
- [ ] 웹 앱 Reload 완료
- [ ] 시크릿 모드에서 확인
- [ ] B. 💰 할인 | 06. 브랜드/패턴 성능표시 메뉴 표시 확인

---

**참고**: 이 문제는 Django의 모델 메타데이터 캐싱과 uWSGI 프로세스 캐싱이 결합되어 발생하는 것으로, 단순 웹 앱 재시작만으로는 해결되지 않을 수 있습니다. 위 단계를 순서대로 따라하면 해결될 것입니다.
