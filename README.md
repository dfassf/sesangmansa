# morning-sesangmansa

매일 아침 AI 뉴스·주식 브리핑을 텔레그램으로 보내주는 봇

## 기능

- **뉴스 브리핑** — Google 검색 기반 주요 뉴스 수집 + Gemini AI 요약
- **주식 브리핑** — 아침(미국 시장 마감), 저녁(한국 시장 마감) 2회
- **월요일 주말 요약** — 주말 동안의 주요 뉴스/시장 동향 종합
- **주말 자동 스킵** — 토·일요일은 브리핑 미발송
- **온디맨드 브리핑** — `/briefing` 명령어로 즉시 브리핑

## 기술 스택

- **Backend**: FastAPI + Uvicorn
- **AI**: Google Gemini 2.5 Flash (검색 + 요약)
- **Bot**: python-telegram-bot (Webhook 모드)
- **배포**: Google Cloud Run + Cloud Scheduler
- **Python**: 3.12+

## 프로젝트 구조

```
app/
├── main.py            # FastAPI 앱 + PTB 라이프사이클
├── config.py          # 환경변수 설정 (Pydantic Settings)
├── ai/
│   ├── prompts.py     # Gemini 프롬프트 템플릿
│   └── summarizer.py  # AI 요약 생성
├── api/
│   └── routes.py      # Webhook + 브리핑 발송 엔드포인트
├── bot/
│   ├── handlers.py    # 텔레그램 커맨드 핸들러
│   └── sender.py      # 브리핑 파이프라인
└── news/
    └── fetcher.py     # Gemini 검색 기반 뉴스 수집
tests/                 # 단위 + E2E 테스트
```

## 설정

`.env.example`을 `.env`로 복사하고 값을 채워주세요:

```env
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_IDS=123456,789012
TELEGRAM_WEBHOOK_SECRET=...
GEMINI_API_KEY=...
WEBHOOK_BASE_URL=https://your-domain.run.app
SCHEDULER_AUTH_TOKEN=...
```

## 실행

```bash
# 의존성 설치
pip install -e .

# 로컬 실행
uvicorn app.main:app --reload

# 테스트
pytest
```

## 브리핑 스케줄

| 시간 | 유형 | 설명 |
|------|------|------|
| 08:00 | news | 일반 뉴스 브리핑 |
| 08:00 | stock_morning | 미국 시장 마감 브리핑 |
| 18:30 | stock_evening | 한국 시장 마감 브리핑 |

## 텔레그램 명령어

- `/start` — 봇 시작 + 채팅 ID 확인
- `/briefing` — 현재 시간 기준 즉시 브리핑
- `/help` — 도움말
