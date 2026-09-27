<div align="center">

# ✈️ Plan-AI: AI 기반 맞춤형 여행 계획 생성 서비스

[![Deployment](https://img.shields.io/badge/Deployment-Vercel-black?style=for-the-badge&logo=vercel)](https://aiplanai.vercel.app/)
![Status](https://img.shields.io/badge/Status-Live_Service-success?style=for-the-badge)
![React](https://img.shields.io/badge/React-19.2.0-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-7.2.2-646CFF?style=for-the-badge&logo=vite&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.121.2-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-2.12.4-E92063?style=for-the-badge&logo=pydantic&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini-flash--latest-4285F4?style=for-the-badge&logo=googlegemini&logoColor=white)
![Render](https://img.shields.io/badge/Backend-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)

> **"Gemini AI가 당신의 취향을 분석하여, 단 몇 초 만에 구조화된 여행 스케줄을 제안합니다."**

### 🔗 [https://aiplanai.vercel.app/](https://aiplanai.vercel.app/) — 라이브 데모 바로가기

</div>

---

## 📖 목차

1. [프로젝트 심층 소개](#-1-프로젝트-심층-소개-overview)
2. [사용 기술 및 라이브러리](#-2-사용-기술-및-라이브러리-tech-stack--dependencies)
3. [핵심 기능 및 상세 로직](#-3-핵심-기능-및-상세-로직-key-features--logic)
4. [프로젝트 구조](#-4-프로젝트-구조-및-파일-설명-directory-structure)
5. [Getting Started](#-5-getting-started-설치-및-실행-가이드)
6. [Troubleshooting & Dev Log](#-6-troubleshooting--dev-log-트러블슈팅-및-개발-일지)

---

## 🧭 1. 프로젝트 심층 소개 (Overview)

### 어떤 문제를 풀기 위한 프로젝트인가

여행 일정을 직접 짜려면 지역 조사, 동선 계산, 예산 배분, 취향 반영까지 최소 수십 분이 걸립니다. **Plan-AI**는 이 과정을 **10단계의 짧은 멀티스텝 폼**으로 구조화해 사용자의 취향(여행지, 기간, 인원, 숙소 위치, 예산, 교통수단, 여행 페이스, 분위기, 관심사, 식사 제한)을 입력받고, 이를 **Gemini 생성형 AI**에게 넘겨 **하루 단위 스케줄 카드**로 즉시 돌려주는 여행 계획 자동화 서비스입니다.

가장 핵심적인 엔지니어링 포인트는 **"자연어 생성 모델의 출력을 신뢰할 수 있는 JSON 데이터로 강제 정형화하는 것"** 입니다. 이를 위해 FastAPI + Pydantic 스키마 검증 계층이 AI와 프론트엔드 사이에서 **데이터 게이트키퍼** 역할을 합니다.

### 전체 아키텍처 흐름 (실제 배포 구조 기준)

```
[React 앱 (Vercel)] ──POST── [FastAPI 서버 (Render)] ──generate_content_async── [Gemini API]
   aiplanai.vercel.app      plan-ai-f9kt.onrender.com/plan-ai
```

**시나리오. 사용자가 부산 3박 4일 여행 계획을 요청한다**

1. 사용자가 `Plan-AI` 첫 화면(`step 0`)에서 "여행 계획 시작하기"를 누르면, `App.jsx`의 `step` 상태가 1씩 증가하며 **총 9개의 입력 스텝**(목적지 → 기간 → 인원 → 숙소 위치 → 예산 → 교통수단 → 페이스/걷기선호 → 분위기 → 관심사/식사제한)을 순서대로 통과한다.
2. 마지막 10번째 화면에서 지금까지 입력한 값을 `renderFinalSummary()`가 표(table) 형태로 요약해 보여주고, "AI 계획 생성하기" 클릭 시 `handleSubmit()`이 `formData` 객체 전체를 그대로 `axios.post(API_URL, formData)`로 전송한다. 이때 `API_URL`은 하드코딩된 Render 백엔드 주소(`https://plan-ai-f9kt.onrender.com/plan-ai`)이다.
3. FastAPI(`main.py`)는 요청 본문을 `TripRequest` Pydantic 모델로 **1차 검증**한다 (타입, `Literal` 허용값 등이 안 맞으면 이 시점에 422 에러로 즉시 차단됨).
4. `_build_ai_prompt()`가 "반드시 JSON 스키마를 지켜라"는 강한 제약 문구 + 스키마 예시 + 사용자 요청 JSON을 하나의 프롬프트 문자열로 합성한다.
5. `ai_model.generate_content_async(ai_prompt)`가 Gemini(`gemini-flash-latest`, `response_mime_type: application/json` 강제)를 비동기 호출한다.
6. 응답 텍스트에서 혹시 모를 마크다운 코드펜스(```json ... ```)를 문자열 파싱으로 제거한 뒤 `json.loads()`로 파이썬 dict로 변환하고, 다시 `TripResponse` Pydantic 모델로 **2차 검증**한다 (필드명/타입이 스키마와 다르면 여기서 걸러짐).
7. 검증을 통과한 JSON이 React로 반환되면, `renderPlanCard()`가 `day → schedule` 배열을 순회하며 시간·아이콘(`lucide-react`)·제목·설명·예상 비용이 담긴 **일자별 카드 UI**를 렌더링한다.
8. 결과 화면 하단의 "후기 남기기" 버튼은 사용자의 입력값(목적지, 기간, 인원)을 **Google Forms URL 파라미터로 프리필**해 새 탭으로 열어주는 방식으로 피드백을 수집한다.

---

## 🧰 2. 사용 기술 및 라이브러리 (Tech Stack & Dependencies)

### Frontend (`frontend/package.json`)

| 구분 | 기술 | 버전 |
|---|---|---|
| 프레임워크 | ![React](https://img.shields.io/badge/React-19.2.0-61DAFB?logo=react&logoColor=black) | 19.2.0 |
| 빌드 도구 | ![Vite](https://img.shields.io/badge/Vite-7.2.2-646CFF?logo=vite&logoColor=white) | 7.2.2 |
| HTTP 클라이언트 | ![Axios](https://img.shields.io/badge/Axios-1.13.2-5A29E4?logo=axios&logoColor=white) | 1.13.2 |
| 아이콘 | ![Lucide](https://img.shields.io/badge/lucide--react-0.554.0-orange) | 0.554.0 |
| 린트 | ![ESLint](https://img.shields.io/badge/ESLint-9.39.1-4B32C3?logo=eslint&logoColor=white) | 9.39.1 |

> ⚠️ 참고: `frontend/index.html` + `public/vite.svg`는 순수 Vite 템플릿 그대로이며, **Tailwind CSS는 실제 React 앱(`App.jsx`)에는 사용되지 않습니다.** (Tailwind는 저장소 루트의 별도 정적 포트폴리오 페이지에서만 CDN으로 로드됩니다. 아래 4번 항목 참고)

### Backend (`backend/requirements.txt`)

| 구분 | 기술 | 버전 |
|---|---|---|
| 웹 프레임워크 | ![FastAPI](https://img.shields.io/badge/FastAPI-0.121.2-009688?logo=fastapi&logoColor=white) | 0.121.2 |
| ASGI 서버 | ![Uvicorn](https://img.shields.io/badge/Uvicorn-0.38.0-499848?logo=uvicorn&logoColor=white) | 0.38.0 |
| 데이터 검증 | ![Pydantic](https://img.shields.io/badge/Pydantic-2.12.4-E92063?logo=pydantic&logoColor=white) | 2.12.4 |
| AI SDK | ![Gemini](https://img.shields.io/badge/google--generativeai-0.8.5-4285F4?logo=googlegemini&logoColor=white) | 0.8.5 |
| 환경변수 | ![dotenv](https://img.shields.io/badge/python--dotenv-1.2.1-yellow) | 1.2.1 |
| 언어 | ![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white) | 3.10+ |

### 배포 & 외부 서비스

| 구분 | 서비스 |
|---|---|
| 프론트엔드 배포 | ![Vercel](https://img.shields.io/badge/Vercel-black?logo=vercel) — `aiplanai.vercel.app` |
| 백엔드 배포 | ![Render](https://img.shields.io/badge/Render-46E3B7?logo=render&logoColor=white) — `plan-ai-f9kt.onrender.com` |
| AI 모델 | Google **Gemini `gemini-flash-latest`** (`response_mime_type=application/json` 강제) |
| 피드백 수집 | Google Forms (프리필 URL 파라미터 연동) |

---

## ⚙️ 3. 핵심 기능 및 상세 로직 (Key Features & Logic)

### 3-1. Pydantic 이중 검증(Double Validation)으로 AI 환각 방어
- **입력 검증**: `TripRequest`가 `main_mode: Literal['own_car','rental_car','public_transport']`처럼 **허용값을 코드 레벨에서 제한**해, 잘못된 입력이 애초에 AI에게 전달되지 않도록 차단한다.
- **출력 검증**: AI가 반환한 JSON도 그대로 신뢰하지 않고 `TripResponse(**ai_response_dict)`로 다시 파싱한다. 이 과정에서 `ValidationError`가 나면 `except ValidationError`가 잡아 `500 (Validation)` 에러로 응답하므로, **스키마를 어긴 응답이 프론트엔드까지 도달하지 않는다.**

### 3-2. 코드펜스 스트리핑 + JSON 파싱 방어 로직
- Gemini는 `response_mime_type: application/json`으로 강제되어 있음에도, 실제로는 응답이 ` ```json ... ``` ` 코드블록으로 감싸져 오는 경우가 있어 `_create_travel_plan_core()`에서 문자열이 ` ``` `로 시작하면 `split("```")`으로 코드펜스를 벗겨낸 뒤 `json.loads()`를 시도한다.
- `json.JSONDecodeError`가 나면 `"AI가 유효한 JSON을 반환하지 않았습니다."`라는 명시적 예외를 던지고, 최종적으로 `HTTPException(500, ...)`으로 응답한다. **(주의: 현재 코드에는 자동 재요청 로직은 없으며, 실패 시 프론트엔드에 에러만 반환된다 — 자세한 내용은 6번 항목 참고)**

### 3-3. CORS: 프로덕션 + Vercel 프리뷰 배포까지 함께 허용
```python
ALLOW_ORIGIN_REGEX = r"https://.*\.vercel\.app"
origins = ["https://aiplanai.vercel.app", "http://localhost:5173", "http://127.0.0.1:5173"]
```
정식 도메인은 화이트리스트로, **Vercel이 PR마다 자동 생성하는 프리뷰 배포 URL**(`*.vercel.app`)은 정규식으로 한 번에 허용해, 브랜치 배포 테스트 시마다 CORS 설정을 다시 건드릴 필요가 없도록 설계되어 있다.

### 3-4. 이중 엔드포인트 지원 (`/api/v1/plan`, `/plan-ai`)
동일한 로직(`_create_travel_plan_core`)을 `/api/v1/plan`(RESTful 표준 네이밍)과 `/plan-ai`(프론트엔드가 실제로 호출하는 레거시 경로) 두 경로에 모두 노출해, **프론트엔드 코드를 건드리지 않고도 API 버전 체계를 점진적으로 도입**할 수 있게 되어 있다.

### 3-5. 멀티스텝 폼 상태 관리 (`App.jsx`)
- `handleInputChange`(최상위 필드), `handleNestedChange`(중첩 객체: `accommodation`, `transportation`, `style`), `handleArrayChange`(콤마 구분 텍스트를 배열로 변환: 관심사, 식사 제한) 3종의 핸들러로 **깊이가 다른 폼 상태를 하나의 패턴으로 통일**해 관리한다.
- `loading` / `error` / `result` 3개의 상태 플래그로 **API 호출의 전체 생명주기**(요청 중 → 실패 → 성공)를 분기 렌더링(`renderStep()`)하며, `handleStartOver()`가 모든 상태를 초기값으로 되돌려 처음부터 다시 시작할 수 있게 한다.

### 3-6. 결과 카드 UI (`renderPlanCard`, `getIconForType`)
- 일정 타입(`food`, `cafe`, `accommodation`, `activity`, `shopping`, `travel`, `sightseeing`, `etc`) 8종을 `lucide-react` 아이콘에 1:1 매핑해 시각적으로 구분하고, `cost_krw`가 0보다 클 때만 `toLocaleString()`으로 천 단위 콤마가 포함된 비용을 노출한다.

---

## 🗂️ 4. 프로젝트 구조 및 파일 설명 (Directory Structure)

```text
Plan-AI-main/
├── index.html                       # ⚠️ React 앱과 무관한 별도 정적 포트폴리오 소개 페이지
│                                     #    (Tailwind CDN + Font Awesome, 개발자 자기소개/프로젝트 회고용)
├── assets/                          # 포트폴리오 페이지에서 쓰는 스크린샷 이미지 8종
│   ├── main-cover.png
│   ├── feature1-code.png / feature1-swagger.png
│   ├── feature2-form.png / feature2-result.png
│   └── form-screenshot-1~4.png       # 사전 사용자 설문조사(13명) 결과 캡처
│
├── backend/                         # FastAPI 백엔드 (Render 배포)
│   ├── .env                          # GOOGLE_API_KEY 보관 (⚠️ .gitignore 처리되어 있어야 함)
│   ├── requirements.txt              # pip 의존성 목록
│   └── app/
│       ├── main.py                   # ✅ 실제 서비스 진입점: 모델 정의 + 프롬프트 빌더 + API 라우팅 전부 포함
│       └── models.py                 # ⚠️ main.py와 동일한 Pydantic 모델이 중복 정의됨, 실제로는 어디서도 import 안 됨 (Dead Code)
│
└── frontend/                        # React (Vite) 프론트엔드 (Vercel 배포)
    ├── index.html                    # Vite 기본 템플릿 (타이틀만 "frontend"로 미변경)
    ├── package.json / package-lock.json
    ├── vite.config.js                # 기본 @vitejs/plugin-react 설정, 프록시/환경변수 설정 없음
    ├── eslint.config.js
    ├── public/vite.svg
    └── src/
        ├── main.jsx                  # ReactDOM 진입점, index.css만 import
        ├── index.css                 # 전역 리셋 스타일 (다크 배경, flex 중앙정렬)
        ├── App.css                   # ⚠️ App.jsx 어디서도 import되지 않는 미사용 파일 (Dead Code, 6번 항목 참고)
        └── App.jsx                   # ✅ 앱의 사실상 전부: 상태관리 + 10단계 폼 + API 호출 + 결과 렌더링 + 스타일(인라인 <style> 태그로 직접 주입)
```

---

## 🚀 5. Getting Started (설치 및 실행 가이드)

### 5-1. 사전 요구 사항
- Python 3.10 이상 / Node.js 18 이상
- **Google Gemini API Key** ([Google AI Studio](https://aistudio.google.com/app/apikey)에서 발급)

### 5-2. 백엔드 환경변수 설정

`backend/.env` 파일을 아래와 같이 직접 생성합니다 (저장소에는 포함되어 있지 않으며, `.gitignore`로 보호되어야 합니다).

```env
GOOGLE_API_KEY=여기에_발급받은_실제_API_키_입력
```

### 5-3. 백엔드 실행 (FastAPI)

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

- 헬스체크: `GET http://localhost:8000/` → `{"status": "ok", "service": "plan-ai"}`
- Swagger 문서: `http://localhost:8000/docs`

### 5-4. 프론트엔드 실행 (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

> ⚠️ **주의**: `App.jsx`의 `API_URL`이 배포된 Render 주소(`https://plan-ai-f9kt.onrender.com/plan-ai`)로 **하드코딩**되어 있습니다. 로컬에서 실행한 백엔드(`localhost:8000`)를 테스트하려면, `App.jsx` 상단의 `API_URL` 값을 직접 `http://localhost:8000/plan-ai`로 바꿔주어야 합니다. (환경변수 분리는 아직 되어 있지 않습니다 — 6번 항목 참고)

### 5-5. 빌드

```bash
npm run build      # frontend/dist 에 정적 파일 생성
npm run preview    # 빌드 결과 로컬 미리보기
```

---

## 🛠️ 6. Troubleshooting & Dev Log (트러블슈팅 및 개발 일지)

실제 코드를 정밀 분석한 결과, 기존에 알고 계셨던 내용과 **코드 상 실제 동작이 다른 지점**들이 있어 정확하게 짚어드립니다. 포트폴리오나 면접에서 설명하실 때 실제 구현과 어긋나지 않도록 참고하시면 좋을 것 같습니다.

### 🔸 [정정] "AI가 JSON 오류 시 자동 재요청(Self-Correction)한다" → 현재는 구현되어 있지 않음
`main.py`의 `_create_travel_plan_core()`를 보면, `json.loads()`가 실패했을 때는 `Exception("AI가 유효한 JSON을 반환하지 않았습니다.")`을 던지고 그대로 `HTTPException(500, ...)`으로 끝날 뿐, **Gemini에게 재요청하는 루프는 존재하지 않습니다.** 즉 사용자는 실패 시 "처음부터 다시하기" 버튼으로 수동 재시도를 해야 하는 구조입니다.
- **개선 방향**: 파싱/검증 실패 시 에러 메시지를 프롬프트에 포함해 `for attempt in range(2): ...` 형태로 1~2회 자동 재요청하는 루프를 추가하면, 실제로 "Self-Correction"이라는 이름에 걸맞은 동작이 됩니다.

### 🔸 [정정] "환경변수(.env)로 개발/배포 API 엔드포인트를 동적 관리한다" → 현재는 하드코딩
프론트엔드 `App.jsx`의 `const API_URL = 'https://plan-ai-f9kt.onrender.com/plan-ai'`는 **상수로 고정**되어 있으며, Vite의 `import.meta.env.VITE_API_URL` 같은 환경변수 참조는 코드 어디에도 없습니다.
- **개선 방향**: `frontend/.env` + `.env.production`을 도입해 `const API_URL = import.meta.env.VITE_API_URL`로 바꾸면, 로컬 개발 시 백엔드 주소를 코드 수정 없이 전환할 수 있습니다.

### 🔸 죽은 코드(Dead Code) 2건 — 리팩터링 중 정리가 덜 된 흔적
1. **`backend/app/models.py`**: `main.py`가 동일한 Pydantic 모델(`TripRequest`, `TripResponse` 등)을 자체적으로 다시 정의하고 있어, `models.py`는 **어디에서도 import되지 않는 완전한 중복 파일**입니다. (심지어 `ScheduleItem.type`의 허용값도 두 파일이 서로 다릅니다 — `models.py`는 6종, `main.py`는 `shopping`/`sightseeing`이 추가된 8종입니다.)
2. **`frontend/src/App.css`**: `main.jsx`는 `App.css`를 import하지 않고 `index.css`만 불러오며, 실제 스타일은 `App.jsx` 내부의 `AppCssStyles` 템플릿 리터럴 문자열이 `<style>` 태그로 직접 렌더링되어 적용됩니다. `App.css` 파일 자체는 미사용 상태입니다.
- **정리 방향**: 두 파일 모두 삭제하거나, 반대로 `main.py`가 `models.py`를 import하도록 통일하고 `App.jsx`가 `App.css`를 정식으로 import하도록 되돌리는 것 중 하나로 일원화하는 것을 권장합니다.

### 🔸 API 키 관리 (`.env`)
`backend/.env`에 `GOOGLE_API_KEY`가 저장되며, `python-dotenv`의 `load_dotenv()`로 로드됩니다. 다행히 루트 `.gitignore`에 `backend/.env`가 명시되어 있어 **Git 커밋 자체는 방지**되고 있습니다. 다만,
- Render(백엔드) / Vercel(프론트엔드) 배포 환경에서는 `.env` 파일이 아니라 **각 플랫폼의 환경변수(Environment Variables) 설정 화면**에 `GOOGLE_API_KEY`를 등록해야 배포본이 정상 동작합니다.
- 로컬의 `.env` 파일이 외부로 공유(압축, 이메일, 채팅 등)되지 않도록 각별히 주의가 필요합니다. 한 번이라도 외부에 노출되었다면 즉시 [Google AI Studio](https://aistudio.google.com/app/apikey)에서 키를 폐기(Revoke)하고 재발급받는 것이 안전합니다.

### 🔸 콜드 스타트(Cold Start) 지연 — Render 무료 플랜 특성
Render 무료 티어는 일정 시간 요청이 없으면 서버가 슬립 상태로 전환됩니다. 첫 요청 시 서버가 깨어나는 데 수십 초가 걸릴 수 있어, 프론트엔드의 `axios.post(..., { timeout: 60000 })` (60초 타임아웃)은 이 콜드 스타트 지연을 감안한 값으로 보입니다. 첫 방문자가 "AI가 계획을 생성 중입니다..." 화면에서 예상보다 오래 대기할 수 있다는 점은 UX상 참고할 부분입니다.

### 🔸 CORS 프리플라이트(OPTIONS) 대응
`@app.options("/plan-ai")`로 프리플라이트 요청에 대한 명시적 200 응답을 별도로 정의해 둔 것은, `CORSMiddleware`만으로 프리플라이트가 간헐적으로 막히는 배포 환경(특히 Render처럼 프록시를 거치는 PaaS)에서 흔히 발생하는 이슈에 대한 보강 조치로 보입니다.

---

<div align="center">

Made with React, FastAPI & Gemini — AI 서비스 신뢰성 확보를 위한 프로젝트

</div>
