"""
재활용 도우미
"""

import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from dotenv import load_dotenv
from modules import Config, RecyclingAgent

load_dotenv()


def main():
    """메인 실행 함수"""
    try:
        # 설정 검증
        if not Config.validate():
            return
        
        # 에이전트 초기화
        agent = RecyclingAgent()
        
        print("🌱 재활용 도우미 버링이")
        print(f"📍 지원 지역: {', '.join(Config.get_supported_regions())}")
        print("💡 예시: '관악구에서 플라스틱 어떻게 버려요?' 또는 '성동구' 입력 후 품목 질문")
        print("💬 종료: 'exit' 입력\n")
        
        while True:
            # 사용자 입력
            user_input = input("\n👤 You: ").strip()
            
            # 종료 조건
            if user_input.lower() in ['exit', 'quit', '종료']:
                print("\n👋 버링이: 안녕히 가세요! 지구를 위해 함께해주셔서 감사해요!")
                break
            
            if not user_input:
                continue
            
            # 응답 생성
            response = agent.get_response(user_input)
            print(f"\n🤖 버링이: {response}")
            
            # 디버그 정보 (선택적)
            if "--debug" in sys.argv:
                summary = agent.get_conversation_summary()
                print(f"\n[DEBUG] {summary}")
                
    except KeyboardInterrupt:
        print("\n\n👋 프로그램을 종료합니다.")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")


if __name__ == "__main__":
    main()
