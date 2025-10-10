"""
광주 ERP 서버에 Firebird 트리거 설치

실행:
    python scripts/install_erp_triggers.py
"""

import fdb

# ERP Firebird 연결 정보
FIREBIRD_CONFIG = {
    'host': 'ITIRE2.iptime.org',
    'database': r'C:\Program Files\PsimCarS\Data\ITIRE.GDB',
    'user': 'SYSDBA',
    'password': 'masterkey',
    'charset': 'NONE'
}


def create_sync_log_table(conn):
    """변경 로그 테이블 생성"""
    cursor = conn.cursor()

    print("=== SYNC_LOG 테이블 생성 ===")

    # 기존 테이블 확인
    cursor.execute("""
        SELECT COUNT(*) FROM RDB$RELATIONS
        WHERE RDB$RELATION_NAME = 'SYNC_LOG'
    """)

    if cursor.fetchone()[0] > 0:
        print("SYNC_LOG 테이블이 이미 존재합니다. 건너뜁니다.")
        cursor.close()
        return

    # 테이블 생성
    cursor.execute("""
        CREATE TABLE SYNC_LOG (
            LOG_ID INTEGER NOT NULL,
            TABLE_NAME VARCHAR(50) NOT NULL,
            OPERATION VARCHAR(10) NOT NULL,
            RECORD_KEY VARCHAR(50) NOT NULL,
            CHANGED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            SYNC_STATUS VARCHAR(20) DEFAULT 'PENDING',
            ERROR_MESSAGE VARCHAR(500),
            RETRY_COUNT INTEGER DEFAULT 0,
            PRIMARY KEY (LOG_ID)
        )
    """)

    # Generator 생성
    try:
        cursor.execute("CREATE GENERATOR GEN_SYNC_LOG_ID")
    except:
        print("Generator가 이미 존재합니다.")

    cursor.execute("SET GENERATOR GEN_SYNC_LOG_ID TO 0")

    # 인덱스 생성
    cursor.execute("CREATE INDEX IDX_SYNC_LOG_STATUS ON SYNC_LOG(SYNC_STATUS)")
    cursor.execute("CREATE INDEX IDX_SYNC_LOG_TABLE ON SYNC_LOG(TABLE_NAME)")
    cursor.execute("CREATE INDEX IDX_SYNC_LOG_CHANGED_AT ON SYNC_LOG(CHANGED_AT)")

    conn.commit()
    cursor.close()

    print("[OK] SYNC_LOG 테이블 생성 완료")


def drop_existing_triggers(conn):
    """기존 트리거 삭제"""
    cursor = conn.cursor()

    print("\n=== 기존 트리거 확인 ===")

    trigger_names = [
        'TRG_CUSTOMS_AI', 'TRG_CUSTOMS_AU', 'TRG_CUSTOMS_AD',
        'TRG_GOODS_AI', 'TRG_GOODS_AU', 'TRG_GOODS_AD'
    ]

    for trigger_name in trigger_names:
        cursor.execute(f"""
            SELECT COUNT(*) FROM RDB$TRIGGERS
            WHERE RDB$TRIGGER_NAME = '{trigger_name}'
        """)

        if cursor.fetchone()[0] > 0:
            print(f"기존 트리거 삭제: {trigger_name}")
            cursor.execute(f"DROP TRIGGER {trigger_name}")

    conn.commit()
    cursor.close()
    print("[OK] 기존 트리거 정리 완료")


def create_triggers(conn):
    """트리거 생성"""
    cursor = conn.cursor()

    print("\n=== 트리거 생성 ===")

    triggers = [
        # CUSTOMS 트리거
        {
            'name': 'TRG_CUSTOMS_AI',
            'sql': """
                CREATE TRIGGER TRG_CUSTOMS_AI FOR CUSTOMS
                ACTIVE AFTER INSERT POSITION 0
                AS
                BEGIN
                    INSERT INTO SYNC_LOG (LOG_ID, TABLE_NAME, OPERATION, RECORD_KEY, CHANGED_AT)
                    VALUES (GEN_ID(GEN_SYNC_LOG_ID, 1), 'CUSTOMS', 'INSERT', NEW.CODE, CURRENT_TIMESTAMP);
                END
            """
        },
        {
            'name': 'TRG_CUSTOMS_AU',
            'sql': """
                CREATE TRIGGER TRG_CUSTOMS_AU FOR CUSTOMS
                ACTIVE AFTER UPDATE POSITION 0
                AS
                BEGIN
                    INSERT INTO SYNC_LOG (LOG_ID, TABLE_NAME, OPERATION, RECORD_KEY, CHANGED_AT)
                    VALUES (GEN_ID(GEN_SYNC_LOG_ID, 1), 'CUSTOMS', 'UPDATE', NEW.CODE, CURRENT_TIMESTAMP);
                END
            """
        },
        {
            'name': 'TRG_CUSTOMS_AD',
            'sql': """
                CREATE TRIGGER TRG_CUSTOMS_AD FOR CUSTOMS
                ACTIVE AFTER DELETE POSITION 0
                AS
                BEGIN
                    INSERT INTO SYNC_LOG (LOG_ID, TABLE_NAME, OPERATION, RECORD_KEY, CHANGED_AT)
                    VALUES (GEN_ID(GEN_SYNC_LOG_ID, 1), 'CUSTOMS', 'DELETE', OLD.CODE, CURRENT_TIMESTAMP);
                END
            """
        },
        # GOODS 트리거
        {
            'name': 'TRG_GOODS_AI',
            'sql': """
                CREATE TRIGGER TRG_GOODS_AI FOR GOODS
                ACTIVE AFTER INSERT POSITION 0
                AS
                BEGIN
                    INSERT INTO SYNC_LOG (LOG_ID, TABLE_NAME, OPERATION, RECORD_KEY, CHANGED_AT)
                    VALUES (GEN_ID(GEN_SYNC_LOG_ID, 1), 'GOODS', 'INSERT', NEW.CODE, CURRENT_TIMESTAMP);
                END
            """
        },
        {
            'name': 'TRG_GOODS_AU',
            'sql': """
                CREATE TRIGGER TRG_GOODS_AU FOR GOODS
                ACTIVE AFTER UPDATE POSITION 0
                AS
                BEGIN
                    INSERT INTO SYNC_LOG (LOG_ID, TABLE_NAME, OPERATION, RECORD_KEY, CHANGED_AT)
                    VALUES (GEN_ID(GEN_SYNC_LOG_ID, 1), 'GOODS', 'UPDATE', NEW.CODE, CURRENT_TIMESTAMP);
                END
            """
        },
        {
            'name': 'TRG_GOODS_AD',
            'sql': """
                CREATE TRIGGER TRG_GOODS_AD FOR GOODS
                ACTIVE AFTER DELETE POSITION 0
                AS
                BEGIN
                    INSERT INTO SYNC_LOG (LOG_ID, TABLE_NAME, OPERATION, RECORD_KEY, CHANGED_AT)
                    VALUES (GEN_ID(GEN_SYNC_LOG_ID, 1), 'GOODS', 'DELETE', OLD.CODE, CURRENT_TIMESTAMP);
                END
            """
        }
    ]

    for trigger in triggers:
        try:
            cursor.execute(trigger['sql'])
            conn.commit()
            print(f"[OK] {trigger['name']} 생성 완료")
        except Exception as e:
            print(f"[FAIL] {trigger['name']} 생성 실패: {e}")

    cursor.close()


def verify_triggers(conn):
    """트리거 확인"""
    cursor = conn.cursor()

    print("\n=== 설치된 트리거 확인 ===")

    cursor.execute("""
        SELECT
            RDB$TRIGGER_NAME,
            RDB$RELATION_NAME,
            RDB$TRIGGER_TYPE,
            RDB$TRIGGER_INACTIVE
        FROM RDB$TRIGGERS
        WHERE RDB$RELATION_NAME IN ('CUSTOMS', 'GOODS')
          AND RDB$SYSTEM_FLAG = 0
        ORDER BY RDB$RELATION_NAME, RDB$TRIGGER_NAME
    """)

    triggers = cursor.fetchall()

    if not triggers:
        print("설치된 트리거가 없습니다!")
        return

    print(f"\n총 {len(triggers)}개의 트리거:")
    for trigger in triggers:
        name = trigger[0].strip()
        table = trigger[1].strip()
        inactive = trigger[3]
        status = "비활성" if inactive else "활성"
        print(f"  - {name} ({table}) - {status}")

    cursor.close()


def test_trigger(conn):
    """트리거 테스트"""
    cursor = conn.cursor()

    print("\n=== 트리거 테스트 ===")

    # 테스트 데이터 업데이트
    try:
        cursor.execute("""
            UPDATE CUSTOMS
            SET NAME = NAME
            WHERE CODE = (SELECT FIRST 1 CODE FROM CUSTOMS)
        """)
        conn.commit()

        # SYNC_LOG 확인
        cursor.execute("SELECT COUNT(*) FROM SYNC_LOG WHERE TABLE_NAME = 'CUSTOMS'")
        count = cursor.fetchone()[0]

        if count > 0:
            print(f"[OK] 트리거 작동 확인: SYNC_LOG에 {count}개 레코드")

            # 최근 로그 확인
            cursor.execute("""
                SELECT FIRST 1 TABLE_NAME, OPERATION, RECORD_KEY, CHANGED_AT
                FROM SYNC_LOG
                ORDER BY LOG_ID DESC
            """)
            log = cursor.fetchone()
            print(f"  최근 로그: {log[0]} {log[1]} {log[2]} {log[3]}")
        else:
            print("[FAIL] 트리거가 작동하지 않습니다!")

    except Exception as e:
        print(f"테스트 중 오류: {e}")

    cursor.close()


def main():
    """메인 실행"""
    print("=" * 60)
    print("광주 ERP 서버 - Firebird 트리거 설치")
    print("=" * 60)
    print(f"\n연결 정보:")
    print(f"  호스트: {FIREBIRD_CONFIG['host']}")
    print(f"  데이터베이스: {FIREBIRD_CONFIG['database']}")
    print(f"  사용자: {FIREBIRD_CONFIG['user']}")

    try:
        print("\n연결 중...")
        conn = fdb.connect(**FIREBIRD_CONFIG)
        print("[OK] 연결 성공\n")

        # 1. SYNC_LOG 테이블 생성
        create_sync_log_table(conn)

        # 2. 기존 트리거 삭제
        drop_existing_triggers(conn)

        # 3. 새 트리거 생성
        create_triggers(conn)

        # 4. 트리거 확인
        verify_triggers(conn)

        # 5. 트리거 테스트
        test_trigger(conn)

        conn.close()

        print("\n" + "=" * 60)
        print("트리거 설치 완료!")
        print("=" * 60)
        print("\n다음 단계:")
        print("1. 동기화 데몬 설치: scripts/erp_sync_daemon.py")
        print("2. PythonAnywhere 배포: git pull")
        print("3. 실시간 동기화 테스트")

    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
