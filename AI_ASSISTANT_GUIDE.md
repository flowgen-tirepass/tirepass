# TirePASS AI 어시스턴트 사용 가이드

> 버전: 1.0 (Prototype)
> 작성일: 2025-10-16

## 목차
1. [소개](#소개)
2. [설치](#설치)
3. [사용법](#사용법)
4. [예제](#예제)
5. [문제 해결](#문제-해결)

---

## 소개

### 무엇인가요?

TirePASS AI 어시스턴트는 사용자와 Claude Code 사이의 **중재자** 역할을 하는 도구입니다.

```
[사용자] ─자연어─> [AI 어시스턴트] ─기술명세─> [Claude Code]
                            ↓
                        불명확한 부분 질문
                        구체적 명세 생성
                        실행 가능한 명령 생성
```

### 왜 필요한가요?

**문제**: 사용자의 자연어 요청이 종종 기술적으로 오해됨

**예시**:
- 사용자: "로고 크게 만들어줘"
- Claude Code 해석 1: CSS transform 적용 (틀림)
- Claude Code 해석 2: 이미지를 너무 크게 (틀림)
- ... 5회 반복 ...

**해결**: AI 어시스턴트가 먼저 명확히 함

- AI: "이미지 파일 자체를 수정할까요, CSS로 표시만 조정할까요?"
- AI: "다른 로고들(Kumho, Hankook)과 비교한 스크린샷이 있나요?"
- → 정확한 명세 생성 → Claude Code 1번에 완료

---

## 설치

### 1. Python 패키지 설치

```bash
pip install anthropic
```

또는 requirements.txt가 있다면:

```bash
pip install -r requirements.txt
```

### 2. Claude API 키 받기

1. https://console.anthropic.com/ 접속
2. 계정 생성/로그인
3. API Keys 메뉴에서 키 생성
4. 키 복사

### 3. API 키 설정

**방법 1: 환경변수 (권장)**

Windows:
```cmd
setx ANTHROPIC_API_KEY "your-api-key-here"
```

macOS/Linux:
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
# ~/.bashrc 또는 ~/.zshrc에 추가하면 영구 적용
```

**방법 2: 실행 시 입력**

API 키가 설정되지 않았다면 실행 시 입력 프롬프트가 나타납니다.

### 4. 실행 테스트

```bash
python tirepass_assistant.py
```

정상 실행되면 다음과 같이 표시됩니다:

```
======================================================================
  TirePASS AI Assistant v1.0
  사용자 ↔ AI 어시스턴트 ↔ Claude Code
======================================================================

명령:
  - 자연어로 요청 입력
  - 'quit' 또는 'exit'로 종료
  - 'clear'로 대화 히스토리 초기화
  - 'save'로 대화 저장

🙂 사용자:
```

---

## 사용법

### 모드 1: 대화형 모드 (권장)

```bash
python tirepass_assistant.py
```

대화형으로 여러 요청을 연속으로 처리할 수 있습니다.

**예시 세션**:
```
🙂 사용자: 굳이어 로고 크기 조정해줘

🤖 AI 어시스턴트:
----------------------------------------------------------------------
[요청 분석]
- 카테고리: UI/디자인 변경
- 대상: Goodyear 브랜드 로고
- 작업: 크기 조정

[질문]
1. 이미지 파일 자체를 리사이즈할까요? (영구적)
   또는 CSS로 표시 크기만 조정할까요? (임시적)

2. 어떤 크기로 조정할까요?
   a) 다른 브랜드 로고들과 동일하게
   b) 특정 크기로 지정
   c) 스크린샷 기반 분석

스크린샷이 있다면 정확한 분석이 가능합니다.
----------------------------------------------------------------------

🙂 사용자: 이미지 파일 수정, 다른 로고들만큼

🤖 AI 어시스턴트:
----------------------------------------------------------------------
[기술 명세]
파일: tire_data/static/mobile/img/brands/goodyear.png

작업 단계:
1. 다른 브랜드 로고 크기 확인
   - kumho.png
   - hankook.png
   - nexen.png

2. 평균 크기 계산 또는 대표 크기 선택

3. Goodyear 로고 리사이즈
   - Pillow 라이브러리 사용
   - LANCZOS 리샘플링
   - 원본 백업 (goodyear_backup.png)

... (상세 명령)
----------------------------------------------------------------------

🙂 사용자: quit
```

### 모드 2: 단일 요청 모드

한 번에 하나의 요청만 처리:

```bash
python tirepass_assistant.py "굳이어 로고 크기 조정해줘"
```

명령행 인자로 전달하면 즉시 분석하고 종료합니다.

### 명령

대화형 모드에서 사용 가능한 명령:

| 명령 | 설명 |
|------|------|
| `quit`, `exit`, `종료` | 프로그램 종료 (대화 자동 저장) |
| `clear` | 대화 히스토리 초기화 |
| `save` | 현재 대화 수동 저장 |

---

## 예제

### 예제 1: 로고 크기 조정 (실제 사례)

**사용자 요청**:
```
굳이어 로고를 다른 로고들만큼 크게 만들어줘
```

**AI 응답**:
```
[요청 분석]
- 카테고리: UI/디자인 변경
- 대상: Goodyear 브랜드 로고
- 작업: 크기 조정
- 기준: 다른 브랜드 로고들

[질문]
1. 이미지 파일을 직접 수정할까요, CSS로 조정할까요?
2. 참고할 다른 브랜드 로고가 있나요? (Kumho, Hankook, Nexen 등)
3. 스크린샷이나 현재 상태 이미지가 있나요?

[추천]
이미지 파일 자체를 리사이즈하는 것을 권장합니다.
다른 로고들과 일관된 크기를 유지할 수 있습니다.
```

**사용자 추가 정보**:
```
이미지 파일 수정해줘. Kumho 로고 크기 기준으로.
```

**AI 최종 명령**:
```
[Claude Code 실행 명령]

다음을 Claude Code에 전달하세요:

---
작업: Goodyear 로고 리사이즈
파일: tire_data/static/mobile/img/brands/goodyear.png
기준: Kumho 로고 (tire_data/static/mobile/img/brands/kumho.png)

단계:
1. Kumho 로고 크기 확인
   from PIL import Image
   img = Image.open('tire_data/static/mobile/img/brands/kumho.png')
   target_size = img.size  # 예: (160, 61)

2. Goodyear 로고 백업
   import shutil
   shutil.copy('goodyear.png', 'goodyear_backup.png')

3. Goodyear 로고 리사이즈
   img = Image.open('tire_data/static/mobile/img/brands/goodyear.png')
   img_resized = img.resize(target_size, Image.LANCZOS)
   img_resized.save('tire_data/static/mobile/img/brands/goodyear.png')

4. Git 커밋
   git add tire_data/static/mobile/img/brands/goodyear.png
   git commit -m "Goodyear 로고 크기 조정 (Kumho 기준)"

5. PythonAnywhere 배포
   - SSH 접속
   - git pull
   - collectstatic
   - Reload

체크리스트:
- [ ] Kumho 로고 크기 확인됨
- [ ] Goodyear 원본 백업됨
- [ ] 리사이즈 완료
- [ ] Git 커밋 완료
- [ ] PythonAnywhere 배포 완료
- [ ] 브라우저 확인 (Ctrl+F5)

롤백 방법:
원본: goodyear_backup.png
---

위 명령을 복사하여 Claude Code에 붙여넣으세요.
```

### 예제 2: 새 기능 추가

**사용자 요청**:
```
관리자 페이지에서 고객 클릭하면 그 고객의 최근 주문 내역 보고 싶어
```

**AI 응답**:
```
[요청 분석]
- 카테고리: 기능 추가
- 대상: 관리자 고객 페이지
- 기능: 주문 내역 조회

[질문]
1. 어떻게 표시할까요?
   a) 같은 페이지에 테이블로
   b) 팝업/모달로
   c) 별도 페이지로 이동

2. 몇 개까지 표시할까요?
   a) 최근 5개
   b) 최근 10개
   c) 전체 (페이지네이션)

[추천]
Django Admin의 Inline 기능을 사용하여
고객 상세 페이지에 주문 테이블을 바로 표시하는 것을 권장합니다.
```

**사용자 추가 정보**:
```
같은 페이지에 테이블로, 최근 10개
```

**AI 최종 명령**:
```
[Claude Code 실행 명령]

파일: tire_data/admin.py

작업:
1. OrderInline 클래스 추가
2. CustomersSimpleAdmin에 inlines 설정

코드:
```python
from django.contrib import admin
from .models import Order, CustomersSimple

class OrderInline(admin.TabularInline):
    model = Order
    extra = 0
    max_num = 10
    can_delete = False
    fields = ['order_number', 'order_date', 'final_amount', 'order_status']
    readonly_fields = ['order_number', 'order_date', 'final_amount', 'order_status']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.order_by('-order_date')[:10]

@admin.register(CustomersSimple)
class CustomersSimpleAdmin(admin.ModelAdmin):
    inlines = [OrderInline]
    # ... 기존 설정 유지
```

테스트:
1. 로컬에서 runserver
2. /admin/tire_data/customerssimple/ 접속
3. 고객 한 명 클릭
4. 하단에 "주문 내역" 테이블 확인

체크리스트:
- [ ] OrderInline 추가
- [ ] CustomersSimpleAdmin 수정
- [ ] 로컬 테스트 완료
- [ ] PythonAnywhere 배포
---
```

### 예제 3: 버그 수정

**사용자 요청**:
```
상품 페이지 에러 나는데 AttributeError: 'NoneType' object has no attribute 'name'
```

**AI 응답**:
```
[요청 분석]
- 카테고리: 버그 수정
- 에러: AttributeError (NoneType)
- 위치: 추정 필요

[질문]
1. 정확한 에러 메시지를 보여주실 수 있나요?
   (파일명, 라인 번호 포함)

2. 언제 발생하나요?
   - 모든 상품?
   - 특정 상품만?

3. 최근에 관련 코드를 수정하셨나요?

4. PythonAnywhere 에러 로그 스크린샷이 있나요?

[다음 단계]
정확한 정보를 주시면 구체적인 수정 방법을 제안하겠습니다.
```

---

## 대화 히스토리

### 저장 위치

대화 내용은 자동으로 저장됩니다:

```
C:\Users\jmyang\Dropbox\1.0_tirepass\.assistant_history\
├── conversation_20251016_143022.json
├── conversation_20251016_151545.json
└── ...
```

### 히스토리 활용

저장된 대화는 다음에 사용할 수 있습니다:
- 이전 요청 참고
- 패턴 분석
- 학습 데이터

---

## 문제 해결

### API 키 관련

**문제**: "ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다"

**해결**:
1. API 키 받기: https://console.anthropic.com/
2. 환경변수 설정:
   ```
   setx ANTHROPIC_API_KEY "sk-ant-..."
   ```
3. 터미널 재시작

### 패키지 없음

**문제**: "ModuleNotFoundError: No module named 'anthropic'"

**해결**:
```bash
pip install anthropic
```

### 데모 모드

API 키 없이도 데모 모드로 실행 가능합니다.
실제 분석은 안 되지만 프로그램 흐름을 이해할 수 있습니다.

### 응답 느림

Claude API 호출은 몇 초 걸릴 수 있습니다.
네트워크 상태에 따라 다릅니다.

---

## 향후 개발

### 계획된 기능

- [ ] 이미지/스크린샷 분석 (Claude Vision API)
- [ ] 웹 인터페이스 (Flask)
- [ ] 대화 히스토리 학습
- [ ] 프로젝트별 패턴 인식
- [ ] Claude Code 직접 통합

### 피드백

개선 아이디어나 버그 제보:
- GitHub Issues: https://github.com/flowgen-tirepass/tirepass/issues
- 또는 직접 수정 후 Pull Request

---

## 팁

### 1. 구체적으로 요청하기

❌ 나쁜 예:
```
로고 고쳐줘
```

✅ 좋은 예:
```
Goodyear 로고를 다른 브랜드 로고들(Kumho, Hankook)만큼 크기로 조정해줘.
이미지 파일 자체를 수정하고 싶어.
```

### 2. 스크린샷 활용 (향후 지원)

시각적 문제는 스크린샷으로 설명하는 것이 가장 정확합니다.
현재는 지원하지 않지만 곧 추가될 예정입니다.

### 3. 대화 이어가기

대화형 모드에서는 이전 컨텍스트가 유지됩니다.
추가 질문이나 수정 요청을 자연스럽게 이어갈 수 있습니다.

### 4. 불확실하면 질문하기

AI가 질문하면 정확히 답변하세요.
추측으로 작업하는 것보다 명확히 하는 것이 시간 절약입니다.

---

**문서 버전**: 1.0
**작성일**: 2025-10-16
**상태**: 프로토타입 완료
