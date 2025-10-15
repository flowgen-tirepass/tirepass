"""
Goodyear 로고를 박스 가득 채우도록 크게 확대

문제: 현재 160x75는 너무 작음
목표: 300x150 (Kumho 150x70의 2배 크기)

Kumho: 150x70 -> 렌더링 69x32 (박스 가득)
목표: 300x150 -> 렌더링 시 박스 가득 채울 예상
"""

from PIL import Image
import os

BASE_PATH = 'tire_data/static/mobile/img/brands'
BRAND = 'goodyear'

def enlarge_goodyear_big():
    # 백업 파일(160x244)을 원본으로 사용
    backup_path = os.path.join(BASE_PATH, f'{BRAND}_244_backup.png')
    image_path = os.path.join(BASE_PATH, f'{BRAND}.png')

    if not os.path.exists(backup_path):
        print(f"[X] 백업 파일이 없습니다: {backup_path}")
        return False

    try:
        # 백업 파일 열기
        img = Image.open(backup_path)
        original_size = img.size

        print(f"원본 크기 (백업): {original_size[0]}x{original_size[1]}")

        # 여러 크기 테스트
        test_sizes = [
            (300, 150, "Kumho의 2배"),
            (350, 175, "Kumho의 2.3배"),
            (400, 200, "Kumho의 2.6배"),
        ]

        print("\n테스트할 크기 옵션:")
        for i, (w, h, desc) in enumerate(test_sizes, 1):
            print(f"  {i}. {w}x{h} ({desc})")

        # 일단 300x150으로 시작
        new_size = (300, 150)

        print(f"\n선택: {new_size[0]}x{new_size[1]}")

        # 리사이징
        resized_img = img.resize(new_size, Image.Resampling.LANCZOS)

        # 저장
        resized_img.save(image_path, 'PNG', optimize=True)

        print(f"\n[OK] {BRAND}: {original_size[0]}x{original_size[1]} -> {new_size[0]}x{new_size[1]}")

        # 확인
        verify_img = Image.open(image_path)
        verify_size = verify_img.size
        print(f"검증: {verify_size[0]}x{verify_size[1]}")

        if verify_size == new_size:
            print("[OK] 크기 변경 성공!")
            return True
        else:
            print(f"[X] 크기 불일치: {verify_size}")
            return False

    except Exception as e:
        print(f"[X] 확대 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=== Goodyear 로고 크게 확대 (300x150) ===\n")
    enlarge_goodyear_big()
