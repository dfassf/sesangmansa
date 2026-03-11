import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.cs import generator


@pytest.mark.asyncio
async def test_generate_cs_note_returns_duplicate_when_detected(monkeypatch):
    monkeypatch.setattr(
        generator, "check_duplicate",
        AsyncMock(return_value=("duplicate", [{"id": 1, "similarity": 0.95}], [])),
    )

    result = await generator.generate_cs_note({
        "id": 1,
        "category": "os",
        "subcategory": "process",
        "title": "프로세스 vs 스레드",
        "difficulty": "beginner",
    })

    assert result["status"] == "duplicate"


@pytest.mark.asyncio
async def test_generate_cs_note_creates_note_on_new(monkeypatch):
    monkeypatch.setattr(
        generator, "check_duplicate",
        AsyncMock(return_value=("new", [], [])),
    )
    monkeypatch.setattr(
        generator, "generate_embedding",
        AsyncMock(return_value=[0.1] * 768),
    )

    gemini_response = MagicMock()
    gemini_response.text = json.dumps({
        "content": "<b>본문</b>",
        "summary": "요약입니다",
        "key_points": ["포인트1", "포인트2"],
        "analogy": "비유",
        "quiz": {"question": "퀴즈?", "options": ["A", "B", "C", "D"], "answer": 0},
        "reading_time_min": 3,
    })

    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(return_value=gemini_response)
    monkeypatch.setattr(generator, "_client", lambda: mock_client)

    mock_supabase = MagicMock()
    mock_insert = MagicMock()
    mock_insert.execute = AsyncMock(return_value=MagicMock(data=[{"id": 42}]))
    mock_supabase.from_.return_value.insert.return_value = mock_insert
    monkeypatch.setattr(generator, "get_supabase", AsyncMock(return_value=mock_supabase))

    result = await generator.generate_cs_note({
        "id": 1,
        "category": "os",
        "subcategory": "process",
        "title": "프로세스 vs 스레드",
        "difficulty": "beginner",
    })

    assert result["status"] == "created"
    assert result["note_id"] == 42


@pytest.mark.asyncio
async def test_generate_cs_note_handles_empty_response(monkeypatch):
    monkeypatch.setattr(
        generator, "check_duplicate",
        AsyncMock(return_value=("new", [], [])),
    )

    gemini_response = MagicMock()
    gemini_response.text = ""

    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(return_value=gemini_response)
    monkeypatch.setattr(generator, "_client", lambda: mock_client)

    result = await generator.generate_cs_note({
        "id": 1,
        "category": "os",
        "subcategory": "process",
        "title": "테스트",
        "difficulty": "beginner",
    })

    assert result["status"] == "error"
