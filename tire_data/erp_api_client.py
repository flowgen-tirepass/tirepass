"""
ERP FastAPI 서버 연동 클라이언트
TgenAI PC의 FastAPI 서버로부터 실시간 ERP 데이터 조회
"""

import requests
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)

# FastAPI 서버 설정
ERP_API_BASE_URL = "http://ITIRE2.iptime.org:8000"
ERP_API_KEY = "tirepass-erp-secret-2024"
TIMEOUT = 10  # 10초 타임아웃


class ERPAPIClient:
    """ERP FastAPI 클라이언트"""

    @staticmethod
    def _get(endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """GET 요청 헬퍼"""
        try:
            if params is None:
                params = {}
            params['api_key'] = ERP_API_KEY

            url = f"{ERP_API_BASE_URL}{endpoint}"
            logger.info(f"ERP API 요청: {url} - params: {params}")

            response = requests.get(url, params=params, timeout=TIMEOUT)
            response.raise_for_status()

            result = response.json()
            logger.info(f"ERP API 응답: {endpoint} - 결과 타입: {type(result)}")

            return result

        except requests.exceptions.Timeout:
            logger.error(f"ERP API timeout: {endpoint}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"ERP API error: {endpoint} - {str(e)}")
            return None
        except Exception as e:
            logger.error(f"ERP API 예외: {endpoint} - {str(e)}")
            return None

    # ========================================
    # 상품(GOODS) API
    # ========================================

    @staticmethod
    def get_goods_count() -> int:
        """상품 총 개수 조회"""
        result = ERPAPIClient._get("/api/goods/count")
        return result.get('count', 0) if result else 0

    @staticmethod
    def get_goods_list(offset: int = 0, limit: int = 100, search: Optional[str] = None) -> List[Dict]:
        """상품 목록 조회"""
        params = {'offset': offset, 'limit': limit}
        if search:
            params['search'] = search

        result = ERPAPIClient._get("/api/goods", params=params)
        return result if result else []

    @staticmethod
    def get_goods_detail(code: str) -> Optional[Dict]:
        """특정 상품 상세 조회"""
        return ERPAPIClient._get(f"/api/goods/{code}")

    # ========================================
    # 고객(CUSTOMERS) API
    # ========================================

    @staticmethod
    def get_customers_count() -> int:
        """고객 총 개수 조회"""
        result = ERPAPIClient._get("/api/customers/count")
        return result.get('count', 0) if result else 0

    @staticmethod
    def get_customers_list(offset: int = 0, limit: int = 100, search: Optional[str] = None) -> List[Dict]:
        """고객 목록 조회"""
        params = {'offset': offset, 'limit': limit}
        if search:
            params['search'] = search

        result = ERPAPIClient._get("/api/customers", params=params)
        return result if result else []

    @staticmethod
    def get_customer_detail(code: str) -> Optional[Dict]:
        """특정 고객 상세 조회"""
        return ERPAPIClient._get(f"/api/customers/{code}")

    # ========================================
    # 주문(ORDERS) API
    # ========================================

    @staticmethod
    def get_orders_count(start_date: Optional[str] = None, end_date: Optional[str] = None) -> int:
        """주문 총 개수 조회"""
        params = {}
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date

        result = ERPAPIClient._get("/api/orders/count", params=params)
        return result.get('count', 0) if result else 0

    @staticmethod
    def get_orders_list(
        offset: int = 0,
        limit: int = 100,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        customer_code: Optional[str] = None
    ) -> List[Dict]:
        """주문 목록 조회"""
        params = {'offset': offset, 'limit': limit}
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        if customer_code:
            params['customer_code'] = customer_code

        result = ERPAPIClient._get("/api/orders", params=params)
        return result if result else []

    @staticmethod
    def get_recent_orders(limit: int = 10) -> List[Dict]:
        """최근 주문 조회"""
        params = {'limit': limit}
        result = ERPAPIClient._get("/api/orders/recent", params=params)
        return result if result else []

    @staticmethod
    def get_customer_orders(customer_code: str, limit: int = 100) -> List[Dict]:
        """특정 고객의 주문 내역 조회"""
        params = {'limit': limit}
        result = ERPAPIClient._get(f"/api/orders/customer/{customer_code}", params=params)
        return result if result else []

    # ========================================
    # 헬스 체크
    # ========================================

    @staticmethod
    def health_check() -> bool:
        """ERP API 서버 연결 확인"""
        try:
            response = requests.get(f"{ERP_API_BASE_URL}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
