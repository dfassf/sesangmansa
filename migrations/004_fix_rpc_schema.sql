-- Migration 004: RPC 함수 sesangmansa 스키마 참조로 업데이트
-- 테이블을 sesangmansa 스키마로 이전 후 RPC 함수가 public 스키마를 참조해 깨진 문제 수정

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
    FROM sesangmansa.cs_notes
    WHERE sesangmansa.cs_notes.embedding IS NOT NULL
    AND 1 - (sesangmansa.cs_notes.embedding <=> query_embedding) > match_threshold
    ORDER BY sesangmansa.cs_notes.embedding <=> query_embedding
    LIMIT match_count;
$$;

-- 다음 CS 토픽 선택
CREATE OR REPLACE FUNCTION pick_next_cs_topic()
RETURNS SETOF sesangmansa.cs_topics
LANGUAGE sql STABLE
AS $$
    (
        SELECT t.*
        FROM sesangmansa.cs_topics t
        LEFT JOIN sesangmansa.cs_notes n ON n.topic_id = t.id
        WHERE n.id IS NULL
        ORDER BY t.category, t.sort_order
        LIMIT 1
    )
    UNION ALL
    (
        SELECT t.*
        FROM sesangmansa.cs_topics t
        JOIN sesangmansa.cs_notes n ON n.topic_id = t.id
        LEFT JOIN sesangmansa.cs_sent_log sl ON sl.note_id = n.id
        WHERE NOT EXISTS (
            SELECT 1 FROM sesangmansa.cs_topics t2
            LEFT JOIN sesangmansa.cs_notes n2 ON n2.topic_id = t2.id
            WHERE n2.id IS NULL
        )
        GROUP BY t.id
        ORDER BY MAX(sl.sent_at) ASC NULLS FIRST
        LIMIT 1
    )
    LIMIT 1;
$$;

-- 다음 표현 클러스터 선택
CREATE OR REPLACE FUNCTION pick_next_expression_cluster()
RETURNS SETOF sesangmansa.expr_clusters
LANGUAGE sql STABLE
AS $$
    (
        SELECT c.*
        FROM sesangmansa.expr_clusters c
        LEFT JOIN sesangmansa.expr_notes n ON n.cluster_id = c.id
        WHERE n.id IS NULL
        ORDER BY c.category, c.sort_order
        LIMIT 1
    )
    UNION ALL
    (
        SELECT c.*
        FROM sesangmansa.expr_clusters c
        JOIN sesangmansa.expr_notes n ON n.cluster_id = c.id
        LEFT JOIN sesangmansa.expr_sent_log sl ON sl.note_id = n.id
        WHERE NOT EXISTS (
            SELECT 1 FROM sesangmansa.expr_clusters c2
            LEFT JOIN sesangmansa.expr_notes n2 ON n2.cluster_id = c2.id
            WHERE n2.id IS NULL
        )
        GROUP BY c.id
        ORDER BY MAX(sl.sent_at) ASC NULLS FIRST
        LIMIT 1
    )
    LIMIT 1;
$$;
