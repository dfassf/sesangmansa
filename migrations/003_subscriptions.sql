-- Migration 003: 봇-채팅방 구독 매핑 테이블
-- 어떤 봇(bot_token)이 어떤 채팅방(chat_id)에 어떤 유형의 브리핑을 보낼지 관리

CREATE TABLE subscriptions (
    id SERIAL PRIMARY KEY,
    label TEXT,                            -- 표시용 이름 (예: "메인 채팅방", "주식 전용")
    chat_id BIGINT NOT NULL,
    bot_token TEXT NOT NULL,
    briefing_types TEXT[] NOT NULL,        -- ['news', 'stock_morning', 'stock_evening', 'cs_note', 'expression']
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(bot_token, chat_id)
);

CREATE INDEX idx_subscriptions_active ON subscriptions(active);
CREATE INDEX idx_subscriptions_briefing_types ON subscriptions USING gin(briefing_types);
