"""Gera título e legenda do post. Usa Claude se ANTHROPIC_API_KEY existir; senão, um modelo fixo."""
import json
import re

import requests


def _limpo(txt: str) -> str:
    return re.sub(r"\s+", " ", txt or "").strip()


def _titulo_ruim(t: str) -> bool:
    letras = re.sub(r"[^a-zA-ZÀ-ÿ]", "", t)
    sem_risada = re.sub(r"(?i)k|h|a|s|j|r", "", letras)  # kkkk, hahaha, asjkas...
    return len(letras) < 4 or len(sem_risada) < 3


def textos_padrao(clipe: dict, hashtags: list[str]) -> dict:
    streamer = clipe["broadcaster_name"]
    titulo = _limpo(clipe.get("title"))
    if _titulo_ruim(titulo):
        titulo = f"{streamer} no GTA 6 😂" if "k" in titulo.lower() else f"Momento insano do {streamer} no GTA 6"
    link = f"https://www.twitch.tv/{clipe['broadcaster_name'].lower()}"
    tags = " ".join(hashtags)
    return {
        "titulo_video": titulo[:60],
        "titulo_post": f"{titulo[:80]} 😱 — @{streamer} {tags}"[:150],
        "descricao": f"{titulo}\n\n🎮 Live de {streamer}: {link}\nClipe original: {clipe['url']}\n\n{tags}",
    }


def textos_com_ia(clipe: dict, hashtags: list[str], transcricao: str, api_key: str) -> dict:
    base = textos_padrao(clipe, hashtags)
    prompt = (
        "Você escreve títulos de cortes virais de GTA 6 para TikTok/Shorts/Reels em português do Brasil.\n"
        f"Streamer: {clipe['broadcaster_name']}\nTítulo do clipe na Twitch: {clipe.get('title')}\n"
        f"O que foi falado: {transcricao[:1500] or '(sem fala)'}\n\n"
        "Responda só com JSON: {\"titulo_video\": até 45 caracteres, chamativo, sem hashtag, "
        "\"gancho\": frase curta para a legenda do post, sem hashtag}. Não invente fatos que não estão acima."
    )
    try:
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={"model": "claude-haiku-5-5", "max_tokens": 300,
                  "messages": [{"role": "user", "content": prompt}]},
            timeout=60,
        )
        r.raise_for_status()
        txt = r.json()["content"][0]["text"]
        dados = json.loads(txt[txt.find("{"): txt.rfind("}") + 1])
        tv, gancho = _limpo(dados["titulo_video"])[:60], _limpo(dados["gancho"])
        tags = " ".join(hashtags)
        base["titulo_video"] = tv
        base["titulo_post"] = f"{gancho} — @{clipe['broadcaster_name']} {tags}"[:150]
        base["descricao"] = f"{gancho}\n\n" + base["descricao"]
    except Exception as e:  # IA é opcional: se falhar, segue com o padrão
        print(f"  (IA indisponível, usando título padrão: {e})")
    return base
