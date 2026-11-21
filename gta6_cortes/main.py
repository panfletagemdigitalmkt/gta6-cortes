"""Pipeline completo: buscar -> baixar -> editar -> postar.

Uso:
  python -m gta6_cortes.main                 # roda (simulado se POSTAR != "true")
  python -m gta6_cortes.main --listar        # só mostra os clipes encontrados
  python -m gta6_cortes.main --video x.mp4   # testa só a edição num vídeo local
"""
import argparse
import os
import sys
from pathlib import Path

from . import estado as est
from .baixar import baixar
from .config import RAIZ, carregar_config, segredo
from .editar import editar
from .textos import textos_com_ia, textos_padrao
from .twitch import Twitch, filtrar_clipes

TRAB = RAIZ / "trabalho"
SAIDA = RAIZ / "saida"


def processar(clipe: dict, cfg: dict, postar_de_verdade: bool, estado: dict) -> None:
    login = clipe["broadcaster_name"].lower()
    print(f"\n▶ {clipe['broadcaster_name']} — {clipe['title']!r} ({clipe['view_count']} views)")
    bruto = baixar(clipe["url"], TRAB / clipe["id"])
    hashtags = cfg["postagem"].get("hashtags", [])
    textos = textos_padrao(clipe, hashtags)
    chave_ia = segredo("ANTHROPIC_API_KEY")
    if chave_ia:
        from .legendas import transcrever
        fala = " ".join(p["txt"] for p in transcrever(
            bruto, cfg["edicao"].get("modelo_whisper", "small"), cfg["edicao"].get("idioma_legenda", "pt")))
        textos = textos_com_ia(clipe, hashtags, fala, chave_ia)
    SAIDA.mkdir(exist_ok=True)
    final = editar(bruto, SAIDA / f"{clipe['id']}.mp4", cfg["edicao"],
                   textos["titulo_video"], f"twitch.tv/{login}")
    print(f"  ✓ editado: {final.name}  | título: {textos['titulo_video']}")

    resposta = None
    if postar_de_verdade:
        from .postar import postar
        resposta = postar(final, textos, cfg["postagem"], segredo("UPLOADPOST_API_KEY", obrigatorio=True))
        print(f"  ✓ enviado ao upload-post: {resposta.get('request_id') or resposta}")
    else:
        print("  (modo simulado: não postou. Defina POSTAR=true para publicar)")
    est.registrar(estado, clipe, textos["titulo_video"], resposta, simulado=not postar_de_verdade)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--listar", action="store_true")
    ap.add_argument("--video", help="testa a edição num vídeo local")
    args = ap.parse_args()
    cfg = carregar_config()

    if args.video:
        SAIDA.mkdir(exist_ok=True)
        out = editar(Path(args.video), SAIDA / "teste.mp4", cfg["edicao"], "Teste de corte GTA 6", "twitch.tv/exemplo")
        print(f"Vídeo de teste: {out}")
        return 0

    tw = Twitch(segredo("TWITCH_CLIENT_ID", True), segredo("TWITCH_CLIENT_SECRET", True))
    game_id = tw.id_do_jogo(cfg["busca"]["jogo"])
    ao_vivo = tw.lives_ao_vivo(game_id, cfg["busca"].get("idiomas"))
    print(f"🔴 {len(ao_vivo)} lives de GTA 6 ao vivo agora "
          f"({', '.join(s['user_login'] for s in ao_vivo[:10])}{'...' if len(ao_vivo) > 10 else ''})")

    estado = est.carregar()
    if args.listar:
        # só lista (não baixa nem posta): mostra todos os streamers, para você escolher quem pedir autorização
        cfg = {**cfg, "somente_autorizados": False}
    candidatos = filtrar_clipes(tw.clipes(game_id, cfg["busca"]["janela_horas"]), cfg, est.ids(estado))
    print(f"🎬 {len(candidatos)} clipes aprovados nos filtros")
    if cfg.get("somente_autorizados", True) and not cfg.get("streamers_autorizados"):
        print("⚠ Nenhum streamer em streamers_autorizados (config.yaml). Adicione quem liberou cortes.")

    if args.listar:
        autorizados = {s.lower() for s in cfg.get("streamers_autorizados") or []}
        for c in candidatos[:30]:
            marca = "✅" if c["broadcaster_name"].lower() in autorizados else "  "
            print(f"  {marca} {c['view_count']:>6} views | {c['broadcaster_name']:<20} | {c['duration']:>4.0f}s | "
                  f"{c['title']} | {c['url']}")
        return 0

    postar_de_verdade = os.environ.get("POSTAR", "").lower() == "true"
    erros = 0
    for clipe in candidatos[: cfg.get("cortes_por_execucao", 3)]:
        try:
            processar(clipe, cfg, postar_de_verdade, estado)
        except Exception as e:
            erros += 1
            print(f"  ✗ falhou: {e}", file=sys.stderr)
    return 1 if erros and erros == min(len(candidatos), cfg.get("cortes_por_execucao", 3)) else 0


if __name__ == "__main__":
    raise SystemExit(main())
