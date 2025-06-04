# Backend
## LLM과 RAG를 활용한 코드 리뷰 자동화 어시스턴트
### 경북대학교 종합설계프로젝트2 10팀 

#### 강보권, 고상희, 류영교, 송기영, 이준용

이 레포는 Backend 코드 및 LLM 코드라 들어있는 레포입니다.

사용을 위해서는 .env 파일에 아래의 값들을 입력해야 합니다.

    DB_URL=
    RABBITMQ_HOST=
    RABBITMQ_PORT=
    GEMINI_API_KEY=

사용법에 대해서는 api-docs를 참고하시면 감사하겠습니다.

주요 기능은 ZIP파일 또는 GITHUB URL을 입력하여, 프로젝트 분석 결과를 보고서(PDF)로 반환합니다.

입력값 및 출력값은 tests/sample_project.zip과 pdf_sample.pdf를 참고하시면 됩니다.
