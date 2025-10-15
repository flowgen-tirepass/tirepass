"""
Goodyear 로고를 Kumho처럼 브랜드 박스를 가득 채우도록 크기 조정

현재: 160x244 (세로가 너무 김 - 박스에서 작게 표시됨)
목표: 160x75 (Kumho 비율과 비슷하게 - 박스를 가득 채움)

Kumho 비율: 150:70 ≈ 2.14:1
목표 비율: 160:75 ≈ 2.13:1
"""

from PIL import Image
import os

BASE_PATH = 'tire_data/static/mobile/img/brands'
BRAND = 'goodyear'
NEW_SIZE = (160, 75)  # Kumho와 비슷한 가로:세로 비율

def fix_goodyear_fill_box():
    image_path = os.path.join(BASE_PATH, f'{BRAND}.png')

    if not os.path.exists(image_path):
        print(f"[X] {BRAND}.png 파일이 없습니다")
        return False

    try:
        # 이미지 열기
        img = Image.open(image_path)
        original_size = img.size

        print(f"현재 크기: {original_size[0]}x{original_size[1]}")
        print(f"목표 크기: {NEW_SIZE[0]}x{NEW_SIZE[1]}")
        print(f"\n비율 비교:")
        print(f"  Kumho 비율: 150:70 = 2.14:1 (가로가 세로보다 2배 이상)")
        print(f"  현재 Goodyear: {original_size[0]}:{original_size[1]} = {original_size[0]/original_size[1]:.2f}:1")
        print(f"  목표 Goodyear: {NEW_SIZE[0]}:{NEW_SIZE[1]} = {NEW_SIZE[0]/NEW_SIZE[1]:.2f}:1")

        # 백업 저장 (244 버전)
        backup_path = image_path.replace('.png', '_244_backup.png')
        if not os.path.exists(backup_path):
            img.save(backup_path)
            print(f"\n백업 저장: {backup_path}")
        else:
            print(f"\n백업 파일 이미 존재: {backup_path}")

        # 리사이징 (고품질 LANCZOS)
        resized_img = img.resize(NEW_SIZE, Image.Resampling.LANCZOS)

        # 저장
        resized_img.save(image_path, 'PNG', optimize=True)

        print(f"\n[OK] {BRAND}: {original_size[0]}x{original_size[1]} -> {NEW_SIZE[0]}x{NEW_SIZE[1]}")

        # 확인
        verify_img = Image.open(image_path)
        verify_size = verify_img.size
        print(f"\n검증: {verify_size[0]}x{verify_size[1]}")

        if verify_size == NEW_SIZE:
            print("[OK] 크기 변경 성공!")
            print("\n✅ 이제 Goodyear가 Kumho처럼 브랜드 박스를 가득 채울 것입니다!")
            return True
        else:
            print(f"[X] 크기 불일치: {verify_size}")
            return False

    except Exception as e:
        print(f"[X] 리사이징 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=== Goodyear 로고 박스 가득 채우기 (160x75) ===\n")
    fix_goodyear_fill_box()
