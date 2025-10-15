# Goodyear 로고 배포 가이드 (2분)

## ✅ 로컬 완료 사항
- Goodyear 로고 크기: 160x244 → **300x150** ✓
- Git 커밋 & 푸시 완료 ✓
- 백업 파일: goodyear_244_backup.png ✓
- **목적**: Kumho(150×70)의 2배 크기로 확대하여 브랜드 박스를 가득 채우기

---

## 🚀 PythonAnywhere 배포 (2분)

### 1. SSH Console에서 실행

```bash
cd ~/tirepass
source ~/.virtualenvs/itire-venv/bin/activate

# 최신 코드 가져오기
git pull origin main

# 정적 파일 수집 (브랜드 로고 이미지 포함)
python manage.py collectstatic --noinput

# 웹앱 재시작
touch /var/www/tirepass_pythonanywhere_com_wsgi.py
```

---

## ✅ 확인

1. **모바일 홈 페이지 접속:**
   ```
   https://tirepass.pythonanywhere.com/mobile/home/
   ```

2. **Goodyear 로고 크기 확인:**
   - Goodyear 로고가 Kumho처럼 브랜드 박스를 가득 채워야 함
   - 이미지 크기: 300x150 (Kumho 150x70의 2배)
   - 렌더링 시 다른 브랜드들과 비슷한 크기로 표시되어야 함

3. **모든 브랜드 로고 정상 표시 확인:**
   - Kumho, Nexen, Dunlop, Michelin, Bridgestone
   - Yokohama, Continental, Pirelli, Hankook, Goodyear

---

## 📊 브랜드 로고 최종 크기

```
goodyear        : 300 x 150 픽셀 ⭐ Kumho의 2배 크기 - 박스 가득!
kumho           : 150 x 70 픽셀  (비교 기준)
dunlop          : 160 x 132 픽셀
michelin        : 160 x 132 픽셀
continental     : 160 x 126 픽셀
hankook         : 160 x 114 픽셀
yokohama        : 157 x 104 픽셀
bridgestone     : 160 x 100 픽셀
pirelli         : 155 x 100 픽셀
nexen           : 160 x 92 픽셀
```

---

**작성일:** 2025-10-16
**예상 시간:** 2분
