"""
벡터 인덱스 빌드 스크립트
재활용 정보 JSON 파일들을 벡터 데이터베이스로 변환
"""

import sys
from pathlib import Path

# 프로젝트 루트 경로 추가
sys.path.append(str(Path(__file__).parent))

from modules import Config, DocumentLoader, VectorStoreManager
from modules.exceptions import VectorStoreError


def build_index_for_region(region_name: str, vector_manager: VectorStoreManager):
    """특정 지역의 인덱스 빌드"""
    print(f"\n{'='*50}")
    print(f"{region_name} 처리 시작")
    print(f"{'='*50}")
    
    region_path = Config.DATA_DIR / region_name
    
    if not region_path.exists():
        print(f"경로가 존재하지 않음: {region_path}")
        return False
    
    try:
        # 문서 로드
        print("문서 로드 중...")
        documents = DocumentLoader.load_all_documents(region_path)
        
        if not documents:
            print(f"{region_name}: 문서가 없습니다.")
            return False
        
        print(f"총 {len(documents)}개 문서 로드 완료")
        
        # 벡터 스토어 생성
        vector_store = vector_manager.create_vector_store(documents)
        
        # 저장
        vector_manager.save_vector_store(vector_store, region_name)
        
        print(f"{region_name} 인덱스 생성 완료!")
        return True
        
    except VectorStoreError as e:
        print(f"{region_name} 처리 중 오류: {e}")
        return False
    except Exception as e:
        print(f"{region_name} 처리 중 예상치 못한 오류: {e}")
        return False


def main():
    """메인 실행 함수"""
    print("벡터 인덱스 빌드 시작\n")
    
    # 설정 검증
    if not Config.validate():
        return
    
    # 벡터 스토어 매니저 생성
    try:
        vector_manager = VectorStoreManager()
    except VectorStoreError as e:
        print(f"초기화 실패: {e}")
        return
    
    # 각 지역별로 인덱스 빌드
    success_count = 0
    for region_name in Config.get_supported_regions():
        if build_index_for_region(region_name, vector_manager):
            success_count += 1
    
    # 결과 요약
    print(f"\n{'='*50}")
    print("빌드 완료")
    print(f"성공: {success_count}/{len(Config.get_supported_regions())} 지역")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
