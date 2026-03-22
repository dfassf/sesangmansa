import logging
from typing import Any, Awaitable, Callable

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from pydantic import BaseModel

from app.config import settings
from app.cs.sender import resend_cs_note
from app.db.supabase import get_db
from app.expression.sender import resend_expr_note

router = APIRouter(prefix="/admin")
logger = logging.getLogger(__name__)

BRIEFING_TYPES = {"news", "stock_morning", "stock_evening", "cs_note", "expression"}


def verify_admin_token(authorization: str | None = Header(None)) -> None:
    if not settings.admin_token:
        raise HTTPException(status_code=501, detail="Admin token not configured")
    if authorization != f"Bearer {settings.admin_token}":
        raise HTTPException(status_code=401, detail="Unauthorized")


Auth = Depends(verify_admin_token)

ResendFn = Callable[[int, Any], Awaitable[int]]


def _validate_briefing_types(types: list[str]) -> None:
    invalid = set(types) - BRIEFING_TYPES
    if invalid:
        raise HTTPException(status_code=422, detail=f"Invalid briefing_types: {invalid}")


async def _list_curriculum_rows(
    *,
    table: str,
    category: str | None,
    difficulty: str | None,
) -> list[dict[str, Any]]:
    supabase = await get_db()
    query = supabase.from_(table).select("*").order("category").order("sort_order")
    if category:
        query = query.eq("category", category)
    if difficulty:
        query = query.eq("difficulty", difficulty)
    result = await query.execute()
    return result.data or []


async def _get_latest_note(
    *,
    table: str,
    fk_column: str,
    fk_value: int,
    select_fields: str,
) -> dict[str, Any]:
    supabase = await get_db()
    result = await (
        supabase
        .from_(table)
        .select(select_fields)
        .eq(fk_column, fk_value)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Note not found")
    return result.data[0]


async def _resend_log(
    *,
    request: Request,
    log_table: str,
    log_id: int,
    resend_fn: ResendFn,
) -> dict[str, Any]:
    db = await get_db()
    log = await db.from_(log_table).select("note_id").eq("id", log_id).execute()
    if not log.data:
        raise HTTPException(status_code=404, detail="Log not found")

    note_id = log.data[0]["note_id"]
    bot = request.app.state.ptb_app.bot
    sent = await resend_fn(note_id, bot)
    return {"recipients": sent}


async def _list_sent_logs(
    *,
    table: str,
    select_fields: str,
    page: int,
    page_size: int,
) -> dict[str, Any]:
    supabase = await get_db()
    offset = (page - 1) * page_size
    result = await (
        supabase
        .from_(table)
        .select(select_fields)
        .order("sent_at", desc=True)
        .range(offset, offset + page_size - 1)
        .execute()
    )
    return {"items": result.data or [], "page": page, "page_size": page_size}


def _build_subscription_updates(body: "SubscriptionPatch") -> dict[str, Any]:
    updates: dict[str, Any] = {}
    if body.label is not None:
        updates["label"] = body.label
    if body.briefing_types is not None:
        updates["briefing_types"] = body.briefing_types
    if body.active is not None:
        updates["active"] = body.active
    return updates


# ── CS ──────────────────────────────────────────────────────────────────────

@router.get("/cs/topics", dependencies=[Auth])
async def get_cs_topics(
    category: str | None = None,
    difficulty: str | None = None,
) -> list[dict[str, Any]]:
    return await _list_curriculum_rows(
        table="cs_topics",
        category=category,
        difficulty=difficulty,
    )


@router.get("/cs/topics/{topic_id}/note", dependencies=[Auth])
async def get_cs_note(topic_id: int) -> dict[str, Any]:
    return await _get_latest_note(
        table="cs_notes",
        fk_column="topic_id",
        fk_value=topic_id,
        select_fields="id, topic_id, summary, key_points, analogy, quiz, reading_time_min, created_at",
    )


@router.post("/cs/logs/{log_id}/resend", dependencies=[Auth])
async def resend_cs_log(log_id: int, request: Request) -> dict[str, Any]:
    return await _resend_log(
        request=request,
        log_table="cs_sent_log",
        log_id=log_id,
        resend_fn=resend_cs_note,
    )


@router.get("/cs/logs", dependencies=[Auth])
async def get_cs_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
) -> dict[str, Any]:
    return await _list_sent_logs(
        table="cs_sent_log",
        select_fields="id, note_id, sent_at, cs_notes(topic_id, cs_topics(title, category))",
        page=page,
        page_size=page_size,
    )


# ── Expression ──────────────────────────────────────────────────────────────

@router.get("/expr/clusters", dependencies=[Auth])
async def get_expr_clusters(
    category: str | None = None,
    difficulty: str | None = None,
) -> list[dict[str, Any]]:
    return await _list_curriculum_rows(
        table="expr_clusters",
        category=category,
        difficulty=difficulty,
    )


@router.get("/expr/clusters/{cluster_id}/note", dependencies=[Auth])
async def get_expr_note(cluster_id: int) -> dict[str, Any]:
    return await _get_latest_note(
        table="expr_notes",
        fk_column="cluster_id",
        fk_value=cluster_id,
        select_fields="id, cluster_id, intro, expressions, comparison, usage_tip, created_at",
    )


@router.post("/expr/logs/{log_id}/resend", dependencies=[Auth])
async def resend_expr_log(log_id: int, request: Request) -> dict[str, Any]:
    return await _resend_log(
        request=request,
        log_table="expr_sent_log",
        log_id=log_id,
        resend_fn=resend_expr_note,
    )


@router.get("/expr/logs", dependencies=[Auth])
async def get_expr_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
) -> dict[str, Any]:
    return await _list_sent_logs(
        table="expr_sent_log",
        select_fields="id, note_id, sent_at, expr_notes(cluster_id, expr_clusters(base_word, category))",
        page=page,
        page_size=page_size,
    )


# ── Subscriptions ────────────────────────────────────────────────────────────

class SubscriptionCreate(BaseModel):
    label: str | None = None
    chat_id: int
    bot_token: str
    briefing_types: list[str]
    active: bool = True

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
    _validate_briefing_types(body.briefing_types)
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
        _validate_briefing_types(body.briefing_types)
    updates = _build_subscription_updates(body)

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
