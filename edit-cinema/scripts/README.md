# Pipeline de referência — edit-cinema

Implementação usada para criar o primeiro vídeo nesse estilo (3 min, 9:16, 100 beats). Python + ffmpeg, renderizando frame a frame com PIL/numpy/OpenCV. Testado em Mac Apple Silicon.

## Instalar

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python mlx-whisper numpy "opencv-python-headless<5" pillow soundfile onnxruntime librosa
brew install ffmpeg yt-dlp
# fontes Poppins 300/500/600/700/800 em fonts/ (github.com/google/fonts/ofl/poppins)
# modelos: rvm.onnx (RobustVideoMatting mobilenetv3), yunet.onnx (OpenCV zoo face_detection_yunet)
```

## Ordem

| Etapa | Arquivo | O que faz |
|---|---|---|
| 1 | `transcribe.py`, `words.py` | transcrição com tempo por palavra (mlx-whisper) |
| 2 | `exemplo_takes.py` → `takes.py` | janela do melhor take de cada frase (no vídeo original) |
| 3 | `regions.py`, `verify.py`, `dumpwords.py` | regiões de fala por energia; confere cada uma transcrevendo isolada |
| 4 | `segs.py` | corte final: segue o decaimento da sílaba; `SKIP` remove frases redundantes |
| 5 | `timeline.py` | monta `voice_raw.wav` + `timeline.json` (palavras na linha do tempo final); aperta silêncios fora do lip-sync; acelera o mínimo para caber em `MAXLEN` |
| 6 | `presenter.py` | frames do apresentador nos trechos em que ele aparece + matte (RVM) para recorte |
| 7 | `fetch.py`, `sheet.py` | busca imagens (Wikimedia/Openverse) e folha de contato |
| 8 | cenas de filme | `yt-dlp` → trecho de 3 s em `filme/shots/<id>/0001..0090.jpg` (ver SKILL.md, seção 3) |
| 9 | `danca_blur.py` | trechos com rostos desfocados (YuNet) |
| 10 | `exemplo_beats.py` → `beats.py` | **o roteiro visual**: um `B(tempo, layout, textos, ...)` por beat; `HIT()` = pancada + flash |
| 11 | `render.py sheet out.jpg t1 t2 …` | folha de contato de qualquer instante (use antes de renderizar) |
| 12 | `audio.py` | trilha de abertura opcional (`INTRO_BED`) + batida + clássica crescendo + silêncio estratégico (`SILENCES`) + sfx + pancadas + TV desligando + voz → `mix.wav` (−14 LUFS) |
| 13 | `render.py chunk i n` | render paralelo em n partes; depois concat + mux com `mix.wav` |

`lib.py` = primitivas (Ken Burns, cards, tipografia palavra-a-palavra, apresentador, lente, grade de cinema). `layouts.py` = layouts e motion graphics (globo, comparativo, folha de estudo, ranking, cases, grade 3×3, portal TV/celular/quadro, CTA…).

Caminhos esperados: vídeo bruto em `../`, prints de cases em `../cases/`, imagens em `imgs/`, cenas em `filme/shots/`, saída em `../saida/`.
Ajuste `SRC` em `timeline.py`/`presenter.py` e `CASES` em `layouts.py` para o seu material.
