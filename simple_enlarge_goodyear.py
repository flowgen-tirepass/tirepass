"""
Goodyear 로고 단순 확대 (깔끔하게)

goodyear_244_backup.png (160x244)를
단순히 가로 2배 확대: 320x488
"""

from PIL import Image
import os

BASE_PATH = 'tire_data/static/mobile/img/brands'

def simple_enlarge():
    backup_path = os.path.join(BASE_PATH, 'goodyear_244_backup.png')
    output_path = os.path.join(BASE_PATH, 'goodyear.png')

    img = Image.open(backup_path)
    original_size = img.size

    print(f"원본: {original_size[0]}x{original_size[1]}")

    # 2배 확대
    new_size = (original_size[0] * 2, original_size[1] * 2)

    enlarged = img.resize(new_size, Image.Resampling.LANCZOS)
    enlarged.save(output_path, 'PNG', optimize=True)

    print(f"확대: {new_size[0]}x{new_size[1]}")
    print("\n[OK] 완료!")

    return True

if __name__ == '__main__':
    print("=== Goodyear 단순 2배 확대 ===\n")
    simple_enlarge()
