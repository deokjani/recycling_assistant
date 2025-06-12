"""
리팩토링된 재활용 챗봇 워크플로우
"""

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from .state import RecyclingState
from .nodes import (
    parse_context_node,
    handle_recycling_node,
    handle_casual_node,
    should_handle_recycling
)


def create_recycling_graph():
    """재활용 챗봇 그래프"""
    workflow = StateGraph(RecyclingState)
    
    # 노드 추가
    workflow.add_node("parse", parse_context_node)
    workflow.add_node("recycling", handle_recycling_node)
    workflow.add_node("casual", handle_casual_node)
    
    # 플로우 정의
    workflow.set_entry_point("parse")
    
    # parse -> recycling or casual
    workflow.add_conditional_edges(
        "parse",
        should_handle_recycling,
        {
            "recycling": "recycling",
            "casual": "casual"
        }
    )
    
    # 모든 노드는 END로
    workflow.add_edge("recycling", END)
    workflow.add_edge("casual", END)
    
    return workflow.compile(checkpointer=MemorySaver())


# 그래프 인스턴스
recycling_graph = create_recycling_graph()
