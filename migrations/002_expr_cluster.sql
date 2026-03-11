-- 표현 모듈 클러스터 기반 재설계
-- 기존 빈 테이블 삭제 후 새 스키마 생성

-- ==========================================
-- 기존 테이블 삭제 (데이터 없음, 시딩 전)
-- ==========================================

DROP TABLE IF EXISTS expr_sent_log;
DROP TABLE IF EXISTS expr_notes;
DROP TABLE IF EXISTS expr_topics;
DROP FUNCTION IF EXISTS pick_next_expression_topic();

-- ==========================================
-- 클러스터 테이블
-- ==========================================

CREATE TABLE expr_clusters (
    id SERIAL PRIMARY KEY,
    category TEXT NOT NULL,
    base_word TEXT NOT NULL UNIQUE,
    expressions JSONB NOT NULL,
    difficulty TEXT NOT NULL CHECK (difficulty IN ('beginner', 'intermediate', 'advanced')),
    sort_order INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_expr_clusters_category ON expr_clusters (category, sort_order);

-- ==========================================
-- 노트 테이블
-- ==========================================

CREATE TABLE expr_notes (
    id SERIAL PRIMARY KEY,
    cluster_id INTEGER NOT NULL REFERENCES expr_clusters(id),
    intro TEXT NOT NULL,
    expressions JSONB NOT NULL,
    comparison TEXT NOT NULL,
    usage_tip TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_expr_notes_cluster ON expr_notes (cluster_id);

-- ==========================================
-- 발송 로그
-- ==========================================

CREATE TABLE expr_sent_log (
    id SERIAL PRIMARY KEY,
    note_id INTEGER NOT NULL REFERENCES expr_notes(id),
    sent_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_expr_sent_log_sent ON expr_sent_log (sent_at);

-- ==========================================
-- RPC: 다음 클러스터 선택
-- ==========================================

CREATE OR REPLACE FUNCTION pick_next_expression_cluster()
RETURNS SETOF expr_clusters
LANGUAGE sql STABLE
AS $$
    (
        SELECT c.*
        FROM expr_clusters c
        LEFT JOIN expr_notes n ON n.cluster_id = c.id
        WHERE n.id IS NULL
        ORDER BY c.category, c.sort_order
        LIMIT 1
    )
    UNION ALL
    (
        SELECT c.*
        FROM expr_clusters c
        JOIN expr_notes n ON n.cluster_id = c.id
        LEFT JOIN expr_sent_log sl ON sl.note_id = n.id
        WHERE NOT EXISTS (
            SELECT 1 FROM expr_clusters c2
            LEFT JOIN expr_notes n2 ON n2.cluster_id = c2.id
            WHERE n2.id IS NULL
        )
        GROUP BY c.id
        ORDER BY MAX(sl.sent_at) ASC NULLS FIRST
        LIMIT 1
    )
    LIMIT 1;
$$;
