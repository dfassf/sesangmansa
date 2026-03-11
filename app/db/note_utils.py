from typing import Any, Awaitable, Callable

GenerateNoteFn = Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]


async def load_latest_note_by_topic(
    supabase: Any,
    *,
    table: str,
    select_fields: str,
    topic_id: int,
) -> dict[str, Any] | None:
    result = await (
        supabase
        .from_(table)
        .select(select_fields)
        .eq("topic_id", topic_id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    if not result.data:
        return None
    return result.data[0]


async def load_or_create_note(
    supabase: Any,
    *,
    table: str,
    select_fields: str,
    topic: dict[str, Any],
    generate_note: GenerateNoteFn,
) -> tuple[dict[str, Any] | None, str | None]:
    note = await load_latest_note_by_topic(
        supabase,
        table=table,
        select_fields=select_fields,
        topic_id=topic["id"],
    )
    if note is not None:
        return note, None

    generated = await generate_note(topic)
    if generated.get("status") != "created":
        return None, generated.get("message", "생성 실패")

    note_id = generated["note_id"]
    note_result = await (
        supabase
        .from_(table)
        .select(select_fields)
        .eq("id", note_id)
        .single()
        .execute()
    )
    if not note_result.data:
        return None, f"생성된 노트를 찾을 수 없습니다: {note_id}"

    return note_result.data, None


async def insert_sent_log(supabase: Any, *, table: str, note_id: int) -> None:
    await supabase.from_(table).insert({"note_id": note_id}).execute()
