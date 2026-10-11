"""Toy CRUD API for providers."""

import sqlite3
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, Field

from app.database import get_db

router = APIRouter(prefix="/api/providers", tags=["providers"])

Db = Annotated[sqlite3.Connection, Depends(get_db)]


class ProviderIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    url: str = Field(min_length=1, max_length=500)
    enabled: bool = True


class Provider(ProviderIn):
    id: int


def _to_provider(row: sqlite3.Row) -> Provider:
    return Provider(id=row["id"], name=row["name"], url=row["url"], enabled=bool(row["enabled"]))


def _get_or_404(db: sqlite3.Connection, provider_id: int) -> Provider:
    row = db.execute("SELECT * FROM providers WHERE id = ?", (provider_id,)).fetchone()
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Provider not found")
    return _to_provider(row)


@router.get("")
def list_providers(db: Db) -> list[Provider]:
    rows = db.execute("SELECT * FROM providers ORDER BY id").fetchall()
    return [_to_provider(row) for row in rows]


@router.post("", status_code=status.HTTP_201_CREATED)
def create_provider(body: ProviderIn, db: Db) -> Provider:
    try:
        with db:
            cur = db.execute(
                "INSERT INTO providers (name, url, enabled) VALUES (?, ?, ?)",
                (body.name, body.url, int(body.enabled)),
            )
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, "Provider name already exists") from exc
    assert cur.lastrowid is not None
    return _get_or_404(db, cur.lastrowid)


@router.get("/{provider_id}")
def get_provider(provider_id: int, db: Db) -> Provider:
    return _get_or_404(db, provider_id)


@router.put("/{provider_id}")
def update_provider(provider_id: int, body: ProviderIn, db: Db) -> Provider:
    _get_or_404(db, provider_id)
    try:
        with db:
            db.execute(
                "UPDATE providers SET name = ?, url = ?, enabled = ? WHERE id = ?",
                (body.name, body.url, int(body.enabled), provider_id),
            )
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, "Provider name already exists") from exc
    return _get_or_404(db, provider_id)


@router.delete("/{provider_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_provider(provider_id: int, db: Db) -> Response:
    _get_or_404(db, provider_id)
    with db:
        db.execute("DELETE FROM providers WHERE id = ?", (provider_id,))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
