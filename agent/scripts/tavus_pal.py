"""Tavus helper: list stock faces or create a PAL wired for LiveKit.

Usage (from the agent/ folder):
    uv run scripts/tavus_pal.py faces
    uv run scripts/tavus_pal.py create --face <face-id> [--name "Coral"]
"""

import argparse
import os
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv

_AGENT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(_AGENT_DIR.parent / ".env")
load_dotenv(_AGENT_DIR / ".env.local")

API = "https://tavusapi.com/v2"


def _client() -> httpx.Client:
    key = os.getenv("TAVUS_API_KEY")
    if not key:
        sys.exit("TAVUS_API_KEY is not set (put it in the repo root .env)")
    return httpx.Client(base_url=API, headers={"x-api-key": key}, timeout=30)


def list_faces() -> None:
    with _client() as c:
        r = c.get("/replicas", params={"replica_type": "system", "limit": 100})
        r.raise_for_status()
        data = r.json().get("data", [])
    for f in data:
        # Tavus still returns replica_* keys on this endpoint
        print(f"{f.get('replica_id')}\t{f.get('replica_name')}")
    print(f"\n{len(data)} stock faces. Put one in TAVUS_FACE_ID.")


def create_pal(face_id: str, name: str) -> None:
    body = {
        "pal_name": name,
        "default_face_id": face_id,
        "pipeline_mode": "echo",
        "layers": {"transport": {"transport_type": "livekit"}},
    }
    with _client() as c:
        r = c.post("/pals", json=body)
        if r.status_code >= 400:
            sys.exit(f"Tavus error {r.status_code}: {r.text}")
        data = r.json()
    pal_id = data.get("pal_id") or data.get("persona_id")
    print(f"Created PAL {pal_id}. Put it in TAVUS_PAL_ID.")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("faces", help="list stock faces")
    c = sub.add_parser("create", help="create an echo-mode PAL with LiveKit transport")
    c.add_argument("--face", required=True, help="face id to use as default")
    c.add_argument("--name", default="Coral", help="PAL name")
    args = p.parse_args()
    if args.cmd == "faces":
        list_faces()
    else:
        create_pal(args.face, args.name)


if __name__ == "__main__":
    main()
