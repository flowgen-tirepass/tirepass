# URL Parameter Fix 배포 가이드

## 🐛 문제
TypeError 발생:
- URL: `https://tirepass.pythonanywhere.com/admin/tire_data/customers/0-1-0002/adjust-points/`
- 원인: URL 패턴이 `<path:object_id>`를 사용하지만 뷰 함수는 `customer_id` 파라미터를 기대함

## ✅ 수정 내용

### 수정된 파일
- `tire_data/admin.py` (Line 1202)

### Before → After
```python
# Before (Line 1202)
path('<path:object_id>/adjust-points/',

# After (Line 1202)
path('<path:customer_id>/adjust-points/',
```

## 🚀 배포 방법

### PythonAnywhere Bash 콘솔에서 실행:

```bash
cd ~/tirepass
git pull origin main
touch /var/www/tirepass_pythonanywhere_com_wsgi.py
```

### 수정 확인:
```bash
grep -n "customer_id" tire_data/admin.py | grep "1202"
```

예상 출력:
```
1202:            path('<path:customer_id>/adjust-points/',
```

## 🧪 테스트

1. **고객 관리 페이지 접속**
   - https://tirepass.pythonanywhere.com/admin/tire_data/customers/

2. **포인트 조정 기능 테스트**
   - 임의의 고객 상세 페이지 열기
   - "포인트 조정" 섹션 확인
   - 포인트 100 지급 테스트
   - 성공 메시지 확인: "✅ [고객명]님에게 100P를 지급했습니다."
   - 페이지 새로고침 없이 잔액 업데이트 확인

3. **에러 확인**
   - TypeError가 사라졌는지 확인
   - AJAX 요청이 정상적으로 JSON 응답을 받는지 확인

## ✅ 성공 확인

- [ ] Git pull 성공
- [ ] 웹앱 재시작 완료
- [ ] Line 1202에 `customer_id` 패턴 확인
- [ ] 포인트 지급 성공
- [ ] TypeError 에러 사라짐
- [ ] JSON 응답 정상 수신

---

**마지막 업데이트**: 2025-11-19
**Commit**: 7ad650d
**관련 파일**: tire_data/admin.py
