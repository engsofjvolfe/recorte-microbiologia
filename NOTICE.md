# Avisos de licença

Este projeto usa duas licenças diferentes, para dois tipos de arquivo diferentes, mais
uma exceção para material de terceiros. Leia esta página inteira antes de reusar qualquer
coisa daqui.

## 1. Código (scripts Python) — GPL-3.0

Os scripts (`scripts/montar_deck.py`, `docs/material-gerado/buscar_imagens.py`,
`docs/material-gerado/curar_imagens.py`) estão sob a **GNU General Public License v3.0**.
Texto completo em [`LICENSE`](LICENSE). Resumindo: você pode usar, estudar, modificar e
redistribuir o código livremente, mas qualquer trabalho derivado dele também precisa
continuar sob GPL-3.0 (copyleft) e vir com o código-fonte disponível.

## 2. Conteúdo gerado — CC BY-NC-SA 4.0

Os dicionários de gatilhos, fichas determinísticas, biologia fundamental, o CSV de
perguntas, o JSON de agentes e o deck do Anki (tudo em `docs/material-gerado/` e
`anki-decks/`) estão sob **Creative Commons Atribuição-NãoComercial-CompartilhaIgual 4.0
Internacional (CC BY-NC-SA 4.0)**. Texto completo em
[`LICENSE-CONTENT.txt`](LICENSE-CONTENT.txt). Resumindo: você pode usar, adaptar e
redistribuir esse conteúdo, desde que dê crédito, **não use para fins comerciais** e
mantenha qualquer versão adaptada sob a mesma licença.

## 3. Material de terceiros — fora de qualquer licença deste projeto

Os PDFs em [`docs/material-base/`](docs/material-base/) (`INTRODUCAO_A_MICROBIOLOGIA.pdf`,
`INTRODUCAO_A_MICOLOGIA.pdf`, `MICOLOGIA_ESPECIAL.pdf`, `VIROLOGIA_GERAL.pdf`,
`VIROLOGIA_ESPECIAL_I.pdf`, `VIROLOGIA_ESPECIAL_II_III.pdf`) **não são cobertos por
nenhuma das licenças acima**. São material de aula de uma universidade de Minas Gerais,
obtidos por meio de um aluno da disciplina — quem mantém este repositório não é o autor
desses PDFs e não tem autorização para relicenciá-los. Por isso:

- Essa pasta está no [`.gitignore`](.gitignore) e não deve ser publicada/redistribuída
  junto com o restante do projeto.
- Se você recebeu este projeto com essa pasta preenchida, trate como material pessoal de
  estudo, não como parte do pacote de código aberto.

## Como creditar

Se for reusar o conteúdo (item 2), credite como: "Núcleo de Microbiologia — Virologia &
Micologia, licenciado sob CC BY-NC-SA 4.0", com link para este repositório.
