"""
Goodyear 로고를 160x244로 확대

현재: 160x122
목표: 160x244 (2배 확대)
"""

from PIL import Image
import os

BASE_PATH = 'tire_data/static/mobile/img/brands'
BRAND = 'goodyear'
NEW_SIZE = (160, 244)

def enlarge_goodyear():
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

        # 백업 저장 (122 버전)
        backup_path = image_path.replace('.png', '_122_backup.png')
        img.save(backup_path)
        print(f"백업 저장: {backup_path}")

        # 리사이징 (고품질 LANCZOS로 확대)
        enlarged_img = img.resize(NEW_SIZE, Image.Resampling.LANCZOS)

        # 저장
        enlarged_img.save(image_path, 'PNG', optimize=True)

        print(f"\n[OK] {BRAND}: {original_size[0]}x{original_size[1]} -> {NEW_SIZE[0]}x{NEW_SIZE[1]}")

        # 확인
        verify_img = Image.open(image_path)
        verify_size = verify_img.size
        print(f"\n검증: {verify_size[0]}x{verify_size[1]}")

        if verify_size == NEW_SIZE:
            print("[OK] 크기 변경 성공!")
            return True
        else:
            print(f"[X] 크기 불일치: {verify_size}")
            return False

    except Exception as e:
        print(f"[X] 확대 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=== Goodyear 로고 확대 (160x244) ===\n")
    enlarge_goodyear()
