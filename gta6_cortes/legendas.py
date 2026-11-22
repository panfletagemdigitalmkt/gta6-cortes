"""Transcreve a fala (faster-whisper, roda em CPU) e gera legenda .ass estilo Shorts."""
from pathlib import Path

_modelo = None


def _audio_16k(video: Path):
    """Extrai o áudio com o FFmpeg (mono, 16 kHz) — evita depender do PyAV."""
    import subprocess

    import numpy as np

    bruto = subprocess.run(
        ["ffmpeg", "-nostdin", "-loglevel", "error", "-i", str(video),
         "-vn", "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
        capture_output=True, check=True,
    ).stdout
    return np.frombuffer(bruto, np.int16).astype(np.float32) / 32768.0


def transcrever(video: Path, modelo: str = "small", idioma: str = "pt") -> list[dict]:
    global _modelo
    from faster_whisper import WhisperModel

    if _modelo is None:
        _modelo = WhisperModel(modelo, device="cpu", compute_type="int8")
    segmentos, _ = _modelo.transcribe(_audio_16k(video), language=idioma, word_timestamps=True, vad_filter=True)
    palavras = []
    for s in segmentos:
        for p in s.words or []:
            texto = p.word.strip()
            if texto:
                palavras.append({"ini": p.start, "fim": p.end, "txt": texto})
    return palavras


def _t(seg: float) -> str:
    h, resto = divmod(max(seg, 0), 3600)
    m, s = divmod(resto, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def _esc(txt: str) -> str:
    # remove emojis (a fonte do vídeo não tem) e caracteres que quebram o .ass
    txt = "".join(ch for ch in txt if ord(ch) < 0x2190 or 0x3000 <= ord(ch) < 0xD800)
    return txt.replace("\\", "").replace("{", "(").replace("}", ")").replace("\n", " ").strip()


def gerar_ass(palavras: list[dict], saida: Path, titulo: str | None, credito: str | None,
              duracao: float, por_bloco: int = 3) -> Path:
    cab = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Legenda,Montserrat Black,92,&H00FFFFFF,&H0000FFFF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,7,3,2,60,60,560,1
Style: Titulo,Montserrat Black,70,&H00FFFFFF,&H00FFFFFF,&H00000000,&HB4000000,1,0,0,0,100,100,0,0,3,18,0,8,70,70,170,1
Style: Credito,Montserrat,44,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,1,0,0,0,100,100,0,0,3,10,0,2,60,60,120,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    linhas = []
    if titulo:
        linhas.append(f"Dialogue: 1,{_t(0)},{_t(duracao)},Titulo,,0,0,0,,{_esc(titulo.upper())}")
    if credito:
        linhas.append(f"Dialogue: 1,{_t(0)},{_t(duracao)},Credito,,0,0,0,,{_esc(credito)}")
    for i in range(0, len(palavras), por_bloco):
        bloco = palavras[i:i + por_bloco]
        ini, fim = bloco[0]["ini"], bloco[-1]["fim"]
        if i + por_bloco < len(palavras):
            fim = min(max(fim, ini + 0.3), palavras[i + por_bloco]["ini"])
        # palavra falada no momento fica amarela (efeito karaokê)
        partes = []
        for p in bloco:
            cs = max(int((p["fim"] - p["ini"]) * 100), 1)
            partes.append(f"{{\\k{cs}}}{_esc(p['txt']).upper()}")
        linhas.append(f"Dialogue: 0,{_t(ini)},{_t(fim)},Legenda,,0,0,0,,{' '.join(partes)}")
    saida.write_text(cab + "\n".join(linhas) + "\n", encoding="utf-8")
    return saida
