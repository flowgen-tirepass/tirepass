# 🚨 긴급: ERP 서버 트리거 롤백 가이드

## 📞 광주 ERP 담당자님께 즉시 전달

### 상황 설명
- 오늘 설치한 Firebird 트리거가 ERP 업무를 방해하고 있을 가능성이 높습니다
- 트리거를 즉시 비활성화하거나 삭제해야 합니다
- **트리거를 제거해도 기존 ERP 데이터는 전혀 손상되지 않습니다**

### ⚡ 긴급 조치 (5분 소요)

#### 1단계: Firebird isql 접속

명령 프롬프트를 **관리자 권한**으로 실행 후:

```cmd
cd "C:\Program Files (x86)\Firebird\Firebird_2_5\bin"
isql -user SYSDBA -password masterkey "C:\Program Files\PsimCarS\Data\ITIRE.GDB"
```

#### 2단계: 트리거 즉시 비활성화 (안전)

isql 프롬프트에서 다음을 **복사해서 붙여넣기**:

```sql
ALTER TRIGGER TRG_CUSTOMS_AI INACTIVE;
ALTER TRIGGER TRG_CUSTOMS_AU INACTIVE;
ALTER TRIGGER TRG_CUSTOMS_AD INACTIVE;
ALTER TRIGGER TRG_GOODS_AI INACTIVE;
ALTER TRIGGER TRG_GOODS_AU INACTIVE;
ALTER TRIGGER TRG_GOODS_AD INACTIVE;
COMMIT;
```

**결과 확인:**
- "Statement executed successfully" 메시지가 6번 나타나야 함
- 에러 발생 시 아래 "문제 해결" 참조

#### 3단계: ERP 정상 작동 확인

isql에서:

```sql
-- 테스트 쿼리 (데이터 변경 없음)
SELECT FIRST 1 CODE, NAME FROM CUSTOMS;
```

**정상이면**: 데이터가 조회됨

#### 4단계: ERP 프로그램 테스트

- ERP 프로그램에서 고객 정보 수정 시도
- 상품 재고 변경 시도
- **정상 작동하면 트리거 비활성화 성공**

---

## 🔧 문제 해결

### 에러 1: "object TRG_CUSTOMS_AI is in use"

```sql
-- 현재 연결된 모든 사용자 확인
SELECT MON$USER, MON$REMOTE_ADDRESS, MON$ATTACHMENT_ID
FROM MON$ATTACHMENTS
WHERE MON$ATTACHMENT_ID <> CURRENT_CONNECTION;

-- 필요 시 관리자가 모든 사용자 접속 종료 후 재시도
```

### 에러 2: "trigger not found"

```sql
-- 트리거 목록 확인
SELECT RDB$TRIGGER_NAME, RDB$TRIGGER_INACTIVE
FROM RDB$TRIGGERS
WHERE RDB$RELATION_NAME IN ('CUSTOMS', 'GOODS')
  AND RDB$SYSTEM_FLAG = 0;
```

---

## 🗑️ 완전 삭제 (비활성화 후 실행, 선택사항)

트리거를 영구적으로 제거하려면:

```sql
-- isql에서 실행
DROP TRIGGER TRG_CUSTOMS_AI;
DROP TRIGGER TRG_CUSTOMS_AU;
DROP TRIGGER TRG_CUSTOMS_AD;
DROP TRIGGER TRG_GOODS_AI;
DROP TRIGGER TRG_GOODS_AU;
DROP TRIGGER TRG_GOODS_AD;
DROP TABLE SYNC_LOG;
COMMIT;
EXIT;
```

---

## 📋 확인 체크리스트

비활성화 후 확인할 사항:

- [ ] isql에서 "Statement executed successfully" 확인
- [ ] ERP 프로그램에서 고객 정보 수정 가능
- [ ] ERP 프로그램에서 상품 재고 변경 가능
- [ ] 주문 처리 정상 작동
- [ ] 팀뷰어 재접속 허용

---

## 📞 긴급 연락

조치 후 결과를 알려주세요:
- ✅ 트리거 비활성화 성공
- ✅ ERP 정상 작동 확인
- ❌ 에러 발생 (에러 메시지 전달)

---

## 🔍 로그 확인 (선택사항)

문제 원인 파악을 위해:

```cmd
notepad "C:\Program Files (x86)\Firebird\Firebird_2_5\firebird.log"
```

**찾아야 할 키워드:**
- `SYNC_LOG`
- `TRG_CUSTOMS`
- `TRG_GOODS`
- `error`
- `exception`

해당 내용을 캡처하거나 복사해주세요.

---

## ⚠️ 중요 사항

1. **데이터 손실 없음**: 트리거 삭제해도 CUSTOMS, GOODS 테이블 데이터는 안전
2. **ERP 프로그램 정상**: 트리거는 별도 기능이므로 삭제해도 ERP는 정상 작동
3. **SYNC_LOG 테이블**: 실시간 동기화용으로 만든 테이블 (ERP 업무와 무관)

---

## 📱 즉시 실행 요청

광주 ERP 담당자님께:

1. 팀뷰어 로그인
2. 위 "긴급 조치" 1~4단계 실행
3. 결과 보고

**예상 소요 시간: 5분**
