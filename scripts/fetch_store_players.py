#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple
import http.client
import urllib.parse

# -----------------------------
# Config & CLI
# -----------------------------


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Download all player profiles and write them to ../src/assets/players_profiles.json"
    )
    p.add_argument(
        "--api-key",
        default=os.getenv("API_SPORTS_KEY") or os.getenv("RAPIDAPI_KEY"),
        help="API key for v3.football.api-sports.io (env: API_SPORTS_KEY or RAPIDAPI_KEY)",
    )
    p.add_argument(
        "--host",
        default="v3.football.api-sports.io",
        help="API host (default: v3.football.api-sports.io)",
    )
    p.add_argument(
        "--output",
        default=None,
        help="Output JSON path (default: ../src/assets/players_profiles.json relative to this script)",
    )
    p.add_argument(
        "--fresh",
        action="store_true",
        help="Ignore any existing checkpoint and start from page 1",
    )
    p.add_argument(
        "--wait-for-reset",
        action="store_true",
        help="If daily rate limit is reached, wait until reset (based on headers) and continue automatically.",
    )
    p.add_argument(
        "--max-retries",
        type=int,
        default=5,
        help="Max retries for transient errors/429s (default: 5)",
    )
    p.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="HTTP connection timeout seconds (default: 60)",
    )
    return p.parse_args()


# -----------------------------
# Paths & Files
# -----------------------------


def default_output_path() -> Path:
    here = Path(__file__).resolve().parent
    out_dir = (here / ".." / "src" / "assets").resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir / "players_profiles.json"


def checkpoint_paths(out_path: Path) -> Tuple[Path, Path]:
    """
    Return paths for partial data and checkpoint files next to the final output.
    """
    partial = out_path.with_suffix(".partial.json")
    checkpoint = out_path.with_suffix(".checkpoint.json")
    return partial, checkpoint


# -----------------------------
# HTTP / API helpers
# -----------------------------


def make_headers(api_key: str, host: str) -> Dict[str, str]:
    return {
        "Accept": "application/json",
        "Connection": "keep-alive",
        "x-rapidapi-host": host,
        "x-rapidapi-key": api_key,
    }


def parse_json(body: bytes) -> Dict[str, Any]:
    try:
        return json.loads(body.decode("utf-8"))
    except Exception as e:
        raise ValueError(
            f"Failed to parse JSON: {e}; body (first 500 bytes): {body[:500]!r}"
        )


def headers_ci_dict(h: http.client.HTTPMessage) -> Dict[str, str]:
    # Normalize headers to lower-case keys for easy lookup
    return {k.lower(): v for k, v in h.items()}


def read_rate_limits(h: Dict[str, str]) -> Dict[str, Any]:
    """
    Tries to interpret common API-Sports/RapidAPI rate limit headers.
    Values may vary by plan; we attempt to be flexible.
    """

    # Common header spellings (case-insensitive):
    # - x-ratelimit-requests-limit / x-ratelimit-requests-remaining / x-ratelimit-requests-reset
    # - x-ratelimit-limit / x-ratelimit-remaining
    # - retry-after (when 429)
    def get_int(key: str) -> int | None:
        value = h.get(key)
        if value and value.isdigit():
            return int(value)
        return None

    rl = {
        "requests_limit": get_int("x-ratelimit-requests-limit"),
        "requests_remaining": get_int("x-ratelimit-requests-remaining")
        or get_int("x-ratelimit-remaining"),
        "requests_reset": get_int("x-ratelimit-requests-reset"),
        "retry_after": get_int("retry-after"),
    }
    return rl


def sleep_until_reset(headers_ci: Dict[str, str]) -> None:
    rl = read_rate_limits(headers_ci)
    # Prefer Retry-After if present (seconds)
    if rl["retry_after"]:
        wait = rl["retry_after"]
        print(f"[rate-limit] Retry-After present. Sleeping {wait}s...")
        time.sleep(wait)
        return

    # Fallback: if requests_reset is a unix timestamp (or seconds), try to compute duration
    reset = rl["requests_reset"]
    now = int(time.time())
    if reset and reset > now and reset - now < 24 * 3600:
        wait = reset - now
        print(f"[rate-limit] Daily reset at {reset} (unix). Sleeping {wait}s...")
        time.sleep(max(0, wait))
    else:
        # No usable reset info; do a conservative backoff
        print(
            "[rate-limit] No reset headers; sleeping 60s as a conservative backoff..."
        )
        time.sleep(60)


def fetch_page(
    conn: http.client.HTTPSConnection, host: str, api_key: str, page: int, timeout: int
) -> Tuple[int, Dict[str, str], Dict[str, Any]]:
    path = "/players/profiles?" + urllib.parse.urlencode({"page": page})
    headers = make_headers(api_key, host)
    conn.timeout = timeout
    conn.request("GET", path, headers=headers)
    res: http.client.HTTPResponse = conn.getresponse()
    status = res.status
    headers_ci = headers_ci_dict(res.headers)
    body = res.read()
    return status, headers_ci, parse_json(body)


def merge_players(
    target: Dict[int, Dict[str, Any]], items: List[Dict[str, Any]]
) -> int:
    """
    items look like: {"player": { ... player fields ... }}
    We keep unique players keyed by player.id
    """
    added = 0
    for item in items:
        player = item.get("player", {})
        pid = player.get("id")
        if isinstance(pid, int):
            if pid not in target:
                target[pid] = player
                added += 1
            else:
                # Optionally merge/refresh fields if needed; we just keep first seen
                pass
    return added


def save_partial(
    out_partial: Path,
    out_checkpoint: Path,
    players_by_id: Dict[int, Dict[str, Any]],
    current_page: int,
    total_pages: int | None,
) -> None:
    out_partial.write_text(
        json.dumps(
            {
                "meta": {
                    "pages_fetched_up_to": current_page,
                    "total_pages_reported": total_pages,
                    "player_count": len(players_by_id),
                },
                "players": list(players_by_id.values()),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    out_checkpoint.write_text(
        json.dumps(
            {
                "next_page": current_page + 1,
                "total_pages": total_pages,
                "saved_at": int(time.time()),
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def load_checkpoint(
    out_partial: Path, out_checkpoint: Path
) -> Tuple[int, int | None, Dict[int, Dict[str, Any]]]:
    if not out_checkpoint.exists() or not out_partial.exists():
        return 1, None, {}
    try:
        chk = json.loads(out_checkpoint.read_text())
        data = json.loads(out_partial.read_text())
        next_page = int(chk.get("next_page", 1))
        total_pages = chk.get("total_pages")
        players_list = data.get("players", [])
        players_by_id = {
            p["id"]: p for p in players_list if isinstance(p, dict) and "id" in p
        }
        print(
            f"[resume] Resuming from page {next_page}. Already have {len(players_by_id)} players."
        )
        return max(1, next_page), total_pages, players_by_id
    except Exception as e:
        print(f"[resume] Failed to read checkpoint, starting fresh. Reason: {e}")
        return 1, None, {}


def finalize(out_partial: Path, out_path: Path) -> None:
    # Move/overwrite final file with the partial content
    out_path.write_text(out_partial.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"[done] Wrote {out_path} ({out_path.stat().st_size:,} bytes)")
    # Cleanup checkpoint files
    try:
        out_partial.unlink(missing_ok=True)
    except Exception:
        pass


# -----------------------------
# Main
# -----------------------------


def main() -> int:
    args = parse_args()
    if not args.api_key:
        print(
            "ERROR: Missing API key. Use --api-key or set API_SPORTS_KEY / RAPIDAPI_KEY.",
            file=sys.stderr,
        )
        return 2

    out_path = Path(args.output) if args.output else default_output_path()
    out_partial, out_checkpoint = checkpoint_paths(out_path)

    if args.fresh:
        for p in (out_partial, out_checkpoint):
            try:
                p.unlink(missing_ok=True)
            except Exception:
                pass

    # Resume if possible
    page, total_pages_reported, players_by_id = load_checkpoint(
        out_partial, out_checkpoint
    )

    conn = http.client.HTTPSConnection(args.host, timeout=args.timeout)
    consecutive_retries = 0

    try:
        while True:
            if total_pages_reported is not None and page > total_pages_reported:
                print("[pagination] Reached reported total pages. Stopping.")
                break

            print(f"[fetch] Page {page} ...")
            status, headers_ci, payload = fetch_page(
                conn, args.host, args.api_key, page, args.timeout
            )

            # Handle HTTP status codes
            if status == 200:
                consecutive_retries = 0
                response_items = payload.get("response", [])
                paging = payload.get("paging", {}) or {}
                current = paging.get("current")
                total = paging.get("total")
                if isinstance(total, int):
                    total_pages_reported = total

                added = merge_players(players_by_id, response_items)
                print(
                    f"[fetch] Page {page} OK. Added {added} players. Total unique: {len(players_by_id)}"
                )

                # Save partial + checkpoint every page
                save_partial(
                    out_partial,
                    out_checkpoint,
                    players_by_id,
                    page,
                    total_pages_reported,
                )

                # Stop if this page had no items
                if not response_items:
                    print("[pagination] Empty page received. Assuming end of dataset.")
                    break

                # Move to next page
                page += 1
                continue

            elif status in (429, 503, 504):
                # Rate-limited or transient server issue
                consecutive_retries += 1
                print(
                    f"[warn] HTTP {status}. Attempt {consecutive_retries}/{args.max_retries}."
                )

                # If explicit daily remaining header says 0, either wait or exit
                rl = read_rate_limits(headers_ci)
                remaining = rl.get("requests_remaining")
                if remaining is not None and remaining <= 0:
                    if args.wait_for_reset:
                        print(
                            "[rate-limit] Daily limit reached. Waiting for reset to continue..."
                        )
                        sleep_until_reset(headers_ci)
                        continue
                    else:
                        print(
                            "[rate-limit] Daily limit reached. Saving progress and exiting."
                        )
                        break

                # Otherwise backoff (Retry-After or exponential)
                if consecutive_retries > args.max_retries:
                    print("[error] Max retries exceeded. Saving progress and exiting.")
                    break

                # Respect Retry-After if present
                retry_after = rl.get("retry_after")
                if retry_after and retry_after > 0:
                    print(f"[backoff] Retry-After={retry_after}s")
                    time.sleep(retry_after)
                else:
                    wait = min(2**consecutive_retries, 60)
                    print(f"[backoff] Sleeping {wait}s before retry...")
                    time.sleep(wait)
                continue

            else:
                consecutive_retries += 1
                print(
                    f"[warn] Unexpected HTTP {status}. Attempt {consecutive_retries}/{args.max_retries}."
                )
                if consecutive_retries > args.max_retries:
                    print("[error] Max retries exceeded. Saving progress and exiting.")
                    break
                wait = min(2**consecutive_retries, 60)
                print(f"[backoff] Sleeping {wait}s before retry...")
                time.sleep(wait)
                continue

    finally:
        try:
            conn.close()
        except Exception:
            pass

    # Finalize: write final JSON and remove checkpoint files
    if out_partial.exists():
        finalize(out_partial, out_path)
    else:
        # If nothing written (no data), still create an empty file for consistency
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps({"meta": {}, "players": []}, ensure_ascii=False))
        print(f"[done] No data fetched; created empty {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
