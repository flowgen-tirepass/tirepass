"""
TgenAI ERP 게이트웨이 24/7 모니터링 및 자동 복구 시스템

역할:
1. ERP API 서버 상태 모니터링 (매분 체크)
2. ERP API 서버 다운 시 자동 재시작
3. PythonAnywhere 연결 상태 모니터링
4. 네트워크 장애 시 재연결 시도
5. 모든 이벤트 로그 기록

설치:
    pip install requests psutil

실행:
    python tgenai_erp_gateway_monitor.py

Windows 작업 스케줄러 등록:
    - 트리거: 시스템 시작 시
    - 작업: python C:\Users\jmyang\Dropbox\1.0_tirepass\tgenai_erp_gateway_monitor.py
    - 권한: 최고 수준 권한으로 실행
"""

import requests
import time
import subprocess
import sys
import os
import psutil
import logging
from datetime import datetime
from pathlib import Path

# ============================================
# 설정
# ============================================

# 현재 스크립트 경로
BASE_DIR = Path(__file__).resolve().parent

# ERP API 서버 설정
ERP_API_SERVER = {
    'script_path': BASE_DIR / 'erp_api_server.py',
    'port': 8000,
    'health_url': 'http://localhost:8000/health',
    'process_name': 'erp_api_server.py',
    'start_command': [
        sys.executable,  # Python 실행 파일
        str(BASE_DIR / 'erp_api_server.py')
    ]
}

# PythonAnywhere 설정
PYTHONANYWHERE = {
    'api_url': 'https://tirepass.pythonanywhere.com/api/admin/erp/status/',
    'timeout': 10
}

# 모니터링 설정
MONITOR_CONFIG = {
    'check_interval': 60,  # 60초마다 체크
    'restart_cooldown': 300,  # 재시작 후 5분 대기 (빈번한 재시작 방지)
    'max_restart_attempts': 3,  # 최대 재시도 횟수 (연속)
    'health_check_timeout': 5,  # 헬스체크 타임아웃 (초)
}

# 로깅 설정
LOG_FILE = BASE_DIR / 'tgenai_gateway_monitor.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# 상태 추적 변수
last_restart_time = None
consecutive_failures = 0


# ============================================
# 유틸리티 함수
# ============================================

def check_erp_api_server_process():
    """
    ERP API 서버 프로세스가 실행 중인지 확인

    Returns:
        tuple: (is_running: bool, process: psutil.Process or None)
    """
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info.get('cmdline')
            if cmdline and any('erp_api_server.py' in str(arg) for arg in cmdline):
                return True, proc
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return False, None


def check_erp_api_health():
    """
    ERP API 서버 헬스체크 (/health 엔드포인트)

    Returns:
        dict: {'status': 'healthy'|'unhealthy', 'goods_count': int, 'error': str}
    """
    try:
        response = requests.get(
            ERP_API_SERVER['health_url'],
            timeout=MONITOR_CONFIG['health_check_timeout']
        )

        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'healthy':
                return {
                    'status': 'healthy',
                    'goods_count': data.get('total_goods', 0),
                    'database': data.get('database', 'unknown'),
                    'error': None
                }
            else:
                return {
                    'status': 'unhealthy',
                    'goods_count': 0,
                    'error': f"Database: {data.get('database', 'unknown')}"
                }
        else:
            return {
                'status': 'unhealthy',
                'goods_count': 0,
                'error': f'HTTP {response.status_code}'
            }

    except requests.exceptions.ConnectionError:
        return {
            'status': 'unhealthy',
            'goods_count': 0,
            'error': 'Connection refused - Server not running'
        }
    except requests.exceptions.Timeout:
        return {
            'status': 'unhealthy',
            'goods_count': 0,
            'error': 'Connection timeout'
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'goods_count': 0,
            'error': str(e)
        }


def check_pythonanywhere_connection():
    """
    PythonAnywhere API 연결 상태 확인

    Returns:
        dict: {'status': 'connected'|'disconnected', 'error': str}
    """
    try:
        response = requests.get(
            PYTHONANYWHERE['api_url'],
            timeout=PYTHONANYWHERE['timeout']
        )

        if response.status_code == 200:
            return {
                'status': 'connected',
                'error': None
            }
        else:
            return {
                'status': 'disconnected',
                'error': f'HTTP {response.status_code}'
            }

    except requests.exceptions.ConnectionError:
        return {
            'status': 'disconnected',
            'error': 'Connection refused'
        }
    except requests.exceptions.Timeout:
        return {
            'status': 'disconnected',
            'error': 'Connection timeout'
        }
    except Exception as e:
        return {
            'status': 'disconnected',
            'error': str(e)
        }


def start_erp_api_server():
    """
    ERP API 서버 시작

    Returns:
        bool: 시작 성공 여부
    """
    global last_restart_time

    try:
        logging.info("🚀 ERP API 서버 시작 시도...")

        # 백그라운드 프로세스로 시작
        # Windows에서는 CREATE_NO_WINDOW 플래그 사용
        if sys.platform == 'win32':
            # Windows: 새 콘솔 창 없이 백그라운드 실행
            CREATE_NO_WINDOW = 0x08000000
            process = subprocess.Popen(
                ERP_API_SERVER['start_command'],
                creationflags=CREATE_NO_WINDOW,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        else:
            # Linux/Mac: nohup 사용
            process = subprocess.Popen(
                ERP_API_SERVER['start_command'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True
            )

        # 시작 대기 (10초)
        time.sleep(10)

        # 헬스체크로 시작 확인
        health = check_erp_api_health()

        if health['status'] == 'healthy':
            last_restart_time = datetime.now()
            logging.info(f"✅ ERP API 서버 시작 성공 (PID: {process.pid}, 상품: {health['goods_count']:,}개)")
            return True
        else:
            logging.error(f"❌ ERP API 서버 시작 실패 (헬스체크 실패: {health['error']})")
            return False

    except Exception as e:
        logging.error(f"❌ ERP API 서버 시작 중 오류: {e}")
        import traceback
        traceback.print_exc()
        return False


def stop_erp_api_server(process):
    """
    ERP API 서버 중지

    Args:
        process: psutil.Process 객체

    Returns:
        bool: 중지 성공 여부
    """
    try:
        logging.info(f"🛑 ERP API 서버 중지 중... (PID: {process.pid})")

        # 정상 종료 시도 (SIGTERM)
        process.terminate()

        # 10초 대기
        try:
            process.wait(timeout=10)
            logging.info("✅ ERP API 서버 정상 종료")
            return True
        except psutil.TimeoutExpired:
            # 강제 종료 (SIGKILL)
            logging.warning("⚠️ 정상 종료 실패 - 강제 종료 시도")
            process.kill()
            process.wait(timeout=5)
            logging.info("✅ ERP API 서버 강제 종료")
            return True

    except Exception as e:
        logging.error(f"❌ ERP API 서버 중지 실패: {e}")
        return False


def restart_erp_api_server(process=None):
    """
    ERP API 서버 재시작

    Args:
        process: 기존 프로세스 (있는 경우)

    Returns:
        bool: 재시작 성공 여부
    """
    global consecutive_failures, last_restart_time

    # 재시작 쿨다운 체크
    if last_restart_time:
        elapsed = (datetime.now() - last_restart_time).total_seconds()
        if elapsed < MONITOR_CONFIG['restart_cooldown']:
            logging.warning(f"⏳ 재시작 쿨다운 중 ({int(elapsed)}초/{MONITOR_CONFIG['restart_cooldown']}초)")
            return False

    # 최대 재시도 횟수 체크
    if consecutive_failures >= MONITOR_CONFIG['max_restart_attempts']:
        logging.error(f"🚫 최대 재시작 시도 횟수 초과 ({consecutive_failures}회) - 수동 개입 필요")
        return False

    # 기존 프로세스 중지
    if process:
        stop_erp_api_server(process)
        time.sleep(3)

    # 새 프로세스 시작
    success = start_erp_api_server()

    if success:
        consecutive_failures = 0
        logging.info("✅ ERP API 서버 재시작 성공")
        return True
    else:
        consecutive_failures += 1
        logging.error(f"❌ ERP API 서버 재시작 실패 (시도 {consecutive_failures}/{MONITOR_CONFIG['max_restart_attempts']})")
        return False


# ============================================
# 메인 모니터링 루프
# ============================================

def monitor_loop():
    """메인 모니터링 루프 (무한 반복)"""
    global consecutive_failures

    logging.info("=" * 80)
    logging.info("🚀 TgenAI ERP 게이트웨이 모니터링 시작")
    logging.info("=" * 80)
    logging.info(f"📂 작업 디렉토리: {BASE_DIR}")
    logging.info(f"🔍 체크 주기: {MONITOR_CONFIG['check_interval']}초")
    logging.info(f"🔄 재시작 쿨다운: {MONITOR_CONFIG['restart_cooldown']}초")
    logging.info(f"📊 로그 파일: {LOG_FILE}")
    logging.info("=" * 80)

    # 초기 시작 시 ERP API 서버 상태 확인
    is_running, process = check_erp_api_server_process()

    if not is_running:
        logging.warning("⚠️ ERP API 서버가 실행되지 않음 - 시작 시도")
        start_erp_api_server()
    else:
        logging.info(f"✅ ERP API 서버 실행 중 (PID: {process.pid})")

    # 무한 루프
    iteration = 0

    while True:
        try:
            iteration += 1

            # ========================================
            # 1. ERP API 서버 상태 체크
            # ========================================

            is_running, process = check_erp_api_server_process()

            if not is_running:
                logging.error("❌ ERP API 서버 프로세스 없음 - 재시작 필요")
                restart_erp_api_server()
            else:
                # 헬스체크
                health = check_erp_api_health()

                if health['status'] == 'healthy':
                    consecutive_failures = 0

                    # 30분마다 상태 로그 (자세한 정보)
                    if iteration % 30 == 0:
                        logging.info(
                            f"✅ ERP API 정상 | "
                            f"PID: {process.pid} | "
                            f"상품: {health['goods_count']:,}개 | "
                            f"DB: {health['database']}"
                        )
                else:
                    consecutive_failures += 1
                    logging.error(
                        f"❌ ERP API 서버 헬스체크 실패 ({consecutive_failures}회) | "
                        f"오류: {health['error']}"
                    )

                    # 3회 연속 실패 시 재시작
                    if consecutive_failures >= 3:
                        logging.error("🔄 3회 연속 실패 - 재시작 시도")
                        restart_erp_api_server(process)

            # ========================================
            # 2. PythonAnywhere 연결 체크 (5분마다)
            # ========================================

            if iteration % 5 == 0:
                pa_status = check_pythonanywhere_connection()

                if pa_status['status'] == 'connected':
                    logging.info("✅ PythonAnywhere API 연결 정상")
                else:
                    logging.warning(
                        f"⚠️ PythonAnywhere API 연결 실패 | "
                        f"오류: {pa_status['error']}"
                    )

            # 대기
            time.sleep(MONITOR_CONFIG['check_interval'])

        except KeyboardInterrupt:
            logging.info("⛔ 사용자에 의해 중단됨")
            break

        except Exception as e:
            logging.error(f"❌ 모니터링 루프 오류: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(MONITOR_CONFIG['check_interval'])


# ============================================
# 메인 실행
# ============================================

if __name__ == '__main__':
    try:
        monitor_loop()
    except Exception as e:
        logging.error(f"❌ 치명적 오류: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
