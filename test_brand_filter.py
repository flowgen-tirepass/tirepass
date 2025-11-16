"""
브랜드 필터 + 검색 로직 테스트
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import re

# ERP API에서 피렐리 제품 확인
ERP_API_URL = "http://ITIRE2.iptime.org:8000"
ERP_API_KEY = "tirepass-erp-secret-2024"

def test_brand_filter():
    # 1. 전체 상품 가져오기
    params = {
        'offset': 0,
        'limit': 6651,
        'api_key': ERP_API_KEY
    }
    response = requests.get(f"{ERP_API_URL}/api/goods", params=params)
    if response.status_code != 200:
        print(f"❌ ERP API 오류: {response.status_code}")
        print(f"응답: {response.text}")
        return

    all_goods = response.json()
    print(f"📦 전체 상품: {len(all_goods)}개")

    # 2. 브랜드 필터 적용 (Pirelli)
    brand_keywords = ['피렐리', 'PIRELLI', 'P ZERO']
    brand_prefixes = ['P-']

    filtered_goods = []

    for goods in all_goods:
        bun1 = (goods.get('bun1', '') or '').strip()
        name = (goods.get('name', '') or '').strip()
        code = (goods.get('code', '') or '').strip().upper()
        jaego = float(goods.get('jaego', 0))

        # 키워드 매칭
        keyword_match = any(
            kw in bun1 or kw in bun1.upper() or kw in name or kw in name.upper()
            for kw in brand_keywords
        )

        # 코드 접두사 매칭
        code_match = any(code.startswith(prefix) for prefix in brand_prefixes)

        # OR 로직
        brand_match = keyword_match or code_match

        # 브랜드 매칭 안되면 skip
        if not brand_match:
            continue

        # 타이어 코드 체크
        tire_code_prefixes = [
            'ANNAITE-', 'BFG-', 'BS-', 'C-', 'CT-', 'D-', 'G-', 'H-',
            'HIFLY-', 'HILO-', 'K-', 'M-', 'MAXXIS-', 'N-', 'P-'
        ]
        is_tire = any(code.startswith(prefix) for prefix in tire_code_prefixes)

        if is_tire:
            filtered_goods.append(goods)

    print(f"✅ 피렐리 타이어: {len(filtered_goods)}개")

    # 3. 검색어 필터 적용 (2354518 → 235/45R18)
    search_term = '2354518'
    numeric_only = re.sub(r'[^0-9]', '', search_term)

    if len(numeric_only) >= 7:
        width = numeric_only[:3]
        aspect = numeric_only[3:5]
        rim = numeric_only[5:7]
        enhanced_search_term = f"{width}/{aspect}R{rim}"
        search_patterns = [search_term, enhanced_search_term]
    else:
        search_patterns = [search_term]

    print(f"🔍 검색 패턴: {search_patterns}")

    search_results = []
    for goods in filtered_goods:
        code = (goods.get('code', '') or '').strip()
        name = (goods.get('name', '') or '').strip()

        matched = False
        for pattern in search_patterns:
            if (pattern in code or pattern in name or pattern.upper() in name.upper()):
                matched = True
                break

        if matched:
            search_results.append(goods)

    print(f"🎯 검색 결과: {len(search_results)}개")

    # 결과 출력
    if len(search_results) > 0:
        print("\n검색 결과 (처음 5개):")
        for i, goods in enumerate(search_results[:5]):
            code = goods.get('code', 'N/A')
            name = goods.get('name', 'N/A')
            jaego = goods.get('jaego', 0)
            print(f"  [{i+1}] {code} - {name[:60]} (재고: {jaego})")
    else:
        print("\n❌ 검색 결과 없음!")

        # 디버깅: 235/45R18 포함된 제품 찾기
        print("\n🔍 디버깅: 피렐리 제품 중 '235/45R18' 포함된 제품:")
        for goods in filtered_goods[:10]:
            name = goods.get('name', '')
            if '235/45R18' in name or '235/45' in name:
                print(f"  ✓ {goods.get('code')} - {name[:60]}")

if __name__ == '__main__':
    test_brand_filter()
