# 즉시 배포 가이드

## 변경사항
✅ Django admin 상품 목록 페이지 페이지네이션 수정
- "6519 상품목록" → "6528 상품목록" (ERP 실시간 개수)
- Django 기본 queryset 제거
- ERP 데이터로 완전 교체

## PythonAnywhere 배포 단계

### 1. PythonAnywhere Bash 콘솔 접속
https://www.pythonanywhere.com/user/tirepass/consoles/

### 2. 코드 업데이트
```bash
cd ~/itire
git pull
```

### 3. 웹 앱 재시작
```bash
# 옵션 A: 터치 명령 (더 빠름)
touch /var/www/tirepass_pythonanywhere_com_wsgi.py

# 옵션 B: Web 탭에서 "Reload" 버튼 클릭
# https://www.pythonanywhere.com/user/tirepass/webapps/#tab_id_tirepass_pythonanywhere_com
```

## 배포 확인

### 1. 상품 목록 페이지 접속
https://tirepass.pythonanywhere.com/admin/tire_data/goods/

### 2. 확인 사항
- [x] 상단: "🔄 ERP 실시간 연결 6528 개 상품 (ERP)"
- [x] 타이어만 체크박스 작동
- [x] 재고있는 상품만 체크박스 작동
- [x] 하단 페이지네이션: "6528 상품목록" (6519 아님)
- [x] 상품 데이터가 ERP에서 실시간 로드됨

### 3. 한글 인코딩 확인
- [ ] 상품명이 한글로 정상 표시 (깨짐 없음)
- [ ] 분류(BUN1)가 한글로 정상 표시

**참고**: 한글 인코딩은 TgenAI 서버 재시작 후 정상화됨

## 문제 발생시

### Git Pull 실패
```bash
# 충돌 파일 확인
git status

# 로컬 변경사항 제거
git reset --hard HEAD
git pull
```

### 웹 앱 500 에러
```bash
# 에러 로그 확인
tail -50 /var/log/tirepass.pythonanywhere.com.error.log
```

### Static 파일 문제
```bash
source ~/.virtualenvs/itire-venv/bin/activate
python manage.py collectstatic --noinput
```

## 다음 단계 (배포 후)

1. ✅ Pythonanywhere 배포 완료
2. ⏳ TgenAI 서버 재시작 (한글 인코딩 적용)
3. ⏳ 관리자 통합 주문 내역 페이지
4. ⏳ TgenAI 24/7 자동 시작 설정
5. ⏳ 모바일 실시간 재고 표시

## 최근 커밋
```
Django 기본 queryset 제거, ERP 카운트로 완전 교체
- get_queryset() override로 빈 queryset 반환
- 페이지네이션 블록 숨김
- ERP 실시간 카운트 표시
```
