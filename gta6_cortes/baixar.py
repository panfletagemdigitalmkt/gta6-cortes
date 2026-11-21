"""Baixa o clipe com yt-dlp (veja .claude/skills/yt-dlp)."""
from pathlib import Path

import yt_dlp


def baixar(url: str, destino: Path) -> Path:
    destino.parent.mkdir(parents=True, exist_ok=True)
    opcoes = {
        "outtmpl": str(destino.with_suffix(".%(ext)s")),
        "format": "best[ext=mp4]/best",
        "quiet": True,
        "no_warnings": True,
        "merge_output_format": "mp4",
    }
    with yt_dlp.YoutubeDL(opcoes) as ydl:
        info = ydl.extract_info(url, download=True)
        return Path(ydl.prepare_filename(info))
