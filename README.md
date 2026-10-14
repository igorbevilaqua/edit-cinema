# edit-voiceover — skill de edição para Claude

Skill que ensina o Claude a editar **vídeos verticais (9:16) em voice over** no estilo "a narração conduz e a imagem obedece à palavra":

- imagens fortes trocando a cada ~0,5 s, sincronizadas com cada palavra
- tipografia cinética palavra a palavra no centro da tela
- alternância de fundo preto (drama) e branco (clareza / CTA)
- motion graphics, colagens, cards e acabamento "lente" (aberração cromática, bloom, grão, vinheta)
- aparições estratégicas do apresentador: moldura, recorte em cantos alternados, "portal" (dentro de TV, celular, quadro)

O roteiro completo do estilo está em [`edit-voiceover/SKILL.md`](edit-voiceover/SKILL.md).

## Como instalar

**Claude Code**

```bash
git clone https://github.com/igorbevilaqua/edit-voiceover.git
cp -r edit-voiceover/edit-voiceover ~/.claude/skills/
```

Depois é só pedir: "edita esse vídeo no estilo voiceover".

**Claude.ai (app / web)**

Compacte a pasta `edit-voiceover/` em `.zip` e envie em *Settings → Capabilities → Skills → Upload skill*.

## Observações

- A skill cita a skill irmã `edit-tay` (talking head com tela dividida) para pipeline técnico, cortes e som; ela não é obrigatória, mas complementa.
- O pipeline usa ferramentas abertas: ffmpeg, Python (PIL, numpy, OpenCV), transcrição com timestamps por palavra e remoção de fundo (u2net / Robust Video Matting).
- Imagens, músicas e trechos de vídeo de terceiros usados nas edições têm direitos dos respectivos donos — prefira acervos em domínio público ou licenças abertas.
