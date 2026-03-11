from unittest.mock import AsyncMock, MagicMock

import pytest

from app.cs import sender as cs_sender


@pytest.mark.asyncio
async def test_prepare_cs_briefing_returns_error_when_no_topics(monkeypatch):
    mock_supabase = MagicMock()
    mock_supabase.rpc.return_value.execute = AsyncMock(
        return_value=MagicMock(data=[]),
    )
    monkeypatch.setattr(cs_sender, "get_supabase", AsyncMock(return_value=mock_supabase))

    result = await cs_sender.prepare_cs_briefing()

    assert "error" in result


@pytest.mark.asyncio
async def test_format_telegram_message_includes_quiz():
    topic = {"category": "os", "subcategory": "process", "title": "테스트", "difficulty": "beginner"}
    note = {
        "summary": "요약입니다",
        "key_points": ["a"],
        "analogy": "비유",
        "quiz": {"question": "퀴즈?", "options": ["A", "B", "C", "D"], "answer": 0},
    }

    text = cs_sender._format_telegram_message(topic, note, "https://telegra.ph/test")

    assert "🖥️ 오늘의 CS 노트" in text
    assert "테스트" in text
    assert "기초" in text
    assert "퀴즈?" in text
    assert "https://telegra.ph/test" in text


@pytest.mark.asyncio
async def test_format_telegram_message_without_quiz():
    topic = {"category": "database", "subcategory": "index", "title": "인덱스", "difficulty": "intermediate"}
    note = {"summary": "요약", "key_points": ["a"], "analogy": "비유", "quiz": None}

    text = cs_sender._format_telegram_message(topic, note, "https://telegra.ph/test")

    assert "🗄️ 오늘의 CS 노트" in text
    assert "퀴즈" not in text
