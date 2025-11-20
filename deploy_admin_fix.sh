#!/bin/bash
# Admin.py F-string 포맷팅 수정 배포 스크립트

cd ~/tirepass

echo "🔧 tire_data/admin.py 수정 중..."

# Line 943: point_balance_display
sed -i '943s/{:,}P/{}P/g' tire_data/admin.py

# Line 971: adjust_points_form 현재 잔액
sed -i '971s/{balance:,}/{balance}/g' tire_data/admin.py

# Line 1653-1654: balance_display
sed -i '1653s/{:,}P/{}P/g' tire_data/admin.py

# Line 1659: total_earned_display
sed -i '1659s/{obj.total_earned:,}/{obj.total_earned}/g' tire_data/admin.py

# Line 1663: total_used_display
sed -i '1663s/{obj.total_used:,}/{obj.total_used}/g' tire_data/admin.py

# Line 1694: amount_display (positive)
sed -i '1694s/+{:,}P/+{}P/g' tire_data/admin.py

# Line 1697: amount_display (negative)
sed -i '1697s/{:,}P/{}P/g' tire_data/admin.py

# Line 1703: balance_after_display
sed -i '1703s/{obj.balance_after:,}/{obj.balance_after}/g' tire_data/admin.py

# Line 2297-2299: erp_goods_count_display (단순화)
sed -i '2297,2299c\            return format_html(\n                '"'"'<strong style="color: #2563eb;">{}개</strong>'"'"',\n                obj.erp_goods_count\n            )' tire_data/admin.py

# Line 2422-2425: jaego_display
sed -i '2422c\        return format_html(' tire_data/admin.py
sed -i '2423c\            '"'"'<strong style="color: #059669;">{}개</strong>'"'"',' tire_data/admin.py
sed -i '2424c\            obj.jaego' tire_data/admin.py

# Line 2434-2435: change_display (positive)
sed -i '2434c\            return format_html(' tire_data/admin.py
sed -i '2435c\                '"'"'<span style="color: #10b981; font-weight: bold; font-size: 14px;">🟢 +{}</span>'"'"',' tire_data/admin.py
sed -i '2436c\                obj.change_from_prev' tire_data/admin.py

# Line 2440-2441: change_display (negative)
sed -i '2440c\            return format_html(' tire_data/admin.py
sed -i '2441c\                '"'"'<span style="color: #ef4444; font-weight: bold; font-size: 14px;">🔴 {}</span>'"'"',' tire_data/admin.py

# Line 2651: adjust_points 메시지 (지급)
sed -i '2651s/{amount:,}/{amount}/g; s/{customer_point.balance:,}/{customer_point.balance}/g' tire_data/admin.py

# Line 2656: adjust_points 메시지 (잔액 초과)
sed -i '2656s/{amount:,}/{amount}/g; s/{customer_point.balance:,}/{customer_point.balance}/g' tire_data/admin.py

# Line 2664: adjust_points 메시지 (차감)
sed -i '2664s/{amount:,}/{amount}/g; s/{customer_point.balance:,}/{customer_point.balance}/g' tire_data/admin.py

echo "✅ 수정 완료!"
echo ""
echo "🔍 수정 확인 중..."
grep -n "obj.balance_after" tire_data/admin.py | grep "1703"

echo ""
echo "🔄 웹앱 재시작 중..."
touch /var/www/tirepass_pythonanywhere_com_wsgi.py

echo "✅ 배포 완료!"
echo ""
echo "🧪 테스트 URL:"
echo "https://tirepass.pythonanywhere.com/admin/tire_data/pointtransaction/"
