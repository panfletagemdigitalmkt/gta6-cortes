"""Posta direto no YouTube Shorts pela YouTube Data API v3 (grátis, sem upload-post).

Precisa de 3 secrets no GitHub (como gerar: README, seção "YouTube direto"):
  YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN
Cota padrão: 100 uploads/dia por projeto do Google Cloud.
"""
from pathlib import Path

import requests

TOKEN_URL = "https://oauth2.googleapis.com/token"
UPLOAD_URL = "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status"


def _access_token(client_id: str, client_secret: str, refresh_token: str) -> str:
    r = requests.post(TOKEN_URL, data={
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }, timeout=30)
    if r.status_code >= 400:
        raise RuntimeError(f"Google recusou o refresh token ({r.status_code}): {r.text[:300]}")
    return r.json()["access_token"]


def _tags(hashtags: list[str]) -> list[str]:
    return [h.lstrip("#") for h in hashtags if h.strip("#")]


def postar_youtube(video: Path, textos: dict, cfg_post: dict,
                   client_id: str, client_secret: str, refresh_token: str) -> dict:
    token = _access_token(client_id, client_secret, refresh_token)
    titulo = f"{textos['titulo_video']} #shorts"[:100]
    corpo = {
        "snippet": {
            "title": titulo,
            "description": textos["descricao"][:4900],  # links do streamer ficam clicáveis
            "tags": _tags(cfg_post.get("hashtags", [])),
            "categoryId": "20",  # Gaming
            "defaultLanguage": "pt-BR",
        },
        "status": {
            "privacyStatus": cfg_post.get("youtube_privacidade", "public"),
            "selfDeclaredMadeForKids": False,
        },
    }
    tamanho = video.stat().st_size
    ini = requests.post(UPLOAD_URL, json=corpo, timeout=60, headers={
        "Authorization": f"Bearer {token}",
        "X-Upload-Content-Type": "video/mp4",
        "X-Upload-Content-Length": str(tamanho),
    })
    if ini.status_code >= 400:
        raise RuntimeError(f"YouTube recusou o envio ({ini.status_code}): {ini.text[:500]}")
    with open(video, "rb") as f:
        up = requests.put(ini.headers["Location"], data=f, timeout=900, headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "video/mp4",
            "Content-Length": str(tamanho),
        })
    if up.status_code >= 400:
        raise RuntimeError(f"Falha no upload para o YouTube ({up.status_code}): {up.text[:500]}")
    vid = up.json()["id"]
    return {"youtube_id": vid, "youtube_url": f"https://youtube.com/shorts/{vid}"}
