# Instruções para agentes neste repositório

Projeto: pipeline automático de cortes de lives de GTA 6 (Twitch → vertical legendado → TikTok/Shorts/Reels).

- Código em `gta6_cortes/`; configuração do usuário em `config.yaml`; roda no GitHub Actions (`.github/workflows/cortes.yml`).
- Responda e escreva textos em português do Brasil.
- Nunca remova o filtro `somente_autorizados` nem o crédito ao streamer sem pedido explícito do usuário.
- Nunca coloque chaves de API no código; use os Secrets do GitHub.
- Para testar edição sem internet: `python -m gta6_cortes.main --video arquivo.mp4`.
- Skills locais: `.claude/skills/yt-dlp` (download), `.claude/skills/upload-post` (API de postagem; use para campos por plataforma), `.claude/skills/video-highlight-extraction` (opcional, pago).
