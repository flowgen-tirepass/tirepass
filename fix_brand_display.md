# 브랜드 로고 표시 문제 해결

## 문제: Goodyear 로고가 웹페이지에 안 보임

### 원인
- 이미지 파일은 300x150으로 정상 존재
- 브라우저 캐시 또는 Django static 파일 미갱신

---

## 해결 방법

### 1. 로컬 개발 서버인 경우

#### A. Django 서버 재시작
```bash
# 현재 실행 중인 서버 종료 (Ctrl+C)
# 그 다음 다시 시작
venv\Scripts\python.exe manage.py runserver
```

#### B. 브라우저 강력 새로고침
```
Chrome/Edge: Ctrl + Shift + R
또는: Ctrl + F5
```

#### C. 브라우저 캐시 완전 삭제
1. F12 (개발자 도구 열기)
2. Network 탭
3. "Disable cache" 체크
4. 페이지 새로고침

---

### 2. PythonAnywhere인 경우

#### SSH Console에서 실행:
```bash
cd ~/tirepass
source ~/.virtualenvs/itire-venv/bin/activate

# 최신 코드 가져오기
git pull origin main

# Static 파일 수집 (브랜드 이미지 포함)
python manage.py collectstatic --noinput

# 웹앱 재시작
touch /var/www/tirepass_pythonanywhere_com_wsgi.py
```

---

## 확인 사항

### 이미지 파일 확인
```bash
venv\Scripts\python.exe check_brand_size.py
```

예상 출력:
```
goodyear.png        : 300 x 150 픽셀  ← 정상!
kumho.png           : 150 x 70 픽셀
(기타 브랜드들...)
```

### 브라우저에서 직접 이미지 확인
```
http://localhost:8000/static/mobile/img/brands/goodyear.png
```

또는 PythonAnywhere:
```
https://tirepass.pythonanywhere.com/static/mobile/img/brands/goodyear.png
```

---

## 최종 확인

모바일 홈 페이지에서 Goodyear가:
- ✅ 첫 번째 칸(1행 1열)에 표시
- ✅ Kumho보다 크게 표시 (300x150 vs 150x70)
- ✅ 박스를 가득 채우며 표시

되면 성공!
