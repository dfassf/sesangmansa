import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.expression import generator


@pytest.mark.asyncio
async def test_generate_expression_note_creates_note(monkeypatch):
    gemini_response = MagicMock()
    gemini_response.text = json.dumps({
        "intro": "'매우'나 '되게' 대신 이 표현들을 쓰면 문장에 깊이가 생깁니다.",
        "expressions": [
            {"word": "자못", "meaning": "꽤, 상당히", "example": "자못 진지한 표정", "nuance": "문어적이고 무게감"},
            {"word": "한껏", "meaning": "최대한", "example": "한껏 멋을 부렸다", "nuance": "최대치 강조"},
            {"word": "사뭇", "meaning": "꽤, 예상 밖으로", "example": "분위기가 사뭇 달랐다", "nuance": "예상과 다른 정도"},
            {"word": "더없이", "meaning": "더할 나위 없이", "example": "더없이 행복했다", "nuance": "최상급 표현"},
            {"word": "지극히", "meaning": "매우, 극히", "example": "지극히 개인적인 이야기", "nuance": "극한 강조"},
        ],
        "comparison": "자못은 문어적, 한껏은 최대치, 사뭇은 예상 밖, 더없이는 최상급, 지극히는 극한.",
        "usage_tip": "글에서 '매우'를 반복하지 않으려면 이 표현들을 섞어 쓰세요.",
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
        "base_word": "매우/되게",
        "expressions": ["자못", "한껏", "사뭇", "더없이", "지극히"],
    })

    assert result["status"] == "created"
    assert result["note_id"] == 10

    insert_call = mock_supabase.from_.return_value.insert.call_args[0][0]
    assert insert_call["cluster_id"] == 1
    assert insert_call["intro"] == "'매우'나 '되게' 대신 이 표현들을 쓰면 문장에 깊이가 생깁니다."
    assert len(insert_call["expressions"]) == 5


@pytest.mark.asyncio
async def test_generate_expression_note_handles_empty_response(monkeypatch):
    gemini_response = MagicMock()
    gemini_response.text = ""

    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(return_value=gemini_response)
    monkeypatch.setattr(generator, "_client", lambda: mock_client)

    result = await generator.generate_expression_note({
        "id": 1,
        "base_word": "매우/되게",
        "expressions": ["자못", "한껏", "사뭇", "더없이", "지극히"],
    })

    assert result["status"] == "error"
