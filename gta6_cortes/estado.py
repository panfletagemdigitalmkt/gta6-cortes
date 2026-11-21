"""Guarda quais clipes já foram postados (data/postados.json), para nunca repetir."""
import json
from datetime import datetime, timezone

from .config import RAIZ

ARQ = RAIZ / "data" / "postados.json"


def carregar() -> dict:
    if ARQ.exists():
        return json.loads(ARQ.read_text(encoding="utf-8"))
    return {"postados": []}


def ids(estado: dict) -> set[str]:
    return {p["clip_id"] for p in estado["postados"]}


def registrar(estado: dict, clipe: dict, titulo: str, resposta: dict | None, simulado: bool) -> None:
    estado["postados"].append({
        "clip_id": clipe["id"],
        "streamer": clipe["broadcaster_name"],
        "url": clipe["url"],
        "titulo": titulo,
        "views_twitch": clipe["view_count"],
        "quando": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "simulado": simulado,
        "request_id": (resposta or {}).get("request_id"),
    })
    estado["postados"] = estado["postados"][-2000:]
    ARQ.parent.mkdir(parents=True, exist_ok=True)
    ARQ.write_text(json.dumps(estado, ensure_ascii=False, indent=2), encoding="utf-8")
