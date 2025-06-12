"""재활용 정보 문서 로더"""

import json
from pathlib import Path
from typing import List

from langchain_core.documents import Document


class DocumentLoader:
    """JSON과 TXT 파일을 결합하여 Document 생성"""
    
    @staticmethod
    def load_all_documents(directory: Path) -> List[Document]:
        """디렉토리의 모든 문서 로드"""
        all_docs = []
        
        # 폴더별로 처리
        for folder in set(f.parent for f in directory.glob("**/*.json")):
            # TXT 파일에서 출처 정보 로드
            source_info = {}
            for txt in folder.glob("*.txt"):
                with open(txt, encoding="utf-8") as f:
                    content = f.read().strip()
                    lines = content.split('\n')
                    for line in lines:
                        if line.startswith('[경로]'):
                            source_info['source'] = line[4:].strip()
                        elif line.startswith('[URL]'):
                            source_info['url'] = line[5:].strip()
            
            # JSON 파일 처리
            for json_file in folder.glob("*.json"):
                try:
                    with open(json_file, encoding="utf-8") as f:
                        data = json.load(f)
                    
                    region = data.get('지역', '')
                    
                    # 각 품목을 Document로 변환
                    for item_name, item_info in data.items():
                        if item_name == '지역' or not isinstance(item_info, dict):
                            continue
                        
                        # 문서 내용 생성
                        content = f"지역: {region}\n품목: {item_name}"
                        
                        # 선택적 필드 추가 (있는 경우에만)
                        for field in ["배출방법", "배출요일", "세척여부", "주의사항"]:
                            if field in item_info and item_info[field]:
                                content += f"\n{field}: {item_info[field]}"
                        
                        # 메타데이터 구성
                        metadata = {
                            "품목": item_name,
                            "지역": region,
                            "파일명": json_file.name
                        }
                        
                        # 출처 정보 추가
                        if source_info:
                            metadata.update(source_info)
                        
                        # Document 생성
                        doc = Document(
                            page_content=content,
                            metadata=metadata
                        )
                        all_docs.append(doc)
                        
                except Exception as e:
                    print(f"Error loading {json_file}: {e}")
        
        return all_docs
