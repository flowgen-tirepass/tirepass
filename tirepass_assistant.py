#!/usr/bin/env python3
"""
TirePASS AI Assistant (Prototype v1.0)

사용자(비기술적) ↔ AI 어시스턴트 ↔ Claude Code(기술적)

사용법:
    python tirepass_assistant.py

기능:
- 자연어 요청 분석
- 불명확한 부분 질문
- 구조화된 기술 명세 생성
- Claude Code 실행 가능한 명령 생성
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Anthropic API 사용 (Claude)
try:
    import anthropic
except ImportError:
    print("[오류] anthropic 패키지가 설치되지 않았습니다.")
    print("다음 명령으로 설치하세요:")
    print("  pip install anthropic")
    sys.exit(1)


class TirePassAssistant:
    """TirePASS AI 어시스턴트"""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.system_info_path = self.project_root / "SYSTEM_INFO.md"
        self.context_path = self.project_root / ".claude" / "project-context.md"
        self.conversation_history = []

        # Claude API 클라이언트
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            print("[경고] ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다.")
            print("Claude API를 사용하려면 API 키가 필요합니다.")
            print()
            api_key = input("API 키를 입력하세요 (Enter로 건너뛰기): ").strip()
            if api_key:
                os.environ["ANTHROPIC_API_KEY"] = api_key
            else:
                print("데모 모드로 실행합니다 (실제 API 호출 없음)")
                self.demo_mode = True
                return

        self.client = anthropic.Anthropic(api_key=api_key)
        self.demo_mode = False

        # 시스템 컨텍스트 로드
        self.system_context = self._load_system_context()

    def _load_system_context(self):
        """시스템 정보 및 프로젝트 컨텍스트 로드"""
        context = "TirePASS 프로젝트 컨텍스트:\n\n"

        # SYSTEM_INFO.md 로드
        if self.system_info_path.exists():
            context += "## 시스템 정보 (요약)\n"
            with open(self.system_info_path, 'r', encoding='utf-8') as f:
                # 전체 읽기는 너무 길 수 있으므로 처음 100줄만
                lines = f.readlines()[:100]
                context += "".join(lines)
                if len(lines) >= 100:
                    context += "\n... (전체 문서는 SYSTEM_INFO.md 참조)\n"
            context += "\n"

        # 프로젝트 컨텍스트 로드
        if self.context_path.exists():
            context += "## 프로젝트 컨텍스트\n"
            with open(self.context_path, 'r', encoding='utf-8') as f:
                context += f.read()
            context += "\n"

        return context

    def _create_system_prompt(self):
        """시스템 프롬프트 생성"""
        return f"""당신은 TirePASS 프로젝트의 AI 어시스턴트입니다.

역할:
- 사용자(비기술적)와 Claude Code(기술적) 사이의 중재자
- 사용자의 자연어 요청을 정확한 기술 명세로 변환
- 불명확한 부분을 질문하여 명확히 함
- Claude Code가 즉시 실행 가능한 명령 생성

{self.system_context}

대화 규칙:
1. 사용자 의도를 정확히 파악
2. 불명확한 부분은 질문 (가정하지 말 것)
3. 이미지/스크린샷이 있으면 상세 분석
4. 기술적 명세는 구체적으로 (파일명, 라인 번호, 정확한 수치)
5. 여러 해결 방법이 있으면 선택지 제공
6. 최종 명령은 체크리스트 포함

응답 형식:
1. [요청 분석] - 의도 파악
2. [질문] - 불명확한 부분 (있다면)
3. [기술 명세] - 구조화된 작업 명세
4. [Claude Code 명령] - 실행 가능한 명령

항상 친절하고 명확하게 설명하세요.
"""

    def analyze_request(self, user_input):
        """사용자 요청 분석"""

        if self.demo_mode:
            return self._demo_response(user_input)

        # Claude API 호출
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })

        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                system=self._create_system_prompt(),
                messages=self.conversation_history
            )

            assistant_message = response.content[0].text

            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })

            return assistant_message

        except Exception as e:
            return f"[오류] 오류 발생: {str(e)}"

    def _demo_response(self, user_input):
        """데모 모드 응답 (API 없이)"""
        return f"""[데모 모드 - 실제 분석 없음]

요청: "{user_input}"

[요청 분석]
- 카테고리: (자동 분석 필요 - API 키 설정)
- 대상: (자동 분석 필요)
- 작업: (자동 분석 필요)

[질문]
실제 분석을 위해서는 ANTHROPIC_API_KEY 환경변수를 설정하세요.

[데모 명령]
이것은 데모 응답입니다. 실제 분석을 위해:
1. Claude API 키를 받으세요: https://console.anthropic.com/
2. 환경변수 설정: export ANTHROPIC_API_KEY=your-key
3. 다시 실행하세요

또는 실행 시 API 키를 입력할 수 있습니다.
"""

    def save_conversation(self):
        """대화 히스토리 저장"""
        if not self.conversation_history:
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        history_dir = self.project_root / ".assistant_history"
        history_dir.mkdir(exist_ok=True)

        history_file = history_dir / f"conversation_{timestamp}.json"

        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": timestamp,
                "conversation": self.conversation_history
            }, f, ensure_ascii=False, indent=2)

        print(f"\n[저장] 대화 내역 저장: {history_file}")

    def run_interactive(self):
        """대화형 모드 실행"""
        print("=" * 70)
        print("  TirePASS AI Assistant v1.0")
        print("  사용자 ↔ AI 어시스턴트 ↔ Claude Code")
        print("=" * 70)
        print()
        print("명령:")
        print("  - 자연어로 요청 입력")
        print("  - 'quit' 또는 'exit'로 종료")
        print("  - 'clear'로 대화 히스토리 초기화")
        print("  - 'save'로 대화 저장")
        print()

        if self.demo_mode:
            print("[경고] 데모 모드로 실행 중 (API 키 없음)")
            print()

        while True:
            try:
                # 사용자 입력
                user_input = input("\n[사용자] ").strip()

                if not user_input:
                    continue

                # 명령 처리
                if user_input.lower() in ['quit', 'exit', '종료']:
                    print("\n종료합니다.")
                    self.save_conversation()
                    break

                if user_input.lower() == 'clear':
                    self.conversation_history = []
                    print("[완료] 대화 히스토리 초기화됨")
                    continue

                if user_input.lower() == 'save':
                    self.save_conversation()
                    continue

                # 요청 분석
                print("\n[AI 어시스턴트]")
                print("-" * 70)
                response = self.analyze_request(user_input)
                print(response)
                print("-" * 70)

            except KeyboardInterrupt:
                print("\n\n종료합니다.")
                self.save_conversation()
                break
            except Exception as e:
                print(f"\n[오류] {e}")

    def run_single_request(self, request):
        """단일 요청 처리"""
        print("=" * 70)
        print("  TirePASS AI Assistant")
        print("=" * 70)
        print()
        print(f"[사용자] {request}")
        print()
        print("[AI 어시스턴트]")
        print("-" * 70)
        response = self.analyze_request(request)
        print(response)
        print("-" * 70)
        print()


def main():
    """메인 함수"""
    assistant = TirePassAssistant()

    # 명령행 인자 확인
    if len(sys.argv) > 1:
        # 단일 요청 모드
        request = " ".join(sys.argv[1:])
        assistant.run_single_request(request)
    else:
        # 대화형 모드
        assistant.run_interactive()


if __name__ == "__main__":
    main()
