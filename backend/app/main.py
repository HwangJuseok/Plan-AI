# backend/app/main.py

import os
import json
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ValidationError
from typing import List, Literal, Optional

# AI 라이브러리 및 .env 로더
import google.generativeai as genai
from dotenv import load_dotenv

# ----------------------------------------------------
# 1) 모델 정의
# ----------------------------------------------------

# 입력 모델 (React -> Python)
class Accommodation(BaseModel):
    address_name: str
    latitude: float = Field(default=35.16, description="위도")
    longitude: float = Field(default=129.1636, description="경도")

class Transportation(BaseModel):
    main_mode: Literal['own_car', 'rental_car', 'public_transport']
    preferences: List[str]

class Style(BaseModel):
    pace: Literal['relaxed', 'packed']
    atmosphere: Literal['quiet', 'crowded']
    walking: Literal['dislike', 'neutral', 'like']
    interests: List[str]
    food_restrictions: List[str]

class TripRequest(BaseModel):
    destination: str
    duration_days: int
    party_size: int
    accommodation: Accommodation
    budget_krw: int
    transportation: Transportation
    style: Style

# 출력 모델 (Python/AI -> React)
class Location(BaseModel):
    name: str
    address: str
    latitude: float
    longitude: float

class ScheduleItem(BaseModel):
    time: str
    # AI가 사용하는 타입을 허용 목록에 포함
    type: Literal['accommodation', 'cafe', 'food', 'activity', 'travel', 'etc', 'shopping', 'sightseeing']
    title: str
    description: str
    location: Location
    cost_krw: Optional[int] = Field(default=0)

class DailyPlan(BaseModel):
    day: int
    theme: str
    schedule: List[ScheduleItem]

class TripResponse(BaseModel):
    trip_title: str
    overall_summary: str
    plan: List[DailyPlan]

# ----------------------------------------------------
# 2) .env 로드 및 Gemini 설정
# ----------------------------------------------------
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise ValueError("GOOGLE_API_KEY가 .env 또는 Render 환경변수에 설정되지 않았습니다.")

genai.configure(api_key=API_KEY)

ai_model = genai.GenerativeModel(
    'gemini-flash-latest',
    generation_config={
        "response_mime_type": "application/json",
    }
)

# ----------------------------------------------------
# 3) FastAPI & CORS
# ----------------------------------------------------
app = FastAPI(
    title="Plan-AI API",
    description="React 프론트엔드와 통신하는 Plan-AI의 백엔드 API입니다."
)

# 허용 오리진 (프로덕션/프리뷰/로컬)
ALLOW_ORIGIN_REGEX = r"https://.*\.vercel\.app"
origins = [
    "https://aiplanai.vercel.app",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=ALLOW_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],   # OPTIONS 포함
    allow_headers=["*"],
)

# 루트 헬스체크
@app.get("/")
def health():
    return {"status": "ok", "service": "plan-ai"}

# (보강용) 프리플라이트 명시 허용
@app.options("/plan-ai")
def options_plan_ai():
    return Response(status_code=200)

# ----------------------------------------------------
# 4) 프롬프트 빌더
# ----------------------------------------------------
def _build_ai_prompt(request: TripRequest) -> str:
    system_prompt = f"""
당신은 "Plan-AI"이며, 사용자가 제공한 JSON 입력을 기반으로 맞춤형 여행 계획을 생성하는 JSON 출력 전문 AI입니다.

[최우선 규칙]
1) 반드시 아래 OUTPUT_JSON_SCHEMA 구조를 그대로 따르세요.
2) 필드명(trip_title, plan, day, schedule, type 등)을 바꾸거나 임의 추가 금지.
3) 'type'은 'accommodation'|'cafe'|'food'|'activity'|'travel'|'etc'|'shopping'|'sightseeing' 중 하나만 사용.
4) 예산/음식제한/걷기선호 등 제약조건을 충족.

[OUTPUT_JSON_SCHEMA]
```json
{{
  "trip_title": "string",
  "overall_summary": "string",
  "plan": [
    {{
      "day": "int (1부터)",
      "theme": "string",
      "schedule": [
        {{
          "time": "string (예: 14:00)",
          "type": "string ('accommodation'|'cafe'|'food'|'activity'|'travel'|'etc'|'shopping'|'sightseeing')",
          "title": "string",
          "description": "string",
          "location": {{
            "name": "string",
            "address": "string",
            "latitude": "float",
            "longitude": "float"
          }},
          "cost_krw": "int"
        }}
      ]
    }}
  ]
}}
```
"""
    user_request_json = request.model_dump_json(indent=2)
    final_prompt = f"""
{system_prompt}

[사용자 요청 JSON]
{user_request_json}

위 규격(OUTPUT_JSON_SCHEMA)에 맞는 JSON 객체만 반환하십시오.
"""
    return final_prompt

# ----------------------------------------------------
# 5) 공통 생성 로직
# ----------------------------------------------------
async def _create_travel_plan_core(request: TripRequest) -> TripResponse:
    print("--- React로부터 요청 받음 ---")
    ai_prompt = _build_ai_prompt(request)
    print("--- AI에게 보낼 최종 프롬프트 ---")
    print("-" * 50)

    try:
        print("--- AI 호출 시작 ---")
        response = await ai_model.generate_content_async(ai_prompt)
        ai_response_text = (response.text or "").strip()
        print("--- AI 응답 수신 ---")
        print("-" * 50)

        # ```json 코드블록 제거
        if ai_response_text.startswith("```"):
            parts = ai_response_text.split("```")
            if len(parts) >= 2:
                ai_response_text = parts[1].replace("json", "", 1).strip()

        try:
            ai_response_dict = json.loads(ai_response_text)
        except json.JSONDecodeError as e:
            print(f"JSON 파싱 실패: {e}")
            raise Exception("AI가 유효한 JSON을 반환하지 않았습니다.")

        final_response = TripResponse(**ai_response_dict)
        print("--- Pydantic 검증 성공 ---")
        return final_response

    except ValidationError as e:
        print(f"AI 응답 검증 실패: {e}")
        raise HTTPException(status_code=500, detail="AI가 응답 형식을 잘못 생성했습니다. (Validation)")
    except Exception as e:
        print(f"최종 처리 오류: {e}")
        raise HTTPException(status_code=500, detail=f"AI 계획 생성에 실패했습니다. (오류: {e})")

# ----------------------------------------------------
# 6) 엔드포인트 (두 경로 모두 지원)
# ----------------------------------------------------
@app.post("/api/v1/plan", response_model=TripResponse)
async def create_travel_plan_v1(request: TripRequest):
    return await _create_travel_plan_core(request)

@app.post("/plan-ai", response_model=TripResponse)
async def create_travel_plan_alias(request: TripRequest):
    return await _create_travel_plan_core(request)
