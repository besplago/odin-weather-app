#!/usr/bin/env python3
from __future__ import annotations

"""
Download all NBA players via balldontlie and write them to ../src/assets/players_profiles.json.

Features:
- Progressive saving: after each page, data is merged and written atomically.
- Checkpointing: players_profiles.state.json stores the next cursor to fetch.
- Resume: on restart, the script resumes from the last safe checkpoint.
- Rate limit: 5 req/min (12s spacing), with retries + exponential backoff.
- De-dupes by player id.

Run: python fetch_all_players.py
"""

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable

# ---- Config ----
API_KEY: str = "ab7d3912-b6a7-42f1-acec-11659c260395"  # free key, hardcoded by request
PER_PAGE: int = 100
REQS_PER_MINUTE: int = 5
MIN_SECONDS_BETWEEN_CALLS: float = 60.0 / REQS_PER_MINUTE
MAX_EMPTY_STREAK: int = 5  # safety valve

# ---- Third-party ----
from balldontlie import BalldontlieAPI  # type: ignore
from balldontlie.base import PaginatedListResponse  # type: ignore
from balldontlie.nba.models import NBAPlayer  # type: ignore


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def atomic_write_json(path: Path, data: Any) -> None:
    """Write JSON atomically to avoid partial/corrupt files on crash."""
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)  # atomic on POSIX + Windows


def load_json_or(path: Path, default: Any) -> Any:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default
    except Exception as e:
        print(f"[warn] Failed to parse {path.name}: {e}. Starting fresh.")
        return default


def to_plain_dict(obj: Any) -> Dict[str, Any]:
    """Convert NBAPlayer (or nested models) into plain dicts for JSON."""
    if isinstance(obj, dict):
        return obj
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if hasattr(obj, "dict"):
        return obj.dict()  # type: ignore[no-any-return]
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
    return {"value": str(obj)}


def throttle(last_call_ts: float | None) -> float:
    """Sleep to keep at/below 5 req/min; returns new call timestamp."""
    now = time.monotonic()
    if last_call_ts is not None:
        elapsed = now - last_call_ts
        if elapsed < MIN_SECONDS_BETWEEN_CALLS:
            time.sleep(MIN_SECONDS_BETWEEN_CALLS - elapsed)
    return time.monotonic()


def save_progress(
    players_by_id: dict[int, dict],
    out_path: Path,
    state_path: Path,
    resume_cursor: int | None,
) -> None:
    # Save players list (sorted by id) atomically
    players_list = [players_by_id[k] for k in sorted(players_by_id.keys())]
    atomic_write_json(out_path, players_list)

    # Save checkpoint state atomically
    state = {
        "resume_cursor": resume_cursor,  # cursor to pass next time (None means done)
        "per_page": PER_PAGE,
        "total_saved": len(players_by_id),
        "last_saved_at": utc_now_iso(),
    }
    atomic_write_json(state_path, state)


def fetch_all_players_progressive(api_key: str, out_dir: Path) -> None:
    assets_dir = out_dir
    ensure_dir(assets_dir)

    out_path = assets_dir / "players_profiles.json"
    state_path = assets_dir / "players_profiles.state.json"

    # Load existing data (if any) and checkpoint
    existing_players = load_json_or(out_path, default=[])
    players_by_id: dict[int, dict] = {}
    for item in existing_players:
        try:
            pid = int(item.get("id"))  # type: ignore[arg-type]
            players_by_id[pid] = item
        except Exception:
            continue  # skip malformed rows

    state = load_json_or(state_path, default={"resume_cursor": None})
    cursor: int | None = state.get("resume_cursor") if isinstance(state, dict) else None

    # Announce resume position
    if cursor is None and players_by_id:
        print(
            f"[info] No resume cursor found, but {len(players_by_id)} players already saved. Starting from beginning."
        )
    elif cursor is None:
        print("[info] Fresh run. Starting from the beginning (no cursor).")
    else:
        print(
            f"[info] Resuming from cursor={cursor} with {len(players_by_id)} players already saved."
        )

    api = BalldontlieAPI(api_key=api_key)
    last_call_ts: float | None = None
    empty_streak = 0
    page_idx = 0
    retries_for_page = 0

    while True:
        kwargs: Dict[str, Any] = {"per_page": PER_PAGE}
        if cursor is not None:
            kwargs["cursor"] = cursor

        last_call_ts = throttle(last_call_ts)

        try:
            page_idx += 1
            resp: PaginatedListResponse[NBAPlayer] = api.nba.players.list(**kwargs)
            retries_for_page = 0
        except Exception as e:
            retries_for_page += 1
            if retries_for_page > 5:
                print(f"[error] Permanent failure on page {page_idx}: {e}")
                print("[info] Latest progress is preserved. You can rerun to resume.")
                return
            backoff = min(2 ** (retries_for_page - 1), 32)
            print(f"[warn] Error on page {page_idx} ({e}); retrying in {backoff}s...")
            time.sleep(backoff)
            page_idx -= 1
            continue

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

        # Determine next cursor
        meta = getattr(resp, "meta", None)
        next_cursor = None
        if meta is not None:
            next_cursor = getattr(meta, "next_cursor", None)
            if next_cursor is None and isinstance(meta, dict):
                next_cursor = meta.get("next_cursor")

        # Persist after every page (progressive save)
        save_progress(
            players_by_id,
            out_path,
            state_path,
            int(next_cursor) if next_cursor is not None else None,
        )

        total_so_far = len(players_by_id)
        print(
            f"[info] Page {page_idx}: fetched {page_count} players | total={total_so_far} | next_cursor={next_cursor}"
        )

        # Stop conditions
        if empty_streak >= MAX_EMPTY_STREAK:
            print("[info] Reached maximum consecutive empty pages; assuming end.")
            break
        if not next_cursor:
            print("[info] No next_cursor; reached the end.")
            break

        cursor = int(next_cursor)

    # Clean up checkpoint on success (optional: keep it with resume_cursor=null)
    try:
        final_state = load_json_or(state_path, {})
        if isinstance(final_state, dict):
            final_state["resume_cursor"] = None
            final_state["last_saved_at"] = utc_now_iso()
            atomic_write_json(state_path, final_state)
    except Exception as e:
        print(f"[warn] Could not finalize state file: {e}")

    print(f"[done] Wrote {len(players_by_id)} players to {out_path}")


def main() -> None:
    # Resolve ../src/assets relative to this script
    out_dir = Path(__file__).resolve().parent.parent / "src" / "assets"
    fetch_all_players_progressive(API_KEY, out_dir)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[info] Interrupted by user. Progress already saved; rerun to resume.")
