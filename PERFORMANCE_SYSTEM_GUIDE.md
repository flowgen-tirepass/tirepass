# 성능표기 시스템 완전 가이드

## 시스템 개요

모바일 상품 카드에 **4개의 성능표기 박스를 2x2 그리드**로 표시합니다.

### 구조
```
┌─────────────┬─────────────┐
│ 승차감: 탁월  │ 핸들링: 탁월  │
├─────────────┼─────────────┤
│ 연비: 우수    │ 소음: 탁월    │
└─────────────┴─────────────┘
```

## 1단계: pythonanywhere MySQL 설정

### Bash Console 접속
```bash
mysql -u tirepass -p tirepass$itire_db
```

### SQL 실행
로컬의 `setup_performance_system.sql` 파일 내용을 복사하여 MySQL에서 실행:

```sql
-- 1. 기존 데이터 모두 삭제
DELETE FROM goods_performance_tags;
DELETE FROM performance_tags;
DELETE FROM performance_categories;

-- 2-4. 테이블 생성, 카테고리/태그 생성 (파일 참조)

-- 5. 피렐리 상품 2개 성능표기 추가
-- ... (파일 참조)
```

### 결과 확인
```sql
-- 성능표기 확인
SELECT
    gpt.goods_code as '상품코드',
    pc.display_name as '카테고리',
    pt.name as '태그'
FROM goods_performance_tags gpt
JOIN performance_tags pt ON gpt.tag_id = pt.id
JOIN performance_categories pc ON pt.category_id = pc.id
ORDER BY gpt.goods_code, pc.`order`;
```

**예상 결과:**
```
+----------+----------+------+
| 상품코드  | 카테고리  | 태그  |
+----------+----------+------+
| P-CP7R-04| 승차감    | 탁월  |
| P-CP7R-04| 핸들링    | 탁월  |
| P-CP7R-04| 연비      | 우수  |
| P-CP7R-04| 소음      | 탁월  |
| P-SCOR-18| 승차감    | 우수  |
| P-SCOR-18| 핸들링    | 우수  |
| P-SCOR-18| 연비      | 양호  |
| P-SCOR-18| 소음      | 우수  |
+----------+----------+------+
```

## 2단계: 로컬 변경사항 Git 커밋

```bash
git add tire_data/templates/mobile/products.html
git add setup_performance_system.sql
git add PERFORMANCE_SYSTEM_GUIDE.md
git commit -m "성능표기 시스템 구현 - 모바일 2x2 그리드

- 성능표기 박스 4개씩 2x2 그리드로 배치
- CSS: flex-wrap → grid (2열 2행)
- 렌더링: 카테고리:값 형식으로 표시
- SQL: 카테고리 4개, 태그 각 3개 (탁월/우수/양호)
- 피렐리 상품 2개(P-CP7R-04, P-SCOR-18) 성능표기 추가

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
git push origin main
```

## 3단계: pythonanywhere 배포

### Bash Console에서
```bash
cd ~/tirepass
git pull origin main
```

### Web 탭에서 Reload
https://www.pythonanywhere.com/user/tirepass/webapps/
→ **Reload** 버튼 클릭

## 4단계: 모바일 화면 확인

https://tirepass.pythonanywhere.com/mobile/products/

### 확인 사항
1. ✅ P-CP7R-04 상품 카드에 성능표기 4개가 2x2 그리드로 표시
2. ✅ P-SCOR-18 상품 카드에 성능표기 4개가 2x2 그리드로 표시
3. ✅ 각 박스: "카테고리: 값" 형식 (예: "승차감: 탁월")
4. ✅ 모바일 반응형 작동

## 5단계: Admin에서 성능표기 관리

### 카테고리 관리
https://tirepass.pythonanywhere.com/admin/tire_data/performancecategory/

- 4개 카테고리: 승차감, 핸들링, 연비, 소음
- order 필드로 표시 순서 조정

### 태그 관리
https://tirepass.pythonanywhere.com/admin/tire_data/performancetag/

- 각 카테고리당 3개 태그: 탁월, 우수, 양호
- order 필드로 표시 순서 조정

### 상품 성능표기 배정
https://tirepass.pythonanywhere.com/admin/tire_data/goodsperformancetag/

**새 상품 추가 방법:**
1. "상품 성능표기 추가+" 클릭
2. 상품코드 입력 (예: K-ENZA-01)
3. 성능표기 선택 (예: 승차감 - 탁월)
4. 저장
5. 같은 상품에 4개의 성능표기 추가 반복

## 브랜드별 추천 성능표기

### 프리미엄 세단용 (예: 피렐리 Cinturato)
- 승차감: 탁월
- 핸들링: 탁월
- 연비: 우수
- 소음: 탁월

### SUV용 (예: 피렐리 Scorpion)
- 승차감: 우수
- 핸들링: 우수
- 연비: 양호
- 소음: 우수

### 경제형 (예: 금호 엔자라)
- 승차감: 우수
- 핸들링: 양호
- 연비: 탁월
- 소음: 우수

### 고성능 (예: 미쉐린 PS4)
- 승차감: 우수
- 핸들링: 탁월
- 연비: 양호
- 소음: 우수

## 문제 해결

### 성능표기가 안 보이는 경우
1. MySQL 데이터 확인
   ```sql
   SELECT * FROM goods_performance_tags WHERE goods_code='P-CP7R-04';
   ```
2. pythonanywhere 웹앱 Reload
3. 브라우저 캐시 삭제 (Ctrl + Shift + R)

### CSS가 적용 안 되는 경우
1. git pull 확인
2. products.html 파일 업데이트 확인
3. 웹앱 Reload 다시 시도

## 완료!

모든 단계를 완료하면:
- ✅ 모바일 상품 카드에 성능표기 4개 2x2 그리드 표시
- ✅ Admin에서 손쉽게 관리
- ✅ 브랜드별, 상품별 맞춤 성능표기
