"""
TgenAI PC Wake-on-LAN (WOL) 전송 스크립트

로컬 네트워크 또는 인터넷을 통해 TgenAI PC의 전원을 원격으로 켭니다.

사용법:
    python wake_tgenai.py

설정:
    - TgenAI_MAC: TgenAI PC의 MAC 주소 (자동 감지 또는 수동 설정)
    - BROADCAST_IP: 브로드캐스트 주소 (로컬 네트워크용)
    - PUBLIC_IP: 공인 IP (외부 네트워크용)
"""

import socket
import struct
import sys
import time

# ============================================
# 설정 (TgenAI PC 정보)
# ============================================

# TgenAI PC의 MAC 주소
# 형식: "00-1A-2B-3C-4D-5E" 또는 "00:1a:2b:3c:4d:5e"
# TODO: TgenAI PC의 실제 MAC 주소로 변경하세요!
TGENAI_MAC = "00-00-00-00-00-00"  # ⚠️ 실제 MAC 주소로 변경 필요!

# 브로드캐스트 주소 (로컬 네트워크)
BROADCAST_IP = "255.255.255.255"

# 공인 IP 및 포트 (외부 네트워크용)
PUBLIC_IP = "itire2.iptime.org"  # 또는 실제 공인 IP
WOL_PORT = 9


# ============================================
# Wake-on-LAN 함수
# ============================================

def validate_mac_address(mac):
    """
    MAC 주소 유효성 검사

    Args:
        mac (str): MAC 주소

    Returns:
        bool: 유효하면 True
    """
    # 구분자 제거
    mac_clean = mac.replace(':', '').replace('-', '').replace('.', '')

    # 12자리 16진수인지 확인
    if len(mac_clean) != 12:
        return False

    try:
        int(mac_clean, 16)
        return True
    except ValueError:
        return False


def create_magic_packet(mac_address):
    """
    Magic Packet 생성

    Magic Packet 구조:
    - 6바이트 0xFF (동기화 스트림)
    - MAC 주소 16번 반복 (6바이트 × 16 = 96바이트)
    - 총 102바이트

    Args:
        mac_address (str): MAC 주소

    Returns:
        bytes: Magic Packet
    """
    # MAC 주소에서 구분자 제거
    mac_clean = mac_address.replace(':', '').replace('-', '').replace('.', '')

    # 2자리씩 쪼개서 바이트로 변환
    mac_bytes = bytes.fromhex(mac_clean)

    # Magic Packet 생성
    # 1. 6바이트 0xFF (동기화 스트림)
    magic_packet = b'\xff' * 6

    # 2. MAC 주소 16번 반복
    magic_packet += mac_bytes * 16

    return magic_packet


def send_wol(mac_address, ip_address=BROADCAST_IP, port=WOL_PORT):
    """
    Wake-on-LAN Magic Packet 전송

    Args:
        mac_address (str): 대상 PC의 MAC 주소
        ip_address (str): 브로드캐스트 IP 또는 공인 IP
        port (int): WOL 포트 (기본: 9)

    Returns:
        bool: 전송 성공 여부
    """
    try:
        # MAC 주소 유효성 검사
        if not validate_mac_address(mac_address):
            print(f"❌ 잘못된 MAC 주소 형식: {mac_address}")
            print("   올바른 형식: 00-1A-2B-3C-4D-5E 또는 00:1a:2b:3c:4d:5e")
            return False

        # Magic Packet 생성
        magic_packet = create_magic_packet(mac_address)

        # UDP 소켓 생성
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        # Magic Packet 전송
        sock.sendto(magic_packet, (ip_address, port))
        sock.close()

        print(f"✅ Magic Packet 전송 성공!")
        print(f"   대상 MAC: {mac_address}")
        print(f"   대상 IP: {ip_address}:{port}")
        print(f"   패킷 크기: {len(magic_packet)} 바이트")

        return True

    except socket.error as e:
        print(f"❌ 네트워크 오류: {e}")
        return False

    except Exception as e:
        print(f"❌ 전송 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def wake_tgenai_local():
    """로컬 네트워크에서 TgenAI PC 깨우기"""
    print("=" * 60)
    print("🌐 TgenAI PC Wake-on-LAN (로컬 네트워크)")
    print("=" * 60)
    print()

    if TGENAI_MAC == "00-00-00-00-00-00":
        print("⚠️ 경고: TgenAI MAC 주소가 설정되지 않았습니다!")
        print()
        print("설정 방법:")
        print("1. TgenAI PC에서 다음 명령 실행:")
        print("   ipconfig /all")
        print()
        print("2. '물리적 주소'를 확인 (예: 00-1A-2B-3C-4D-5E)")
        print()
        print("3. 이 파일(wake_tgenai.py)을 열어서")
        print("   TGENAI_MAC 값을 실제 MAC 주소로 변경")
        print()
        return False

    # 로컬 브로드캐스트로 전송
    success = send_wol(TGENAI_MAC, BROADCAST_IP)

    if success:
        print()
        print("📌 다음 단계:")
        print("   1. 30초 정도 대기하세요")
        print("   2. TeamViewer로 접속 시도")
        print("   3. 접속 안 되면 1-2분 더 대기 후 재시도")
        print()

    return success


def wake_tgenai_remote():
    """외부 네트워크에서 TgenAI PC 깨우기"""
    print("=" * 60)
    print("🌍 TgenAI PC Wake-on-LAN (외부 네트워크)")
    print("=" * 60)
    print()

    if TGENAI_MAC == "00-00-00-00-00-00":
        print("⚠️ 경고: TgenAI MAC 주소가 설정되지 않았습니다!")
        print("   설정 방법은 wake_tgenai_local() 참조")
        return False

    # 공인 IP로 전송 (포트 포워딩 필요)
    print("📌 주의사항:")
    print("   - 공유기에서 UDP 포트 9번 포트 포워딩 필요")
    print("   - 자세한 설정은 WAKE_ON_LAN_SETUP_GUIDE.md 참조")
    print()

    success = send_wol(TGENAI_MAC, PUBLIC_IP)

    if success:
        print()
        print("📌 다음 단계:")
        print("   1. 1-2분 정도 대기하세요 (외부 연결은 시간 더 걸림)")
        print("   2. TeamViewer로 접속 시도")
        print()

    return success


def interactive_mode():
    """대화형 모드"""
    print("=" * 60)
    print("🔌 TgenAI PC Wake-on-LAN 전송 도구")
    print("=" * 60)
    print()
    print("현재 설정:")
    print(f"  - TgenAI MAC: {TGENAI_MAC}")
    print(f"  - 로컬 브로드캐스트: {BROADCAST_IP}")
    print(f"  - 공인 IP: {PUBLIC_IP}")
    print()

    while True:
        print("=" * 60)
        print("메뉴:")
        print("  1. 로컬 네트워크에서 WOL 전송 (같은 건물/네트워크)")
        print("  2. 외부 네트워크에서 WOL 전송 (인터넷)")
        print("  3. MAC 주소 변경")
        print("  4. 종료")
        print("=" * 60)

        choice = input("선택 (1-4): ").strip()

        if choice == '1':
            print()
            wake_tgenai_local()
        elif choice == '2':
            print()
            wake_tgenai_remote()
        elif choice == '3':
            print()
            new_mac = input("새 MAC 주소 입력 (예: 00-1A-2B-3C-4D-5E): ").strip()
            if validate_mac_address(new_mac):
                global TGENAI_MAC
                TGENAI_MAC = new_mac
                print(f"✅ MAC 주소 변경됨: {TGENAI_MAC}")
            else:
                print("❌ 잘못된 MAC 주소 형식")
        elif choice == '4':
            print()
            print("👋 종료합니다.")
            break
        else:
            print("❌ 잘못된 선택")

        print()
        time.sleep(1)


# ============================================
# 메인 실행
# ============================================

if __name__ == '__main__':
    if len(sys.argv) > 1:
        # 명령줄 인자로 MAC 주소 전달
        mac = sys.argv[1]

        if not validate_mac_address(mac):
            print(f"❌ 잘못된 MAC 주소: {mac}")
            sys.exit(1)

        # 로컬 또는 원격 선택
        if len(sys.argv) > 2 and sys.argv[2] == 'remote':
            send_wol(mac, PUBLIC_IP)
        else:
            send_wol(mac, BROADCAST_IP)

    else:
        # 대화형 모드
        try:
            interactive_mode()
        except KeyboardInterrupt:
            print()
            print()
            print("👋 사용자에 의해 중단됨")
            sys.exit(0)
