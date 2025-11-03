#!/usr/bin/env python
"""
고객 전화번호 자동 정리 스크립트
- TEL1에 있는 휴대전화(010) → TEL3로 이동
- TEL3에 있는 일반전화(02, 031, 032 등) → TEL1로 이동
"""

import os
import django
import sys

# Django 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itire.settings')
django.setup()

from tire_data.models import Customers


def is_mobile_number(phone):
    """휴대전화 번호인지 확인 (010으로 시작)"""
    if not phone:
        return False
    phone_clean = str(phone).strip()
    return phone_clean.startswith('010')


def is_landline_number(phone):
    """일반전화 번호인지 확인 (02, 031, 032 등으로 시작)"""
    if not phone:
        return False
    phone_clean = str(phone).strip()
    # 빈 문자열이거나 특수문자만 있는 경우 제외
    if not phone_clean or phone_clean.startswith('*') or phone_clean.startswith('#'):
        return False
    # 일반전화 지역번호로 시작하는지 확인
    return (
        phone_clean.startswith('02-') or
        phone_clean.startswith('031-') or
        phone_clean.startswith('032-') or
        phone_clean.startswith('033-') or
        phone_clean.startswith('041-') or
        phone_clean.startswith('042-') or
        phone_clean.startswith('043-') or
        phone_clean.startswith('044-') or
        phone_clean.startswith('051-') or
        phone_clean.startswith('052-') or
        phone_clean.startswith('053-') or
        phone_clean.startswith('054-') or
        phone_clean.startswith('055-') or
        phone_clean.startswith('061-') or
        phone_clean.startswith('062-') or
        phone_clean.startswith('063-') or
        phone_clean.startswith('064-') or
        phone_clean.startswith('070-')  # 인터넷전화
    )


def fix_phone_numbers(dry_run=True):
    """전화번호 자동 정리"""
    print("=" * 80)
    print("고객 전화번호 자동 정리 스크립트")
    print("=" * 80)

    if dry_run:
        print("\n⚠️  DRY RUN 모드: 실제로 변경하지 않고 분석만 수행합니다.")
        print("   실제 변경하려면 fix_phone_numbers(dry_run=False)로 실행하세요.\n")
    else:
        print("\n🚨 실제 변경 모드: 데이터베이스를 변경합니다!\n")

    all_customers = Customers.objects.all()
    total_customers = all_customers.count()

    print(f"📊 전체 고객 수: {total_customers}명\n")

    # 분석 카운터
    swap_needed = []  # TEL1↔TEL3 스왑 필요
    move_tel1_to_tel3 = []  # TEL1→TEL3 이동 (TEL1에 휴대전화)
    move_tel3_to_tel1 = []  # TEL3→TEL1 이동 (TEL3에 일반전화)
    already_correct = 0
    no_phone = 0

    for customer in all_customers:
        tel1 = customer.tel1 or ''
        tel3 = customer.tel3 or ''

        tel1_is_mobile = is_mobile_number(tel1)
        tel3_is_mobile = is_mobile_number(tel3)
        tel1_is_landline = is_landline_number(tel1)
        tel3_is_landline = is_landline_number(tel3)

        # 케이스 1: TEL1에 휴대전화, TEL3에 일반전화 → 스왑
        if tel1_is_mobile and tel3_is_landline:
            swap_needed.append({
                'customer': customer,
                'current_tel1': tel1,
                'current_tel3': tel3,
                'action': 'SWAP'
            })

        # 케이스 2: TEL1에만 휴대전화 (TEL3 비어있음) → TEL1→TEL3 이동
        elif tel1_is_mobile and not tel3.strip():
            move_tel1_to_tel3.append({
                'customer': customer,
                'current_tel1': tel1,
                'current_tel3': tel3,
                'action': 'MOVE_TO_TEL3'
            })

        # 케이스 3: TEL3에만 일반전화 (TEL1 비어있음) → TEL3→TEL1 이동
        elif tel3_is_landline and not tel1.strip():
            move_tel3_to_tel1.append({
                'customer': customer,
                'current_tel1': tel1,
                'current_tel3': tel3,
                'action': 'MOVE_TO_TEL1'
            })

        # 올바른 경우: TEL1에 일반전화, TEL3에 휴대전화
        elif (tel1_is_landline or not tel1.strip()) and (tel3_is_mobile or not tel3.strip()):
            already_correct += 1

        # 전화번호가 둘 다 없는 경우
        elif not tel1.strip() and not tel3.strip():
            no_phone += 1

    # 분석 결과 출력
    print("=" * 80)
    print("📊 분석 결과")
    print("=" * 80)

    print(f"\n1️⃣  TEL1↔TEL3 스왑 필요: {len(swap_needed)}건")
    print("    (TEL1에 휴대전화, TEL3에 일반전화)")
    if len(swap_needed) > 0:
        print("    샘플 (최대 5건):")
        for item in swap_needed[:5]:
            c = item['customer']
            print(f"      {c.code} | {c.name} | TEL1: {item['current_tel1']} | TEL3: {item['current_tel3']}")

    print(f"\n2️⃣  TEL1→TEL3 이동 필요: {len(move_tel1_to_tel3)}건")
    print("    (TEL1에만 휴대전화, TEL3 비어있음)")
    if len(move_tel1_to_tel3) > 0:
        print("    샘플 (최대 5건):")
        for item in move_tel1_to_tel3[:5]:
            c = item['customer']
            print(f"      {c.code} | {c.name} | TEL1: {item['current_tel1']} → TEL3")

    print(f"\n3️⃣  TEL3→TEL1 이동 필요: {len(move_tel3_to_tel1)}건")
    print("    (TEL3에만 일반전화, TEL1 비어있음)")
    if len(move_tel3_to_tel1) > 0:
        print("    샘플 (최대 5건):")
        for item in move_tel3_to_tel1[:5]:
            c = item['customer']
            print(f"      {c.code} | {c.name} | TEL3: {item['current_tel3']} → TEL1")

    print(f"\n4️⃣  이미 올바른 상태: {already_correct}건")
    print(f"5️⃣  전화번호 없음: {no_phone}건")

    total_fixes = len(swap_needed) + len(move_tel1_to_tel3) + len(move_tel3_to_tel1)
    print(f"\n📝 총 수정 필요: {total_fixes}건")

    # 실제 변경 수행
    if not dry_run and total_fixes > 0:
        print("\n" + "=" * 80)
        print("🚨 데이터베이스 변경 시작")
        print("=" * 80)

        success_count = 0
        error_count = 0

        # 1. 스왑
        for item in swap_needed:
            try:
                customer = item['customer']
                # TEL1 ↔ TEL3 스왑
                temp = customer.tel1
                customer.tel1 = customer.tel3
                customer.tel3 = temp
                customer.save()
                success_count += 1
                print(f"✅ SWAP: {customer.code} | {customer.name}")
            except Exception as e:
                error_count += 1
                print(f"❌ 오류: {customer.code} | {e}")

        # 2. TEL1 → TEL3 이동
        for item in move_tel1_to_tel3:
            try:
                customer = item['customer']
                customer.tel3 = customer.tel1
                customer.tel1 = ''
                customer.save()
                success_count += 1
                print(f"✅ MOVE: {customer.code} | {customer.name} (TEL1 → TEL3)")
            except Exception as e:
                error_count += 1
                print(f"❌ 오류: {customer.code} | {e}")

        # 3. TEL3 → TEL1 이동
        for item in move_tel3_to_tel1:
            try:
                customer = item['customer']
                customer.tel1 = customer.tel3
                customer.tel3 = ''
                customer.save()
                success_count += 1
                print(f"✅ MOVE: {customer.code} | {customer.name} (TEL3 → TEL1)")
            except Exception as e:
                error_count += 1
                print(f"❌ 오류: {customer.code} | {e}")

        print("\n" + "=" * 80)
        print("✅ 변경 완료")
        print("=" * 80)
        print(f"성공: {success_count}건")
        print(f"실패: {error_count}건")

    elif dry_run and total_fixes > 0:
        print("\n" + "=" * 80)
        print("💡 다음 단계")
        print("=" * 80)
        print("실제로 변경하려면 다음 명령어를 실행하세요:")
        print("  python check_customer_phone.py")
        print("  >>> from fix_customer_phone_numbers import fix_phone_numbers")
        print("  >>> fix_phone_numbers(dry_run=False)")

    print("\n" + "=" * 80)


if __name__ == '__main__':
    try:
        # DRY RUN 모드로 실행 (실제 변경 안함)
        # fix_phone_numbers(dry_run=True)

        # 실제 변경 실행
        fix_phone_numbers(dry_run=False)

    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
