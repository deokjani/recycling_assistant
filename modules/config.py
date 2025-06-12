"""
애플리케이션 설정 모듈
"""

import os
from pathlib import Path
from typing import Dict, Optional

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# 환경 변수 로드
load_dotenv()


class Config:
    """애플리케이션 설정 클래스"""
    
    # 기본 경로
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "재활용정보"
    INDEX_DIR = BASE_DIR / "faiss_index"
    
    # API 설정
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    # 모델 설정
    LLM_MODEL = "gemini-2.0-flash"
    EMBEDDING_MODEL = "models/gemini-embedding-exp-03-07"
    
    # LLM 파라미터
    LLM_TEMPERATURE = 0.0  # 재활용 정보용 (정확도 우선)
    LLM_TEMPERATURE_CASUAL = 0.7  # 일반 대화용 (창의성)
    LLM_MAX_TOKENS = 1000
    LLM_MAX_TOKENS_SHORT = 200  # 짧은 응답용
    
    # 검색 설정
    SEARCH_K = 3  # 유사도 검색 시 반환할 문서 수
    
    # 지역 매핑
    REGION_MAP: Dict[str, str] = {
        "관악구": "gwanakgu",
        "성동구": "seongdonggu"
    }
    
    # 배치 처리 설정
    EMBEDDING_BATCH_SIZE = 5
    API_SLEEP_TIME = 5  # 초
    ERROR_SLEEP_TIME = 5  # 초
    
    # LLM 인스턴스 캐시
    _llm_instances: Dict[str, ChatGoogleGenerativeAI] = {}
    
    @classmethod
    def validate(cls) -> bool:
        """설정 유효성 검사"""
        if not cls.GOOGLE_API_KEY:
            print("GOOGLE_API_KEY가 설정되지 않았습니다.")
            print(".env 파일에 GOOGLE_API_KEY를 추가하세요.")
            return False
        
        if not cls.DATA_DIR.exists():
            print(f"데이터 디렉토리가 없습니다: {cls.DATA_DIR}")
            return False
        
        return True
    
    @classmethod
    def get_region_code(cls, region_name: str) -> Optional[str]:
        """지역명으로 지역 코드 반환"""
        return cls.REGION_MAP.get(region_name)
    
    @classmethod
    def get_supported_regions(cls) -> list[str]:
        """지원하는 지역 목록 반환"""
        return list(cls.REGION_MAP.keys())
    
    @classmethod
    def get_index_path(cls, region_name: str) -> Optional[Path]:
        """지역별 인덱스 경로 반환"""
        region_code = cls.get_region_code(region_name)
        if region_code:
            return cls.INDEX_DIR / region_code
        return None
    
    @classmethod
    def get_llm(cls, purpose: str = "recycling") -> ChatGoogleGenerativeAI:
        """용도별 LLM 인스턴스 반환 (싱글톤)
        - recycling: 재활용 관련 (정확도 우선)
        - casual: 일상 대화 (친근함 우선)
        """
        if purpose not in cls._llm_instances:
            if purpose == "casual":
                # 일상 대화용
                temperature = cls.LLM_TEMPERATURE_CASUAL
            else:
                # 재활용 관련
                temperature = cls.LLM_TEMPERATURE
            
            cls._llm_instances[purpose] = ChatGoogleGenerativeAI(
                model=cls.LLM_MODEL,
                temperature=temperature,
                google_api_key=cls.GOOGLE_API_KEY,
                max_tokens=cls.LLM_MAX_TOKENS
            )
        return cls._llm_instances[purpose]
