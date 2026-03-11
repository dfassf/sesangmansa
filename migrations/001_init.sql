-- morning-sesangmansa 고도화: CS 노트 + 어휘 표현 모듈
-- Supabase SQL Editor에서 실행

CREATE EXTENSION IF NOT EXISTS vector;

-- ==========================================
-- CS Note 테이블
-- ==========================================

CREATE TABLE cs_topics (
    id SERIAL PRIMARY KEY,
    category TEXT NOT NULL,
    subcategory TEXT NOT NULL,
    title TEXT NOT NULL UNIQUE,
    sort_order INTEGER NOT NULL,
    difficulty TEXT NOT NULL CHECK (difficulty IN ('beginner', 'intermediate', 'advanced')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_cs_topics_category ON cs_topics (category, sort_order);

CREATE TABLE cs_notes (
    id SERIAL PRIMARY KEY,
    topic_id INTEGER NOT NULL REFERENCES cs_topics(id),
    content TEXT NOT NULL,
    summary TEXT NOT NULL,
    key_points JSONB NOT NULL,
    analogy TEXT,
    quiz JSONB,
    reading_time_min INTEGER NOT NULL DEFAULT 3,
    embedding vector(768),
    version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_cs_notes_topic ON cs_notes (topic_id);
CREATE INDEX idx_cs_notes_embedding ON cs_notes
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 10);

CREATE TABLE cs_sent_log (
    id SERIAL PRIMARY KEY,
    note_id INTEGER NOT NULL REFERENCES cs_notes(id),
    sent_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_cs_sent_log_sent ON cs_sent_log (sent_at);

CREATE TABLE cs_telegraph_articles (
    id SERIAL PRIMARY KEY,
    note_id INTEGER NOT NULL UNIQUE REFERENCES cs_notes(id),
    url TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ==========================================
-- Expression (수식어/부사) 테이블
-- ==========================================

CREATE TABLE expr_topics (
    id SERIAL PRIMARY KEY,
    category TEXT NOT NULL,
    expression TEXT NOT NULL UNIQUE,
    common_alternative TEXT NOT NULL,
    difficulty TEXT NOT NULL CHECK (difficulty IN ('beginner', 'intermediate', 'advanced')),
    sort_order INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_expr_topics_category ON expr_topics (category, sort_order);

CREATE TABLE expr_notes (
    id SERIAL PRIMARY KEY,
    topic_id INTEGER NOT NULL REFERENCES expr_topics(id),
    meaning TEXT NOT NULL,
    example_sentences JSONB NOT NULL,
    nuance TEXT NOT NULL,
    similar_expressions JSONB,
    usage_tip TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_expr_notes_topic ON expr_notes (topic_id);

CREATE TABLE expr_sent_log (
    id SERIAL PRIMARY KEY,
    note_id INTEGER NOT NULL REFERENCES expr_notes(id),
    sent_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_expr_sent_log_sent ON expr_sent_log (sent_at);

-- ==========================================
-- RPC 함수
-- ==========================================

-- CS 노트 유사도 검색
CREATE OR REPLACE FUNCTION match_cs_notes(
    query_embedding vector(768),
    match_threshold float DEFAULT 0.75,
    match_count int DEFAULT 5
)
RETURNS TABLE (
    id int,
    topic_id int,
    similarity float
)
LANGUAGE sql STABLE
AS $$
    SELECT
        cs_notes.id,
        cs_notes.topic_id,
        1 - (cs_notes.embedding <=> query_embedding) AS similarity
    FROM cs_notes
    WHERE cs_notes.embedding IS NOT NULL
    AND 1 - (cs_notes.embedding <=> query_embedding) > match_threshold
    ORDER BY cs_notes.embedding <=> query_embedding
    LIMIT match_count;
$$;

-- 다음 CS 토픽 선택 (노트 미생성 우선, 없으면 가장 오래전 발송된 것)
CREATE OR REPLACE FUNCTION pick_next_cs_topic()
RETURNS SETOF cs_topics
LANGUAGE sql STABLE
AS $$
    (
        SELECT t.*
        FROM cs_topics t
        LEFT JOIN cs_notes n ON n.topic_id = t.id
        WHERE n.id IS NULL
        ORDER BY t.category, t.sort_order
        LIMIT 1
    )
    UNION ALL
    (
        SELECT t.*
        FROM cs_topics t
        JOIN cs_notes n ON n.topic_id = t.id
        LEFT JOIN cs_sent_log sl ON sl.note_id = n.id
        WHERE NOT EXISTS (
            SELECT 1 FROM cs_topics t2
            LEFT JOIN cs_notes n2 ON n2.topic_id = t2.id
            WHERE n2.id IS NULL
        )
        GROUP BY t.id
        ORDER BY MAX(sl.sent_at) ASC NULLS FIRST
        LIMIT 1
    )
    LIMIT 1;
$$;

-- 다음 표현 토픽 선택
CREATE OR REPLACE FUNCTION pick_next_expression_topic()
RETURNS SETOF expr_topics
LANGUAGE sql STABLE
AS $$
    (
        SELECT t.*
        FROM expr_topics t
        LEFT JOIN expr_notes n ON n.topic_id = t.id
        WHERE n.id IS NULL
        ORDER BY t.category, t.sort_order
        LIMIT 1
    )
    UNION ALL
    (
        SELECT t.*
        FROM expr_topics t
        JOIN expr_notes n ON n.topic_id = t.id
        LEFT JOIN expr_sent_log sl ON sl.note_id = n.id
        WHERE NOT EXISTS (
            SELECT 1 FROM expr_topics t2
            LEFT JOIN expr_notes n2 ON n2.topic_id = t2.id
            WHERE n2.id IS NULL
        )
        GROUP BY t.id
        ORDER BY MAX(sl.sent_at) ASC NULLS FIRST
        LIMIT 1
    )
    LIMIT 1;
$$;
