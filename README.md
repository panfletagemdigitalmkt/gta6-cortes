# 🎮 GTA 6 Cortes — agentes automáticos

Três agentes rodando sozinhos no **GitHub Actions** (sem precisar do seu computador ligado):

| Agente | O que faz |
|---|---|
| 🔎 **Buscador** (`twitch.py`) | Acha as lives de GTA 6 ao vivo e os **clipes mais vistos** das últimas horas na Twitch. Os clipes são os momentos que o próprio público marcou como bons. |
| ✂️ **Editor** (`editar.py`, `legendas.py`) | Baixa com yt-dlp, transforma em vertical 9:16 (gameplay no centro, fundo desfocado), transcreve a fala e queima **legenda animada**, título no topo e crédito `twitch.tv/streamer`. |
| 📤 **Postador** (`postar.py`) | Publica no **TikTok, YouTube Shorts e Instagram Reels** de uma vez via [upload-post.com](https://upload-post.com), com o link do streamer clicável na descrição do YouTube. |

Roda a cada 3 horas, posta até 3 cortes por rodada e nunca repete um clipe (`data/postados.json`).

---

## ⚙️ Configuração (uma vez só)

### 1. Twitch (grátis)
1. Acesse [dev.twitch.tv/console/apps](https://dev.twitch.tv/console/apps) → **Register Your Application**
2. Nome: `gta6-cortes` · OAuth Redirect URL: `http://localhost` · Categoria: *Application Integration* · Client Type: *Confidential*
3. Copie o **Client ID** e gere um **Client Secret**

### 2. upload-post (postagem nas 3 redes)
1. Crie conta em [upload-post.com](https://upload-post.com)
2. Conecte TikTok, YouTube e Instagram
3. Crie um **Profile** chamado `gta6cortes` (ou mude `perfil_upload_post` no `config.yaml`)
4. Gere uma **API Key**

### 3. Colocar as chaves no GitHub
Em **Settings → Secrets and variables → Actions**:

**Secrets** (aba *Secrets*):
| Nome | Valor |
|---|---|
| `TWITCH_CLIENT_ID` | Client ID da Twitch |
| `TWITCH_CLIENT_SECRET` | Client Secret da Twitch |
| `UPLOADPOST_API_KEY` | API Key do upload-post |
| `ANTHROPIC_API_KEY` | *(opcional)* títulos escritos por IA |

**Variables** (aba *Variables*):
| Nome | Valor |
|---|---|
| `POSTAR` | `false` para testar · `true` para postar de verdade |

### 4. Streamers autorizados ⚠️
Edite o `config.yaml` e coloque em `streamers_autorizados` o login da Twitch de quem **liberou canais de cortes**. Sem isso o robô não corta ninguém, para evitar strike de direitos autorais.

---

## ▶️ Como testar
1. Aba **Actions** → **Cortes GTA 6** → **Run workflow** → `postar: false`
2. Quando terminar, baixe os vídeos em **Artifacts** no fim da página da execução
3. Gostou? Mude a variável `POSTAR` para `true` e o robô passa a postar sozinho a cada 3 horas

## 🧠 Ajustes rápidos (`config.yaml`)
- `idiomas`: `["pt"]` só clipes em português; `[]` todos
- `min_visualizacoes`, `janela_horas`: qualidade × quantidade de cortes
- `cortes_por_execucao`: quantos vídeos por rodada
- `modelo_whisper`: `small` (padrão) ou `medium` (legenda melhor, mais lento)
- frequência: linha `cron` em `.github/workflows/cortes.yml`

## 💻 Rodar no computador (opcional)
```bash
pip install -r requirements.txt          # precisa do ffmpeg instalado
export TWITCH_CLIENT_ID=... TWITCH_CLIENT_SECRET=...
python -m gta6_cortes.main --listar      # só lista os clipes encontrados
python -m gta6_cortes.main               # gera os vídeos em saida/ (sem postar)
```

## 🧩 Skills de agente incluídas (`.claude/skills`)
Instaladas com `npx skills add` para o Claude trabalhar neste repositório:
- `yt-dlp` — download de vídeos/clipes
- `upload-post` — referência completa da API de postagem
- `video-highlight-extraction` — detecção de melhores momentos por IA (eachlabs, pago, opcional para VODs longas)

## ⚖️ Regras importantes
- Corte só streamers que permitem. Sempre dê crédito (o robô já coloca o link).
- YouTube e TikTok reduzem o alcance de conteúdo "reaproveitado" sem nada novo. Título, legenda e edição ajudam. Comentar o corte ajuda ainda mais.
