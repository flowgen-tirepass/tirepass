"""
브랜드 로고 이미지 현재 크기 확인
"""
from PIL import Image
import os

brand_dir = r"C:\Users\jmyang\Dropbox\1.0_tirepass\tire_data\static\mobile\img\brands"
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

print("현재 브랜드 이미지 크기:")
print("-" * 50)

for brand_file in brands:
    file_path = os.path.join(brand_dir, brand_file)
    if os.path.exists(file_path):
        img = Image.open(file_path)
        print(f"{brand_file:20s}: {img.size[0]} x {img.size[1]} 픽셀")
    else:
        print(f"{brand_file:20s}: 파일 없음")
