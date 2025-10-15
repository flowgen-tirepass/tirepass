"""
브랜드 로고 이미지 크기 변경 스크립트
높이를 2배로 늘리고 로고는 중앙에 배치
"""
from PIL import Image
import os

# 브랜드 이미지 디렉토리
brand_dir = r"C:\Users\jmyang\Dropbox\1.0_tirepass\tire_data\static\mobile\img\brands"

# 브랜드 이미지 파일 목록
brands = [
    "goodyear.png",
    "kumho.png",
    "nexen.png",
    "dunlop.png",
    "michelin.png",
    "bridgestone.png",
    "yokohama.png",
    "continental.png",
    "pirelli.png",
    "hankook.png"
]

print(f"브랜드 이미지 크기 변경 시작...")
print(f"디렉토리: {brand_dir}")
print(f"작업: 높이를 2배로 늘리고 로고 중앙 배치")
print("-" * 70)

for brand_file in brands:
    file_path = os.path.join(brand_dir, brand_file)

    if not os.path.exists(file_path):
        print(f"[X] {brand_file}: 파일이 없습니다")
        continue

    try:
        # 이미지 열기
        img = Image.open(file_path)
        original_width, original_height = img.size

        # 새로운 크기 계산 (높이만 2배)
        new_width = original_width
        new_height = original_height * 2

        # 새로운 캔버스 생성 (흰색 배경)
        new_img = Image.new('RGBA', (new_width, new_height), (255, 255, 255, 0))

        # 원본 이미지를 중앙에 배치
        # 세로 중앙: (new_height - original_height) // 2
        paste_y = (new_height - original_height) // 2
        new_img.paste(img, (0, paste_y), img if img.mode == 'RGBA' else None)

        # 원본 파일 덮어쓰기
        new_img.save(file_path, 'PNG', optimize=True)

        print(f"[OK] {brand_file:20s}: {original_width}x{original_height} -> {new_width}x{new_height}")

    except Exception as e:
        print(f"[ERROR] {brand_file}: 에러 발생 - {str(e)}")

print("-" * 70)
print("브랜드 이미지 크기 변경 완료!")
