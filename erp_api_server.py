"""
ERP Firebird 데이터를 제공하는 FastAPI 서버
화성 로컬 PC에서 24시간 실행

실행:
    uvicorn erp_api_server:app --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import fdb
from typing import Optional, List
from pydantic import BaseModel
import os

app = FastAPI(
    title="ERP API Server",
    description="ERP Firebird 데이터 실시간 조회 API",
    version="1.0.0"
)

# CORS 설정 (pythonanywhere에서 접근 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 운영시에는 pythonanywhere 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ERP Firebird 연결 정보
FIREBIRD_CONFIG = {
    'host': 'ITIRE2.iptime.org',
    'database': r'C:\Program Files\PsimCarS\Data\ITIRE.GDB',
    'user': 'SYSDBA',
    'password': 'masterkey',
    'charset': 'WIN1252'  # 한글 Windows 인코딩
}

# API Key (보안용)
API_KEY = os.environ.get('ERP_API_KEY', 'tirepass-erp-secret-2024')


class GoodsResponse(BaseModel):
    """상품 정보 응답 모델"""
    code: str
    name: str
    bun1: Optional[str] = None
    jaego: int = 0
    fixp: int = 0


class CustomerResponse(BaseModel):
    """고객 정보 응답 모델"""
    code: str
    name: str
    rep: Optional[str] = None
    tel1: Optional[str] = None
    tel3: Optional[str] = None
    enno: Optional[str] = None


class OrderResponse(BaseModel):
    """주문 정보 응답 모델"""
    fdate: str  # 날짜
    fno: str  # 전표번호
    io: Optional[str] = None  # 입출고 구분
    cust: Optional[str] = None  # 고객코드
    good: Optional[str] = None  # 상품코드
    qty: float = 0.0  # 수량
    cost: float = 0.0  # 단가
    amou: float = 0.0  # 금액
    goodname: Optional[str] = None  # 상품명


def get_db_connection():
    """ERP Firebird 연결"""
    return fdb.connect(**FIREBIRD_CONFIG)


@app.get("/")
def root():
    """API 서버 상태 확인"""
    return {
        "status": "ok",
        "message": "ERP API Server is running",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    """헬스 체크 (DB 연결 테스트)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM GOODS")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()

        return {
            "status": "healthy",
            "database": "connected",
            "total_goods": count
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }


@app.get("/api/goods/count")
def get_goods_count(api_key: str):
    """상품 총 개수 조회"""
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM GOODS")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()

        return {"count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/goods", response_model=List[GoodsResponse])
def get_goods_list(
    api_key: str,
    offset: int = 0,
    limit: int = 100,
    search: Optional[str] = None
):
    """상품 목록 조회 (페이징)"""
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 쿼리 생성
        if search:
            query = """
                SELECT CODE, NAME, BUN1, JAEGO, FIXP
                FROM GOODS
                WHERE NAME LIKE ? OR CODE LIKE ?
                ORDER BY CODE
                ROWS ? TO ?
            """
            search_pattern = f"%{search}%"
            cursor.execute(query, (search_pattern, search_pattern, offset + 1, offset + limit))
        else:
            query = """
                SELECT CODE, NAME, BUN1, JAEGO, FIXP
                FROM GOODS
                ORDER BY CODE
                ROWS ? TO ?
            """
            cursor.execute(query, (offset + 1, offset + limit))

        goods_list = []
        for row in cursor.fetchall():
            code, name, bun1, jaego, fixp = row
            goods_list.append(GoodsResponse(
                code=code,
                name=name,
                bun1=bun1,
                jaego=int(jaego) if jaego else 0,
                fixp=int(fixp) if fixp else 0
            ))

        cursor.close()
        conn.close()

        return goods_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/goods/{code}", response_model=GoodsResponse)
def get_goods_detail(code: str, api_key: str):
    """특정 상품 상세 조회"""
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT CODE, NAME, BUN1, JAEGO, FIXP
            FROM GOODS
            WHERE CODE = ?
        """
        cursor.execute(query, (code,))
        row = cursor.fetchone()

        if not row:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Product not found")

        code, name, bun1, jaego, fixp = row
        goods = GoodsResponse(
            code=code,
            name=name,
            bun1=bun1,
            jaego=int(jaego) if jaego else 0,
            fixp=int(fixp) if fixp else 0
        )

        cursor.close()
        conn.close()

        return goods
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# 고객(CUSTOMERS) API
# ============================================================

@app.get("/api/customers/count")
def get_customers_count(api_key: str):
    """고객 총 개수 조회"""
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM CUSTOMS")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()

        return {"count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/customers", response_model=List[CustomerResponse])
def get_customers_list(
    api_key: str,
    offset: int = 0,
    limit: int = 100,
    search: Optional[str] = None
):
    """고객 목록 조회 (페이징)"""
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 쿼리 생성
        if search:
            query = """
                SELECT CODE, NAME, REP, TEL1, TEL3, ENNO
                FROM CUSTOMS
                WHERE NAME LIKE ? OR CODE LIKE ?
                ORDER BY CODE
                ROWS ? TO ?
            """
            search_pattern = f"%{search}%"
            cursor.execute(query, (search_pattern, search_pattern, offset + 1, offset + limit))
        else:
            query = """
                SELECT CODE, NAME, REP, TEL1, TEL3, ENNO
                FROM CUSTOMS
                ORDER BY CODE
                ROWS ? TO ?
            """
            cursor.execute(query, (offset + 1, offset + limit))

        customers_list = []
        for row in cursor.fetchall():
            code, name, rep, tel1, tel3, enno = row
            customers_list.append(CustomerResponse(
                code=code if code else "",
                name=name if name else "",
                rep=rep,
                tel1=tel1,
                tel3=tel3,
                enno=enno
            ))

        cursor.close()
        conn.close()

        return customers_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/customers/{code}", response_model=CustomerResponse)
def get_customer_detail(code: str, api_key: str):
    """특정 고객 상세 조회"""
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT CODE, NAME, REP, TEL1, TEL3, ENNO
            FROM CUSTOMS
            WHERE CODE = ?
        """
        cursor.execute(query, (code,))
        row = cursor.fetchone()

        if not row:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Customer not found")

        code, name, rep, tel1, tel3, enno = row
        customer = CustomerResponse(
            code=code if code else "",
            name=name if name else "",
            rep=rep,
            tel1=tel1,
            tel3=tel3,
            enno=enno
        )

        cursor.close()
        conn.close()

        return customer
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# 주문(DATAS) API
# ============================================================

@app.get("/api/orders/count")
def get_orders_count(api_key: str, start_date: Optional[str] = None, end_date: Optional[str] = None):
    """주문 총 개수 조회"""
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if start_date and end_date:
            query = "SELECT COUNT(*) FROM DATAS WHERE FDATE BETWEEN ? AND ?"
            cursor.execute(query, (start_date, end_date))
        else:
            cursor.execute("SELECT COUNT(*) FROM DATAS")

        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()

        return {"count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/orders", response_model=List[OrderResponse])
def get_orders_list(
    api_key: str,
    offset: int = 0,
    limit: int = 100,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    customer_code: Optional[str] = None
):
    """주문 목록 조회 (페이징, 날짜/고객 필터)"""
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 쿼리 생성
        base_query = """
            SELECT FDATE, FNO, IO, CUST, GOOD, QTY, COST, AMOU, GOODNAME
            FROM DATAS
        """

        conditions = []
        params = []

        if start_date and end_date:
            conditions.append("FDATE BETWEEN ? AND ?")
            params.extend([start_date, end_date])

        if customer_code:
            conditions.append("CUST = ?")
            params.append(customer_code)

        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)

        base_query += " ORDER BY FDATE DESC, FNO DESC ROWS ? TO ?"
        params.extend([offset + 1, offset + limit])

        cursor.execute(base_query, params)

        orders_list = []
        for row in cursor.fetchall():
            fdate, fno, io, cust, good, qty, cost, amou, goodname = row
            orders_list.append(OrderResponse(
                fdate=str(fdate) if fdate else "",
                fno=fno if fno else "",
                io=io,
                cust=cust,
                good=good,
                qty=float(qty) if qty else 0.0,
                cost=float(cost) if cost else 0.0,
                amou=float(amou) if amou else 0.0,
                goodname=goodname
            ))

        cursor.close()
        conn.close()

        return orders_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/orders/recent", response_model=List[OrderResponse])
def get_recent_orders(api_key: str, limit: int = 10):
    """최근 주문 조회"""
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT FIRST ? FDATE, FNO, IO, CUST, GOOD, QTY, COST, AMOU, GOODNAME
            FROM DATAS
            ORDER BY FDATE DESC, FNO DESC
        """
        cursor.execute(query, (limit,))

        orders_list = []
        for row in cursor.fetchall():
            fdate, fno, io, cust, good, qty, cost, amou, goodname = row
            orders_list.append(OrderResponse(
                fdate=str(fdate) if fdate else "",
                fno=fno if fno else "",
                io=io,
                cust=cust,
                good=good,
                qty=float(qty) if qty else 0.0,
                cost=float(cost) if cost else 0.0,
                amou=float(amou) if amou else 0.0,
                goodname=goodname
            ))

        cursor.close()
        conn.close()

        return orders_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/orders/customer/{code}", response_model=List[OrderResponse])
def get_customer_orders(code: str, api_key: str, limit: int = 100):
    """특정 고객의 주문 내역 조회"""
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT FIRST ? FDATE, FNO, IO, CUST, GOOD, QTY, COST, AMOU, GOODNAME
            FROM DATAS
            WHERE CUST = ?
            ORDER BY FDATE DESC, FNO DESC
        """
        cursor.execute(query, (limit, code))

        orders_list = []
        for row in cursor.fetchall():
            fdate, fno, io, cust, good, qty, cost, amou, goodname = row
            orders_list.append(OrderResponse(
                fdate=str(fdate) if fdate else "",
                fno=fno if fno else "",
                io=io,
                cust=cust,
                good=good,
                qty=float(qty) if qty else 0.0,
                cost=float(cost) if cost else 0.0,
                amou=float(amou) if amou else 0.0,
                goodname=goodname
            ))

        cursor.close()
        conn.close()

        return orders_list
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("ERP API Server 시작")
    print("=" * 60)
    print(f"ERP Host: {FIREBIRD_CONFIG['host']}")
    print(f"API URL: http://localhost:8000")
    print(f"Docs: http://localhost:8000/docs")
    print("=" * 60)

    uvicorn.run(app, host="0.0.0.0", port=8000)
