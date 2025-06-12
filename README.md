# 재활용 도우미 챗봇 "버링이"

## 프로젝트 소개
"버링이"는 지역별 재활용 분리수거 정보를 제공하는 AI 챗봇입니다. 사용자가 특정 지역에서 어떤 품목을 어떻게 버려야 하는지 물어보면, 해당 지역의 공식 재활용 가이드라인을 기반으로 정확한 답변을 제공합니다.

## 주요 기능
- **지역별 맞춤 정보**: 현재 관악구, 성동구 지원
- **자연어 질의응답**: 일상적인 질문으로 재활용 방법 검색
- **대화 맥락 이해**: 이전 대화 내용을 기억하여 연속적인 질문 처리
- **출처 자동 표시**: 모든 답변에 공식 출처와 URL 제공
- **친근한 대화**: "버링이" 캐릭터를 통한 부드러운 안내

## 기술 스택
- **Python 3.11+**
- **LangChain**: 문서 처리, 벡터 저장소, 프롬프트 관리
- **LangGraph**: 상태 기반 워크플로우 관리
- **FAISS**: 벡터 유사도 검색
- **Google Gemini API**: LLM for 의도 분석 및 답변 생성

![image](https://github.com/user-attachments/assets/f01ba085-6c14-4ca5-889f-42303d1f27aa)


## 프로젝트 구조
```
recycling_assistant/
├── main.py                 # 프로그램 진입점, 콘솔 UI
├── build_index.py          # 벡터 인덱스 생성 스크립트
├── requirements.txt        # 의존성 패키지 목록
├── .env                    # 환경 변수 (API 키 등)
│
├── modules/                # 핵심 모듈
│   ├── agent.py           # 대화 상태 관리
│   ├── graph.py           # LangGraph 워크플로우 정의
│   ├── nodes.py           # 워크플로우 노드 구현
│   ├── tools.py           # 검색 및 답변 생성 도구
│   ├── vector_store.py    # 벡터 DB 관리
│   ├── document_loader.py # 문서 로딩 및 전처리
│   ├── config.py          # 설정 관리
│   └── prompts.py         # 프롬프트 템플릿
│
├── faiss_index/           # 생성된 벡터 인덱스
│   ├── gwanakgu/
│   └── seongdonggu/
│
└── 재활용정보/            # 원본 데이터
    ├── 관악구/
    │   ├── 재활용품_분리배출/
    │   └── 생활쓰레기_배출/
    └── 성동구/
        ├── 음식물쓰레기/
        └── 재활용품재활용_불가품목/
```

## 시스템 아키텍처

### 데이터 처리 파이프라인
1. **데이터 수집**: 지역별 재활용 정보를 JSON 형식으로 저장
2. **문서 변환**: DocumentLoader가 JSON과 출처 정보(TXT)를 LangChain Document로 변환
3. **벡터화**: 각 문서를 임베딩하여 FAISS 벡터 DB에 저장
4. **검색**: 사용자 질문을 임베딩하여 유사한 문서 검색

### 대화 처리 플로우
1. **사용자 입력**: main.py에서 입력 받기
2. **상태 관리**: agent.py가 대화 히스토리와 상태 유지
3. **의도 분석**: LangGraph의 Parse Node가 재활용 질문 여부 판단
4. **처리 분기**:
   - 재활용 질문 → Recycling Node → 벡터 검색 → 답변 생성
   - 일반 대화 → Casual Node → 캐릭터 응답 생성
5. **응답 출력**: 생성된 답변을 사용자에게 표시

## 설치 및 실행

### 사전 요구사항
- Python 3.11 이상
- Google Gemini API 키

### 설치 방법
```bash
# 1. 저장소 클론
git clone https://github.com/yourusername/recycling_assistant.git
cd recycling_assistant

# 2. 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 환경 변수 설정
# .env 파일에 GOOGLE_API_KEY 추가
echo "GOOGLE_API_KEY=your_api_key_here" > .env

# 5. 벡터 인덱스 생성
python build_index.py

# 6. 실행
python main.py
```

## 사용 예시
```
재활용 도우미 버링이
지원 지역: 관악구, 성동구
예시: '관악구에서 플라스틱 어떻게 버려요?' 또는 '성동구' 입력 후 품목 질문
종료: 'exit' 입력

You: 관악구에서 플라스틱 어떻게 버려요?
버링이: 관악구에서 플라스틱은 투명 비닐봉투에 담아서 배출해주시면 돼요! 
        내용물을 비우고 깨끗이 헹궈서 버려주세요.
        [출처] 관악구청 > 재활용품 분리배출
        [URL] https://www.gwanak.go.kr/...

You: 스티로폼은요?
버링이: 스티로폼도 재활용이 가능해요! 관악구에서는...
```

## 확장 계획
- [ ] 더 많은 지역 데이터 추가
- [ ] 웹 인터페이스 개발
- [ ] 이미지 인식 기능 (쓰레기 사진 분류)
- [ ] 다국어 지원
- [ ] 모바일 앱 개발

## 기여 방법
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 라이선스
이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 문의
프로젝트 관련 문의사항이 있으시면 이슈를 생성해주세요.
