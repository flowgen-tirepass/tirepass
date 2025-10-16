"""
Goodyear 로고 투명 여백 제거 및 확대

문제: 300x150 이미지에서 로고가 중앙 작은 부분만 차지
해결: 투명 여백 자동 제거(crop) → 캔버스 가득 채우도록 확대
"""

from PIL import Image
import os

BASE_PATH = 'tire_data/static/mobile/img/brands'
BRAND = 'goodyear'

def get_bbox(img):
    """투명하지 않은 영역의 경계 박스 계산"""
    # RGBA 이미지에서 알파 채널 가져오기
    if img.mode != 'RGBA':
        img = img.convert('RGBA')

    # 알파 채널 추출
    alpha = img.split()[3]

    # 투명하지 않은 영역 찾기
    bbox = alpha.getbbox()
    return bbox

def crop_and_enlarge_goodyear():
    image_path = os.path.join(BASE_PATH, f'{BRAND}.png')

    if not os.path.exists(image_path):
        print(f"[X] {BRAND}.png 파일이 없습니다")
        return False

    try:
        # 이미지 열기
        img = Image.open(image_path)
        original_size = img.size

        print(f"원본 크기: {original_size[0]}x{original_size[1]}")

        # 투명 여백 제거 (crop)
        bbox = get_bbox(img)

        if bbox:
            print(f"투명 여백 제거: {bbox}")
            cropped_img = img.crop(bbox)
            cropped_size = cropped_img.size
            print(f"Crop 후 크기: {cropped_size[0]}x{cropped_size[1]}")
        else:
            print("투명 영역 없음 - crop 건너뜀")
            cropped_img = img
            cropped_size = img.size

        # 목표 크기로 확대 (300x150)
        target_size = (300, 150)

        # 비율 유지하면서 최대한 크게
        # 가로세로 비율 계산
        aspect_ratio = cropped_size[0] / cropped_size[1]
        target_aspect = target_size[0] / target_size[1]

        if aspect_ratio > target_aspect:
            # 가로가 더 긴 경우 - 가로를 기준으로
            new_width = target_size[0]
            new_height = int(new_width / aspect_ratio)
        else:
            # 세로가 더 긴 경우 - 세로를 기준으로
            new_height = target_size[1]
            new_width = int(new_height * aspect_ratio)

        print(f"리사이즈: {new_width}x{new_height}")

        # 리사이징
        resized_img = cropped_img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # 300x150 캔버스 생성 (투명 배경)
        final_img = Image.new('RGBA', target_size, (0, 0, 0, 0))

        # 중앙에 배치
        x_offset = (target_size[0] - new_width) // 2
        y_offset = (target_size[1] - new_height) // 2

        final_img.paste(resized_img, (x_offset, y_offset), resized_img)

        # 백업 저장
        backup_path = image_path.replace('.png', '_before_crop.png')
        img.save(backup_path)
        print(f"\n백업 저장: {backup_path}")

        # 저장
        final_img.save(image_path, 'PNG', optimize=True)

        print(f"\n[OK] {BRAND}: {original_size[0]}x{original_size[1]} -> {target_size[0]}x{target_size[1]}")
        print(f"실제 로고 크기: {new_width}x{new_height} (캔버스 가득 채움)")

        # 확인
        verify_img = Image.open(image_path)
        verify_size = verify_img.size
        print(f"\n검증: {verify_size[0]}x{verify_size[1]}")

        if verify_size == target_size:
            print("[OK] 크기 변경 성공!")
            print("\n이제 Goodyear 로고가 캔버스를 가득 채워서 브랜드 박스에 크게 표시됩니다!")
            return True
        else:
            print(f"[X] 크기 불일치: {verify_size}")
            return False

    except Exception as e:
        print(f"[X] 처리 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=== Goodyear 로고 투명 여백 제거 및 확대 ===\n")
    crop_and_enlarge_goodyear()
