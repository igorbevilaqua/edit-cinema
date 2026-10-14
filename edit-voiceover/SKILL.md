---
name: "edit-voiceover"
description: "Edita vídeos verticais em voice over com imagens fortes trocando na palavra, tipografia cinética e aparições estratégicas do apresentador (moldura, recorte em cantos, portal)."
---

# edit-voiceover — voice over cinético com imagens fortes (9:16)

Estilo de edição em que **a narração conduz e a imagem obedece à palavra**. Quase o vídeo inteiro é voice over sobre imagens de impacto que trocam a cada ~0,5 s, com tipografia palavra a palavra no centro da tela, alternância brusca entre fundo preto e branco, cards flutuantes, colagens de prints e um acabamento "lente" (aberração cromática, bloom, grão, vinheta). O apresentador **aparece pouco e de propósito**: em moldura, recortado em cantos alternados sobre o vídeo, ou "dentro" do material (tela, celular, janela).

Referência analisada: Reel "Distribution is the final boss" (87 s, 4:5, 233 palavras, VO sem rosto). Os números das seções 3 a 6 vêm dela.

Os pilares são **SINCRONIA** (cada substantivo tem uma imagem e cada corte cai numa sílaba), **ESCALA** (palavra pequena × palavra gigante, rosto × planeta, card × tela cheia) e **CONTRASTE DE ATO** (preto = drama, branco = clareza/sistema/CTA).

Skill irmã: `edit-tay` (talking head com tela dividida). Reaproveite dela o pipeline técnico, os cortes secos, o som e a entrega; aqui só muda a linguagem visual.

---

## 1. Antes de começar

Pergunte só o que não dá para deduzir (AskUserQuestion):

1. **Material de voz:** é um take filmado (vídeo + áudio, então o apresentador pode aparecer com sincronia labial) ou só áudio? Sem vídeo, as aparições da seção 7 ficam restritas a planos sem fala (reação, olhar, gesto).
2. **Banco de imagens:** pasta com B-roll, prints, fotos de pessoas citadas, logos. Se faltar, a etapa 4 do pipeline gera o **mapa visual** para o usuário completar antes do render.
3. **Formato:** padrão 9:16 1080×1920 30 fps. A referência é 4:5. Mantenha tudo que importa dentro da **área segura central 1080×1350**, assim o mesmo render serve para feed 4:5.
4. **Cor de marca:** a referência usa um azul elétrico (#2027FE) só no ato final (marca/produto/CTA). Pergunte a cor do usuário; se não houver, use esse azul.
5. **CTA:** palavra-chave de comentário ("Comente MÚSICA") e o que é entregue (ebook, aula, playbook).

---

## 2. Pipeline técnico

Mesmo ambiente da `edit-tay` (HuggingFace bloqueado, modelos dos releases do GitHub):

```bash
pip install sherpa-onnx onnxruntime librosa soundfile opencv-python-headless --break-system-packages
R=https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models
curl -sSLO $R/sherpa-onnx-whisper-turbo.tar.bz2                   # texto pt
curl -sSLO $R/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8.tar.bz2  # timestamps por palavra (pt; v2 = só inglês)
curl -sSLO $R/silero_vad.onnx
curl -sSL -o u2net_human_seg.onnx https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net_human_seg.onnx
# Fontes (raw.githubusercontent.com/google/fonts/main/ofl/...): Poppins (300/500/600/700/800), Inter, InstrumentSerif (itálico de contraste, opcional)
```

Sherpa: `tokens` que começam com espaço iniciam palavra nova; decodifique em janelas de ≤20 s e some o offset.

**Etapas:**

1. **Proxies e áudio:** igual à `edit-tay` (30 fps h264 crf 14; áudio 48 kHz mix + 16 kHz mono).
2. **Transcrição** com timestamps por palavra (VAD → Whisper texto → Parakeet tempos → alinhar com difflib).
3. **Limpeza da fala:** mesma classificação FALA / INSTRUÇÃO / TAKE_REPETIDO / ERRO e as mesmas regras de **corte seco** da `edit-tay` (ataque −44 dBFS, corte 35 ms antes, gap 0,02 s). Em VO a tolerância a respiro é ainda menor: o único silêncio permitido é a **pausa de respiro visual** (seção 3).
4. **Roteiro visual (beat sheet) — obrigatório antes de renderizar:**
   - Quebre a fala em **beats de 1–4 palavras**. Cada beat recebe: `t_in`, `t_out`, `texto`, `palavra_chave`, `imagem` (arquivo ou MG a gerar), `layout` (seção 5), `texto_estilo` (seção 6), `transição` (seção 8), `sfx`.
   - **Mapeamento literal:** todo substantivo concreto ou nome próprio vira imagem ("iPhone" → keynote do iPhone; "mídia" → parede de TVs; "Elon" → foto do Elon). Conceitos abstratos viram metáfora visual forte ("barreira" → muro; "fracasso" → multidão no escuro com flash).
   - Gere `mapa_visual.md` (tabela tempo | fala | imagem necessária | tenho? ) e mostre ao usuário o que falta. Só renderize com o mapa fechado ou com a decisão explícita de gerar MG no lugar.
5. **EDL** (`edl.py`): lista de beats em frames (30 fps). Camadas por beat: `bg` (cor/imagem/vídeo), `media` (card/fullscreen/colagem), `presenter` (nenhum/moldura/recorte/portal), `text`, `fx`.
6. **Render:** Python (PIL + numpy + cv2) frame a frame por pipe rawvideo → libx264 crf 15; leitor de fonte via ffmpeg `-ss T -i SRC -vf crop,scale,fps=30 -f rawvideo -`; 2 processos em paralelo; validar contagem de frames; **folha de contato com 3 frames por beat antes do render final**.
7. **Passe final de "lente"** (seção 9) + mix (seção 10) → entrega (seção 12).

---

## 3. Ritmo (números da referência)

| Medida | Valor |
|---|---|
| Velocidade da fala | ~160 palavras/min, quase sem pausas |
| Mudança visual (corte, troca de imagem ou de texto grande) | **mediana 0,45 s**, média 1,0 s, máx ~6,8 s (só em colagem animada) |
| Cortes que caem no início de uma palavra (±120 ms) | ~60%; o resto cai no meio de uma palavra longa ou em tempo de música |
| Densidade por trecho | 0–30 s: ~1,5 mudança/s · 30–60 s: ~0,9/s · 60 s–fim: ~0,8/s, mas com movimento interno contínuo (colagens, zooms) |
| Rajada de abertura | 10 rostos em 1,3 s (**3–4 frames cada**) |
| Rajadas internas | 3–6 planos de 5–10 frames numa mesma frase ("GREAT DISTRIBUTION", "extrapolated to any business") |
| Trilha | ~112 BPM, contínua |

**Regras:**

- **Nada parado.** Toda imagem tem movimento: push-in 1.00→1.08 em 1 s, parallax, Ken Burns, flutuação de cards, scroll de colagem.
- **A frase-tese segura; o resto voa.** Os dois únicos planos "quietos" da referência são a tese ("Distribution is the final boss", ~1,1 s em preto) e o reset minimalista ("THE ONLY THING THAT MATTERS", ~1,7 s em branco). Use 1–2 respiros desses por minuto, nunca mais.
- **Acelere no começo, organize no fim.** O primeiro terço é corte puro na palavra. O último terço troca cortes por colagens e transformações de objeto (perfil → círculos → produto).
- Rajada = mesma ideia em várias imagens. Use para listas ("negócio, marca pessoal"), progressões (Elon jovem → atual) e ênfase.

---

## 4. Arco narrativo que a edição acompanha

A referência é um vídeo de **tese → prova → ponte para a própria marca → CTA de comentário**. A edição muda de linguagem a cada ato:

| Ato | Tempo ref. | Fala (resumo) | Linguagem visual |
|---|---|---|---|
| 1. Gancho/tese | 0–2,4 s | "Distribution is the final boss" | Rajada de rostos famosos (3–4 frames) com UMA palavra fixa no centro → corte para preto com a frase-tese em glow |
| 2. Contexto/mundo | 2,5–9 s | "Num mundo onde qualquer pessoa cria qualquer coisa em minutos…" | Zoom-out de escala (satélite → globo), match de forma (globo → círculo branco → círculo preto no branco), MG minimalista (ponto que explode em partículas), print de UI digitando um prompt |
| 3. Reset | 9,4–11 s | "a única coisa que importa é…" | Branco total, caixa alta fina e espaçada surgindo palavra a palavra |
| 4. Definição + contraste A/B | 11–27 s | "distribuição e mídia… ideia ótima + zero distribuição = fracasso; ideia ruim + boa distribuição = sucesso" | Uma imagem-símbolo por conceito (feed no celular, parede de TVs, outdoor na estrada vazia); tela dividida cima/baixo (ilustração + contador do YouTube caindo a 0); flash invertido no "VOCÊ VAI FALHAR" |
| 5. Autoridade | 27–38 s | "Ideias não bastam mais…" | Progressão de rosto travado (mesma pessoa, 5 idades), clipes de keynote em cards pequenos no preto, card que cresce até tela cheia em "na frente das pessoas" |
| 6. Generalização | 38–58 s | "vale para qualquer negócio… o produto só é tão bom quanto a distribuição" | Montagem cheia de B-roll cinematográfico com legenda de 2 linhas; cenas de filme em letterbox com UMA palavra por vez; logos de fundos de VC como tiles 3D com glow; pilha de prints de posts |
| 7. Ponte para a marca | 58–80 s | "você aprende vendo quem já conseguiu… por isso criamos a página" | Colagem escura de janelas (estilo macOS) e perfis; barra de busca do Google nascendo de um ponto; grade de celulares com os próprios vídeos no branco; mosaico denso com glitch; objeto da marca orbitado por círculos da cor de marca |
| 8. CTA | 83–87 s | "Comente MEP e a gente te envia" | Branco limpo, pílula com contorno, palavra-chave revelada letra a letra, linha de apoio embaixo |

Use esse arco como molde quando o roteiro for desse tipo. Para outros roteiros, mantenha a lógica: **cada mudança de ato muda fundo, escala ou tipo de mídia.**

---

## 5. Layouts de beat (sem apresentador)

| Layout | Composição | Uso |
|---|---|---|
| **FULL** | Imagem/vídeo tela cheia, texto centralizado por cima | Padrão para B-roll forte, montagens, rajadas |
| **CARD** | Mídia num card (4:5, 16:9 ou letterbox 2.39:1) ocupando 55–96% da largura, sobre preto ou branco liso. Bordas com franja de aberração cromática (verde→ciano→azul), não contorno desenhado; glow suave ao redor | Clipes de keynote, prints, cenas de filme, "citação visual". Transmite curadoria |
| **CARD→FULL** | O card escala até preencher a tela (8–12 frames, ease-in-out) | Momento de imersão: "na frente das pessoas", "dentro do mercado" |
| **STACK** | Tela dividida vertical: cima = imagem conceitual, baixo = prova (print, contador, gráfico); legenda pequena em caixa alta na emenda | Causa → efeito, ideia → resultado |
| **TIPO PURO** | Só texto sobre preto (com glow) ou branco (sem glow) | Tese, reset, CTA |
| **MG** | Motion graphics gerados: ponto → partículas, círculos, ícones de pessoas orbitando, tiles 3D de logos, barra de busca, janelas | Conceitos abstratos e o ato da marca |
| **COLAGEM** | 4–20 cards (janelas com semáforo do macOS, celulares, polaroids, prints) em grade ou mosaico, com scroll/parallax lento e entradas defasadas de 2–3 frames | Prova social, volume de trabalho, "estudos de caso" |

**Fundo como sinal de ato:** preto = drama, tese, autoridade, cinema. Branco = sistema, clareza, produto, CTA. Troque o fundo **no corte de mudança de ideia**, nunca no meio de uma frase.

---

## 6. Tipografia (o segundo protagonista)

- **Família:** Poppins (geométrica). SemiBold 600 para frases, Bold/ExtraBold 700–800 para palavras-chave, Light 300 em caixa alta espaçada (tracking +0,3 em) para momentos minimalistas.
- **Posição:** **centro da tela** (ou terço superior quando o assunto ocupa o centro). Não é legenda de rodapé.
- **Revelação palavra a palavra (padrão):** a palavra entra no seu timestamp com 4 frames de fade + blur 8→0 px + subida de 12 px. Variante "karaokê": a frase inteira aparece em cinza a 35% e cada palavra fica branca quando é dita.
- **Hierarquia em dois níveis:** frase em ~40–48 px (a 1080 de largura) + palavra-chave em 130–200 px logo abaixo ("And creation is no longer a / **Barrier**"; "ADVERSELY YOU CAN HAVE A / **TERRIBLE IDEA**"). A palavra grande entra com um "punch" (escala 1.15→1.0 em 5 frames).
- **Palavra única:** em letterbox e em rajadas, uma palavra por vez (≤3 frames de sobreposição com a próxima).
- **Glow:** texto branco sobre escuro recebe bloom (cópia desfocada com raio ~18 px a 35%). No branco, sem glow; texto preto ou cinza-escuro.
- **Texto dentro da cena:** sempre que der, o texto vira objeto do mundo: outdoor, tela de TV, barra de busca sendo digitada, janela de alerta estilo Windows 95 ("made $10,000"), destaque azul tipo marca-texto em print.
- **Texto sobre rosto:** na rajada de abertura, a palavra fica fixa no centro (na altura dos olhos) enquanto os rostos trocam por baixo; blend normal com sombra leve, ou "difference" para ler em qualquer fundo.
- Sem legenda quando o texto já está na imagem.
- Em português, escolha a palavra-chave pela **semântica**, não pela posição: em "a distribuição é o chefão final", a chave é "distribuição", depois "chefão final".

---

## 7. Aparições do apresentador (mecanismos)

Regra geral: **o apresentador é tempero.** 10–20% do tempo de tela, aparições de 1,5–4 s, nunca duas seguidas, nunca no primeiro segundo (o gancho é visual). Cada aparição usa um mecanismo diferente da anterior. Com take filmado, o vídeo usa **exatamente o mesmo timestamp do áudio** (sincronia labial); sem vídeo, só reações mudas.

**Quando aparecer:**

- **Revelação da tese / virada** ("e é aqui que todo mundo erra"): o rosto dá peso pessoal.
- **Opinião ou confissão** ("eu aprendi isso do pior jeito").
- **Ponte para a marca** ("por isso a gente criou…"): o apresentador "assina" o que vem depois.
- **Antes do CTA:** 1–2 s de rosto pedindo o comentário, depois o card do CTA.
- Nunca no meio de uma rajada de prova; ali o material fala sozinho.

**Mecanismos:**

| # | Mecanismo | Como fazer | Quando |
|---|---|---|---|
| A | **MOLDURA** | O apresentador num card igual aos de mídia (4:5, 60–70% da largura, sobre preto/branco, franja cromática + glow, flutuação leve). Pode alternar com cards de mídia no mesmo lugar, como se ele fosse "mais um clipe" da curadoria | Opinião curta entre provas; manter a estética coesa |
| B | **MOLDURA→FULL** | A moldura cresce até a tela cheia (CARD→FULL) na palavra de virada e volta a card, ou corta seco para B-roll | Virada, frase-tese pessoal |
| C | **RECORTE EM CANTOS ALTERNADOS** | Fundo removido (u2net_human_seg + refinamento da borda com guided filter / feather 2 px). O apresentador ocupa 45–55% da altura, ancorado embaixo, **colado à borda esquerda numa frase e à direita na seguinte**. O B-roll continua tela cheia atrás, escurecido 20–30% e com blur leve (3–6 px) para destacar. Entrada deslizando da lateral em 6 frames com overshoot; troca de lado sempre num corte de B-roll + whoosh. Sombra de contato suave e rim light branco a 20% na borda do recorte | Comentar "sobre" o material, como um apresentador de telejornal moderno |
| D | **TEXTO ENTRE CAMADAS** | Fundo (B-roll) → palavra gigante → apresentador recortado na frente, cobrindo parte das letras | Palavra-chave dita por ele ("DISTRIBUIÇÃO") |
| E | **PORTAL** | O apresentador aparece **dentro** de um objeto do material: uma das TVs da parede, um celular da grade, uma janela da colagem, o outdoor. Homografia com cv2.getPerspectiveTransform nos 4 cantos da tela + leve reflexo/scanlines para integrar | Ponte para a marca ("eu também estou aqui"); colagens |
| F | **ÚLTIMO ROSTO DA RAJADA** | Na rajada de rostos famosos com o olhar travado na mesma posição (seção 8), o último rosto é o dele, que segura e começa a falar | Gancho autoral: "e eu descobri por quê" |
| G | **ÍRIS** | Um círculo (o mesmo do match de forma) se abre e revela o apresentador; ou ele fecha a cena encolhendo para um círculo que vira o próximo objeto | Transição de ato |
| H | **CONGELA + FLASH** | Na palavra de impacto, frame do apresentador congela, inverte para P&B de alto contraste por 3–4 frames com riscos de luz, e volta | Ênfase dramática, no máximo 1× por vídeo |

**Enquadramento:** rosto com o topo da cabeça a 8–15% do topo do quadro (ou do card); olhos no terço superior. Em recorte, nunca corte o queixo nem as mãos no meio do gesto. A grade de cor do apresentador segue a do B-roll ao redor (contraste alto, pretos esmagados, saturação ×0,85) para não parecer colado.

---

## 8. Transições (catálogo)

Corte seco na sílaba é 80% delas. As especiais marcam mudanças de ato:

- **Corte na palavra + glitch de 2 frames** (deslocamento RGB 6–10 px + fatia horizontal deslocada) nas trocas de mídia mais bruscas.
- **Rajada com olhar travado (face-lock):** alinhe os rostos pelos olhos (detector de landmarks do OpenCV / mediapipe; ou alinhamento manual por 2 pontos) para que os olhos fiquem no mesmo lugar em todos os frames; 3–5 frames por rosto.
- **Zoom de escala:** do macro ao cósmico (rua → satélite → globo) ou o inverso, com crossfade de 4–6 frames e zoom contínuo.
- **Match de forma:** o objeto vira forma (globo → círculo branco), a forma inverte (círculo branco no preto → círculo preto no branco) e a forma vira o próximo assunto (círculo → ponto → partículas).
- **Ponto que nasce:** um ponto de luz cresce até virar o objeto (barra do Google, avatar, ícone).
- **Card que cresce (CARD→FULL)** e o inverso (tela cheia que encolhe para card e se junta à colagem).
- **Flash invertido:** P&B de alto contraste com riscos de luz, 3–6 frames, no impacto.
- **Transformação de objeto:** avatar → círculos da cor da marca → capa do produto, com círculos de overshoot passando pela tela.
- **Marquee:** texto gigante correndo horizontal sobre o produto, com motion blur.

---

## 9. Acabamento "lente" (passe final)

Aplicado sobre tudo, inclusive o apresentador:

- **Aberração cromática radial:** 0 px no centro → 3–4 px nas bordas (desloque R para fora e B para dentro). É ela que cria a franja azul/verde na borda dos cards.
- **Bloom/halação:** realces acima de ~85% de luminância → blur de raio 20 px → screen a 25%.
- **Desfoque de periferia:** máscara radial, blur de 4–6 px fora de 70% do raio (vale principalmente para fotos de rosto tela cheia).
- **Grão leve** (`noise=c0s=5:c0f=t+u`) e **vinheta** (`vignette=PI/5`).
- **Grade:** contraste alto, pretos esmagados, saturação ×0,85–0,9, leve calor nos médios. Imagens de fontes diferentes passam pela mesma grade para parecerem da mesma família.

---

## 10. Som

Base igual à `edit-tay` (cadeia de voz, −14 LUFS, SFX cortados com fade no fim da cena). Específico deste estilo:

- **Trilha contínua** (~105–120 BPM, cinematográfica/eletrônica, sem vocal) a −18/−20 dB do RMS da voz, com ducking leve. No reset branco e no CTA, a trilha pode baixar ou abrir para um pad.
- **SFX densos e baixos** (−18 a −24 dB): whoosh curto em troca de layout, glitch nos glitches, "tick" de digitação na barra de busca e em prints, pop nas entradas de cards e ícones, impacto grave no flash invertido e na frase-tese, riser de 1–1,5 s antes da ponte para a marca.
- Na rajada de abertura, um "stutter" de clique ou batida por rosto vende a velocidade.
- Sem banco de áudio: sintetize em numpy e **avise o usuário que é sintético**.

(A análise da trilha da referência foi feita por espectro e detecção de onsets, não por audição: ~112 BPM, nível estável, transientes agudos coincidindo com boa parte das trocas visuais.)

---

## 11. QA obrigatório

1. Folha de contato a cada 0,5 s do primeiro 10 s (o gancho) e a cada 2 s do resto. Confira: texto fora da área segura 4:5, legenda colidindo com rosto, card cortado, imagem repetida em beats seguidos.
2. Transcreva o áudio final: nenhuma instrução ao editor, nenhuma frase sem começo, ordem certa.
3. **Sincronia:** para cada beat com palavra-chave, a imagem correspondente aparece no máximo 2 frames antes e 3 frames depois do início da palavra.
4. **Mudança visual:** nenhum trecho > 2 s sem mudança ou movimento perceptível (exceto os respiros planejados).
5. Apresentador em 10–20% do tempo; nenhuma aparição seguida de outra com o mesmo mecanismo.
6. Frames por beat = esperado; duração do áudio = duração do vídeo.
7. Diga ao usuário o que você não consegue verificar (você não ouve o resultado nem vê movimento em tempo real) e o que vale ele conferir.

---

## 12. Entrega

Igual à `edit-tay`: final versionado em `/mnt/user-data/outputs/NOME_vN.mp4`, nunca sobrescrever; pasta conectada com o contorno de `split` para mp4 grande; prévia ≤30 MB (720×1280, 2 passes) para ver no celular. Entregue também o `mapa_visual.md` atualizado, porque ele é a lista de troca de imagens para as próximas versões. Resposta final curta: o que mudou, por pedido, e o que conferir.

---

## 13. Lições da referência

- A força vem da **escolha da imagem**, não do efeito: rostos que todo mundo reconhece, escala extrema (planeta, multidão, parede de TVs), cinema, e prints reais como prova. Efeito sem imagem forte vira ruído.
- **Uma ideia, uma imagem, uma palavra na tela.** Quando a frase tem duas ideias, são dois planos.
- Repetir a mesma palavra-chave em imagens diferentes ("distribution" é dita 8 vezes em 87 s) costura o vídeo inteiro. Escolha a palavra-tese e volte a ela.
- Prova da própria marca vem **depois** da tese universal e de autoridades externas. A ordem é: o mundo → os grandes → você.
- O CTA é o momento mais limpo do vídeo (branco, uma pílula, uma palavra). Depois do caos, o silêncio visual faz a pessoa ler.