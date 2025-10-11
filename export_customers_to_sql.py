"""
로컬 DB의 customers_simple 데이터를 SQL INSERT 문으로 추출
pythonanywhere에 업로드하기 위한 스크립트
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itire.settings')
django.setup()

from tire_data.models import Customers

print("-- customers_simple 데이터 덤프")
print("-- 생성일시:", __import__('datetime').datetime.now())
print("-- UTF-8 인코딩")
print()
print("SET NAMES utf8mb4;")
print("SET CHARACTER SET utf8mb4;")
print()

customers = Customers.objects.filter(is_registered=True).order_by('code')
count = customers.count()

print(f"-- 총 {count}명의 고객 데이터")
print()

for customer in customers:
    # NULL 처리
    name = f"'{customer.name}'" if customer.name else 'NULL'
    rep = f"'{customer.rep}'" if customer.rep else 'NULL'
    tel1 = f"'{customer.tel1}'" if customer.tel1 else 'NULL'
    tel3 = f"'{customer.tel3}'" if customer.tel3 else 'NULL'
    enno = f"'{customer.enno}'" if customer.enno else 'NULL'
    password = f"'{customer.password}'" if customer.password else 'NULL'
    user_id = customer.user_id if customer.user_id else 'NULL'

    # SQL INSERT 문 생성
    sql = f"""INSERT INTO customers_simple (code, name, rep, tel1, tel3, enno, password, is_registered, user_id, must_change_password)
VALUES ('{customer.code}', {name}, {rep}, {tel1}, {tel3}, {enno}, {password}, {1 if customer.is_registered else 0}, {user_id}, {1 if customer.must_change_password else 0})
ON DUPLICATE KEY UPDATE
  name = VALUES(name),
  rep = VALUES(rep),
  tel1 = VALUES(tel1),
  tel3 = VALUES(tel3),
  enno = VALUES(enno),
  password = VALUES(password),
  is_registered = VALUES(is_registered),
  user_id = VALUES(user_id),
  must_change_password = VALUES(must_change_password);"""

    print(sql)
    print()

print(f"-- 완료: {count}명")
