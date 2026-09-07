# Núcleo de Microbiologia — Virologia & Micologia

![Licenca codigo](https://img.shields.io/badge/C%C3%B3digo-GPL--3.0-blue)
![Licenca conteudo](https://img.shields.io/badge/Conte%C3%BAdo-CC_BY--NC--SA_4.0-blue)

## O que é isto

Um material de estudo de microbiologia médica (virologia e micologia). Veja o
**[INDICE.md](INDICE.md)** para navegar por todos os documentos, agente por agente, ou o
**[MANUAL.md](MANUAL.md)** para um guia rápido e não técnico de como usar o material. Este
README é a documentação técnica do projeto.

## Aviso importante — leia antes de usar

Este conteúdo foi construído a partir do material de microbiologia disponibilizado (ver
seção [Origem do conteúdo](#origem-do-conteúdo) abaixo) e **organizado em torno da grade
específica de uma disciplina de graduação**. Isso significa que:

- A seleção de quais 48 agentes entraram no núcleo, qual achado clínico é "o mais
  cobrado" e qual tratamento é "a resposta esperada" reflete a ênfase **daquele curso e
  daquele professor específico** — não é necessariamente a cobertura completa da
  literatura médica, nem substitui diretrizes oficiais (CDC, OMS, sociedades médicas)
  ou o material didático original da disciplina.
- Simplificações propositais foram feitas para caber no formato de flashcard (uma
  resposta "canônica" por pergunta), o que pode omitir nuances, exceções e
  controvérsias que um material de referência completo traria.
- **Use como ferramenta de revisão e fixação, não como fonte primária de estudo.**
  Sempre confira fatos clinicamente relevantes com a bibliografia oficial da sua
  disciplina antes de uma prova ou de qualquer decisão clínica real.

## Mecanismo de busca de imagens

![Busca de imagens](https://img.shields.io/badge/Busca_de_imagens-experimental_%2F_sem_garantia-important)

As imagens anexadas aos cards vêm de um mecanismo de busca **ainda experimental** (API da
Wikimedia Commons + conferência visual manual obrigatória, sem garantia de determinismo
para agentes novos). Detalhes completos, incluindo por que duas tentativas anteriores de
automatizar mais essa busca falharam, estão no
[README do mecanismo de busca](docs/material-gerado/README.md).

## Proposta de plataforma futura

Este núcleo de microbiologia é a prova de conceito de uma ideia maior: generalizar
o mecanismo para qualquer disciplina, de forma colaborativa. A visão geral dessa
proposta (ponto de partida, no espírito do modelo V, para um futuro documento de
Requisitos formal) está em
[`docs/proposta-plataforma/01-visao-geral.md`](docs/proposta-plataforma/01-visao-geral.md).

## Origem do conteúdo

O material de microbiologia original que serviu de base para este núcleo (INTRODUÇÃO À
MICROBIOLOGIA, s.d.; INTRODUÇÃO À MICOLOGIA, s.d.; MICOLOGIA ESPECIAL, s.d.; VIROLOGIA
GERAL, s.d.; VIROLOGIA ESPECIAL I, s.d.; VIROLOGIA ESPECIAL II E III, s.d.) está em
[`docs/material-base/`](docs/material-base/) — referências completas na seção
[Referências](#referências), ao final deste documento.

Esses PDFs são material de aula de uma universidade de Minas Gerais, obtidos por meio de
um aluno da disciplina — **não foram produzidos por quem mantém este repositório e não
estão cobertos pela licença deste projeto** (ver [Licença](#licença) abaixo). Todo o
resto (dicionários de gatilhos, fichas determinísticas, CSV, JSON, scripts e deck) foi
escrito/reorganizado a partir desses PDFs, mas é conteúdo derivado próprio deste
repositório, não uma cópia do material original.

Para os dois documentos de biologia fundamental (vírus e fungos), a curadoria também
comparou o resumo publicado contra uma **transcrição OCR integral e literal** dos slides
originais (`docs/material-base/gerados-ocr/`), usada só como conferência para achar
lacunas — ela não é conteúdo derivado nosso (é cópia literal do material de terceiros),
por isso fica no mesmo regime dos PDFs: **não versionada** (`.gitignore`) e não
redistribuída.

## Licença

Este projeto usa duas licenças, para duas partes diferentes, mais uma exceção — texto
completo e detalhado em [`NOTICE.md`](NOTICE.md):

| Parte | Licença | Significa que... |
|---|---|---|
| Código (`scripts/`, `docs/material-gerado/*.py`) | [GPL-3.0](LICENSE) | Pode usar/modificar/redistribuir, mas derivados também precisam ficar abertos (copyleft) |
| Conteúdo (dicionários, fichas, CSV, JSON, deck) | [CC BY-NC-SA 4.0](LICENSE-CONTENT.txt) | Pode usar/adaptar com crédito, **sem fins comerciais**, mantendo a mesma licença |
| PDFs em `docs/material-base/` | Nenhuma — são de terceiros | Não redistribuir; ficam fora do controle de versão (`.gitignore`) |

## Estrutura do projeto

| Arquivo | O que é |
|---|---|
| [`docs/material-gerado/perguntas-nucleo-dicionarios.csv`](docs/material-gerado/perguntas-nucleo-dicionarios.csv) | Fonte da verdade: as 240 perguntas/respostas por agente (48 agentes × 5 tipos) |
| [`docs/material-gerado/perguntas-fundamentos-virus.csv`](docs/material-gerado/perguntas-fundamentos-virus.csv) | Fonte da verdade: 95 perguntas/respostas de biologia fundamental de vírus (8 tópicos) |
| [`docs/material-gerado/perguntas-fundamentos-fungos.csv`](docs/material-gerado/perguntas-fundamentos-fungos.csv) | Fonte da verdade: 56 perguntas/respostas de biologia fundamental de fungos (5 tópicos) |
| [`fila-busca-imagens-agentes.json`](fila-busca-imagens-agentes.json) | Índice mestre dos 34 agentes originais + termos de busca de imagem por necessidade |
| [`docs/material-gerado/dicionario-gatilhos-virologia.md`](docs/material-gerado/dicionario-gatilhos-virologia.md) | Cadeia causal didática (5 elos) dos 23 vírus |
| [`docs/material-gerado/dicionario-gatilhos-micologia.md`](docs/material-gerado/dicionario-gatilhos-micologia.md) | Cadeia causal didática (5 elos) dos 25 fungos |
| [`docs/material-gerado/virologia-especial-determinismo.md`](docs/material-gerado/virologia-especial-determinismo.md) | Ficha determinística (6 eixos) dos 23 vírus |
| [`docs/material-gerado/micologia-especial-determinismo.md`](docs/material-gerado/micologia-especial-determinismo.md) | Ficha determinística (6 eixos) dos 25 fungos |
| [`docs/material-gerado/biologia-fundamental-virus.md`](docs/material-gerado/biologia-fundamental-virus.md) | Base teórica geral: estrutura, taxonomia e ciclo de vida viral |
| [`docs/material-gerado/biologia-fundamental-fungos.md`](docs/material-gerado/biologia-fundamental-fungos.md) | Base teórica geral: biologia e fisiologia fúngica |
| [`docs/material-gerado/CRITERIOS-BUSCA-IMAGENS.md`](docs/material-gerado/CRITERIOS-BUSCA-IMAGENS.md) | Regras de curadoria de imagens por tipo de pergunta |
| [`docs/material-gerado/README.md`](docs/material-gerado/README.md) | Explica o mecanismo de busca de imagens (experimental) em detalhe |
| [`imagens_agentes/`](imagens_agentes/) | Pastas por agente com imagens confirmadas + `manifest.json` |
| [`docs/material-gerado/buscar_imagens.py`](docs/material-gerado/buscar_imagens.py) | Busca/baixa candidatos de imagem (Wikimedia Commons) — experimental |
| [`docs/material-gerado/curar_imagens.py`](docs/material-gerado/curar_imagens.py) | Aplica a conferência visual manual sobre os candidatos baixados |
| [`anki-decks/Microbiologia Nucleo.apkg`](anki-decks/Microbiologia%20Nucleo.apkg) | Deck pronto para importar no Anki, por agente (240 cards, 107 imagens) |
| [`anki-decks/Fundamentos-Microbiologia.apkg`](anki-decks/Fundamentos-Microbiologia.apkg) | Deck pronto para importar no Anki, biologia fundamental (151 cards, sem imagem por enquanto) |
| [`scripts/montar_deck.py`](scripts/montar_deck.py) | Gera os dois `.apkg` (nucleo por agente + fundamentos), reaproveitando o mesmo modelo de nota |
| [`INDICE.md`](INDICE.md) | **Índice com link direto para qualquer agente/seção de qualquer documento** |
| [`MANUAL.md`](MANUAL.md) | Guia rápido e não técnico de como usar o material e como colaborar |
| [`LICENSE`](LICENSE) | Texto completo da GPL-3.0 (código) |
| [`LICENSE-CONTENT.txt`](LICENSE-CONTENT.txt) | Texto completo da CC BY-NC-SA 4.0 (conteúdo) |
| [`NOTICE.md`](NOTICE.md) | Explica qual licença cobre qual arquivo, e a exceção dos PDFs de terceiros |
| [`.gitignore`](.gitignore) | Exclui os PDFs de terceiros, caches e artefatos temporários do controle de versão |

## Como usar

1. Para estudar: importe `anki-decks/Microbiologia Nucleo.apkg` (por agente) e
   `anki-decks/Fundamentos-Microbiologia.apkg` (biologia geral) no Anki — são dois
   pacotes independentes, pode importar só um dos dois se preferir.
2. Para consultar rapidamente um agente específico: abra o [`INDICE.md`](INDICE.md) e
   clique no agente — ele leva direto para a ficha certa no documento certo.
3. Para editar conteúdo: mude o CSV correspondente em `docs/material-gerado/` (cada um é
   a fonte da verdade do seu deck) e rode `python scripts/montar_deck.py` para
   regenerar os dois pacotes — ou `python scripts/montar_deck.py nucleo` /
   `fundamentos` para regenerar só um deles. O script acha os CSVs sozinho mesmo se
   mudarem de pasta de novo.

## Ver também

**[INDICE.md](INDICE.md)** — navegação completa, agente por agente, para todos os documentos.

## Referências

Material de aula que serviu de fonte primária para o conteúdo deste projeto (ver
[Origem do conteúdo](#origem-do-conteúdo)). Sem autoria individual identificada; local,
editora e data desconhecidos:

INTRODUÇÃO À MICOLOGIA. [S.l.: s.n., s.d.]. Material de aula (slides), não publicado.
Localização: `docs/material-base/INTRODUCAO_A_MICOLOGIA.pdf` (arquivo de terceiros, não
versionado neste repositório).

INTRODUÇÃO À MICROBIOLOGIA. [S.l.: s.n., s.d.]. Material de aula (slides), não publicado.
Localização: `docs/material-base/INTRODUCAO_A_MICROBIOLOGIA.pdf` (arquivo de terceiros,
não versionado neste repositório).

MICOLOGIA ESPECIAL. [S.l.: s.n., s.d.]. Material de aula (slides), não publicado.
Localização: `docs/material-base/MICOLOGIA_ESPECIAL.pdf` (arquivo de terceiros, não
versionado neste repositório).

VIROLOGIA ESPECIAL I. [S.l.: s.n., s.d.]. Material de aula (slides), não publicado.
Localização: `docs/material-base/VIROLOGIA_ESPECIAL_I.pdf` (arquivo de terceiros, não
versionado neste repositório).

VIROLOGIA ESPECIAL II E III. [S.l.: s.n., s.d.]. Material de aula (slides), não publicado.
Localização: `docs/material-base/VIROLOGIA_ESPECIAL_II_III.pdf` (arquivo de terceiros, não
versionado neste repositório).

VIROLOGIA GERAL. [S.l.: s.n., s.d.]. Material de aula (slides), não publicado.
Localização: `docs/material-base/VIROLOGIA_GERAL.pdf` (arquivo de terceiros, não
versionado neste repositório).
