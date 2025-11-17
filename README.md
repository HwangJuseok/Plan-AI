✈️ Plan-AI: AI 기반 맞춤형 여행 계획 생성 서비스

1. 프로젝트 개요 및 핵심 목표

Plan-AI는 사용자의 10가지 상세 요구사항(지역, 기간, 예산, 취향, 교통, 식사 제한 등)을 입력받아, 이를 AI가 완벽하게 구조화된 JSON 데이터로 출력하고, 최종적으로 사용자 친화적인 카드 UI로 변환하여 제공하는 Full-Stack AI 프로젝트입니다.

🎯 핵심 목표 (문제 정의 및 해결)

AI 출력 정형화: 자연어 요청을 오류 없이 Pydantic Schema에 맞는 JSON으로 변환하는 AI Integration의 난제 해결.

Full-Stack 통신: 프론트엔드의 멀티 스텝 폼 입력 → 백엔드 API 호출 → AI 요청 → 백엔드 검증 → 프론트엔드 시각화까지의 전 과정 구축.

UX 디자인: 복잡한 JSON 데이터를 모바일 친화적인 단계별 입력 폼 및 카드형 일정표로 제공하여 사용성을 극대화.

2. 기술 스택 (Technical Stack)

구분

기술 스택

핵심 역할 및 특징

Frontend

React (Vite), axios, Lucide-React

10단계 Multi-Step Form 구현 및 상태 관리, axios를 통한 비동기 API 통신, AI 응답(JSON)을 시각적인 일정 카드 UI로 변환 및 렌더링.

Backend

FastAPI, Python, Pydantic, python-dotenv

AI 프롬프트 엔지니어링 및 AI 모델 관리, Pydantic을 이용한 입/출력 데이터 유효성 검사 (검증), CORSMiddleware 설정.

AI/API

Gemini API (Flash-Latest)

고성능 언어 모델을 활용하여 사용자의 복합적인 취향(예: 걷기 싫음, 조용한 곳, 갑각류 제외)을 만족시키는 최적의 여행 경로 및 콘텐츠 생성.

3. 주요 기술 구현 과정 및 해결 경험 (면접 강조 포인트)

이 프로젝트를 진행하며 발생한 가장 중요한 기술적 도전과 해결 방안은 다음과 같습니다. 이는 프로젝트의 기술적 난이도를 보여주는 핵심 증거입니다.

3.1. [문제] AI의 JSON 출력 오류 (Validation Error)

AI는 자연어에는 강하지만, 정확한 JSON 스키마를 100% 따르는 것에 약점이 있습니다. 처음에는 AI가 trip_title 대신 plan_name을, plan 대신 itinerary를 사용하는 등 Pydantic 모델을 통과하지 못하는 오류가 반복되었습니다.

해결책:

모델 확장: AI가 자주 사용하는 shopping, sightseeing 등의 타입을 Pydantic Literal에 추가하여 규칙을 유연하게 확장.

프롬프트 강화 (Chain-of-Thought): AI의 response_schema 옵션 대신, 프롬프트 내에 **"이전 응답에서 너는 이 필드를 틀렸다! 이 필드 이름만 써야 한다!"**는 강력한 경고 및 정확한 JSON 스키마를 재주입하여 AI의 정확성을 최대치로 강제함.

3.2. [문제] 서버 간 통신 불가 (CORS / 405 Error)

React 개발 서버(5173 포트)가 FastAPI 서버(8000 포트)로 요청을 보낼 때, 405 Method Not Allowed 에러가 발생했습니다.

해결책:

FastAPI에 CORSMiddleware를 추가하고, allow_origins에 React의 개발 주소(http://localhost:5173, http://127.0.0.1:5173)를 명시적으로 등록하여 Cross-Origin 요청을 허용했습니다.

allow_methods=["*"]를 설정하여 사전 요청인 OPTIONS 메서드 응답을 정상적으로 처리했습니다.

4. 향후 개선 계획 (Roadmap)

핵심 MVP 기능은 완성되었으며, 포트폴리오 가치 증대 및 사용자 경험 확장을 위해 다음 단계를 계획하고 있습니다.

Phase 2: 서비스 완성도 강화 (UX/Design Focus)

지도 연동 (1순위): AI가 제공하는 위도/경도(Latitude/Longitude) 데이터를 활용하여 카카오맵 또는 Google Maps API와 연동, 일정을 지도 위에 시각적으로 핀(Pin)으로 표시. (여행 계획 앱의 핵심 기능)

반응형 UI/접근성: Tailwind CSS 또는 미디어 쿼리를 활용하여 모바일 환경에서의 입력 폼 및 결과 화면의 가독성 최적화.

Phase 3: AI 안정성 및 데이터 관리 강화

AI 출력 오류 자동 복구 (Retry Logic): ValidationError 발생 시, AI에게 수정된 요청을 자동으로 재전송하여 오류를 사용자가 인지하지 못하게 처리하는 복구 로직 구현.

데이터 지속성: Firebase Firestore 또는 SQLite를 활용하여 생성된 여행 계획을 사용자별로 저장하고 조회할 수 있는 기능 추가.

5. 실행 방법 (Local Development)

5.1. Prerequisites

Python 3.9+

Node.js & npm

Gemini API Key (API Key를 .env 파일에 설정해야 합니다.)

5.2. Backend Setup (Python/FastAPI)

# 1. 백엔드 폴더로 이동
cd backend

# 2. 가상 환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# 3. 필요한 라이브러리 설치
pip install -r requirements.txt 

# 4. API Key 환경 변수 설정 (.env 파일 생성)
# backend/.env 파일에 GOOGLE_API_KEY=YOUR_API_KEY_HERE 를 작성합니다.

# 5. FastAPI 서버 실행 (백그라운드에서 실행 권장)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000


5.3. Frontend Setup (React/Vite)

# 1. 프론트엔드 폴더로 이동
cd frontend

# 2. 필요한 라이브러리 설치
npm install
npm install lucide-react # 아이콘 라이브러리

# 3. 개발 서버 실행
npm run dev
# 보통 http://localhost:5173 에서 실행됩니다.
