"""
goodyear 브랜드 로고 크기 조정
현재 크기 → 160x244
"""
from PIL import Image
import os

# 리사이즈할 파일 목록
brand_files = [
    r"C:\Users\jmyang\Dropbox\1.0_tirepass\tire_data\static\mobile\img\brands\goodyear.png",
    r"C:\Users\jmyang\Dropbox\1.0_tirepass\mobile\static\mobile\img\brands\goodyear.png",
    r"C:\Users\jmyang\Dropbox\1.0_tirepass\mobile\mobile\static\mobile\img\brands\goodyear.png",
]

print("goodyear 로고 크기 조정 시작...")

target_width = 160
target_height = 244

for brand_file in brand_files:
    if not os.path.exists(brand_file):
        print(f"[SKIP] 파일 없음: {brand_file}")
        continue

    try:
        # 이미지 열기
        img = Image.open(brand_file)
        original_width, original_height = img.size
        print(f"\n파일: {brand_file}")
        print(f"현재 크기: {original_width}x{original_height}")

        # RGBA 모드로 변환 (투명도 지원)
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        # 비율 유지하며 리사이즈
        # 160x244에 맞추되, 종횡비 유지
        img.thumbnail((target_width, target_height), Image.Resampling.LANCZOS)
        resized_width, resized_height = img.size

        # 새로운 캔버스 생성 (투명 배경)
        new_img = Image.new('RGBA', (target_width, target_height), (255, 255, 255, 0))

        # 중앙에 배치
        paste_x = (target_width - resized_width) // 2
        paste_y = (target_height - resized_height) // 2
        new_img.paste(img, (paste_x, paste_y), img)

        # 파일 저장
        new_img.save(brand_file, 'PNG', optimize=True)

        print(f"[OK] {original_width}x{original_height} → {target_width}x{target_height}")

    except Exception as e:
        print(f"[ERROR] 에러 발생 - {str(e)}")

print("\ngoodyear 로고 크기 조정 완료!")
