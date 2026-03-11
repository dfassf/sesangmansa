from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.db.note_utils import (
    insert_sent_log,
    load_latest_note_by_topic,
    load_or_create_note,
)


class FakeSupabase:
    def __init__(self, *, latest_data, by_id_data):
        self.latest_data = latest_data
        self.by_id_data = by_id_data
        self._eq_key = None
        self.insert_payload = None

    def from_(self, _table):
        return self

    def select(self, _fields):
        return self

    def eq(self, key, _value):
        self._eq_key = key
        return self

    def order(self, *_args, **_kwargs):
        return self

    def limit(self, _n):
        return self

    def single(self):
        return self

    def insert(self, payload):
        self.insert_payload = payload
        return self

    async def execute(self):
        if self._eq_key in ("topic_id", "cluster_id"):
            return SimpleNamespace(data=self.latest_data)
        if self._eq_key == "id":
            return SimpleNamespace(data=self.by_id_data)
        return SimpleNamespace(data=None)


@pytest.mark.asyncio
async def test_load_latest_note_by_topic_returns_note():
    supabase = FakeSupabase(
        latest_data=[{"id": 1, "summary": "요약"}],
        by_id_data=None,
    )

    note = await load_latest_note_by_topic(
        supabase,
        table="cs_notes",
        select_fields="id, summary",
        topic_id=10,
    )

    assert note == {"id": 1, "summary": "요약"}


@pytest.mark.asyncio
async def test_load_or_create_note_returns_existing_note():
    supabase = FakeSupabase(
        latest_data=[{"id": 7, "summary": "기존"}],
        by_id_data=None,
    )
    generate = AsyncMock()

    note, error = await load_or_create_note(
        supabase,
        table="cs_notes",
        select_fields="id, summary",
        topic={"id": 3, "title": "테스트"},
        generate_note=generate,
    )

    assert error is None
    assert note == {"id": 7, "summary": "기존"}
    generate.assert_not_awaited()


@pytest.mark.asyncio
async def test_load_or_create_note_creates_when_missing():
    supabase = FakeSupabase(
        latest_data=[],
        by_id_data={"id": 12, "summary": "신규"},
    )
    generate = AsyncMock(return_value={"status": "created", "note_id": 12})

    note, error = await load_or_create_note(
        supabase,
        table="cs_notes",
        select_fields="id, summary",
        topic={"id": 3, "title": "테스트"},
        generate_note=generate,
    )

    assert error is None
    assert note == {"id": 12, "summary": "신규"}
    generate.assert_awaited_once()


@pytest.mark.asyncio
async def test_load_or_create_note_returns_generation_error():
    supabase = FakeSupabase(
        latest_data=[],
        by_id_data=None,
    )
    generate = AsyncMock(return_value={"status": "error", "message": "생성 실패"})

    note, error = await load_or_create_note(
        supabase,
        table="cs_notes",
        select_fields="id, summary",
        topic={"id": 3, "title": "테스트"},
        generate_note=generate,
    )

    assert note is None
    assert error == "생성 실패"


@pytest.mark.asyncio
async def test_insert_sent_log_inserts_note_id():
    supabase = FakeSupabase(
        latest_data=None,
        by_id_data=None,
    )

    await insert_sent_log(supabase, table="cs_sent_log", note_id=99)

    assert supabase.insert_payload == {"note_id": 99}
