---
name: "edit-cinema"
description: "Edita vídeos verticais (9:16) em voice over com tom cinematográfico e intelectual: cenas de filme, obras de arte e imagens históricas trocando na palavra, provas reais (manchetes, estudos, números) com fonte, motion graphics didáticos, aparições do apresentador em molduras que conversam com a edição, trilha com batida + música clássica crescendo até um final majestoso."
---

# edit-cinema — voice over cinematográfico (9:16)

**A narração conduz e a imagem obedece à palavra.** O vídeo parece um trailer intelectual: cenas de filmes reconhecíveis, quadros clássicos, filósofos e imagens históricas trocando a cada ~0,5 s, tipografia palavra por palavra no centro da tela, motion graphics quando a explicação pede didática e **provas reais** sempre que a fala afirma algo concreto. O apresentador aparece pouco e de propósito, encaixado em molduras que fazem parte da cena (TV antiga, quadro de museu, tela de celular). Tudo sob um tratamento de cor de cinema e uma trilha que começa com batida e termina orquestral e majestosa.

Pilares: **IMPACTO + COERÊNCIA** (toda imagem tem força visual e diz literalmente o que a fala diz) · **CREDIBILIDADE** (afirmação concreta = prova real com fonte) · **TOM CINEMATOGRÁFICO** (cinema, arte, história; nunca cara de banco de imagem).

Pipeline de referência pronto em `scripts/` (Python + ffmpeg, testado em Mac Apple Silicon). Leia `scripts/README.md`.

---

## 1. Antes de começar

Pergunte só o que não dá para deduzir:

1. Material: take filmado (rosto + voz, horizontal ou vertical) ou só áudio. Takes repetidos são normais; você escolhe o melhor de cada frase.
2. Cor de marca (padrão: azul elétrico `#2027FE`), @ do perfil, e o que o CTA pede (seguir / comentar palavra-chave).
3. Pasta com **prints de resultados reais** (perfil próprio, clientes) se houver momento de autoridade no roteiro.
4. Duração máxima (padrão Reels: **≤ 3:00**).

O apresentador pode deixar instruções faladas no take ("quando eu olho para a câmera é para eu aparecer"; "agora é voice over"). Transcreva tudo e obedeça; nunca deixe instrução ao editor no corte final.

**Fluxo com o usuário:** ele costuma acumular correções em sequência. Quando disser "não renderize ainda", só aplique e confira com folhas de contato; renderize quando ele liberar. Para validar som sem render, mande trechos curtos de áudio (`.m4a`). Entregue sempre prévia ≤ 30 MB (720×1280) + final 1080×1920, versionados (`_v1`, `_v2`…), nunca sobrescreva.

---

## 2. Fala

- Transcrição com tempo por palavra (mlx-whisper large-v3-turbo no Mac). Takes longos (16 min com repetições) → escolha o melhor take de cada frase, confira cada região de fala transcrevendo-a isoladamente (o Whisper alucina e repete em arquivo longo; verifique trechos curtos).
- **Corte seco sem comer sílaba:** o fim do corte segue o decaimento da última sílaba até o ruído de fundo (máx. +0,4 s), parando no vale se a próxima palavra começar. Nunca confie na borda da janela do take; "injust-", "tsunam-" cortados foram o erro mais apontado.
- Pausas planejadas só em respiros dramáticos (após a tese, antes da prova).
- **Cabe em 3 min, nesta ordem:** (1) cortar frase redundante (uma que repete o que uma prova acabou de mostrar), (2) encurtar silêncios internos > 0,2 s para 0,12 s **fora dos trechos com apresentador em cena** (lip-sync), (3) aceleração global ≤ 1,05x (atempo; ~1,02x é imperceptível; 1,1x já soa apressado). O apresentador acompanha a aceleração (`speed` no timeline).

---

## 3. Hierarquia de imagem (regra principal)

Para cada beat de 1–4 palavras, escolha pelo **papel da frase**:

| A fala é… | Use | Exemplo |
|---|---|---|
| **Afirmação concreta / prova** (pessoa real, número, estudo, notícia, resultado) | O real e explícito: clipe da pessoa, manchete original, print, dado com fonte | "o político mais votado" → clipes de Nikolas Ferreira, Pavanato, Eduarda Campopiano, Ana Elisa + manchetes reais (InfoMoney, Gazeta do Povo) |
| **Storytelling / metáfora** | **Cena de filme** reconhecível, **obra de arte**, **filósofo**, **imagem histórica** (tom intelectual) | "texto" → O Iluminado (máquina de escrever); "lixo" → WALL·E; "donos da narrativa" → Cidadão Kane |
| **Explicação didática** (comparação, proporção, processo) | **Motion graphic** | "distribuição ótima vence produto ótimo" → Big Mac 2★ jorrando dinheiro × hambúrguer artesanal 5★ "R$ 0" |
| **Lugar** | **Globo em MG** girando e dando zoom com o local aceso; cidade brasileira → mapa do Brasil com zoom na cidade; depois paisagem, bandeira, pessoas famosas do lugar | "no Brasil" → globo, Brasil azul pulsando |
| Nada acima serve | Banco de imagem — **último recurso**, evite | — |

- **Metáfora explícita ganha de imagem genérica.** "Imagem criada com IA" → Mona Lisa pop gerada do ruído, ganhando óculos, pirulito e orelhas de rato, com o prompt sendo digitado. "Todo mundo age igual" → grade 3×3 de pessoas fazendo a mesma dancinha (rostos desfocados).
- Uma ideia, uma imagem. Rajadas (3–5 frames por imagem) em listas e no gancho.
- Imagens não podem ser brutalmente saturadas; tudo passa pelo grade (seção 8).
- Trophy/objetos: escolha a versão "gloriosa e imponente" (taça da Copa no museu da FIFA, não troféu com bonequinhos) e enquadre sem cortar o objeto.

### Catálogo de cenas que funcionaram (reuse)

| Ideia | Cena |
|---|---|
| texto / escrever | The Shining — "All work and no play" na máquina de escrever |
| vídeo / cinema | Cinema Paradiso — cabine de projeção |
| IA / robô | Ex Machina (Ava); I, Robot (fileiras de NS-5); 2001 (olho do HAL 9000); Matrix (clones de Smith) |
| fabricar / produção em massa | Tempos Modernos — linha de montagem; Chaplin nas engrenagens |
| ninguém ouve / todos no celular | Her — multidão falando com os aparelhos; Theodore com o fone |
| xeque / quem vence | The Queen's Gambit — o rei entregue na mão |
| dominar / dinheiro | O Lobo de Wall Street — discurso batendo no peito; jogando notas no iate |
| McDonald's / distribuição | The Founder — arcos dourados à noite; cozinha "Speedee"; gráfico de franquias |
| dono da narrativa / mídia | Cidadão Kane — pôster gigante; Network — "mad as hell" |
| vencer / o melhor | Rocky — braços erguidos na escadaria |
| arma / arena | Gladiador — "Are you not entertained?" |
| multidão / milhões | Bohemian Rhapsody — Live Aid (aérea de Wembley e plateia batendo palmas) |
| consumo passivo / lixo de conteúdo | WALL·E — humanos nas poltronas com telas; torres e montanhas de lixo |
| ler / ouvir / assistir | Matilda lendo; Her; Laranja Mecânica (olhos presos abertos) |
| grande arte | Com Amor, Van Gogh (Noite Estrelada animada); A Criação de Adão; A Escola de Atenas |
| artificial / plástico | Blade Runner 2049 (holograma Joi); Barbie (sorriso no espelho de plástico) |
| ir além | Interstellar — a nave e o buraco de minhoca |
| inspirar / emocionar / convencer | Sociedade dos Poetas Mortos ("O Captain"); Cinema Paradiso (final); O Grande Ditador (discurso) |
| concorrência | Rush — Hunt × Lauda roda a roda |
| transformação / liberdade | Um Sonho de Liberdade — braços abertos na chuva |
| catástrofe / tsunami | O Impossível (2012) — onda invadindo o resort |
| futuro incerto / contemplação | O Viajante sobre o Mar de Névoa (Friedrich) |
| Brasil / história | Independência ou Morte! (Pedro Américo) |
| dancinha / trend | Saturday Night Fever; grade de dancinha igual; trend "será?" |

Quadros em domínio público para tom intelectual: Mona Lisa, Homem Vitruviano, Escola de Atenas, Criação de Adão, A Grande Onda (Hokusai), A Morte de Sócrates, O Pensador, A Balsa da Medusa, A Liberdade Guiando o Povo, Napoleão cruzando os Alpes, Noite Estrelada.

### Como capturar cenas de filme

1. `yt-dlp --flat-playlist --print "%(id)s | %(duration_string)s | %(title)s | %(channel)s" "ytsearch8:<filme> <cena>"` — prefira Movieclips/estúdio/uploads HD.
2. Baixe cópia leve (`-f "bv*[height<=360]"`), monte folha de contato (1 frame a cada 1–2 s) e **olhe** para achar os 3 s mais fortes.
3. Baixe só o trecho (`--download-sections "*INI-FIM"`, HD) e extraia 3 s a 30 fps em JPG. Apague o bruto (disco).
4. Se aparecer "Sign in to confirm you're not a bot": `--extractor-args "youtube:player_client=web_embedded"` (sem cookies); se vier baixa resolução, force `-f 137`.
5. O renderizador corta faixas pretas (letterbox/pillarbox) e **detecta cortes de cena escondidos** no trecho, usando só o pedaço contínuo (um "frame de outro plano" de milissegundos foi apontado como erro). Trecho curto → câmera lenta.
6. Recorte vertical centrado no personagem (`fx` = posição 0–1; `fx→fx1` se ele se move). Cena escura → `gain`.
7. Para muitas cenas, distribua em agentes paralelos por bloco do roteiro, cada um com pasta própria.

---

## 4. Credibilidade: afirmações concretas

Toda estatística, estudo, notícia ou citação **é pesquisada** e aparece com a fonte:

- **Estudo** → animação de uma folha com a **headline original** (marca-texto na frase-chave) + gráfico simplificado da curva do estudo + "Fonte: …" no rodapé.
- **Notícia / dado** → card de manchete (veículo em vermelho + título real) sobre o MG do número; rodapé com a fonte primária.
- **Citação** → card com a frase original, autor e obra/ano ("Reid Hoffman, *Blitzscaling* (2018)"); nome da pessoa grande embaixo da foto.
- **Ranking / comparação** → barras ou ranking animados com os números reais e a fonte.
- **Pessoas citadas como exemplo** → clipes reais delas + números reais (votos, seguidores).
- Se o dado da fala diverge da fonte, mostre o dado verdadeiro (fala "quase três horas", tela "+2h33") e avise o usuário. Se a fonte tem versão mais nova com números diferentes, avise.

### Autoridade com cases reais

Use os prints do usuário, **nunca IA generativa sobre provas** (pode alterar números). Momento "eu fiz isso no meu perfil e no dos meus clientes":
- Perfil próprio: avatar, @, **contador de seguidores subindo de 0 até o número real**, 3 reels do grid com selo "X views".
- Clientes: um card por cliente entrando em sequência (avatar, nome, contador subindo, melhor reel com selo de views em destaque).
- Dê **1,0–1,5 s de respiro** na voz depois dessa frase para os números serem lidos.
- Se houver números "antes", mostre antes → depois; sem eles, o 0 → N já comunica crescimento (não invente "antes").

---

## 5. Gancho

- Sem rosto no primeiro beat. O gancho é visual + texto.
- A pergunta-tese aparece **grande, palavra por palavra, se completando** no centro ("POR QUE / VIRALIZAR / ESTÁ / DIFÍCIL?"), com pancada de trailer na palavra-chave.
- A frase anterior ("criar conteúdo tá fácil") ganha uma metáfora explícita (Mona Lisa pop gerada por IA).

---

## 6. Apresentador (o usuário elogiou: manter)

10–20% do tempo, aparições de 1,5–4 s, nunca seguidas, mecanismo diferente a cada vez, sincronia labial com o mesmo timestamp do áudio. Aparecer quando ele olha para a câmera, em opinião, virada, ponte para a marca e CTA.

| Mecanismo | Como |
|---|---|
| **Portal TV** | dentro da tela de uma TV antiga (homografia nos 4 cantos, scanlines) — "o que vê na tela" |
| **Quadro de museu** | moldura dourada ao lado da Mona Lisa, plaquinhas "DA VINCI, 1503" / "OBRA HUMANA" — "não é a IA que vai produzir o próximo Da Vinci" |
| **Celular** | na tela de um celular na mão, com interface de rede social — "no meu perfil" |
| **Moldura → tela cheia** | card que cresce na palavra de virada |
| **Recorte em cantos alternados** | fundo removido (Robust Video Matting), ancorado embaixo, esquerda/direita alternando, sobre B-roll escurecido ou mosaico |
| **Tela dividida** | B-roll em cima, ele embaixo |
| **CTA** | card do rosto + botão "Seguir" sendo clicado → "Seguindo" |

---

## 7. Motion graphics (catálogo)

Chat de IA digitando (e riscado com X) · globo/mapa com zoom no lugar · comparativo de produto com estrelas e dinheiro voando · folha de estudo com headline + gráfico · relógio/contador · barras e ranking com fonte · 100 pontos virando % · um ponto azul entre cinzas ("quem se destaca?") · parede de TVs com fãs emocionados (bandeira, militância, fãs de artista) · mosaico de obras que se dilui na "média" · colagem de vídeos com padrão destacado · grade 3×3 "todo mundo igual" com rostos desfocados (YuNet) · X vermelho carimbado · contadores de cases · pessoas cinza virando azuis ("clientes divulgadores") · botão "Publicar"/"Seguir".

---

## 8. Look cinematográfico (passe final em tudo)

- **Grade:** saturação ~0,72, curva em S suave, **sombras levemente frias e altas luzes quentes**, preto levantado (~14/255). Imagens de fontes diferentes viram uma família só.
- **Lente:** aberração cromática radial (0 no centro → ~4 px nas bordas), bloom nos realces, vinheta, grão leve.
- Fundos preto (drama/tese) e branco (clareza/dados/CTA) mudam só na troca de ideia.
- Tipografia: Poppins; frase 40–64 px + palavra-chave 130–300 px com "punch"; centro da tela; glow no escuro. Texto nunca cobre legenda/rosto do material (mova para o topo).

---

## 9. Som

- **Batida** (estilo v1): bumbo, chimbal, grave em colcheias, arpejo e pad (~112 BPM), presente desde o início, ditando o ritmo, uns 13–14 dB abaixo da voz.
- **Música clássica inspiradora em domínio público, levemente acelerada (~1,06x)**, que começa baixa e **vai tomando espaço**: ~22 dB abaixo da voz no início → ~6 dB abaixo no final majestoso. Use o trecho final da peça para o clímax cair no CTA. A batida segue o **beat-grid detectado da própria peça** (librosa), afinada no tom dela; arpejo/pad saem quando a orquestra domina. Testadas: Elgar *Pomp and Circumstance nº1* (US Marine Band, Wikimedia), Grieg *In the Hall of the Mountain King* (Musopen).
- **Pancadas de trailer** (sub + estalo + metais graves) **+ flash branco de 3 frames** nas palavras-tese e nomes de peso ("Silvio Santos, Roberto Marinho, Elon Musk"; "Distribuição é PODER"; "TSUNAMI"). Máx. ~10 por vídeo; riser antes da sequência de nomes. Substituem (não somam) impactos antigos no mesmo ponto.
- Whoosh nas trocas de layout, pop em cards, tick em contadores/digitação, glitch nos glitches.
- **Final:** clique corta a música seco + som de TV desligando; a imagem do CTA espreme numa linha branca, vira um ponto e apaga.
- Voz: HPF 80 Hz, leve corte em 250 Hz, presença em 3,5 kHz, compressor 3:1; mix final −14 LUFS, pico −1,5 dBTP. Ducking ~3 dB sob a voz.
- Sem banco de áudio, sintetize os efeitos e avise que são sintéticos. Você não ouve: diga isso e mande trechos para o usuário validar.

---

## 10. QA obrigatório

1. Folha de contato com 1 frame por beat antes de cada render; confira recorte (rosto/objeto cortado?), texto sobre legenda/rosto, faixa preta, imagem genérica.
2. Cortes de cena escondidos nos trechos de filme (diferença entre frames).
3. Transcreva o áudio final **em trechos curtos**: nenhuma sílaba comida, nenhuma instrução ao editor, ordem certa.
4. Duração ≤ limite; frames do vídeo = duração do áudio.
5. Desfoque automático de rostos: confira vários frames; avise que pode escapar meio segundo.
6. Diga o que não dá para verificar (som, movimento em tempo real) e o que o usuário deve conferir.

## 11. Direitos e cuidados

Cenas de filme, clipes de terceiros e logos têm direitos dos donos: ok para Reels orgânico, arriscado em anúncio pago (Content ID pode silenciar). Prefira domínio público para música. Registre toda origem em `fontes_vN.md`. Avise sobre associações sensíveis (políticos de lados opostos, pessoas com processos) e sobre dados que mudaram.
