"""
ERP 실시간 동기화 API

광주 ERP 서버에서 전송하는 데이터를 받아 MySQL 업데이트
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from tire_data.models import CustomersFull, Goods
import json
import logging

logger = logging.getLogger(__name__)


def verify_api_key(request):
    """API 키 검증"""
    auth_header = request.headers.get('Authorization', '')

    if not auth_header.startswith('Bearer '):
        return False

    api_key = auth_header.replace('Bearer ', '')

    # 환경변수 또는 설정에서 API 키 확인
    # TODO: settings.py에 ERP_SYNC_API_KEY 추가
    from django.conf import settings
    expected_key = getattr(settings, 'ERP_SYNC_API_KEY', 'test_api_key_12345')

    return api_key == expected_key


@csrf_exempt
@require_http_methods(["POST"])
def sync_customer(request):
    """
    고객 데이터 동기화 API

    POST /api/sync/customer/
    {
        "operation": "INSERT|UPDATE|DELETE",
        "record_key": "고객코드",
        "data": {
            "code": "...",
            "name": "...",
            ...
        }
    }
    """

    # API 키 검증
    if not verify_api_key(request):
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    try:
        # 요청 데이터 파싱
        payload = json.loads(request.body)
        operation = payload.get('operation')
        record_key = payload.get('record_key')
        data = payload.get('data')

        logger.info(f"Customer sync: {operation} {record_key}")

        # 작업 처리
        if operation == 'DELETE':
            # 삭제
            CustomersFull.objects.filter(code=record_key).delete()
            logger.info(f"Deleted customer: {record_key}")

        elif operation in ['INSERT', 'UPDATE']:
            # 삽입 또는 업데이트
            if not data:
                return JsonResponse({'error': 'Data required'}, status=400)

            CustomersFull.objects.update_or_create(
                code=data['code'],
                defaults={
                    'name': data.get('name', ''),
                    'rep': data.get('rep', ''),
                    'tel1': data.get('tel1', ''),
                    'tel3': data.get('tel3', ''),
                    'tel4': data.get('tel4', ''),
                    'enno': data.get('enno', ''),
                    'address1': data.get('address1', ''),
                }
            )
            logger.info(f"{operation} customer: {data['code']} - {data.get('name', '')}")

        else:
            return JsonResponse({'error': 'Invalid operation'}, status=400)

        return JsonResponse({
            'success': True,
            'operation': operation,
            'record_key': record_key
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    except Exception as e:
        logger.error(f"Sync customer error: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def sync_goods(request):
    """
    상품 데이터 동기화 API

    POST /api/sync/goods/
    {
        "operation": "INSERT|UPDATE|DELETE",
        "record_key": "상품코드",
        "data": {
            "code": "...",
            "name": "...",
            ...
        }
    }
    """

    # API 키 검증
    if not verify_api_key(request):
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    try:
        # 요청 데이터 파싱
        payload = json.loads(request.body)
        operation = payload.get('operation')
        record_key = payload.get('record_key')
        data = payload.get('data')

        logger.info(f"Goods sync: {operation} {record_key}")

        # 작업 처리
        if operation == 'DELETE':
            # 삭제
            Goods.objects.filter(code=record_key).delete()
            logger.info(f"Deleted goods: {record_key}")

        elif operation in ['INSERT', 'UPDATE']:
            # 삽입 또는 업데이트
            if not data:
                return JsonResponse({'error': 'Data required'}, status=400)

            Goods.objects.update_or_create(
                code=data['code'],
                defaults={
                    'name': data.get('name', ''),
                    'bun1': data.get('bun1', ''),
                    'jaego': data.get('jaego', 0),
                    'fixp': data.get('fixp', 0),
                }
            )
            logger.info(f"{operation} goods: {data['code']} - {data.get('name', '')}")

        else:
            return JsonResponse({'error': 'Invalid operation'}, status=400)

        return JsonResponse({
            'success': True,
            'operation': operation,
            'record_key': record_key
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    except Exception as e:
        logger.error(f"Sync goods error: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def sync_status(request):
    """
    동기화 상태 확인 API

    GET /api/sync/status/
    """

    # API 키 검증
    if not verify_api_key(request):
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    try:
        customer_count = CustomersFull.objects.count()
        goods_count = Goods.objects.count()

        return JsonResponse({
            'success': True,
            'customers': customer_count,
            'goods': goods_count,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Sync status error: {e}")
        return JsonResponse({'error': str(e)}, status=500)


from datetime import datetime
