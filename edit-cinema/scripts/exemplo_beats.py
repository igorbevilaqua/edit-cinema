# beat sheet: B(start, layout, text items, theme, ty, fx, sfx, note). ends = next start.
from layouts import *

BEATS = []
def B(t0, draw, text=(), theme="img", ty=960, fx=(), sfx="cut", img="", f0=55.0):
    BEATS.append(dict(t0=t0 - F1, draw=draw, text=list(text), theme=theme, ty=ty, fx=list(fx), sfx=sfx, img=img, f0=f0))

# pancadas de trailer + flash branco nas frases-tese (palavra de ênfase)
HITS = []
def HIT(t, f0=49.0): HITS.append((t - F1, f0))

S = lambda seg: TL[seg]["t0"]

# 1 GANCHO -------------------------------------------------------------
B(0, burst(["f_texto", "adao", "f_video", "atenas", "f_ia", "kanagawa", "f_starry", "vitruvian", "f_hal", "viajante"], 3), [Tx("Criar conteúdo", "hook1", 0, "sm")],
  sfx="stutter", img="rajada rápida: cinema + obras de arte (3 frames cada)")
B(w("hook1", 2), mg_monapop(w("hook1", 2) - F1, speed=1.8), [Tx("Criar conteúdo", "hook1", 0, "sm", y=1500), Tx("tá fácil", "hook1", 2, "big", y=1640)], theme="dark",
  img="MG: Mona Lisa pop gerada por IA (óculos, pirulito, orelhas) em 'tá fácil'")
Q = dict(toks=[(s, w("hook2", i) - F1) for s, i in (("Por", 1), ("que", 2), ("viralizar", 3), ("está", 4), ("difícil?", 6))], sty="big", color=None, y=None, out=None)
B(w("hook2", 1), tipo(), [Q],
  theme="dark", fx=["glitch"], sfx="impact", img="tipo preto: só voz + escrita sincronizada")

# 2 CONTEXTO ----------------------------------------------------------
B(S("ia1"), mg_chat("crie um post viral pra mim", S("ia1") + 0.1, cps=30), [Tx("Hoje todo mundo gera", "ia1", 0, "sm", y=380)], theme="dark", sfx="whoosh", img="MG chat de IA digitando")
B(w("ia1", 4), film("f_texto", "full", z=(1.05, 1.15), fx=0.5), [Tx("texto", "ia1", 4, "big")], fx=["glitch"], img="máquina de escrever")
B(w("ia1", 5), full("kanagawa", (1.0, 1.12)), [Tx("imagem", "ia1", 5, "big")], theme="img", img="Mona Lisa pop (IA)")
B(w("ia1", 6), film("f_video", "full", z=(1.0, 1.1), fx=0.55), [Tx("vídeo", "ia1", 6, "big")], img="câmera de cinema")
B(w("ia1", 7), tipo(), [Tx("em", "ia1", 7, "sm"), Tx("minutos", "ia1", 8, "big")], theme="dark", img="tipo preto")
B(w("ia1", 9), film("f_ia", "full", z=(1.0, 1.08), fx=0.50), [Tx("com IA", "ia1", 9, "big")], fx=["glitch"], img="robô")
B(S("ia2"), film("f_fabricar", "full", z=(1.0, 1.08), fx=0.45), [Tx("Fabricar", "ia2", 0, "big"), Tx("conteúdo nunca foi", "ia2", 1, "sm")], img="linha de montagem")
B(w("ia2", 4), film("f_simples", "full", z=(1.0, 1.05), fx=0.70, fx1=0.40), [Tx("tão simples", "ia2", 4, "big")], img="data center")

# 3 RESET -------------------------------------------------------------
B(S("ia3"), mg_particles(w("ia3", 3)), [Tx("Mas conteúdo pronto", "ia3", 0, "lt", y=700), Tx("é só o começo", "ia3", 3, "md", y=1400)],
  theme="light", sfx="whoosh", img="MG ponto que explode, branco")
B(S("ouvir"), film("f_ouvir1", "full", z=(1.0, 1.08), fx=0.5), [Tx("Difícil", "ouvir", 0, "big"), Tx("é alguém", "ouvir", 1, "sm")], sfx="whoosh", img="multidão vista de cima")
B(w("ouvir", 3), film("f_ouvir2", "full", z=(1.0, 1.08), fx=0.58), [Tx("parar pra", "ouvir", 3, "sm"), Tx("te ouvir", "ouvir", 5, "big")], img="metrô, todos no celular")

# 4 PODER -------------------------------------------------------------
B(S("injusta"), film("f_chess", "full", z=(1.0, 1.08), fx=0.5), [Tx("No entanto, quem consegue", "injusta", 0, "sm")], img="rei do xadrez")
B(w("injusta", 4), film("f_domina", "full", z=(1.0, 1.06), fx=0.50, fx1=0.66), [Tx("domina", "injusta", 4, "big")], img="Banco Imobiliário")
B(w("injusta", 5), film("f_mercado", "full", z=(1.0, 1.08), fx=0.45), [Tx("qualquer mercado", "injusta", 5, "big")], img="dinheiro na mão")
B(w("injusta", 7), tipo(), [Tx("de forma quase", "injusta", 7, "sm"), Tx("injusta", "injusta", 10, "big")], theme="dark", img="tipo preto")
B(w("injusta", 10), tipo(), [Tx("de forma quase", "injusta", 7, "sm"), Tx("injusta", "injusta", 10, "big")], theme="dark", fx=["flash"], sfx="impact")
B(S("mcd1"), film("f_mcd", "full", z=(1.0, 1.1), fx=0.5), [Tx("Ninguém considera o", "mcd1", 0, "sm"), Tx("McDonald's", "mcd1", 3, "big")], img="McDonald's à noite")
B(w("mcd1", 4), film("f_mcd2", "letterbox", cy=900), [Tx("a melhor", "mcd1", 4, "sm", y=330), Tx("lanchonete?", "mcd1", 6, "md", y=1640)], theme="dark", sfx="pop", img="card: arcos dourados")
B(S("mcd2"), p_split("mcd2", switch((S("mcd2"), film("f_mcd2", "full", fx=0.55)), (w("mcd2", 7), film("f_fatura", "full", fx=0.62)))),
  [Tx("todo mundo sabe quem ela é", "mcd2", 1, "sm", y=640), Tx("quem mais fatura", "mcd2", 11, "md", y=820)], sfx="whoosh",
  img="TELA DIVIDIDA: McDonald's → dinheiro em cima, VOCÊ embaixo")
B(S("poder"), tipo(), [Tx("Distribuição", "poder", 0, "big"), Tx("é poder", "poder", 1, "md")], theme="dark", sfx="impact", img="TESE em preto")

# 5 AUTORIDADE --------------------------------------------------------
B(S("nomes"), full("silvio", (1.1, 1.18), (0.5, 0.3)), [Tx("Silvio Santos", "nomes", 0, "md", y=1560)], sfx="hit", f0=49.0, fx=["whiteflash"], img="Silvio Santos")
B(w("nomes", 2), full("marinho", (1.1, 1.18), (0.55, 0.35)), [Tx("Roberto Marinho", "nomes", 2, "md", y=1560)], sfx="hit", f0=55.0, fx=["whiteflash"], img="Roberto Marinho")
B(w("nomes", 4), full("musk", (1.1, 1.18), (0.5, 0.3)), [Tx("Elon Musk", "nomes", 4, "md", y=1560)], sfx="hit", f0=41.2, fx=["whiteflash"], img="Elon Musk")
B(S("narr1"), mg_tvwall(["silvio", "fan_bandeira", "marinho", "fan_pt", "musk", "fan_choro", "beatlemania", "fan_army", "f_kane", "fan_pt2", "f_narrativa", "f_publico"]),
  [Tx("Empresários que dominam", "narr1", 0, "sm", y=250), Tx("canais de comunicação", "narr1", 3, "md", y=1680)], theme="dark", sfx="whoosh", img="MG parede de TVs")
B(w("narr1", 6), film("f_kane", "full", z=(1.0, 1.1), fx=0.48), [Tx("se tornam", "narr1", 6, "sm"), Tx("donos da narrativa", "narr1", 8, "big")], theme="dark", fx=["glitch"])
B(S("narr2"), film("f_narrativa", "full", z=(1.0, 1.08), fx=0.52), [Tx("E o dono da narrativa diz", "narr2", 0, "sm"), Tx("qual produto", "narr2", 6, "md")], img="Times Square")
B(w("narr2", 8), cardl("taca", aspect=4 / 5, wf=0.72, z=(1.55, 1.65), f=(0.47, 0.24)), [Tx("é melhor", "narr2", 8, "big", y=1620)], theme="dark", sfx="pop", img="card: troféu")

# 6 LINKEDIN ----------------------------------------------------------
B(S("linkedin"), with_overlay(cardl("hoffman", aspect=4 / 5, wf=0.72, cy=900), lambda fr, t, lt, d: quote_card(fr, "A good product with great distribution will almost always beat a great product with poor distribution.", "Reid Hoffman, Blitzscaling (2018)", W / 2, 1640, t, w("linkedin", 4))), [Tx("O cofundador do LinkedIn", "linkedin", 0, "sm", y=300), Tx("Reid Hoffman", "linkedin", 1, "md", y=1420)],
  theme="dark", sfx="pop", img="card: Reid Hoffman")
B(w("linkedin", 7), mg_burgers("linkedin"), [], theme="light", sfx="whoosh", img="MG Big Mac (distribuição ótima, dinheiro jorrando) × hambúrguer artesanal (produto ótimo, distribuição ruim)")

# 7 BRASIL ------------------------------------------------------------
B(S("brasil"), mg_globe(w("brasil", 6) - 0.1), [Tx("Mas", "brasil", 0, "sm", y=300), Tx("no Brasil", "brasil", 1, "big", y=430)], theme="dark", sfx="riser", img="MG globo girando até o Brasil em azul + zoom")
B(w("brasil", 6), full("rio", (1.1, 1.2)), [Tx("em outro", "brasil", 6, "sm"), Tx("patamar", "brasil", 8, "big")], fx=["glitch"], img="Rio de Janeiro")
B(S("horas1"), film("f_her_sub", "full", z=(1.0, 1.06), fx=0.24), [Tx("O brasileiro passa mais de", "horas1", 0, "sm")], img="pessoa no celular")
B(w("horas1", 5), with_overlay(mg_ring(9, "h", w("horas1", 5) - 0.1, w("horas1", 6) + 0.2, 9.22 / 24), lambda fr, t, lt, d: (news_card(fr, "Poder360", "Brasileiros passam 9 horas por dia na internet, diz estudo", W / 2, 260, t, w("horas1", 5)), footnote(fr, "Digital 2024 — DataReportal / We Are Social & Meltwater: 9h13 por dia", 1520, t, w("horas1", 5) + 0.3))),
  [Tx("por dia na internet", "horas1", 7, "sm", y=1420)], theme="dark", sfx="tick", img="MG relógio 9h + manchete Poder360 + fonte")
B(S("horas2"), mg_bars("horas2"), [Tx("quase três horas acima", "horas2", 0, "sm", y=380), Tx("da média do mundo", "horas2", 4, "sm", y=1520)], theme="light", sfx="whoosh", img="MG barras Brasil × mundo")
B(S("segunda"), mg_rank("segunda", w("segunda", 2) - F1), [Tx("Somos a", "segunda", 0, "sm", y=420), Tx("segunda população que mais consome", "segunda", 2, "sm", y=420)], theme="dark", sfx="whoosh", img="MG ranking tempo online (DataReportal)")
B(w("segunda", 7), full("paulista", (1.0, 1.12)), [Tx("conteúdo online", "segunda", 7, "big")], img="multidão na Paulista")
B(w("segunda", 9), full("earth", (1.0, 1.25), (0.42, 0.6)), [Tx("no planeta", "segunda", 9, "big")], img="multidão")
B(S("gente"), p_tv("gente"), [Tx("É muita gente formando opinião", "gente", 0, "sm", y=330), Tx("com o que vê na tela", "gente", 5, "md", y=1600)],
  theme="dark", sfx="whoosh", img="PORTAL: VOCÊ dentro da TV antiga")
B(S("tsunami"), full("independencia", (1.0, 1.15), (0.5, 0.45)), [Tx("Empreender no Brasil sem essa", "tsunami", 0, "sm"), Tx("arma", "tsunami", 5, "big")], img="skyline ao entardecer")
B(w("tsunami", 6), film("swim", "letterbox"), [Tx("é como", "tsunami", 6, "sm", y=1330), Tx("nadar", "tsunami", 8, "big", y=1470)], theme="dark", sfx="whoosh", img="FILME O Impossível: menino nadando na correnteza")
B(w("tsunami", 9), film("aerial", "letterbox"), [Tx("contra a correnteza", "tsunami", 9, "md", y=1430), Tx("de uma", "tsunami", 12, "sm", y=1580)], theme="dark", img="FILME: onda invadindo o resort (aérea)")
B(w("tsunami", 14), film("crash", "full", z=(1.0, 1.25)), [Tx("tsunami", "tsunami", 14, "xl")], fx=["flash"], sfx="impact", img="FILME: parede de água")
B(S("lado1"), film("f_publico", "full", z=(1.0, 1.08), fx=0.5), [Tx("Mas se por um lado tem", "lado1", 0, "sm")], img="plateia com celulares")
B(w("lado1", 6), film("f_consumindo", "full", z=(1.0, 1.08), fx=0.45), [Tx("muita gente", "lado1", 6, "sm"), Tx("consumindo", "lado1", 8, "big")], img="metrô")
B(S("lado2"), tipo(), [Tx("Por outro, a maioria de quem está", "lado2", 0, "sm")], theme="dark")
B(w("lado2", 7), film("f_produzindo", "letterbox", cy=880), [Tx("produzindo", "lado2", 7, "big", y=1640)], theme="dark", sfx="pop")
B(w("lado2", 9), film("f_lixo", "full", z=(1.0, 1.1), fx=0.5), [Tx("está apenas despejando", "lado2", 8, "sm"), Tx("lixo", "lado2", 11, "xl")], fx=["glitch"], img="sacos de lixo")
B(w("lado2", 12), film("f_esquecivel", "full", z=(1.0, 1.1), fx=0.45), [Tx("completamente", "lado2", 12, "sm"), Tx("esquecível", "lado2", 13, "big", out=w("lado2", 14))], img="lixão")

# 8 IA ----------------------------------------------------------------
B(S("estudo"), mg_paper("estudo", w("estudo", 2), w("estudo", 4)), [Tx("Um estudo revelou", "estudo", 0, "md", y=230)], theme="dark", sfx="whoosh", img="MG folha com a headline do estudo da Graphite + gráfico IA × humanos")
B(w("estudo", 10), mg_dots("pct", w("estudo", 10), w("estudo", 16)), [Tx("mais da metade de todo conteúdo novo", "estudo", 4, "sm", y=1500)], theme="dark", sfx="tick", img="MG 100 pontos → 51%")
B(w("estudo", 17), film("f_hal", "full", z=(1.0, 1.15), fx=0.5), [Tx("saiu totalmente da", "estudo", 17, "sm"), Tx("inteligência artificial", "estudo", 20, "big")], fx=["glitch"])
B(S("media"), p_cut("media", "L", mg_average(["starry", "monalisa", "atenas", "adao", "kanagawa", "viajante", "socrates", "medusa", "liberdade", "napoleao", "sistine", "vitruvian"]), height=0.58, bgdark=0.75, bgblur=0),
  [Tx("A IA trabalha produzindo", "media", 0, "sm", y=330), Tx("a média", "media", 5, "big", y=520), Tx("de tudo que já foi produzido", "media", 7, "sm", y=700)],
  theme="img", sfx="whoosh", img="RECORTE ESQUERDA: VOCÊ sobre mosaico que vira cinza (a média)")
B(S("errar"), mg_checks(), [Tx("A IA busca", "errar", 0, "sm"), Tx("nunca errar", "errar", 3, "big")], theme="light", sfx="whoosh", img="MG checks")
B(S("arte"), tipo(), [Tx("Mas é correndo o risco de", "arte", 0, "sm"), Tx("errar", "arte", 6, "big", color=RED)], theme="dark")
B(w("arte", 7), film("f_starry", "letterbox", cy=880), [Tx("que nascem as grandes", "arte", 7, "sm")], img="Noite Estrelada")
B(w("arte", 11), full("adao", (1.0, 1.2), (0.62, 0.45)), [Tx("obras de arte", "arte", 11, "big")], img="Capela Sistina")
B(S("davinci"), p_frame("davinci"), [Tx("Não é a IA que vai produzir o próximo", "davinci", 0, "sm", y=150), Tx("Leonardo da Vinci", "davinci", 9, "md", y=1790)],
  theme="dark", sfx="whoosh", img="QUADRO: VOCÊ numa moldura dourada ao lado da Mona Lisa")
B(S("maioria"), mg_dots("maioria", w("maioria", 6), w("maioria", 8)), [Tx("Mas é ela que vai produzir a", "maioria", 0, "sm", y=330), Tx("esmagadora maioria", "maioria", 7, "md", y=1600)], theme="dark", sfx="tick", img="MG pontos")
B(w("maioria", 9), mg_collage(["f_ia", "f_clones", "f_simples", "f_hal", "f_fabricar", "f_texto", "f_consumindo", "f_assiste"]), [Tx("de todo o conteúdo que você", "maioria", 9, "sm"), Tx("consumir", "maioria", 15, "big")], theme="img", img="MG colagem de vídeos")
B(w("maioria", 16), full("viajante", (1.0, 1.15), (0.5, 0.4)), [Tx("nos próximos anos", "maioria", 16, "md")])
B(S("plastico"), film("f_manequim", "full", z=(1.0, 1.08), fx=0.40), [Tx("E nesse cenário onde tudo é", "plastico", 0, "sm")], img="manequins")
B(w("plastico", 6), film("f_plastico", "full", z=(1.0, 1.08), fx=0.48), [Tx("artificial", "plastico", 6, "big"), Tx("e plástico", "plastico", 7, "md")], img="rosto de boneca")
B(w("plastico", 9), mg_dots("destaque", w("plastico", 11)), [Tx("quem se destaca?", "plastico", 9, "md", y=1560)], theme="dark", sfx="impact", img="MG um ponto azul entre cinzas")
B(S("chatgpt"), film("f_alem", "letterbox", cy=900), [Tx("Criar conteúdo vai muito", "chatgpt", 0, "sm"), Tx("além", "chatgpt", 4, "big")], img="celular com ChatGPT")
B(w("chatgpt", 5), mg_chat("me dá um roteiro viral", w("chatgpt", 5), cps=26, strike=w("chatgpt", 10)), [Tx("de pedir um roteiro no ChatGPT", "chatgpt", 5, "sm", y=380)], theme="dark", sfx="type", img="MG chat + X vermelho")

# 9 O QUE FUNCIONA -----------------------------------------------------
B(S("bom"), tipo(), [Tx("Um bom conteúdo pode", "bom", 0, "md")], theme="dark")
B(w("bom", 4), film("f_inspirar", "full", z=(1.0, 1.08), fx=0.55), [Tx("inspirar", "bom", 4, "big")], img="montanha")
B(w("bom", 5), film("f_emocionar", "full", z=(1.0, 1.1), fx=0.42, gain=1.25), [Tx("emocionar", "bom", 5, "big")], img="show, mãos pro alto")
B(w("bom", 7), film("f_convencer", "full", z=(1.0, 1.06), fx=0.42), [Tx("e inevitavelmente", "bom", 6, "sm"), Tx("convencer", "bom", 8, "big")], img="comício")
B(w("bom", 9), film("f_multidao", "full", z=(1.25, 1.0), fx=0.5), [Tx("milhões de pessoas", "bom", 9, "big")], img="multidão")
B(w("bom", 11), film("f_melhor", "full", z=(1.0, 1.06), fx=0.50, fx1=0.60), [Tx("que o seu produto é", "bom", 11, "sm", y=330), Tx("o melhor", "bom", 17, "big", y=1640)], theme="dark", sfx="pop")
B(S("define"), full("atenas", (1.0, 1.15), (0.5, 0.42)), [Tx("Hoje, criar conteúdo", "define", 0, "sm"), Tx("define", "define", 3, "big")], theme="dark")
B(w("define", 4), mg_politicos(w("define", 4)), [Tx("o político mais votado", "define", 6, "md", y=1780)], theme="dark", sfx="pop", img="MG: Nikolas, Pavanato, Eduarda Campopiano, Ana Elisa em vídeos + manchetes reais (InfoMoney, Gazeta do Povo)")
B(S("pago"), mg_duo(("muzy", "Paulo Muzy"), ("cariani", "Renato Cariani"), S("pago")), [Tx("o profissional", "pago", 0, "sm", y=960), Tx("mais bem pago", "pago", 2, "md", y=960)], theme="dark", sfx="whoosh", img="Paulo Muzy e Renato Cariani (Flow Podcast)")
B(S("desejado"), film("jobs", "letterbox", cy=860), [Tx("o produto", "desejado", 0, "sm", y=1420), Tx("mais desejado", "desejado", 2, "big", y=1420)], theme="dark", sfx="whoosh", img="Steve Jobs apresentando o iPhone (Macworld 2007)")
B(S("enquanto"), mg_chat("roteiro viral sobre meu negócio", S("enquanto") + 0.1, cps=34), [Tx("Mas enquanto a maioria está produzindo roteiro na IA", "enquanto", 0, "sm", y=330)], theme="dark", sfx="type")
B(w("enquanto", 10), mg_zero("enquanto"), [Tx("sem nenhum", "enquanto", 10, "sm", y=380), Tx("resultado", "enquanto", 12, "big", y=1450)], theme="light", sfx="whoosh", img="MG painel: 0 visualizações")
TILES = [("v_jornada", "Jornada Top", 0.5, 0, 3.8e6), ("v_felipe", "Felipe Dantas", 0.5, 0, 2.6e6), ("v_fernando", "Fernando Miranda", 0.5, 0, 4.9e6),
         ("v_carlos", "Carlos Bezerra Jr.", 0.45, 0, 2.1e6), ("v_igor", "Igor Bevilaqua", 0.45, 0, 5.4e6), ("v_hormozi", "Alex Hormozi", 0.5, 0, 6.2e6),
         ("v_gary", "Gary Vee", 0.5, 0, 3.3e6), ("v_igor2", "Igor Bevilaqua", 0.45, 0, 1.8e6), ("v_fernando", "Fernando Miranda", 0.5, 45, 2.9e6)]
B(S("todos"), mg_viral(TILES, S("todos")), [Tx("Todos os dias milhares de vídeos", "todos", 0, "sm", y=210), Tx("alcançam", "todos", 6, "sm", y=1390),
  Tx("milhões de pessoas", "todos", 7, "md", y=1530)], theme="img", sfx="tick",
  img="MG grade 3x3: vídeos de Igor, Jornada Top, Felipe Dantas, Fernando Miranda, Carlos Bezerra Jr., Alex Hormozi, Gary Vee com contador de views explodindo")
B(w("todos", 10), mg_collage(["f_publico", "f_multidao", "fan_bandeira", "f_consumindo", "f_inspirar", "fan_army", "f_emocionar", "fan_pt"], hl=w("todos", 12)),
  [Tx("deixando claro", "todos", 10, "sm"), Tx("padrões", "todos", 12, "big"), Tx("que se repetem em todo vídeo viral", "todos", 13, "sm")], theme="img", img="MG colagem com padrão destacado")
B(S("padroes"), p_cardfull("padroes", w("padroes", 3)), [Tx("Você só precisa conhecer", "padroes", 0, "sm", y=280), Tx("esses padrões", "padroes", 4, "md", y=1640)],
  theme="img", sfx="whoosh", img="MOLDURA → TELA CHEIA: VOCÊ")
B(S("perfil"), mg_profile(["atenas", "viajante", "kanagawa", "starry", "adao", "liberdade", "napoleao", "medusa", "vitruvian"], "segue"), [Tx("É pra isso que", "perfil", 0, "sm", y=230), Tx("esse perfil existe", "perfil", 4, "md", y=1770)], theme="light", sfx="pop", img="MG perfil")

# 10 PONTE / MARCA ----------------------------------------------------
B(S("oferta"), p_cut("oferta", "R", switch((S("oferta"), film("f_publico", "full", fx=0.5)), (w("oferta", 11), film("f_multidao", "full", z=(1.0, 1.2), fx=0.5))), height=0.6),
  [Tx("Postando o conteúdo certo", "oferta", 0, "sm", y=300), Tx("qualquer empreendedor pode botar a sua oferta", "oferta", 4, "sm", y=480),
   Tx("na frente de", "oferta", 11, "sm", y=680), Tx("1 milhão", "oferta", 14, "big", y=880)],
  theme="img", sfx="whoosh", img="RECORTE DIREITA: VOCÊ sobre multidões")
B(S("eusei"), mg_cases("eusei", w("eusei", 6) - F1, w("eusei", 11) - F1, p_phone("eusei")),
  [Tx("Eu sei porque já fiz isso", "eusei", 0, "sm", y=260, out=w("eusei", 6) - 0.25), Tx("no meu perfil", "eusei", 8, "md", y=1700, out=w("eusei", 11) - 0.3),
   Tx("e dos meus clientes", "eusei", 11, "md", y=170)], theme="dark", sfx="whoosh",
  img="Cases reais: seu perfil 0→N seguidores + reels com views; 3 clientes em sequência")
B(S("poste"), mg_post(w("poste", 0) + 0.25), [Tx("Poste", "poste", 0, "xl", y=600)], theme="light", sfx="pop", img="MG botão Publicar")
B(w("poste", 4), tipo(), [Tx("e seja", "poste", 4, "sm"), Tx("dono da narrativa", "poste", 6, "big")], theme="dark", sfx="impact")
B(w("poste", 9), mg_people(w("poste", 10), w("poste", 16)), [Tx("que transforma milhões de desconhecidos em", "poste", 9, "sm", y=200), Tx("clientes divulgadores", "poste", 15, "md", y=1720)],
  theme="dark", sfx="whoosh", img="MG pessoas cinza → azul")
B(S("danca"), mg_xstamp(mg_grid9([f"dance{i}" for i in range(9)], S("danca")), w("danca", 1)), [Tx("sem", "danca", 0, "md", y=230), Tx("dancinha", "danca", 1, "big", y=1720)],
  theme="img", sfx="impact", img="MG grade 3x3: pessoas fazendo a MESMA dancinha (rostos desfocados) + X")
B(w("danca", 2), mg_xstamp(film("sera", "full", z=(1.0, 1.05), fx=0.5), w("danca", 3)), [Tx("trends adolescentes", "danca", 2, "md", y=250)], theme="img", sfx="impact",
  img="Trend 'será?' (Manoel Gomes) + X")
B(w("danca", 4), mg_xstamp(film("futebol_danca", "full", z=(1.0, 1.08), fx=0.5), w("danca", 5)), [Tx("ou músicas em alta", "danca", 4, "md", y=1550)], theme="img", sfx="impact")
B(S("verdade"), p_cut("verdade", "L", cardl("boxes", aspect=1, wf=0.5, cy=790), height=0.56, bgdark=0.9, bgblur=0),
  [Tx("Apenas conteúdo de", "verdade", 0, "sm", y=260), Tx("verdade", "verdade", 3, "big", y=400), Tx("empacotado da forma certa", "verdade", 4, "sm", y=1110)],
  theme="img", sfx="whoosh", img="RECORTE ESQUERDA: VOCÊ + caixa")
B(S("concorr"), film("f_corrida", "full", z=(1.0, 1.08), fx=0.62), [Tx("Sim, a concorrência existe", "concorr", 0, "sm"), Tx("e está aumentando", "concorr", 4, "md")], img="maratona")
B(S("recompensa"), film("f_transformacao", "full", z=(1.0, 1.1), fx=0.52), [Tx("Mas a recompensa é a", "recompensa", 0, "sm"), Tx("transformação", "recompensa", 5, "big")], sfx="riser", img="cidade ao amanhecer")
B(w("recompensa", 6), full("viajante", (1.15, 1.0), (0.5, 0.42)), [Tx("completa da história", "recompensa", 6, "md"), Tx("da tua empresa", "recompensa", 9, "big")])

# 11 CTA --------------------------------------------------------------
B(S("segue"), p_cta("segue"), [Tx("Segue esse perfil", "segue", 0, "sm", y=230), Tx("e se torne hoje um poderoso", "segue", 3, "sm", y=1560),
  Tx("canal de mídia", "segue", 9, "big", color=BLUE, y=1560)], theme="light", sfx="whoosh", img="CTA: VOCÊ em moldura + botão Seguir")

T_OFF = TL["segue"]["t1"] + 0.55   # clique: música corta e a TV desliga
HIT(w("hook2", 3), 46.2); HIT(w("poder", 2), 41.2); HIT(w("injusta", 10), 49.0); HIT(w("narr1", 8), 55.0)
HIT(w("tsunami", 14), 41.2); HIT(w("estudo", 15), 49.0); HIT(w("plastico", 9), 46.2); HIT(w("poste", 6), 41.2)
END = T_OFF + 0.5
BEATS.sort(key=lambda b: b["t0"])
for i, b in enumerate(BEATS): b["t1"] = BEATS[i + 1]["t0"] if i + 1 < len(BEATS) else END
NF = int(math.ceil(END * FPS))
