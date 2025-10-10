"""
광주 ERP 서버에서 실행할 실시간 동기화 데몬

- Firebird SYNC_LOG 테이블 모니터링
- 변경사항 감지 시 PythonAnywhere API로 전송
- Windows 서비스 또는 작업 스케줄러로 실행

설치:
    pip install fdb requests

실행:
    python erp_sync_daemon.py
"""

import fdb
import requests
import time
import json
from datetime import datetime
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('erp_sync_daemon.log'),
        logging.StreamHandler()
    ]
)

# ERP Firebird 연결 정보
FIREBIRD_CONFIG = {
    'host': 'localhost',  # ERP 서버에서 실행하므로 localhost
    'database': r'C:\Program Files\PsimCarS\Data\ITIRE.GDB',
    'user': 'SYSDBA',
    'password': 'masterkey',
    'charset': 'NONE'
}

# PythonAnywhere API 정보
PYTHONANYWHERE_API = {
    'base_url': 'https://tirepass.pythonanywhere.com/api',
    'api_key': 'YOUR_API_KEY_HERE',  # Django에서 생성할 API 키
    'timeout': 30
}

# 동기화 설정
SYNC_CONFIG = {
    'poll_interval': 5,  # 5초마다 체크
    'batch_size': 100,    # 한 번에 처리할 로그 수
    'max_retry': 3        # 최대 재시도 횟수
}


def safe_decode(value):
    """안전하게 문자열 디코딩"""
    if value is None:
        return ''

    if isinstance(value, str):
        return value

    if isinstance(value, bytes):
        for encoding in ['utf-8', 'cp949', 'euc-kr', 'iso-8859-1']:
            try:
                decoded = value.decode(encoding)
                if any('\uac00' <= c <= '\ud7a3' for c in decoded):
                    return decoded
                return decoded
            except:
                continue
        return value.decode('utf-8', errors='ignore')

    return str(value)


def get_pending_logs(conn):
    """동기화 대기 중인 로그 가져오기"""
    cursor = conn.cursor()

    query = """
        SELECT FIRST ? LOG_ID, TABLE_NAME, OPERATION, RECORD_KEY, CHANGED_AT
        FROM SYNC_LOG
        WHERE SYNC_STATUS = 'PENDING' AND RETRY_COUNT < ?
        ORDER BY LOG_ID
    """

    cursor.execute(query, (SYNC_CONFIG['batch_size'], SYNC_CONFIG['max_retry']))
    logs = cursor.fetchall()
    cursor.close()

    return logs


def get_record_data(conn, table_name, record_key):
    """변경된 레코드의 전체 데이터 가져오기"""
    cursor = conn.cursor()

    if table_name == 'CUSTOMS':
        query = """
            SELECT CODE, NAME, REP, TEL1, TEL3, TEL4, ENNO, ADDRESS1
            FROM CUSTOMS
            WHERE CODE = ?
        """
    elif table_name == 'GOODS':
        query = """
            SELECT CODE, NAME, BUN1, JAEGO, FIXP
            FROM GOODS
            WHERE CODE = ?
        """
    else:
        cursor.close()
        return None

    cursor.execute(query, (record_key,))
    row = cursor.fetchone()
    cursor.close()

    if not row:
        return None

    # 데이터 디코딩 및 변환
    if table_name == 'CUSTOMS':
        return {
            'code': safe_decode(row[0]),
            'name': safe_decode(row[1]),
            'rep': safe_decode(row[2]),
            'tel1': safe_decode(row[3]),
            'tel3': safe_decode(row[4]),
            'tel4': safe_decode(row[5]),
            'enno': safe_decode(row[6]),
            'address1': safe_decode(row[7])
        }
    elif table_name == 'GOODS':
        return {
            'code': safe_decode(row[0]),
            'name': safe_decode(row[1]),
            'bun1': safe_decode(row[2]),
            'jaego': int(row[3]) if row[3] else 0,
            'fixp': int(row[4]) if row[4] else 0
        }


def send_to_pythonanywhere(table_name, operation, record_key, data):
    """PythonAnywhere API로 데이터 전송"""

    # API 엔드포인트 결정
    if table_name == 'CUSTOMS':
        endpoint = f"{PYTHONANYWHERE_API['base_url']}/sync/customer/"
    elif table_name == 'GOODS':
        endpoint = f"{PYTHONANYWHERE_API['base_url']}/sync/goods/"
    else:
        return False, "Unknown table"

    # 요청 데이터 구성
    payload = {
        'operation': operation,
        'record_key': record_key,
        'data': data
    }

    headers = {
        'Authorization': f"Bearer {PYTHONANYWHERE_API['api_key']}",
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(
            endpoint,
            json=payload,
            headers=headers,
            timeout=PYTHONANYWHERE_API['timeout']
        )

        if response.status_code == 200:
            return True, "Success"
        else:
            return False, f"HTTP {response.status_code}: {response.text}"

    except requests.exceptions.RequestException as e:
        return False, str(e)


def update_log_status(conn, log_id, status, error_message=None):
    """로그 상태 업데이트"""
    cursor = conn.cursor()

    if status == 'ERROR':
        query = """
            UPDATE SYNC_LOG
            SET SYNC_STATUS = ?, ERROR_MESSAGE = ?, RETRY_COUNT = RETRY_COUNT + 1
            WHERE LOG_ID = ?
        """
        cursor.execute(query, (status, error_message, log_id))
    else:
        query = """
            UPDATE SYNC_LOG
            SET SYNC_STATUS = ?
            WHERE LOG_ID = ?
        """
        cursor.execute(query, (status, log_id))

    conn.commit()
    cursor.close()


def process_sync_logs():
    """동기화 로그 처리"""
    try:
        conn = fdb.connect(**FIREBIRD_CONFIG)

        # 대기 중인 로그 가져오기
        logs = get_pending_logs(conn)

        if not logs:
            conn.close()
            return 0

        logging.info(f"처리할 로그 {len(logs)}개 발견")

        success_count = 0
        error_count = 0

        for log in logs:
            log_id, table_name, operation, record_key, changed_at = log

            logging.info(f"처리 중: {table_name}.{record_key} ({operation})")

            # DELETE 작업은 데이터 없이 전송
            if operation == 'DELETE':
                data = None
            else:
                # 변경된 레코드 데이터 가져오기
                data = get_record_data(conn, table_name, record_key)

                if not data and operation != 'DELETE':
                    logging.warning(f"레코드 없음: {table_name}.{record_key}")
                    update_log_status(conn, log_id, 'ERROR', 'Record not found')
                    error_count += 1
                    continue

            # PythonAnywhere로 전송
            success, message = send_to_pythonanywhere(
                table_name, operation, record_key, data
            )

            if success:
                update_log_status(conn, log_id, 'SENT')
                success_count += 1
                logging.info(f"성공: {table_name}.{record_key}")
            else:
                update_log_status(conn, log_id, 'ERROR', message)
                error_count += 1
                logging.error(f"실패: {table_name}.{record_key} - {message}")

        conn.close()

        logging.info(f"처리 완료 - 성공: {success_count}, 실패: {error_count}")
        return success_count

    except Exception as e:
        logging.error(f"처리 중 오류: {e}")
        import traceback
        traceback.print_exc()
        return 0


def main():
    """메인 루프"""
    logging.info("=== ERP 동기화 데몬 시작 ===")
    logging.info(f"Firebird: {FIREBIRD_CONFIG['host']}")
    logging.info(f"PythonAnywhere: {PYTHONANYWHERE_API['base_url']}")
    logging.info(f"폴링 간격: {SYNC_CONFIG['poll_interval']}초")

    while True:
        try:
            process_sync_logs()
            time.sleep(SYNC_CONFIG['poll_interval'])

        except KeyboardInterrupt:
            logging.info("사용자에 의해 중단됨")
            break

        except Exception as e:
            logging.error(f"메인 루프 오류: {e}")
            time.sleep(SYNC_CONFIG['poll_interval'])


if __name__ == '__main__':
    main()
