"""
kumho 브랜드 로고 크기 조정
159x80 -> 150x65
"""
from PIL import Image
import os

brand_file = r"C:\Users\jmyang\Dropbox\1.0_tirepass\tire_data\static\mobile\img\brands\kumho.png"

print("kumho 로고 크기 조정 시작...")

try:
    # 이미지 열기
    img = Image.open(brand_file)
    original_width, original_height = img.size
    print(f"현재 크기: {original_width}x{original_height}")

    # 새로운 크기
    new_width = 150
    new_height = 65

    # RGBA 모드로 변환 (투명도 지원)
    if img.mode != 'RGBA':
        img = img.convert('RGBA')

    # 비율 유지하며 리사이즈
    # 150x65에 맞추되, 종횡비 유지
    img.thumbnail((new_width, new_height), Image.Resampling.LANCZOS)
    resized_width, resized_height = img.size

    # 새로운 캔버스 생성 (투명 배경)
    new_img = Image.new('RGBA', (new_width, new_height), (255, 255, 255, 0))

    # 중앙에 배치
    paste_x = (new_width - resized_width) // 2
    paste_y = (new_height - resized_height) // 2
    new_img.paste(img, (paste_x, paste_y), img)

    # 파일 저장
    new_img.save(brand_file, 'PNG', optimize=True)

    print(f"[OK] kumho.png: {original_width}x{original_height} -> {new_width}x{new_height}")
    print("kumho 로고 크기 조정 완료!")

except Exception as e:
    print(f"[ERROR] 에러 발생 - {str(e)}")
