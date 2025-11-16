"""
ERP Firebird CUSTOMS 테이블의 전체 컬럼 구조 확인
TgenAI PC에서 실행
"""
import fdb

# Firebird 연결 정보
FIREBIRD_CONFIG = {
    'host': 'localhost',  # TgenAI PC에서 로컬로 접속
    'database': r'C:\Program Files\PsimCarS\Data\ITIRE.GDB',
    'user': 'SYSDBA',
    'password': 'masterkey',
    'charset': 'NONE'
}

print("\n" + "=" * 80)
print("ERP Firebird CUSTOMS 테이블 컬럼 구조 확인")
print("=" * 80)

try:
    # DB 연결
    conn = fdb.connect(**FIREBIRD_CONFIG)
    cursor = conn.cursor()

    # 테이블 컬럼 정보 조회
    cursor.execute("""
        SELECT
            r.RDB$FIELD_NAME as field_name,
            f.RDB$FIELD_TYPE as field_type,
            f.RDB$FIELD_LENGTH as field_length
        FROM RDB$RELATION_FIELDS r
        LEFT JOIN RDB$FIELDS f ON r.RDB$FIELD_SOURCE = f.RDB$FIELD_NAME
        WHERE r.RDB$RELATION_NAME='CUSTOMS'
        ORDER BY r.RDB$FIELD_POSITION
    """)

    columns = cursor.fetchall()

    print(f"\n✅ CUSTOMS 테이블 전체 컬럼 목록 ({len(columns)}개):")
    print("-" * 80)

    for i, (field_name, field_type, field_length) in enumerate(columns, 1):
        field_name = field_name.strip()
        print(f"{i:3d}. {field_name:20s} (type: {field_type}, length: {field_length})")

    print("\n" + "-" * 80)
    print("📋 주소 관련 필드 찾기:")
    print("-" * 80)

    address_keywords = ['ADDR', 'ADDRESS', 'JUSO', 'POST', 'ZIP', 'DONG', 'GU', 'CITY']
    address_fields = []

    for field_name, _, _ in columns:
        field_name = field_name.strip()
        for keyword in address_keywords:
            if keyword in field_name.upper():
                address_fields.append(field_name)
                break

    if address_fields:
        print(f"✅ 주소 관련 필드 {len(address_fields)}개 발견:")
        for field in address_fields:
            print(f"   - {field}")
    else:
        print("❌ 주소 관련 필드를 찾을 수 없습니다.")

    # 샘플 데이터 조회 (주소 필드가 있다면)
    if address_fields:
        print("\n" + "-" * 80)
        print("📊 샘플 데이터 (주소 필드):")
        print("-" * 80)

        # 주소 필드들을 쿼리에 포함
        addr_fields_str = ', '.join(address_fields)
        query = f"SELECT CODE, NAME, {addr_fields_str} FROM CUSTOMS WHERE CODE IS NOT NULL ROWS 1 TO 5"

        cursor.execute(query)
        rows = cursor.fetchall()

        for row in rows:
            code = row[0].strip() if row[0] else ""
            name = row[1].strip() if row[1] else ""
            print(f"\n[{code}] {name}")

            for i, field_name in enumerate(address_fields, 2):
                value = row[i].strip() if row[i] and hasattr(row[i], 'strip') else row[i]
                if value:
                    print(f"   {field_name}: {value}")

    cursor.close()
    conn.close()

    print("\n" + "=" * 80)
    print("✅ 완료!")
    print("=" * 80)

except Exception as e:
    print(f"\n❌ 에러 발생: {e}")
    import traceback
    traceback.print_exc()
