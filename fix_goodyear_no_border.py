"""
Goodyear 로고 테두리 제거 및 재처리

원본(goodyear_244_backup.png)에는 테두리가 없음
이것을 기반으로 투명 여백 제거 후 확대
"""

from PIL import Image
import os

BASE_PATH = 'tire_data/static/mobile/img/brands'
BRAND = 'goodyear'

def get_bbox(img):
    """투명하지 않은 영역의 경계 박스 계산"""
    if img.mode != 'RGBA':
        img = img.convert('RGBA')

    alpha = img.split()[3]
    bbox = alpha.getbbox()
    return bbox

def fix_goodyear_no_border():
    # 테두리 없는 원본 사용
    backup_path = os.path.join(BASE_PATH, f'{BRAND}_244_backup.png')
    output_path = os.path.join(BASE_PATH, f'{BRAND}.png')

    if not os.path.exists(backup_path):
        print(f"[X] 백업 파일 없음: {backup_path}")
        return False

    try:
        # 테두리 없는 원본 열기
        img = Image.open(backup_path)
        original_size = img.size

        print(f"원본 크기 (244_backup): {original_size[0]}x{original_size[1]}")

        # 투명 여백 제거
        bbox = get_bbox(img)

        if bbox:
            print(f"투명 영역 crop: {bbox}")
            cropped_img = img.crop(bbox)
            cropped_size = cropped_img.size
            print(f"Crop 후: {cropped_size[0]}x{cropped_size[1]}")
        else:
            cropped_img = img
            cropped_size = img.size

        # 목표: 300x150 캔버스에 최대한 크게
        target_size = (300, 150)

        aspect_ratio = cropped_size[0] / cropped_size[1]
        target_aspect = target_size[0] / target_size[1]

        if aspect_ratio > target_aspect:
            # 가로가 더 김
            new_width = target_size[0]
            new_height = int(new_width / aspect_ratio)
        else:
            # 세로가 더 김
            new_height = target_size[1]
            new_width = int(new_height * aspect_ratio)

        print(f"확대: {new_width}x{new_height}")

        # 리사이즈
        resized_img = cropped_img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # 300x150 투명 캔버스
        final_img = Image.new('RGBA', target_size, (0, 0, 0, 0))

        # 중앙 배치
        x_offset = (target_size[0] - new_width) // 2
        y_offset = (target_size[1] - new_height) // 2

        final_img.paste(resized_img, (x_offset, y_offset), resized_img)

        # 저장
        final_img.save(output_path, 'PNG', optimize=True)

        print(f"\n[OK] Goodyear 테두리 제거 완료!")
        print(f"최종 크기: {target_size[0]}x{target_size[1]}")
        print(f"로고 크기: {new_width}x{new_height}")

        return True

    except Exception as e:
        print(f"[X] 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=== Goodyear 로고 테두리 제거 ===\n")
    fix_goodyear_no_border()
