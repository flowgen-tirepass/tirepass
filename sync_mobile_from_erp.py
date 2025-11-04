#!/usr/bin/env python
"""
ERP에서 휴대전화 번호(010)를 가져와서 Django DB의 tel3 컬럼 업데이트
- ERP의 TEL1, TEL3 중에서 010으로 시작하는 번호를 찾기
- Django DB customers 테이블의 tel3 컬럼을 해당 번호로 업데이트
"""

import os
import django
import sys

# Django 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itire.settings')
django.setup()

from tire_data.erp_api_client import ERPAPIClient
from tire_data.models import Customers


def extract_mobile_number(tel1, tel3):
    """TEL1, TEL3 중에서 휴대전화 번호(010) 추출"""
    tel1 = (tel1 or '').strip()
    tel3 = (tel3 or '').strip()

    # TEL3에 휴대전화가 있으면 TEL3 우선
    if tel3.startswith('010'):
        return tel3

    # TEL1에 휴대전화가 있으면 TEL1
    if tel1.startswith('010'):
        return tel1

    # 둘 다 없으면 None
    return None


def sync_mobile_numbers_from_erp(dry_run=True, batch_size=100):
    """ERP에서 휴대전화 번호를 가져와서 Django DB 업데이트"""
    print("=" * 80)
    print("ERP → Django DB 휴대전화 번호 동기화")
    print("=" * 80)

    if dry_run:
        print("\n⚠️  DRY RUN 모드: 실제로 변경하지 않고 분석만 수행합니다.")
        print("   실제 변경하려면 sync_mobile_numbers_from_erp(dry_run=False)로 실행하세요.\n")
    else:
        print("\n🚨 실제 변경 모드: 데이터베이스를 변경합니다!\n")

    # ERP API 서버 연결 확인
    print("🔍 ERP API 서버 연결 확인 중...")
    if not ERPAPIClient.health_check():
        print("❌ ERP API 서버에 연결할 수 없습니다.")
        print("   http://itire2.iptime.org:8000 서버가 실행 중인지 확인하세요.")
        return

    print("✅ ERP API 서버 연결 성공\n")

    # ERP 전체 고객 수 확인
    total_erp_customers = ERPAPIClient.get_customers_count()
    print(f"📊 ERP 전체 고객 수: {total_erp_customers}명")

    # Django DB 전체 고객 수 확인
    total_django_customers = Customers.objects.count()
    print(f"📊 Django DB 전체 고객 수: {total_django_customers}명\n")

    # 통계
    found_mobile_in_erp = 0  # ERP에서 휴대전화 찾은 수
    updated_count = 0  # 업데이트된 수
    no_mobile_in_erp = 0  # ERP에 휴대전화 없는 수
    not_found_in_django = 0  # Django에 없는 고객
    already_correct = 0  # 이미 올바른 상태

    updates = []  # 업데이트할 목록 (DRY RUN용)

    # 배치 단위로 ERP 데이터 가져오기
    offset = 0
    batch_num = 1

    while offset < total_erp_customers:
        print(f"\n📥 배치 {batch_num}: ERP 데이터 가져오는 중 (offset: {offset}, limit: {batch_size})...")

        erp_customers = ERPAPIClient.get_customers_list(offset=offset, limit=batch_size)

        if not erp_customers:
            print(f"   ⚠️  데이터를 가져올 수 없습니다. 건너뜁니다.")
            break

        print(f"   ✅ {len(erp_customers)}명의 데이터 로드 완료")

        for erp_customer in erp_customers:
            customer_code = erp_customer.get('code')
            erp_tel1 = erp_customer.get('tel1', '')
            erp_tel3 = erp_customer.get('tel3', '')

            # ERP에서 휴대전화 번호 추출
            mobile_number = extract_mobile_number(erp_tel1, erp_tel3)

            if mobile_number:
                found_mobile_in_erp += 1

                # Django DB에서 해당 고객 찾기
                try:
                    django_customer = Customers.objects.get(code=customer_code)

                    # 현재 tel3와 비교
                    current_tel3 = (django_customer.tel3 or '').strip()

                    if current_tel3 == mobile_number:
                        # 이미 올바른 상태
                        already_correct += 1
                    else:
                        # 업데이트 필요
                        updates.append({
                            'code': customer_code,
                            'name': django_customer.name,
                            'current_tel3': current_tel3,
                            'new_tel3': mobile_number,
                            'source': 'TEL1' if erp_tel1.startswith('010') else 'TEL3'
                        })
                        updated_count += 1

                except Customers.DoesNotExist:
                    not_found_in_django += 1
            else:
                no_mobile_in_erp += 1

        offset += batch_size
        batch_num += 1

        # 진행 상황 출력
        if batch_num % 5 == 0:
            print(f"\n   📊 중간 통계 (처리: {offset}명)")
            print(f"      - ERP에서 휴대전화 찾음: {found_mobile_in_erp}명")
            print(f"      - 업데이트 필요: {updated_count}명")
            print(f"      - 이미 올바름: {already_correct}명")

    # 최종 통계 출력
    print("\n" + "=" * 80)
    print("📊 분석 결과")
    print("=" * 80)

    print(f"\n1️⃣  ERP에서 휴대전화 찾음: {found_mobile_in_erp}명")
    print(f"2️⃣  업데이트 필요: {updated_count}명")
    print(f"3️⃣  이미 올바른 상태: {already_correct}명")
    print(f"4️⃣  ERP에 휴대전화 없음: {no_mobile_in_erp}명")
    print(f"5️⃣  Django에 없는 고객: {not_found_in_django}명")

    # 업데이트 샘플 출력
    if updated_count > 0:
        print(f"\n📝 업데이트 대상 샘플 (최대 10건):")
        for item in updates[:10]:
            print(f"   {item['code']} | {item['name']}")
            print(f"      현재 tel3: {item['current_tel3'] or '(비어있음)'}")
            print(f"      새 tel3:   {item['new_tel3']} (from ERP {item['source']})")

    # 실제 업데이트 수행
    if not dry_run and updated_count > 0:
        print("\n" + "=" * 80)
        print("🚨 데이터베이스 업데이트 시작")
        print("=" * 80)

        success_count = 0
        error_count = 0

        for item in updates:
            try:
                customer = Customers.objects.get(code=item['code'])
                customer.tel3 = item['new_tel3']
                customer.save()
                success_count += 1

                if success_count % 100 == 0:
                    print(f"   진행 중... {success_count}명 업데이트됨")

            except Exception as e:
                error_count += 1
                print(f"   ❌ 오류: {item['code']} | {e}")

        print("\n" + "=" * 80)
        print("✅ 업데이트 완료")
        print("=" * 80)
        print(f"성공: {success_count}명")
        print(f"실패: {error_count}명")

    elif dry_run and updated_count > 0:
        print("\n" + "=" * 80)
        print("💡 다음 단계")
        print("=" * 80)
        print("실제로 변경하려면 다음 명령어를 실행하세요:")
        print("  python sync_mobile_from_erp.py")
        print("  >>> from sync_mobile_from_erp import sync_mobile_numbers_from_erp")
        print("  >>> sync_mobile_numbers_from_erp(dry_run=False)")

    print("\n" + "=" * 80)


if __name__ == '__main__':
    try:
        # DRY RUN 모드로 실행 (실제 변경 안함)
        # sync_mobile_numbers_from_erp(dry_run=True, batch_size=200)

        # 실제 변경 실행
        sync_mobile_numbers_from_erp(dry_run=False, batch_size=200)

    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
