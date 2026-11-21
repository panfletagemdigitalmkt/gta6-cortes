"""Agente 3 — Postador: publica no TikTok, YouTube Shorts e Instagram Reels via upload-post.com.

Referência completa: .claude/skills/upload-post/SKILL.md
"""
from pathlib import Path

import requests

API = "https://api.upload-post.com/api/upload"


def postar(video: Path, textos: dict, cfg_post: dict, api_key: str) -> dict:
    campos = [
        ("user", cfg_post["perfil_upload_post"]),
        ("title", textos["titulo_post"]),
        ("description", textos["descricao"]),
        ("async_upload", "true"),
    ]
    for p in cfg_post["plataformas"]:
        campos.append(("platform[]", p))
    if "youtube" in cfg_post["plataformas"]:
        campos += [
            ("youtube_title", f"{textos['titulo_video']} #shorts"[:100]),
            ("youtube_description", textos["descricao"]),  # links ficam clicáveis no YouTube
            ("privacyStatus", "public"),
        ]
    if "instagram" in cfg_post["plataformas"]:
        campos.append(("media_type", "REELS"))
    if "tiktok" in cfg_post["plataformas"]:
        campos.append(("privacy_level", "PUBLIC_TO_EVERYONE"))
    if cfg_post.get("usar_fila_upload_post"):
        campos.append(("add_to_queue", "true"))
        campos.append(("timezone", cfg_post.get("fuso_horario", "America/Sao_Paulo")))

    with open(video, "rb") as f:
        r = requests.post(
            API,
            headers={"Authorization": f"Apikey {api_key}"},
            data=campos,
            files={"video": (video.name, f, "video/mp4")},
            timeout=600,
        )
    if r.status_code >= 400:
        raise RuntimeError(f"upload-post respondeu {r.status_code}: {r.text[:500]}")
    return r.json()
