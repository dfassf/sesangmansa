from unittest.mock import AsyncMock, MagicMock

import pytest

from app.expression import sender as expr_sender


@pytest.mark.asyncio
async def test_prepare_expression_briefing_returns_error_when_no_clusters(monkeypatch):
    mock_supabase = MagicMock()
    mock_supabase.rpc.return_value.execute = AsyncMock(
        return_value=MagicMock(data=[]),
    )
    monkeypatch.setattr(expr_sender, "get_supabase", AsyncMock(return_value=mock_supabase))

    result = await expr_sender.prepare_expression_briefing()

    assert "error" in result
    assert "클러스터" in result["error"]


def test_format_telegram_message_includes_all_sections():
    cluster = {
        "category": "adverb_degree",
        "base_word": "매우/되게",
    }
    note = {
        "id": 1,
        "intro": "'매우' 대신 이 표현들을 써보세요.",
        "expressions": [
            {"word": "자못", "meaning": "꽤, 상당히", "example": "자못 진지한 표정", "nuance": "문어적 무게감"},
            {"word": "한껏", "meaning": "최대한", "example": "한껏 멋을 부렸다", "nuance": "최대치 강조"},
            {"word": "사뭇", "meaning": "꽤, 예상 밖", "example": "분위기가 사뭇 달랐다", "nuance": "예상과 다른 정도"},
            {"word": "더없이", "meaning": "더할 나위 없이", "example": "더없이 행복했다", "nuance": "최상급"},
            {"word": "지극히", "meaning": "매우, 극히", "example": "지극히 개인적인 이야기", "nuance": "극한 강조"},
        ],
        "comparison": "자못은 문어적, 한껏은 최대치.",
        "usage_tip": "글에서 매우를 반복하지 않으려면 섞어 쓰세요.",
    }

    text = expr_sender._format_telegram_message(cluster, note)

    assert "📏 오늘의 표현" in text
    assert "「매우/되게」 대신 쓸 수 있는 표현들" in text
    assert "🔤 자못 — 꽤, 상당히" in text
    assert "자못 진지한 표정" in text
    assert "🔤 한껏" in text
    assert "🎯" in text
    assert "💡" in text


def test_format_telegram_message_without_usage_tip():
    cluster = {"category": "idiom", "base_word": "노력과 보상"}
    note = {
        "id": 2,
        "intro": "노력에 대한 사자성어들입니다.",
        "expressions": [
            {"word": "고진감래", "meaning": "고생 끝 낙", "example": "고진감래라더니 합격했다", "nuance": "고생 후 보상"},
        ],
        "comparison": "각각 다른 측면의 노력을 표현합니다.",
        "usage_tip": None,
    }

    text = expr_sender._format_telegram_message(cluster, note)

    assert "📜 오늘의 표현" in text
    assert "💡" not in text
