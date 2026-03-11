import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.expression import generator


@pytest.mark.asyncio
async def test_generate_expression_note_creates_note(monkeypatch):
    gemini_response = MagicMock()
    gemini_response.text = json.dumps({
        "meaning": "꽤, 상당히라는 뜻입니다.",
        "example_sentences": ["자못 진지한 표정", "자못 심각한 분위기", "자못 비장한 각오"],
        "nuance": "되게보다 문어적이고 무게감이 있어요.",
        "similar_expressions": ["사뭇", "제법"],
        "usage_tip": "글쓰기에서 쓰면 자연스럽습니다.",
    })

    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(return_value=gemini_response)
    monkeypatch.setattr(generator, "_client", lambda: mock_client)

    mock_supabase = MagicMock()
    mock_insert = MagicMock()
    mock_insert.execute = AsyncMock(return_value=MagicMock(data=[{"id": 10}]))
    mock_supabase.from_.return_value.insert.return_value = mock_insert
    monkeypatch.setattr(generator, "get_supabase", AsyncMock(return_value=mock_supabase))

    result = await generator.generate_expression_note({
        "id": 1,
        "expression": "자못",
        "common_alternative": "꽤/상당히",
    })

    assert result["status"] == "created"
    assert result["note_id"] == 10


@pytest.mark.asyncio
async def test_generate_expression_note_handles_empty_response(monkeypatch):
    gemini_response = MagicMock()
    gemini_response.text = ""

    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(return_value=gemini_response)
    monkeypatch.setattr(generator, "_client", lambda: mock_client)

    result = await generator.generate_expression_note({
        "id": 1,
        "expression": "자못",
        "common_alternative": "꽤",
    })

    assert result["status"] == "error"
