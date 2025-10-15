"""
kumho 브랜드 로고 높이 조정
159x92 -> 159x80
"""
from PIL import Image
import os

brand_file = r"C:\Users\jmyang\Dropbox\1.0_tirepass\tire_data\static\mobile\img\brands\kumho.png"

print("kumho 로고 높이 조정 시작...")

try:
    # 이미지 열기
    img = Image.open(brand_file)
    original_width, original_height = img.size
    print(f"현재 크기: {original_width}x{original_height}")

    # 새로운 크기
    new_width = 159
    new_height = 80

    # 새로운 캔버스 생성 (투명 배경)
    new_img = Image.new('RGBA', (new_width, new_height), (255, 255, 255, 0))

    # 원본 로고 영역 추출 (상단 여백 제거하고 하단 일부 제거)
    # 현재 92px 높이에서 로고가 중앙에 있으므로
    # 원본 이미지에서 로고 부분만 잘라내기
    # 상하 6px씩 제거 (92 - 12 = 80)
    crop_top = 6
    crop_bottom = original_height - 6

    # 원본 로고에서 실제 로고가 있는 부분 찾기
    # 여기서는 단순히 92px에서 80px로 줄이되 중앙 정렬 유지
    paste_y = (new_height - (original_height - 12)) // 2

    # 원본 이미지에서 로고 부분 크롭
    cropped = img.crop((0, crop_top, original_width, crop_bottom))

    # 중앙에 배치
    paste_y = (new_height - cropped.size[1]) // 2
    new_img.paste(cropped, (0, paste_y), cropped if cropped.mode == 'RGBA' else None)

    # 파일 저장
    new_img.save(brand_file, 'PNG', optimize=True)

    print(f"[OK] kumho.png: {original_width}x{original_height} -> {new_width}x{new_height}")
    print("kumho 로고 높이 조정 완료!")

except Exception as e:
    print(f"[ERROR] 에러 발생 - {str(e)}")
