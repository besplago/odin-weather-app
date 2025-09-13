#!/usr/bin/env python3
from __future__ import annotations

"""
Download all NBA players via balldontlie and write them to ../src/assets/players_profiles.json.

- Auto-detects the end by checking PaginationMeta.next_cursor (cursor-based pagination).
- Handles occasional empty pages (continues until no next_cursor).
- Enforces 5 requests per minute (12s minimum spacing).
- Hardcodes the API key as requested.

Run: python fetch_all_players.py
"""

import json
import time
from pathlib import Path
from typing import Any, Dict, Iterable

# ---- Config ----
API_KEY: str = "ab7d3912-b6a7-42f1-acec-11659c260395"  # free key, hardcoded by request
PER_PAGE: int = 100  # max per page to minimize calls
REQS_PER_MINUTE: int = 5
MIN_SECONDS_BETWEEN_CALLS: float = 60.0 / REQS_PER_MINUTE
MAX_EMPTY_STREAK: int = 5  # safety valve in case the API serves multiple empty pages

# ---- Imports after config (so the script can be read without the package installed) ----
from balldontlie import BalldontlieAPI  # type: ignore
from balldontlie.base import PaginatedListResponse  # type: ignore
from balldontlie.nba.models import NBAPlayer  # type: ignore


def to_plain_dict(obj: Any) -> Dict[str, Any]:
    """Convert NBAPlayer (or nested models) into plain dicts for JSON."""
    if isinstance(obj, dict):
        return obj
    # Pydantic v2 style
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    # Pydantic v1 style
    if hasattr(obj, "dict"):
        return obj.dict()  # type: ignore[no-any-return]
    # Fallback: try __dict__ and recursively clean nested models we know about
    if hasattr(obj, "__dict__"):
        raw = {}
        for k, v in vars(obj).items():
            if isinstance(v, (list, tuple)):
                raw[k] = [
                    to_plain_dict(x)
                    if not isinstance(x, (str, int, float, bool, type(None)))
                    else x
                    for x in v
                ]
            elif hasattr(v, "__dict__") or isinstance(v, dict):
                raw[k] = to_plain_dict(v)
            else:
                raw[k] = v
        return raw
    # Last resort: stringify
    return {"value": str(obj)}


def throttle(last_call_ts: float | None) -> float:
    """Sleep as needed to keep at or below 5 req/min; returns the new call timestamp."""
    now = time.monotonic()
    if last_call_ts is not None:
        elapsed = now - last_call_ts
        if elapsed < MIN_SECONDS_BETWEEN_CALLS:
            time.sleep(MIN_SECONDS_BETWEEN_CALLS - elapsed)
    return time.monotonic()


def fetch_all_players(api_key: str, per_page: int = PER_PAGE) -> list[dict]:
    """Fetch all players across all pages (cursor-based), respecting rate limits."""
    api = BalldontlieAPI(api_key=api_key)
    cursor: int | None = None  # start from the beginning
    players_by_id: dict[int, dict] = {}

    last_call_ts: float | None = None
    empty_streak = 0
    page_idx = 0
    retries_for_page = 0

    while True:
        # Build call kwargs (cursor is optional)
        kwargs: Dict[str, Any] = {"per_page": per_page}
        if cursor is not None:
            kwargs["cursor"] = cursor

        # Throttle before each API call
        last_call_ts = throttle(last_call_ts)

        try:
            page_idx += 1
            resp: PaginatedListResponse[NBAPlayer] = api.nba.players.list(**kwargs)
            retries_for_page = 0  # reset retries on success
        except Exception as e:
            # Basic retry with exponential backoff
            retries_for_page += 1
            if retries_for_page > 5:
                raise RuntimeError(
                    f"Failed after multiple retries on page {page_idx}: {e}"
                ) from e
            backoff = min(2 ** (retries_for_page - 1), 32)
            print(f"[warn] Error on page {page_idx} ({e}); retrying in {backoff}s...")
            time.sleep(backoff)
            page_idx -= 1  # redo this page index
            continue

        # Extract rows
        page_data: Iterable[NBAPlayer] | list[dict] = getattr(resp, "data", [])
        page_count = 0
        for item in page_data:
            d = to_plain_dict(item)
            pid = d.get("id")
            if isinstance(pid, int):
                players_by_id[pid] = d
                page_count += 1

        if page_count == 0:
            empty_streak += 1
        else:
            empty_streak = 0

        # Progress
        total_so_far = len(players_by_id)
        print(
            f"[info] Page {page_idx} fetched {page_count} players | total={total_so_far}"
        )

        # Get next cursor (stop when it's missing/falsey)
        meta = getattr(resp, "meta", None)
        next_cursor = None
        if meta is not None:
            # Support both attr and dict-like meta
            next_cursor = getattr(meta, "next_cursor", None)
            if next_cursor is None and isinstance(meta, dict):
                next_cursor = meta.get("next_cursor")

        # Safety: if we see too many empties in a row, bail out
        if empty_streak >= MAX_EMPTY_STREAK:
            print("[info] Reached maximum consecutive empty pages; assuming end.")
            break

        if not next_cursor:
            print("[info] No next_cursor; reached the end.")
            break

        cursor = int(next_cursor)

    # Return a stable list sorted by id
    return [players_by_id[k] for k in sorted(players_by_id.keys())]


def main() -> None:
    # Resolve ../src/assets relative to this script
    out_path = (
        Path(__file__).resolve().parent.parent
        / "src"
        / "assets"
        / "players_profiles.json"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)

    all_players = fetch_all_players(API_KEY, per_page=PER_PAGE)

    with out_path.open("w", encoding="utf-8") as f:
        json.dump(all_players, f, ensure_ascii=False, indent=2, sort_keys=True)

    print(f"[done] Wrote {len(all_players)} players to {out_path}")


if __name__ == "__main__":
    main()
