"""Auth dependency — validates Better-Auth session tokens against PostgreSQL."""

from datetime import datetime, timezone

import asyncpg
from fastapi import Depends, HTTPException, Request, status

from app.config import settings

_pool: asyncpg.Pool | None = None


async def get_db_pool() -> asyncpg.Pool:
    """Lazy-init a connection pool to the same PostgreSQL used by Better-Auth."""
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(settings.database_url, min_size=1, max_size=5)
    return _pool


async def shutdown_pool() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


class AuthenticatedUser:
    """Minimal user context extracted from a valid session."""

    __slots__ = ("id", "email", "name")

    def __init__(self, user_id: str, email: str, name: str) -> None:
        self.id = user_id
        self.email = email
        self.name = name


async def get_current_user(request: Request) -> AuthenticatedUser:
    """FastAPI dependency: extract and validate the Better-Auth session token.

    The token can arrive either as:
      - Authorization: Bearer <token>  (set by the Next.js proxy)
      - Cookie: better-auth.session_token=<token>  (direct browser calls)
    """
    token: str | None = None

    # 1. Check Authorization header (preferred — set by proxy)
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:].strip()

    # 2. Fallback to cookie
    if not token:
        token = request.cookies.get("better-auth.session_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing session token",
        )

    pool = await get_db_pool()

    row = await pool.fetchrow(
        """
        SELECT s."userId", s."expiresAt", u.email, u.name
        FROM "session" s
        JOIN "user" u ON u.id = s."userId"
        WHERE s.token = $1
        """,
        token,
    )

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session token",
        )

    if row["expiresAt"].replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired",
        )

    return AuthenticatedUser(
        user_id=row["userId"],
        email=row["email"],
        name=row["name"],
    )
