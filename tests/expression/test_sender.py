from unittest.mock import AsyncMock, MagicMock

import pytest

from app.expression import sender as expr_sender


@pytest.mark.asyncio
async def test_prepare_expression_briefing_returns_error_when_no_topics(monkeypatch):
    mock_supabase = MagicMock()
    mock_supabase.rpc.return_value.execute = AsyncMock(
        return_value=MagicMock(data=[]),
    )
    monkeypatch.setattr(expr_sender, "get_supabase", AsyncMock(return_value=mock_supabase))

    result = await expr_sender.prepare_expression_briefing()

    assert "error" in result


def test_format_telegram_message_includes_all_sections():
    topic = {
        "category": "adverb_degree",
        "expression": "자못",
        "common_alternative": "꽤/상당히",
    }
    note = {
        "id": 1,
        "meaning": "꽤, 상당히라는 뜻입니다.",
        "example_sentences": ["자못 진지한 표정", "자못 심각한 분위기", "자못 비장한 각오"],
        "nuance": "되게보다 문어적이고 무게감이 있어요.",
        "similar_expressions": ["사뭇", "제법"],
        "usage_tip": "글쓰기에서 쓰면 자연스럽습니다.",
    }

    text = expr_sender._format_telegram_message(topic, note)

    assert "📏 오늘의 표현" in text
    assert "「자못」" in text
    assert "꽤/상당히" in text
    assert "자못 진지한 표정" in text
    assert "사뭇" in text
    assert "글쓰기에서" in text


def test_format_telegram_message_without_optional_fields():
    topic = {"category": "idiom", "expression": "고진감래", "common_alternative": "고생 끝에 낙"}
    note = {
        "id": 2,
        "meaning": "고생 끝에 즐거움이 온다.",
        "example_sentences": ["예문1", "예문2"],
        "nuance": "힘든 시기를 겪은 후에 쓰면 좋아요.",
        "similar_expressions": None,
        "usage_tip": None,
    }

    text = expr_sender._format_telegram_message(topic, note)

    assert "📜 오늘의 표현" in text
    assert "🔄" not in text
    assert "💡" not in text
