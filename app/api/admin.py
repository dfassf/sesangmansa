import logging
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel

from app.config import settings
from app.db.supabase import get_db

router = APIRouter(prefix="/admin")
logger = logging.getLogger(__name__)

BRIEFING_TYPES = {"news", "stock_morning", "stock_evening", "cs_note", "expression"}


def verify_admin_token(authorization: str | None = Header(None)) -> None:
    if not settings.admin_token:
        raise HTTPException(status_code=501, detail="Admin token not configured")
    if authorization != f"Bearer {settings.admin_token}":
        raise HTTPException(status_code=401, detail="Unauthorized")


Auth = Depends(verify_admin_token)


# ── CS ──────────────────────────────────────────────────────────────────────

@router.get("/cs/topics", dependencies=[Auth])
async def get_cs_topics(
    category: str | None = None,
    difficulty: str | None = None,
) -> list[dict[str, Any]]:
    supabase = await get_db()
    q = supabase.from_("cs_topics").select("*").order("category").order("sort_order")
    if category:
        q = q.eq("category", category)
    if difficulty:
        q = q.eq("difficulty", difficulty)
    result = await q.execute()
    return result.data or []


@router.get("/cs/topics/{topic_id}/note", dependencies=[Auth])
async def get_cs_note(topic_id: int) -> dict[str, Any]:
    supabase = await get_db()
    result = await (
        supabase
        .from_("cs_notes")
        .select("id, topic_id, summary, key_points, analogy, quiz, reading_time_min, created_at")
        .eq("topic_id", topic_id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Note not found")
    return result.data[0]


@router.post("/cs/logs/{log_id}/resend", dependencies=[Auth])
async def resend_cs_log(log_id: int) -> dict[str, Any]:
    from app.main import ptb_app
    from app.bot.sender import _get_targets, _send_text
    from app.cs.telegraph import publish_cs_note
    from app.cs.sender import _format_telegram_message as _cs_fmt

    db = await get_db()

    log = await db.from_("cs_sent_log").select("note_id").eq("id", log_id).execute()
    if not log.data:
        raise HTTPException(status_code=404, detail="Log not found")
    note_id = log.data[0]["note_id"]

    note_r = await db.from_("cs_notes").select(
        "id, summary, key_points, analogy, quiz, reading_time_min, cs_topics(title, category, subcategory, difficulty)"
    ).eq("id", note_id).execute()
    if not note_r.data:
        raise HTTPException(status_code=404, detail="Note not found")

    row = note_r.data[0]
    topic = row.pop("cs_topics")
    telegraph_url = await publish_cs_note(note_id)
    text = _cs_fmt(topic, row, telegraph_url)

    targets = await _get_targets("cs_note")
    sent = await _send_text(text, targets, ptb_app.bot)
    return {"recipients": sent}


@router.get("/cs/logs", dependencies=[Auth])
async def get_cs_logs(page: int = 1, page_size: int = 50) -> dict[str, Any]:
    supabase = await get_db()
    offset = (page - 1) * page_size
    result = await (
        supabase
        .from_("cs_sent_log")
        .select("id, note_id, sent_at, cs_notes(topic_id, cs_topics(title, category))")
        .order("sent_at", desc=True)
        .range(offset, offset + page_size - 1)
        .execute()
    )
    return {"items": result.data or [], "page": page, "page_size": page_size}


# ── Expression ──────────────────────────────────────────────────────────────

@router.get("/expr/clusters", dependencies=[Auth])
async def get_expr_clusters(
    category: str | None = None,
    difficulty: str | None = None,
) -> list[dict[str, Any]]:
    supabase = await get_db()
    q = supabase.from_("expr_clusters").select("*").order("category").order("sort_order")
    if category:
        q = q.eq("category", category)
    if difficulty:
        q = q.eq("difficulty", difficulty)
    result = await q.execute()
    return result.data or []


@router.get("/expr/clusters/{cluster_id}/note", dependencies=[Auth])
async def get_expr_note(cluster_id: int) -> dict[str, Any]:
    supabase = await get_db()
    result = await (
        supabase
        .from_("expr_notes")
        .select("id, cluster_id, intro, expressions, comparison, usage_tip, created_at")
        .eq("cluster_id", cluster_id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Note not found")
    return result.data[0]


@router.post("/expr/logs/{log_id}/resend", dependencies=[Auth])
async def resend_expr_log(log_id: int) -> dict[str, Any]:
    from app.main import ptb_app
    from app.bot.sender import _get_targets, _send_text
    from app.expression.sender import _format_telegram_message as _expr_fmt

    db = await get_db()

    log = await db.from_("expr_sent_log").select("note_id").eq("id", log_id).execute()
    if not log.data:
        raise HTTPException(status_code=404, detail="Log not found")
    note_id = log.data[0]["note_id"]

    note_r = await db.from_("expr_notes").select(
        "id, intro, expressions, comparison, usage_tip, expr_clusters(base_word, category)"
    ).eq("id", note_id).execute()
    if not note_r.data:
        raise HTTPException(status_code=404, detail="Note not found")

    row = note_r.data[0]
    cluster = row.pop("expr_clusters")
    text = _expr_fmt(cluster, row)

    targets = await _get_targets("expression")
    sent = await _send_text(text, targets, ptb_app.bot)
    return {"recipients": sent}


@router.get("/expr/logs", dependencies=[Auth])
async def get_expr_logs(page: int = 1, page_size: int = 50) -> dict[str, Any]:
    supabase = await get_db()
    offset = (page - 1) * page_size
    result = await (
        supabase
        .from_("expr_sent_log")
        .select("id, note_id, sent_at, expr_notes(cluster_id, expr_clusters(base_word, category))")
        .order("sent_at", desc=True)
        .range(offset, offset + page_size - 1)
        .execute()
    )
    return {"items": result.data or [], "page": page, "page_size": page_size}


# ── Subscriptions ────────────────────────────────────────────────────────────

class SubscriptionCreate(BaseModel):
    label: str | None = None
    chat_id: int
    bot_token: str
    briefing_types: list[str]
    active: bool = True

    def validate_types(self) -> None:
        invalid = set(self.briefing_types) - BRIEFING_TYPES
        if invalid:
            raise HTTPException(status_code=422, detail=f"Invalid briefing_types: {invalid}")


class SubscriptionPatch(BaseModel):
    label: str | None = None
    briefing_types: list[str] | None = None
    active: bool | None = None


@router.get("/subscriptions", dependencies=[Auth])
async def list_subscriptions() -> list[dict[str, Any]]:
    supabase = await get_db()
    result = await (
        supabase
        .from_("subscriptions")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )
    return result.data or []


@router.post("/subscriptions", dependencies=[Auth], status_code=201)
async def create_subscription(body: SubscriptionCreate) -> dict[str, Any]:
    body.validate_types()
    supabase = await get_db()
    result = await (
        supabase
        .from_("subscriptions")
        .insert({
            "label": body.label,
            "chat_id": body.chat_id,
            "bot_token": body.bot_token,
            "briefing_types": body.briefing_types,
            "active": body.active,
        })
        .execute()
    )
    return result.data[0]


@router.patch("/subscriptions/{sub_id}", dependencies=[Auth])
async def update_subscription(sub_id: int, body: SubscriptionPatch) -> dict[str, Any]:
    if body.briefing_types is not None:
        invalid = set(body.briefing_types) - BRIEFING_TYPES
        if invalid:
            raise HTTPException(status_code=422, detail=f"Invalid briefing_types: {invalid}")

    updates: dict[str, Any] = {}
    if body.label is not None:
        updates["label"] = body.label
    if body.briefing_types is not None:
        updates["briefing_types"] = body.briefing_types
    if body.active is not None:
        updates["active"] = body.active

    if not updates:
        raise HTTPException(status_code=422, detail="No fields to update")

    supabase = await get_db()
    result = await (
        supabase
        .from_("subscriptions")
        .update(updates)
        .eq("id", sub_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return result.data[0]


@router.delete("/subscriptions/{sub_id}", dependencies=[Auth], status_code=204)
async def delete_subscription(sub_id: int) -> None:
    supabase = await get_db()
    await supabase.from_("subscriptions").delete().eq("id", sub_id).execute()
