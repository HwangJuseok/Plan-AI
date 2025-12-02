# ✈️ Plan-AI: AI 기반 맞춤형 여행 계획 생성 서비스

[![Deployment](https://img.shields.io/badge/Deployment-Vercel-black?logo=vercel&style=flat-square)](https://aiplanai.vercel.app/)
![Project Status](https://img.shields.io/badge/Status-Live_Service-success?style=flat-square)
![Tech Stack](https://img.shields.io/badge/Frontend-React%20(Vite)-blue?style=flat-square)
![Tech Stack](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square)

> **"Gemini AI가 당신의 취향을 분석하여, 단 1분 만에 완벽한 여행 스케줄을 제안합니다."**

## 🔗 서비스 바로가기 (Live Demo)
👉 **[https://aiplanai.vercel.app/](https://aiplanai.vercel.app/)**
*(현재 배포된 라이브 서버에서 서비스를 체험하실 수 있습니다.)*

---

## 1. 프로젝트 개요 (Project Overview)

**Plan-AI**는 사용자의 10가지 상세 여행 취향(지역, 예산, 테마, 식사 제한 등)을 심층 분석하여, **AI가 구조화된 여행 계획(JSON)**을 생성하고 이를 **시각적인 타임라인 UI**로 변환해주는 웹 서비스입니다.

### 🎯 핵심 목표 및 성과
* **AI 응답의 정형화:** 자연어 모델(LLM)의 불확실한 출력을 **Pydantic Schema**를 통해 100% 구조화된 JSON 데이터로 변환 성공.
* **End-to-End 구축:** `Frontend(React)` ↔ `Backend(FastAPI)` ↔ `AI(Gemini)` 간의 유기적인 데이터 파이프라인 완성.
* **사용자 경험(UX) 개선:** 복잡한 텍스트 답변 대신, 모바일 친화적인 **카드 뉴스 형태의 일정표** 제공.

## 2. 기술 스택 (Technical Stack)

| 구분 | 기술 스택 | 상세 설명 |
| :--- | :--- | :--- |
| **Frontend** | `React` (Vite), `Tailwind CSS` | 직관적인 **Multi-Step Form** 구현, `Axios` 비동기 통신, 모바일 반응형 디자인 적용. |
| **Backend** | `FastAPI`, `Python 3.11` | REST API 구축, `Pydantic`을 이용한 **데이터 무결성 검증**, AI 모델 요청 핸들링. |
| **AI / Data** | `Gemini 1.5 Flash API` | 사용자 데이터 기반 초개인화 프롬프트 엔지니어링 및 Context Caching 활용. |
| **Deployment** | `Vercel` | Frontend/Backend 통합 배포 및 CI/CD 파이프라인 구축. |

## 3. 핵심 문제 해결 경험 (Troubleshooting)

프로젝트 개발 및 배포 과정에서 마주친 기술적 챌린지와 해결 과정입니다.

### 3.1. [AI] JSON 파싱 오류 및 환각(Hallucination) 제어
AI가 가끔 지정된 키값(`trip_title`) 대신 다른 키(`plan_name`)를 반환하거나, JSON 형식을 깨뜨리는 문제가 발생했습니다.
* **해결:**
    1.  **Strict Schema:** 프롬프트 내에 JSON 구조를 명시하고, System Prompt에 **"You must respond ONLY in JSON format"** 제약 조건을 강력하게 추가.
    2.  **Retry Logic:** Backend에서 `json.loads()` 실패 시, 에러 메시지를 포함하여 AI에게 **자동으로 재요청(Self-Correction)** 하는 로직 구현.

### 3.2. [Network] 배포 환경에서의 CORS 및 Mixed Content 이슈
로컬 개발 환경과 달리, 실제 배포 시 클라이언트(Vercel)와 서버 간의 출처(Origin) 차이로 인한 통신 에러가 발생했습니다.
* **해결:**
    1.  `FastAPI`의 `CORSMiddleware` 설정에 배포된 도메인(`aiplanai.vercel.app`)을 화이트리스트로 등록.
    2.  환경 변수(`.env`)를 통해 개발 모드와 배포 모드를 분리하여 API 엔드포인트를 동적으로 관리.

## 4. 로컬 실행 방법 (Local Development)

라이브 서비스 외에 로컬 환경에서 코드를 실행하려면 아래 절차를 따르세요.

### Prerequisites
* Python 3.9+ / Node.js 18+
* Google Gemini API Key

### Backend (FastAPI)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# .env 파일 생성 후 GOOGLE_API_KEY 입력
uvicorn app.main:app --reload
