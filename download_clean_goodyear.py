"""
깨끗한 Goodyear 로고 다운로드 및 처리

공식 Goodyear 로고를 다운로드하여 사용
"""

import requests
from PIL import Image
from io import BytesIO
import os

BASE_PATH = 'tire_data/static/mobile/img/brands'

def download_and_process_goodyear():
    """
    방법 1: 공식 로고 URL에서 다운로드
    방법 2: 사용자가 직접 제공한 깨끗한 이미지 사용
    """

    # 일단 현재 244_backup을 사용하되, 회색 선 부분을 제거
    backup_path = os.path.join(BASE_PATH, 'goodyear_244_backup.png')
    output_path = os.path.join(BASE_PATH, 'goodyear.png')

    img = Image.open(backup_path)

    # RGBA로 변환
    if img.mode != 'RGBA':
        img = img.convert('RGBA')

    # 픽셀 데이터 가져오기
    pixels = img.load()
    width, height = img.size

    print(f"원본 크기: {width}x{height}")

    # 회색 선 제거: 밝은 회색(RGB 200 이상)을 투명으로
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            # 밝은 회색 또는 흰색에 가까운 색상을 투명으로
            if r > 200 and g > 200 and b > 200 and a > 0:
                pixels[x, y] = (r, g, b, 0)  # 투명하게

    # 투명 여백 제거
    alpha = img.split()[3]
    bbox = alpha.getbbox()

    if bbox:
        print(f"Crop 영역: {bbox}")
        cropped = img.crop(bbox)
    else:
        cropped = img

    # 300x150으로 확대
    target_size = (300, 150)
    cropped_size = cropped.size
    aspect_ratio = cropped_size[0] / cropped_size[1]
    target_aspect = target_size[0] / target_size[1]

    if aspect_ratio > target_aspect:
        new_width = target_size[0]
        new_height = int(new_width / aspect_ratio)
    else:
        new_height = target_size[1]
        new_width = int(new_height * aspect_ratio)

    resized = cropped.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # 투명 캔버스에 배치
    final = Image.new('RGBA', target_size, (0, 0, 0, 0))
    x_offset = (target_size[0] - new_width) // 2
    y_offset = (target_size[1] - new_height) // 2
    final.paste(resized, (x_offset, y_offset), resized)

    # 저장
    final.save(output_path, 'PNG', optimize=True)

    print(f"\n[OK] 깨끗한 Goodyear 로고 생성!")
    print(f"최종: {target_size[0]}x{target_size[1]}")
    print(f"로고: {new_width}x{new_height}")

    return True

if __name__ == '__main__':
    print("=== 깨끗한 Goodyear 로고 생성 ===\n")
    download_and_process_goodyear()
