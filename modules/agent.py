"""
리팩토링된 재활용 챗봇 에이전트
메모리 기반 대화 관리
"""

from typing import Dict, Any, List
import uuid

from .graph import recycling_graph
from .state import RecyclingState


class RecyclingAgent:
    """개선된 버링이 재활용 챗봇"""
    
    def __init__(self):
        """에이전트 초기화"""
        self.graph = recycling_graph
        self.session_id = str(uuid.uuid4())
        self.reset()
    
    def reset(self):
        """대화 상태 초기화"""
        self.state = {
            "conversation_history": [],
            "casual_count": 0,
            "total_turns": 0
        }
    
    def get_response(self, user_input: str) -> str:
        """사용자 입력 처리 및 응답 생성"""
        
        # 현재 상태에 입력 추가
        current_state = {
            **self.state,
            "user_input": user_input
        }
        
        # 그래프 실행
        config = {"configurable": {"thread_id": self.session_id}}
        
        try:
            # 그래프 실행
            result = self.graph.invoke(current_state, config)
            
            # 상태 업데이트
            self._update_state(result)
            
            # 응답 반환 (대화 기록은 노드에서 이미 처리됨)
            answer = result.get("final_answer", "무엇을 도와드릴까요?")
            return answer
            
        except Exception as e:
            return f"처리 중 오류가 발생했습니다: {str(e)}"
    
    def _update_state(self, result: Dict[str, Any]):
        """내부 상태 업데이트"""
        # 대화 기록
        if "conversation_history" in result:
            self.state["conversation_history"] = result["conversation_history"]
        
        # 카운터
        if "casual_count" in result:
            self.state["casual_count"] = result["casual_count"]
        if "total_turns" in result:
            self.state["total_turns"] = result["total_turns"]
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """대화 요약 정보 반환"""
        return {
            "total_turns": self.state["total_turns"],
            "casual_count": self.state["casual_count"],
            "history_length": len(self.state["conversation_history"])
        }
