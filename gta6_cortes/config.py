import os
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parent.parent


def carregar_config(caminho: str | None = None) -> dict:
    caminho = Path(caminho) if caminho else RAIZ / "config.yaml"
    with open(caminho, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def segredo(nome: str, obrigatorio: bool = False) -> str | None:
    valor = os.environ.get(nome, "").strip() or None
    if obrigatorio and not valor:
        raise SystemExit(f"Falta a variável/secret {nome}. Veja o README.")
    return valor
