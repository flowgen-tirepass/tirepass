# MariaDB 설치 및 설정 가이드

## 1. MariaDB 다운로드 및 설치

### 다운로드
1. MariaDB 공식 사이트 접속: https://mariadb.org/download/
2. 버전 선택: **MariaDB 11.4 LTS** 또는 **MariaDB 12.0** (최신 안정 버전)
3. Operating System: **Windows**
4. Architecture: **x86_64**
5. Package Type: **MSI Package** 선택
6. Download 버튼 클릭

### 설치
1. 다운로드한 MSI 파일 실행
2. 설치 마법사 진행:

#### Step 1: License Agreement
- "I accept the terms in the License Agreement" 체크
- Next 클릭

#### Step 2: Custom Setup
- 기본 설정 그대로 유지
- 설치 경로: `C:\Program Files\MariaDB 12.0\` (또는 11.4)
- Next 클릭

#### Step 3: Database instance
- **중요: 여기서 root 비밀번호 설정**
- Root password: **tirepass**
- Modify password for database user 'root': **tirepass** (확인)
- Use UTF8 as default server's character set: **체크 ✓**
- Enable networking: **체크 ✓**
- TCP port: **3306** (기본값 유지)
- Next 클릭

#### Step 4: 서비스 설정
- Install as service: **체크 ✓**
- Service Name: **MariaDB**
- Enable access from remote machines: **선택 사항** (로컬만 사용하면 체크 해제)
- Next 클릭

#### Step 5: 설치 진행
- Install 버튼 클릭
- 설치 완료 대기

#### Step 6: 설치 완료
- Finish 클릭

---

## 2. 설치 확인

### 명령 프롬프트에서 확인
```cmd
# MariaDB 서비스 상태 확인
sc query MariaDB

# 또는 MySQL 명령어로 접속 테스트
"C:\Program Files\MariaDB 12.0\bin\mysql.exe" -uroot -ptirepass
```

접속 성공하면:
```
Welcome to the MariaDB monitor.  Commands end with ; or \g.
Your MariaDB connection id is ...
```

종료하려면: `exit` 또는 `quit` 입력

---

## 3. 데이터베이스 생성

### 방법 1: 명령 프롬프트에서 직접 실행
```cmd
"C:\Program Files\MariaDB 12.0\bin\mysql.exe" -uroot -ptirepass -e "CREATE DATABASE IF NOT EXISTS itire_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

### 방법 2: MySQL 클라이언트에서 실행
```cmd
# MySQL 클라이언트 접속
"C:\Program Files\MariaDB 12.0\bin\mysql.exe" -uroot -ptirepass

# 데이터베이스 생성
CREATE DATABASE IF NOT EXISTS itire_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 데이터베이스 확인
SHOW DATABASES;

# 종료
exit
```

**결과 확인:**
```
+--------------------+
| Database           |
+--------------------+
| information_schema |
| itire_db           |
| mysql              |
| performance_schema |
| sys                |
+--------------------+
```

---

## 4. 백업 데이터 복원

### 백업 파일 경로 확인
프로젝트에 있는 백업 파일:
- `C:\Users\jmyang\Dropbox\1.0_tirepass\db_dumps\itire_db_dump_20251002_201440.sql`

### 복원 실행
```cmd
cd C:\Users\jmyang\Dropbox\1.0_tirepass

"C:\Program Files\MariaDB 12.0\bin\mysql.exe" -uroot -ptirepass itire_db < db_dumps\itire_db_dump_20251002_201440.sql
```

### 복원 확인
```cmd
# 테이블 목록 확인
"C:\Program Files\MariaDB 12.0\bin\mysql.exe" -uroot -ptirepass itire_db -e "SHOW TABLES;"

# 데이터 개수 확인
"C:\Program Files\MariaDB 12.0\bin\mysql.exe" -uroot -ptirepass itire_db -e "SELECT COUNT(*) as goods_count FROM goods; SELECT COUNT(*) as customers_count FROM customers_simple;"
```

**예상 결과:**
- goods: 6,519개
- customers_simple: 1,756개

---

## 5. Django 연결 확인

### settings.py 확인
`C:\Users\jmyang\Dropbox\1.0_tirepass\itire\settings.py` 파일에서:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'itire_db',
        'USER': 'root',
        'PASSWORD': 'tirepass',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}
```

### Django 마이그레이션 동기화
```cmd
cd C:\Users\jmyang\Dropbox\1.0_tirepass

# 가상환경 활성화 (이미 활성화되어 있을 수 있음)
venv\Scripts\activate

# 마이그레이션 히스토리 동기화 (테이블이 이미 존재하므로 --fake 사용)
python manage.py migrate --fake
```

### Django 슈퍼유저 생성 (기존에 없다면)
```cmd
python manage.py createsuperuser
```
- Username: **admin**
- Email: (선택사항, 엔터로 스킵 가능)
- Password: **admin1234** (또는 원하는 비밀번호)

### Django 서버 실행
```cmd
python manage.py runserver 0.0.0.0:8080
```

### 접속 테스트
- Dashboard: http://localhost:8080/
- Admin: http://localhost:8080/admin/

---

## 6. 문제 해결

### 문제 1: "Access denied for user 'root'@'localhost'"
**원인:** 비밀번호가 틀렸거나 root 계정이 설정되지 않음

**해결:**
1. MariaDB 서비스 중지
   ```cmd
   net stop MariaDB
   ```

2. my.ini 파일 편집 (`C:\Program Files\MariaDB 12.0\data\my.ini`)
   ```ini
   [mysqld]
   skip-grant-tables
   ```

3. MariaDB 서비스 시작
   ```cmd
   net start MariaDB
   ```

4. 비밀번호 재설정
   ```cmd
   "C:\Program Files\MariaDB 12.0\bin\mysql.exe" -uroot
   ```
   ```sql
   USE mysql;
   ALTER USER 'root'@'localhost' IDENTIFIED BY 'tirepass';
   FLUSH PRIVILEGES;
   exit
   ```

5. my.ini에서 `skip-grant-tables` 제거

6. MariaDB 서비스 재시작
   ```cmd
   net stop MariaDB
   net start MariaDB
   ```

### 문제 2: "Can't connect to MySQL server on 'localhost' (10061)"
**원인:** MariaDB 서비스가 실행되지 않음

**해결:**
```cmd
# 서비스 시작
net start MariaDB

# 또는 서비스 관리자에서 수동 시작
services.msc
```

### 문제 3: 한글 깨짐 문제
**원인:** Character set이 utf8mb4가 아님

**해결:**
1. 데이터베이스 Character set 확인
   ```sql
   SHOW CREATE DATABASE itire_db;
   ```

2. 필요시 변경
   ```sql
   ALTER DATABASE itire_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

3. 테이블별 변경 (필요시)
   ```sql
   ALTER TABLE goods CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ALTER TABLE customers_simple CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

---

## 7. 환경 변수 설정 (선택사항)

시스템 환경 변수에 MySQL bin 폴더 추가하면 명령어가 간편해집니다.

### 설정 방법
1. "시스템 속성" → "환경 변수" 열기
2. 시스템 변수에서 `Path` 선택 → 편집
3. 새로 만들기: `C:\Program Files\MariaDB 12.0\bin`
4. 확인 후 새 명령 프롬프트 열기

### 설정 후
```cmd
# 짧은 명령어로 접속 가능
mysql -uroot -ptirepass itire_db
```

---

## 8. 요약: 빠른 설정 체크리스트

- [ ] MariaDB 11.4/12.0 다운로드
- [ ] 설치 시 root 비밀번호: **tirepass** 설정
- [ ] UTF8 character set 체크
- [ ] Port 3306 확인
- [ ] 데이터베이스 생성: `CREATE DATABASE itire_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;`
- [ ] 백업 복원: `mysql -uroot -ptirepass itire_db < db_dumps\itire_db_dump_20251002_201440.sql`
- [ ] Django 마이그레이션: `python manage.py migrate --fake`
- [ ] 슈퍼유저 생성: `python manage.py createsuperuser`
- [ ] 서버 실행: `python manage.py runserver 0.0.0.0:8080`
- [ ] 접속 테스트: http://localhost:8080/

---

## 연락처 및 지원

문제 발생 시:
1. 에러 메시지 전체 복사
2. 실행한 명령어 기록
3. MariaDB 버전 확인: `SELECT VERSION();`
