"""
브랜드 로고 실제 크기 확인 스크립트
"""

from PIL import Image
import os

BASE_PATH = 'tire_data/static/mobile/img/brands'

BRANDS = [
    'goodyear',
    'kumho',
    'nexen',
    'dunlop',
    'michelin',
    'bridgestone',
    'yokohama',
    'continental',
    'pirelli',
    'hankook'
]

def check_sizes():
    print("=== 현재 브랜드 로고 크기 확인 ===\n")

    for brand in BRANDS:
        image_path = os.path.join(BASE_PATH, f'{brand}.png')

        if not os.path.exists(image_path):
            print(f"[X] {brand}.png 없음")
            continue

        try:
            img = Image.open(image_path)
            width, height = img.size
            print(f"{brand:15s}: {width:4d} x {height:4d}")

        except Exception as e:
            print(f"[X] {brand} 오류: {e}")

if __name__ == '__main__':
    check_sizes()
