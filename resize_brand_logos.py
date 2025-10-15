"""
브랜드 로고 이미지 리사이징 스크립트

작업 내용:
- goodyear: 160x122 → 160x244 (높이 2배)
- kumho: 159x92 -> 150x70 (작게)
- nexen: 160x46 → 160x92 (높이 2배)
- dunlop: 160x66 → 160x132 (높이 2배)
- michelin: 160x66 → 160x132 (높이 2배)
- bridgestone: 160x50 → 160x100 (높이 2배)
- yokohama: 157x52 → 157x104 (높이 2배)
- continental: 160x63 → 160x126 (높이 2배)
- pirelli: 155x50 → 155x100 (높이 2배)
- hankook: 160x57 → 160x114 (높이 2배)
"""

from PIL import Image
import os

# 브랜드 로고 크기 설정 (width, height)
BRAND_SIZES = {
    'goodyear': (160, 244),
    'kumho': (150, 70),
    'nexen': (160, 92),
    'dunlop': (160, 132),
    'michelin': (160, 132),
    'bridgestone': (160, 100),
    'yokohama': (157, 104),
    'continental': (160, 126),
    'pirelli': (155, 100),
    'hankook': (160, 114),
}

# 이미지 경로
BASE_PATH = 'tire_data/static/mobile/img/brands'

def resize_logo(brand_name, new_size):
    """브랜드 로고 이미지를 새로운 크기로 리사이징"""
    image_path = os.path.join(BASE_PATH, f'{brand_name}.png')

    if not os.path.exists(image_path):
        print(f"[X] {brand_name}.png 파일이 없습니다: {image_path}")
        return False

    try:
        # 이미지 열기
        img = Image.open(image_path)
        original_size = img.size

        # 리사이징 (고품질 LANCZOS)
        resized_img = img.resize(new_size, Image.Resampling.LANCZOS)

        # 백업 저장
        backup_path = image_path.replace('.png', '_backup.png')
        img.save(backup_path)

        # 새 이미지 저장
        resized_img.save(image_path, 'PNG', optimize=True)

        print(f"[OK] {brand_name}: {original_size[0]}x{original_size[1]} -> {new_size[0]}x{new_size[1]}")
        return True

    except Exception as e:
        print(f"[X] {brand_name} 리사이징 실패: {e}")
        return False

def main():
    print("=== 브랜드 로고 리사이징 시작 ===\n")

    success_count = 0
    fail_count = 0

    for brand_name, new_size in BRAND_SIZES.items():
        if resize_logo(brand_name, new_size):
            success_count += 1
        else:
            fail_count += 1

    print(f"\n=== 완료 ===")
    print(f"성공: {success_count}개")
    print(f"실패: {fail_count}개")
    print(f"\n백업 파일: *_backup.png")

if __name__ == '__main__':
    main()
