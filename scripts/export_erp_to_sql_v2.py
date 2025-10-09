"""
ERP Firebird에서 고객 데이터를 가져와 SQL INSERT 파일 생성 (UTF-8 인코딩 개선)

실행:
    python scripts/export_erp_to_sql_v2.py
"""

import fdb
from datetime import datetime

# ERP Firebird 연결 정보
FIREBIRD_CONFIG = {
    'host': 'ITIRE2.iptime.org',
    'database': r'C:\Program Files\PsimCarS\Data\ITIRE.GDB',
    'user': 'SYSDBA',
    'password': 'masterkey',
    'charset': 'NONE'  # NONE으로 설정하고 수동으로 디코딩
}


def safe_decode(value):
    """안전하게 문자열 디코딩"""
    if value is None:
        return ''

    if isinstance(value, str):
        return value

    if isinstance(value, bytes):
        # 여러 인코딩 시도
        for encoding in ['utf-8', 'cp949', 'euc-kr', 'iso-8859-1']:
            try:
                decoded = value.decode(encoding)
                # 한글이 포함되어 있으면 성공
                if any('\uac00' <= c <= '\ud7a3' for c in decoded):
                    return decoded
                return decoded
            except:
                continue
        # 모두 실패하면 무시
        return value.decode('utf-8', errors='ignore')

    return str(value)


def export_to_sql():
    """ERP 데이터를 SQL INSERT 문으로 생성"""
    print("=== ERP Firebird 서버 연결 중 (charset=NONE) ===")

    try:
        conn = fdb.connect(**FIREBIRD_CONFIG)
        cursor = conn.cursor()

        # CUSTOMS 테이블에서 데이터 조회
        query = """
            SELECT CODE, NAME, REP, ENNO, TEL1, TEL3, TEL4, ADDRESS1
            FROM CUSTOMS
            WHERE ENNO IS NOT NULL AND ENNO <> ''
        """

        cursor.execute(query)
        customers = cursor.fetchall()

        print(f"총 {len(customers)}명의 고객 데이터를 가져왔습니다.")

        # 샘플 데이터 출력 (인코딩 확인)
        if customers:
            sample = customers[0]
            print(f"\n샘플 데이터:")
            print(f"  CODE: {safe_decode(sample[0])}")
            print(f"  NAME: {safe_decode(sample[1])}")
            print(f"  REP: {safe_decode(sample[2])}")

        cursor.close()
        conn.close()

        # SQL 파일 생성
        output_file = 'erp_customers_insert.sql'

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("-- ERP 고객 데이터 INSERT (UTF-8)\n")
            f.write(f"-- 생성일: {datetime.now()}\n")
            f.write(f"-- 총 {len(customers)}명\n\n")

            f.write("USE tirepass$itire_db;\n\n")

            batch_size = 100
            valid_count = 0

            for i, customer in enumerate(customers):
                code, name, rep, enno, tel1, tel3, tel4, address1 = customer

                # 사업자번호 정제
                if not enno:
                    continue

                enno_str = safe_decode(enno)
                enno_clean = enno_str.replace('-', '').strip()

                if not enno_clean.isdigit() or len(enno_clean) != 10:
                    continue

                # 모든 필드 디코딩 및 이스케이프
                code_clean = safe_decode(code).strip().replace("'", "''")
                name_clean = safe_decode(name).strip().replace("'", "''")
                rep_clean = safe_decode(rep).strip().replace("'", "''")
                tel1_clean = safe_decode(tel1).strip().replace("'", "''")
                tel3_clean = safe_decode(tel3).strip().replace("'", "''")
                tel4_clean = safe_decode(tel4).strip().replace("'", "''")
                address1_clean = safe_decode(address1).strip().replace("'", "''")

                if valid_count % batch_size == 0:
                    if valid_count > 0:
                        f.write(";\n\n")
                    f.write("INSERT INTO customers (CODE, NAME, REP, TEL1, TEL3, TEL4, ENNO, ADDRESS1, LAST_SYNC) VALUES\n")
                else:
                    f.write(",\n")

                f.write(f"  ('{code_clean}', '{name_clean}', '{rep_clean}', '{tel1_clean}', '{tel3_clean}', '{tel4_clean}', '{enno_clean}', '{address1_clean}', NOW())")

                valid_count += 1

            if valid_count > 0:
                f.write(";\n")

        print(f"\n=== SQL 파일 생성 완료 ===")
        print(f"파일: {output_file}")
        print(f"유효한 고객: {valid_count}명")

    except Exception as e:
        print(f"에러: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    export_to_sql()
