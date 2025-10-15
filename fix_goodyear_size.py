"""
Goodyear 로고를 다른 브랜드와 비슷한 크기로 조정

현재: 160x244 (너무 큼)
목표: 160x122 (다른 로고들과 비슷)
"""

from PIL import Image
import os

BASE_PATH = 'tire_data/static/mobile/img/brands'
BRAND = 'goodyear'
NEW_SIZE = (160, 122)

def resize_goodyear():
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

        # 백업 저장
        backup_path = image_path.replace('.png', '_244_backup.png')
        img.save(backup_path)
        print(f"백업 저장: {backup_path}")

        # 리사이징 (고품질 LANCZOS)
        resized_img = img.resize(NEW_SIZE, Image.Resampling.LANCZOS)

        # 저장
        resized_img.save(image_path, 'PNG', optimize=True)

        print(f"\n[OK] {BRAND}: {original_size[0]}x{original_size[1]} -> {NEW_SIZE[0]}x{NEW_SIZE[1]}")
        print("\n다른 브랜드와 크기 비교:")

        # 다른 브랜드 크기 표시
        brands = ['kumho', 'nexen', 'dunlop', 'michelin', 'bridgestone',
                  'yokohama', 'continental', 'pirelli', 'hankook']

        for brand in brands:
            brand_path = os.path.join(BASE_PATH, f'{brand}.png')
            if os.path.exists(brand_path):
                brand_img = Image.open(brand_path)
                w, h = brand_img.size
                print(f"  {brand:15s}: {w:3d}x{h:3d}")

        print(f"  {BRAND:15s}: {NEW_SIZE[0]:3d}x{NEW_SIZE[1]:3d} (수정됨)")

        return True

    except Exception as e:
        print(f"[X] 리사이징 실패: {e}")
        return False

if __name__ == '__main__':
    print("=== Goodyear 로고 크기 조정 ===\n")
    resize_goodyear()
