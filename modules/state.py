"""
LangGraph 상태 정의
챗봇의 상태 관리
"""

from typing import TypedDict, List, Optional
from langgraph.graph import MessagesState
from langchain_core.messages import BaseMessage


class RecyclingState(MessagesState):
    """재활용 챗봇의 상태"""
    # 현재 입력
    user_input: str
    
    # 분석 결과
    is_recycling_query: bool
    current_region: Optional[str]
    
    # 대화 맥락
    conversation_history: List[BaseMessage]
    
    # 최종 결과
    final_answer: Optional[str]
    
    # 대화 트래킹
    casual_count: int
    total_turns: int
