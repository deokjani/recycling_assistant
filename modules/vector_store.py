"""
벡터 스토어 관리 모듈
FAISS 벡터 데이터베이스 생성 및 관리
"""

import time
from pathlib import Path
from typing import List, Optional

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from .config import Config
from .exceptions import VectorStoreError


class VectorStoreManager:
    """벡터 스토어 생성 및 관리 클래스"""
    
    def __init__(self):
        """벡터 스토어 매니저 초기화"""
        if not Config.GOOGLE_API_KEY:
            raise VectorStoreError("Google API 키가 설정되지 않았습니다.")
        
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=Config.EMBEDDING_MODEL,
            google_api_key=Config.GOOGLE_API_KEY
        )
        
        # 인덱스 디렉토리 생성
        Config.INDEX_DIR.mkdir(exist_ok=True)
    
    def create_vector_store(
        self, 
        documents: List[Document],
        batch_size: int = None
    ) -> FAISS:
        """
        문서 리스트로부터 벡터 스토어 생성
        
        Args:
            documents: Document 객체 리스트
            batch_size: 배치 크기 (기본값: Config에서 가져옴)
            
        Returns:
            FAISS 벡터 스토어
            
        Raises:
            VectorStoreError: 벡터 스토어 생성 실패 시
        """
        if not documents:
            raise VectorStoreError("문서가 비어있습니다.")
        
        if batch_size is None:
            batch_size = Config.EMBEDDING_BATCH_SIZE
        
        print(f"벡터 스토어 생성 중... (총 {len(documents)}개 문서)")
        
        vector_store = None
        total_batches = (len(documents) + batch_size - 1) // batch_size
        
        # 배치 처리
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i+batch_size]
            batch_num = i // batch_size + 1
            
            print(f"  배치 {batch_num}/{total_batches} 처리 중...")
            
            try:
                if vector_store is None:
                    # 첫 배치로 벡터 스토어 생성
                    vector_store = FAISS.from_documents(batch, self.embeddings)
                else:
                    # 이후 배치는 추가
                    texts = [doc.page_content for doc in batch]
                    metadatas = [doc.metadata for doc in batch]
                    vector_store.add_texts(texts, metadatas)
                
                # API 속도 제한 대응
                if batch_num < total_batches:
                    time.sleep(Config.API_SLEEP_TIME)
                    
            except Exception as e:
                print(f"  배치 {batch_num} 처리 실패: {e}")
                time.sleep(Config.ERROR_SLEEP_TIME)
                raise VectorStoreError(f"벡터 스토어 생성 실패: {e}")
        
        return vector_store
    
    def save_vector_store(self, vector_store: FAISS, region_name: str) -> Path:
        """
        벡터 스토어를 파일로 저장
        
        Args:
            vector_store: FAISS 벡터 스토어
            region_name: 지역명
            
        Returns:
            저장된 경로
            
        Raises:
            VectorStoreError: 저장 실패 시
        """
        save_path = Config.get_index_path(region_name)
        if not save_path:
            raise VectorStoreError(f"지원하지 않는 지역: {region_name}")
        
        try:
            save_path.mkdir(exist_ok=True, parents=True)
            vector_store.save_local(str(save_path))
            print(f"벡터 스토어 저장 완료: {save_path}")
            return save_path
            
        except Exception as e:
            raise VectorStoreError(f"벡터 스토어 저장 실패: {e}")
    
    def load_vector_store(self, region_name: str) -> Optional[FAISS]:
        """
        저장된 벡터 스토어 로드
        
        Args:
            region_name: 지역명
            
        Returns:
            FAISS 벡터 스토어 또는 None
        """
        index_path = Config.get_index_path(region_name)
        if not index_path or not index_path.exists():
            return None
        
        try:
            return FAISS.load_local(
                str(index_path),
                self.embeddings,
                allow_dangerous_deserialization=True
            )
        except Exception as e:
            print(f"벡터 스토어 로드 실패: {e}")
            return None
