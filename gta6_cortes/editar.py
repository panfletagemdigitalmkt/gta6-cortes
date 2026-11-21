"""Agente 2 — Editor: transforma o clipe horizontal em vertical 9:16 com legenda."""
import json
import subprocess
from pathlib import Path

from .legendas import gerar_ass, transcrever


def duracao(video: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(video)],
        capture_output=True, text=True, check=True,
    ).stdout
    return float(json.loads(out)["format"]["duration"])


def editar(video: Path, saida: Path, cfg_edicao: dict, titulo: str | None, credito: str | None) -> Path:
    dur = duracao(video)
    palavras = []
    if cfg_edicao.get("legenda_automatica", True):
        palavras = transcrever(video, cfg_edicao.get("modelo_whisper", "small"),
                               cfg_edicao.get("idioma_legenda", "pt"))
    ass = gerar_ass(
        palavras, saida.with_suffix(".ass"),
        titulo if cfg_edicao.get("mostrar_titulo_no_video", True) else None,
        credito if cfg_edicao.get("mostrar_credito", True) else None,
        dur,
    )
    # fundo: o próprio vídeo ampliado e desfocado; frente: gameplay inteiro, centralizado
    filtro = (
        "[0:v]split=2[a][b];"
        "[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5,eq=brightness=-0.08[fundo];"
        "[b]scale=1080:-2[frente];"
        "[fundo][frente]overlay=(W-w)/2:(H-h)/2,"
        f"subtitles='{ass.as_posix()}'[v]"
    )
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(video),
         "-filter_complex", filtro, "-map", "[v]", "-map", "0:a?",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p",
         "-r", "30", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(saida)],
        check=True,
    )
    return saida
