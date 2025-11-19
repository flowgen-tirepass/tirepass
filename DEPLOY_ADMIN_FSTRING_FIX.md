# Admin.py F-string Formatting Fix 배포 가이드

## 🐛 문제
PointTransaction Admin 페이지에서 ValueError 발생:
- URL: https://tirepass.pythonanywhere.com/admin/tire_data/pointtransaction/
- 원인: Python 3.10에서 f-string에 `:,` 포맷팅 사용 불가

## ✅ 수정 내용

### 수정된 파일
- `tire_data/admin.py`

### 수정된 라인들
1. **Line 943**: `point_balance_display()` - CustomerAdmin
2. **Line 971**: `adjust_points_form()` - 현재 잔액 표시
3. **Line 1653-1654**: `balance_display()` - CustomerPointAdmin
4. **Line 1659**: `total_earned_display()`
5. **Line 1663**: `total_used_display()`
6. **Line 1694**: `amount_display()` - PointTransactionAdmin (증가)
7. **Line 1697**: `amount_display()` - PointTransactionAdmin (감소)
8. **Line 1703**: `balance_after_display()`
9. **Line 2298**: `erp_goods_count_display()` - ERPSyncStatusAdmin
10. **Line 2424**: `jaego_display()` - GoodsSnapshotAdmin
11. **Line 2434**: `change_display()` - 증가
12. **Line 2441**: `change_display()` - 감소
13. **Line 2651**: adjust_points 메시지 - 지급
14. **Line 2656**: adjust_points 메시지 - 잔액 초과
15. **Line 2664**: adjust_points 메시지 - 차감

### Before → After
```python
# Before
f'{amount:,}P'
format_html('{}P', f'{obj.balance:,}')

# After
f'{amount}P'
format_html('{}P', obj.balance)
```

## 🚀 배포 방법

### 옵션 1: Git Pull (추천)

```bash
# PythonAnywhere Bash 콘솔에서
cd ~/tirepass
git pull origin main
touch /var/www/tirepass_pythonanywhere_com_wsgi.py
```

### 옵션 2: 직접 수정 (Git 문제 시)

```bash
cd ~/tirepass

# Line 943
sed -i '943s/{:,}P/{}/g' tire_data/admin.py

# Line 971
sed -i '971s/{balance:,}/{balance}/g' tire_data/admin.py

# Line 1653
sed -i '1653s/{:,}P/{}/g' tire_data/admin.py

# Line 1659
sed -i '1659s/{obj.total_earned:,}/{obj.total_earned}/g' tire_data/admin.py

# Line 1663
sed -i '1663s/{obj.total_used:,}/{obj.total_used}/g' tire_data/admin.py

# Line 1694
sed -i '1694s/+{:,}P/+{}P/g' tire_data/admin.py

# Line 1697
sed -i '1697s/{:,}P/{}P/g' tire_data/admin.py

# Line 1703
sed -i '1703s/{obj.balance_after:,}/{obj.balance_after}/g' tire_data/admin.py

# Line 2298 (erp_goods_count - 3줄 → 1줄로 단순화)
sed -i '2296,2302d' tire_data/admin.py
sed -i '2296i\        if obj.erp_goods_count > 0:\n            return format_html(\n                '\''<strong style="color: #2563eb;">{}개</strong>'\'',\n                obj.erp_goods_count\n            )\n        return '\''-'\''' tire_data/admin.py

# Line 2424 (재고수량)
sed -i '2422s/formatted_jaego = f'\''{obj.jaego:,}'\''/obj.jaego/g' tire_data/admin.py
sed -i '2425s/formatted_jaego/obj.jaego/g' tire_data/admin.py

# Line 2434, 2441 (변화량 표시)
sed -i '2434s/formatted_change = f'\''+{obj.change_from_prev:,}'\''/obj.change_from_prev/g' tire_data/admin.py
sed -i '2437s/formatted_change/obj.change_from_prev/g' tire_data/admin.py
sed -i '2441s/formatted_change = f'\''{obj.change_from_prev:,}'\''/obj.change_from_prev/g' tire_data/admin.py
sed -i '2444s/formatted_change/obj.change_from_prev/g' tire_data/admin.py

# Line 2651, 2656, 2664
sed -i '2651s/{amount:,}/{amount}/g; s/{customer_point.balance:,}/{customer_point.balance}/g' tire_data/admin.py
sed -i '2656s/{amount:,}/{amount}/g; s/{customer_point.balance:,}/{customer_point.balance}/g' tire_data/admin.py
sed -i '2664s/{amount:,}/{amount}/g; s/{customer_point.balance:,}/{customer_point.balance}/g' tire_data/admin.py

# 웹앱 재시작
touch /var/www/tirepass_pythonanywhere_com_wsgi.py
```

## 🧪 테스트

1. **PointTransaction Admin 접속**
   - https://tirepass.pythonanywhere.com/admin/tire_data/pointtransaction/
   - ValueError 없이 정상 로딩 확인

2. **특정 고객의 거래내역 필터링**
   - https://tirepass.pythonanywhere.com/admin/tire_data/pointtransaction/?customer__code=0-1-0005
   - 거래내역 목록 정상 표시 확인

3. **포인트 표시 확인**
   - 금액, 잔액이 숫자로 표시됨 (쉼표 없음)
   - 색상 및 스타일은 정상 유지

## ✅ 성공 확인

- [ ] PointTransaction Admin 페이지 로딩 성공
- [ ] ValueError 에러 사라짐
- [ ] 포인트 금액 정상 표시
- [ ] 고객별 필터링 정상 작동

---

**마지막 업데이트**: 2025-11-19
**Commit**: 98a23eb
