"""Agente 1 — Buscador: encontra os melhores momentos de GTA 6 na Twitch.

Usa os clipes da própria Twitch: cada clipe é um momento que o público
já marcou como bom, então servem de "detector de melhores momentos".
"""
from datetime import datetime, timedelta, timezone

import requests

API = "https://api.twitch.tv/helix"


class Twitch:
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        r = requests.post(
            "https://id.twitch.tv/oauth2/token",
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": "client_credentials",
            },
            timeout=30,
        )
        r.raise_for_status()
        self.token = r.json()["access_token"]

    def _get(self, rota: str, **params) -> dict:
        r = requests.get(
            f"{API}/{rota}",
            params=params,
            headers={"Client-Id": self.client_id, "Authorization": f"Bearer {self.token}"},
            timeout=30,
        )
        r.raise_for_status()
        return r.json()

    def id_do_jogo(self, nome: str) -> str:
        dados = self._get("games", name=nome)["data"]
        if not dados:
            raise SystemExit(f"Jogo '{nome}' não encontrado na Twitch.")
        return dados[0]["id"]

    def lives_ao_vivo(self, game_id: str, idiomas: list[str]) -> list[dict]:
        params = {"game_id": game_id, "first": 100}
        if idiomas:
            params["language"] = idiomas
        return self._get("streams", **params)["data"]

    def clipes(self, game_id: str, janela_horas: int, paginas: int = 3) -> list[dict]:
        inicio = (datetime.now(timezone.utc) - timedelta(hours=janela_horas)).strftime("%Y-%m-%dT%H:%M:%SZ")
        todos, cursor = [], None
        for _ in range(paginas):
            params = {"game_id": game_id, "started_at": inicio, "first": 100}
            if cursor:
                params["after"] = cursor
            resp = self._get("clips", **params)
            todos += resp["data"]
            cursor = resp.get("pagination", {}).get("cursor")
            if not cursor:
                break
        return todos


def filtrar_clipes(clipes: list[dict], cfg: dict, ja_postados: set[str]) -> list[dict]:
    b = cfg["busca"]
    idiomas = set(b.get("idiomas") or [])
    autorizados = {s.lower() for s in cfg.get("streamers_autorizados") or []}
    bloqueados = {s.lower() for s in cfg.get("streamers_bloqueados") or []}
    bons = []
    for c in clipes:
        login = c["broadcaster_name"].lower()
        if c["id"] in ja_postados or login in bloqueados:
            continue
        if cfg.get("somente_autorizados", True) and login not in autorizados:
            continue
        if idiomas and c.get("language") not in idiomas:
            continue
        if c["view_count"] < b.get("min_visualizacoes", 0):
            continue
        if not (b.get("duracao_min_seg", 0) <= c["duration"] <= b.get("duracao_max_seg", 60)):
            continue
        bons.append(c)
    # melhores primeiro; no máximo 1 clipe por streamer em cada rodada
    bons.sort(key=lambda c: c["view_count"], reverse=True)
    vistos, unicos = set(), []
    for c in bons:
        if c["broadcaster_name"].lower() not in vistos:
            vistos.add(c["broadcaster_name"].lower())
            unicos.append(c)
    return unicos
