"""
재활용 챗봇 도구들 - 간결 버전
"""

from typing import List, Optional, Dict, Any
from langchain_core.tools import tool
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from pydantic import BaseModel, Field

from .config import Config
from .vector_store import VectorStoreManager
from .prompts import (
    ANSWER_PROMPT,
    SYSTEM_PROMPT,
    NO_DOCUMENTS_MESSAGE,
    ERROR_MESSAGES,
    INTENT_ANALYSIS_PROMPT
)


# 전역 인스턴스
_vector_store_manager = None

def get_vector_store_manager():
    global _vector_store_manager
    if not _vector_store_manager:
        _vector_store_manager = VectorStoreManager()
    return _vector_store_manager


# 분석 결과 스키마
class IntentAnalysis(BaseModel):
    is_recycling: bool = Field(description="재활용 관련 질문 여부")
    region: Optional[str] = Field(description="언급된 지역")


@tool
def check_recycling_intent(user_input: str, conversation_history: List[Any] = []) -> Dict[str, Any]:
    """LLM으로 재활용 의도와 지역 파악"""
    llm = Config.get_llm("recycling")
    parser = JsonOutputParser(pydantic_object=IntentAnalysis)
    
    # 최근 대화 맥락 구성
    context = ""
    if conversation_history:
        recent = conversation_history[-4:]  # 최근 2쌍의 대화
        if recent:
            context = "최근 대화:\n"
            for msg in recent:
                if isinstance(msg, HumanMessage):
                    context += f"사용자: {msg.content}\n"
                elif isinstance(msg, AIMessage):
                    context += f"AI: {msg.content}\n"
    
    try:
        result = llm.invoke(
            INTENT_ANALYSIS_PROMPT.format_prompt(
                regions=", ".join(Config.get_supported_regions()),
                context=context if context else "(대화 시작)",
                input=user_input,
                format_instructions=parser.get_format_instructions()
            ).to_messages()
        )
        return parser.parse(result.content)
    except:
        return {"is_recycling": False, "region": None}


@tool
def process_recycling_query(user_input: str, current_region: Optional[str], conversation_history: List[Any] = []) -> Dict[str, Any]:
    """재활용 질문 통합 처리"""
    # 1. 지역 확인 (현재 입력 또는 최근 대화에서)
    if not current_region:
        # 현재 입력에서 찾기
        for region in Config.get_supported_regions():
            if region in user_input:
                current_region = region
                break
        
        # 없으면 최근 대화에서 찾기
        if not current_region and conversation_history:
            for msg in reversed(conversation_history[-4:]):
                if isinstance(msg, HumanMessage):
                    for region in Config.get_supported_regions():
                        if region in msg.content:
                            current_region = region
                            break
                if current_region:
                    break
    
    # 2. 지역 유효성 검증 (지역이 있는 경우)
    if current_region and not Config.get_region_code(current_region):
        # 잘못된 지역명이 언급된 경우
        supported = Config.get_supported_regions()
        return {
            "answer": f"'{current_region}'은(는) 지원하지 않는 지역입니다.\n\n현재 지원하는 지역은 {', '.join(supported)}입니다.\n어느 지역의 분리배출 방법이 궁금하신가요?"
        }
    
    # 3. 지역이 없는 경우
    if not current_region:
        supported = Config.get_supported_regions()
        return {
            "answer": f"재활용 방법을 알려드릴게요!\n\n현재 지원하는 지역은 {', '.join(supported)}입니다.\n어느 지역의 분리배출 방법이 궁금하신가요?"
        }
    
    # 4. 유효한 지역이 있는 경우 - 재활용 정보 검색 및 답변
    try:
        vector_store = get_vector_store_manager().load_vector_store(current_region)
        if not vector_store:
            return {
                "answer": f"{current_region} 데이터를 찾을 수 없습니다."
            }
        
        # 검색 쿼리가 없으면 물어보기
        if not user_input.strip():
            return {
                "answer": f"{current_region}에서 어떤 품목의 재활용 방법이 궁금하신가요?"
            }
        
        # 유사 문서 검색
        docs = vector_store.similarity_search(user_input, k=3)
        if not docs:
            return {
                "answer": NO_DOCUMENTS_MESSAGE
            }
        
        # 중복 제거
        unique_docs = []
        seen_contents = set()
        for doc in docs:
            content = doc.page_content
            if content not in seen_contents:
                seen_contents.add(content)
                unique_docs.append(doc)
        
        # 답변 생성을 위한 컨텍스트 구성
        context_parts = []
        for i, doc in enumerate(unique_docs, 1):
            context_parts.append(f"[{i}] {doc.page_content}")
            # 메타데이터 정보 추가
            if doc.metadata:
                if 'source' in doc.metadata:
                    context_parts.append(f"출처: {doc.metadata['source']}")
                if 'url' in doc.metadata:
                    context_parts.append(f"URL: {doc.metadata['url']}")
        
        context = "\n\n".join(context_parts)
        
        llm = Config.get_llm("recycling")
        response = llm.invoke(
            ANSWER_PROMPT.format_prompt(
                region=current_region,
                question=user_input,
                context=context
            ).to_messages()
        )
        
        return {
            "answer": response.content
        }
        
    except Exception as e:
        return {
            "answer": ERROR_MESSAGES["search_error"] + f": {str(e)}"
        }


@tool
def generate_casual_response(user_input: str, casual_count: int = 0) -> str:
    """일반 대화 응답 생성"""
    llm = Config.get_llm("casual")
    
    # 버링이 캐릭터 유지하면서 재활용 주제로 유도
    guide = "재활용 주제로 자연스럽게 유도하세요." if casual_count >= 4 else "친근하게 대화하세요."
    
    messages = [
        ("system", SYSTEM_PROMPT),
        ("human", f"사용자: '{user_input}'\n\n{guide} 1-2문장으로 답하세요.")
    ]
    
    response = llm.invoke(messages)
    return response.content
