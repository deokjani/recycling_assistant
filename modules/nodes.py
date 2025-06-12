"""
LangGraph 노드들 - 간결한 컨트롤러
상태를 받아 도구를 호출하고 다음 상태로 전달
"""

from typing import Dict, Any
from langchain_core.messages import HumanMessage, AIMessage

from .state import RecyclingState
from .tools import (
    check_recycling_intent,
    process_recycling_query,
    generate_casual_response
)


def parse_context_node(state: RecyclingState) -> Dict[str, Any]:
    """Step 1: 대화 맥락 분석"""
    user_input = state.get("user_input", "")
    conversation_history = state.get("conversation_history", [])
    
    # 의도 분석
    intent_result = check_recycling_intent.invoke({
        "user_input": user_input,
        "conversation_history": conversation_history
    })
    
    # 대화 기록 업데이트
    updated_history = conversation_history + [HumanMessage(content=user_input)]
    
    return {
        "is_recycling_query": intent_result.get("is_recycling", False),
        "current_region": intent_result.get("region"),
        "conversation_history": updated_history,
        "total_turns": state.get("total_turns", 0) + 1
    }


def handle_recycling_node(state: RecyclingState) -> Dict[str, Any]:
    """Step 2A: 재활용 질문 처리"""
    user_input = state.get("user_input", "")
    current_region = state.get("current_region")
    conversation_history = state.get("conversation_history", [])
    
    # 재활용 처리
    result = process_recycling_query.invoke({
        "user_input": user_input,
        "current_region": current_region,
        "conversation_history": conversation_history
    })
    
    # 대화 기록 업데이트
    answer = result["answer"]
    updated_history = conversation_history + [AIMessage(content=answer)]
    
    return {
        "final_answer": answer,
        "conversation_history": updated_history,
        "casual_count": 0
    }


def handle_casual_node(state: RecyclingState) -> Dict[str, Any]:
    """Step 2B: 일반 대화 처리"""
    user_input = state.get("user_input", "")
    casual_count = state.get("casual_count", 0)
    conversation_history = state.get("conversation_history", [])
    
    # 일반 대화 응답
    response = generate_casual_response.invoke({
        "user_input": user_input,
        "casual_count": casual_count
    })
    
    # 대화 기록 업데이트
    updated_history = conversation_history + [AIMessage(content=response)]
    
    return {
        "final_answer": response,
        "casual_count": casual_count + 1,
        "conversation_history": updated_history
    }


def should_handle_recycling(state: RecyclingState) -> str:
    """라우팅 결정"""
    return "recycling" if state.get("is_recycling_query", False) else "casual"
