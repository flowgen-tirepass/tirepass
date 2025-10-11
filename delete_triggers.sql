/**
 * ERP 트리거 완전 삭제 스크립트
 *
 * 경고: 비활성화 후 ERP가 정상 작동하는지 확인한 후 실행하세요!
 *
 * 실행 방법:
 *   1. 명령 프롬프트 관리자 권한 실행
 *   2. cd "C:\Program Files (x86)\Firebird\Firebird_2_5\bin"
 *   3. isql -user SYSDBA -password masterkey "C:\Program Files\PsimCarS\Data\ITIRE.GDB" -i "C:\Users\jmyang\Dropbox\1.0_tirepass\delete_triggers.sql"
 */

/* 트리거 삭제 */
DROP TRIGGER TRG_CUSTOMS_AI;
DROP TRIGGER TRG_CUSTOMS_AU;
DROP TRIGGER TRG_CUSTOMS_AD;
DROP TRIGGER TRG_GOODS_AI;
DROP TRIGGER TRG_GOODS_AU;
DROP TRIGGER TRG_GOODS_AD;

/* SYNC_LOG 테이블 삭제 */
DROP TABLE SYNC_LOG;

COMMIT;

/* 삭제 확인 */
SELECT 'Cleanup completed successfully' AS RESULT FROM RDB$DATABASE;
