# Orders 테이블 최종 수정 (1분)

## ✅ 확인 완료

테이블 구조 확인 결과, 모든 컬럼이 이미 존재합니다:
- ✓ cancelled_date
- ✓ cancelled_reason
- ✓ returned_date
- ✓ returned_reason
- ✓ **order_source** ← 핵심 컬럼 존재!
- ✓ **erp_order_number**

---

## 🔧 해결 방법 (1분)

Django가 테이블 변경사항을 인식하도록 **Migration fake 처리** 및 **웹앱 재시작**만 하면 됩니다.

### PythonAnywhere Bash Console에서 실행:

```bash
cd ~/tirepass
source ~/.virtualenvs/itire-venv/bin/activate

# Migration fake 처리
python manage.py migrate tire_data 0007_add_order_fields --fake

# 웹앱 재시작
touch /var/www/tirepass_pythonanywhere_com_wsgi.py
```

---

## ✅ 확인

**Admin 접속:**
```
https://tirepass.pythonanywhere.com/admin/tire_data/order/
```

오류 없이 주문 목록이 표시되면 **성공!** 🎉

---

## 🔍 추가 확인 (선택사항)

Migration 상태 확인:

```bash
cd ~/tirepass
source ~/.virtualenvs/itire-venv/bin/activate
python manage.py showmigrations tire_data
```

**예상 출력:**
```
tire_data
 [X] 0001_initial
 [X] 0002_...
 [X] 0007_add_order_fields  ← fake로 표시됨
 [ ] 0012_goodsrealtimesnapshot
```

0012 migration도 적용:
```bash
python manage.py migrate tire_data
touch /var/www/tirepass_pythonanywhere_com_wsgi.py
```

---

**작성일:** 2025-10-16
**예상 시간:** 1분
