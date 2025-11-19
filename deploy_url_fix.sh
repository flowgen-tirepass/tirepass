#!/bin/bash
# URL Parameter Fix 배포 스크립트

cd ~/tirepass

echo "🔄 Git Pull 중..."
git pull origin main

echo "✅ Pull 완료!"
echo ""

echo "🔍 수정 확인 중..."
grep -n "customer_id" tire_data/admin.py | grep "1202"

echo ""
echo "🔄 웹앱 재시작 중..."
touch /var/www/tirepass_pythonanywhere_com_wsgi.py

echo "✅ 배포 완료!"
echo ""
echo "🧪 테스트 URL:"
echo "https://tirepass.pythonanywhere.com/admin/tire_data/customers/"
echo ""
echo "포인트 조정 기능을 테스트해보세요!"
