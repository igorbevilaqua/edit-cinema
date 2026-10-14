# edit-cinema — skill de edição para Claude

Skill que ensina o Claude a editar **vídeos verticais (9:16) em voice over com tom cinematográfico e intelectual**:

- **cenas de filme, obras de arte, filósofos e imagens históricas** trocando na palavra (nada de cara de banco de imagem)
- **provas reais** sempre que a fala afirma algo concreto: manchete original, estudo com headline e fonte, citação com autor e obra, clipes das pessoas citadas, prints de resultados com contadores subindo
- **motion graphics didáticos** (comparativos, rankings, globo com zoom no lugar citado, gráficos de estudo)
- tipografia cinética palavra a palavra e gancho com a pergunta-tese grande se completando
- aparições do apresentador em **molduras que conversam com a edição**: TV antiga, quadro de museu ao lado da Mona Lisa, tela de celular, card que vira tela cheia, recorte em cantos alternados
- tratamento de cor de cinema + lente (aberração cromática, bloom, grão, vinheta)
- trilha com **batida desde o início + música clássica em domínio público crescendo até um final majestoso**, pancadas de trailer nas frases-tese e um final com clique e TV desligando

O manual completo está em [`edit-cinema/SKILL.md`](edit-cinema/SKILL.md), com o catálogo de cenas de filme por tema, a hierarquia de escolha de imagem, as regras de credibilidade, os níveis de mixagem e o QA. Um pipeline de referência (Python + ffmpeg) está em [`edit-cinema/scripts/`](edit-cinema/scripts/).

> Antes chamada `edit-voiceover`.

## Como instalar

**Claude Code**

```bash
git clone https://github.com/igorbevilaqua/edit-cinema.git
cp -r edit-cinema/edit-cinema ~/.claude/skills/
```

Depois é só pedir: "edita esse vídeo no estilo edit-cinema".

**Claude.ai (app / web)**

Compacte a pasta `edit-cinema/` em `.zip` e envie em *Settings → Capabilities → Skills → Upload skill*.

## Observações

- Cenas de filme, clipes e logos de terceiros têm direitos dos respectivos donos: ok para Reels orgânico, arriscado em anúncio pago. Prefira música em domínio público.
- A skill pede para registrar a origem de toda imagem, vídeo e dado em um arquivo de fontes a cada versão.
