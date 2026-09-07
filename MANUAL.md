# Manual de Uso — Núcleo de Microbiologia

Este manual explica como usar este material, do jeito mais rápido possível. Não é
documentação técnica — é um guia para quem só quer estudar (ou ajudar a melhorar o
material) sem precisar entender a estrutura interna do projeto inteiro.

## Antes de tudo: isto foi feito por uma pessoa só, à mão

Todo o material deste projeto — texto, cartão ou imagem — foi selecionado e escrito de
forma **manual e subjetiva** por quem organizou o projeto. Não é uma revisão sistemática,
não passou por banca revisora, e não foi gerado por um processo automatizado e
determinístico. Na prática, isso quer dizer:

- **Pode ter erro em qualquer parte** — texto, resposta de cartão ou imagem.
- **A escolha de quais assuntos entraram, e a profundidade de cada um, foi um julgamento
  pessoal** de quem organizou o material — não uma cobertura garantidamente completa ou
  objetiva do tema.
- **É esperado que partes do material original em PDF não estejam representadas aqui.**
  Faltar alguma coisa não é (necessariamente) erro — pode só não ter sido considerado
  prioritário para o recorte deste material.

Use este material como **apoio de revisão**, não como fonte única de verdade. Sempre
confira com o material oficial da sua disciplina antes de uma prova ou qualquer decisão
importante. E se achar algo errado ou faltando, veja como colaborar no
[Nível 4](#nível-4--erros-e-como-colaborar) abaixo.

Está organizado em níveis. Comece pelo Nível 1. Só desça pros próximos se quiser entender
mais ou ajudar a corrigir alguma coisa.

---

## Nível 1 — Só quero estudar agora

1. Abra o Anki no computador ou celular.
2. Importe os dois arquivos de `anki-decks/` (arraste pro Anki, ou use Arquivo >
   Importar, um de cada vez):
   - `Microbiologia Nucleo.apkg` — os 48 agentes (vírus e fungos específicos).
   - `Fundamentos-Microbiologia.apkg` — a base teórica geral (estrutura, classificação,
     ciclo de multiplicação, antivirais etc.), separada do primeiro.
3. Pronto. No `Microbiologia Nucleo.apkg` você vai ver dois grupos de cartões —
   **Virologia** (23 agentes) e **Micologia** (25 agentes). No
   `Fundamentos-Microbiologia.apkg` você vai ver os mesmos dois grupos, mas organizados
   por tópico de biologia geral em vez de por agente.

Cada agente do núcleo tem 5 cartões, sempre no mesmo formato:

| Tipo de cartão | O que ele pergunta |
|---|---|
| **Categoria** | Que tipo de bicho é esse (vírus ou fungo, de qual família) |
| **Transmissão** | Como se pega |
| **Achado** | O sinal/sintoma mais característico — o que mais cai em prova |
| **Vinheta** | Um caso clínico resumido, pra você adivinhar o agente antes de virar o cartão |
| **Aplicado** | Qual o tratamento |

Já os cartões de fundamentos não seguem esse molde por agente — a maioria é tipo
**Conceito** (uma pergunta direta sobre um conceito de biologia geral), com algumas
**Vinheta** também, mas descrevendo um achado ou cenário genérico (não um caso clínico de
doença específica) para você identificar a estrutura ou o fenômeno biológico por trás.
Nenhum cartão de fundamentos tem imagem por enquanto — o campo existe no modelo, pronto
para quando isso for adicionado, mas hoje fica em branco.

---

## Nível 2 — De onde isso veio

O projeto tem duas pastas de conteúdo bem diferentes:

**`docs/material-base/`** — o material geral, "cru". São os PDFs originais das aulas de
uma disciplina de graduação (microbiologia/virologia/micologia). É a fonte bruta de tudo que foi gerado nesse projeto.

**`docs/material-gerado/`** — todo o conteúdo dos PDFs reescrito e reorganizado em texto
corrido, mais claro. Isso não é só "matéria-prima do deck" — é, por si só, material de
estudo completo. Dá pra estudar só lendo os `.md`, sem nunca abrir o Anki. Tem três tipos
de arquivo dentro dessa pasta:

- **Dicionário de gatilhos** (um por disciplina) — conta cada doença como uma historinha
  em cadeia: você pega o bicho de um jeito → ele entra no corpo por tal porta → se
  multiplica de tal forma → isso causa tal sintoma → por isso o tratamento é esse. Bom
  para **entender o porquê**, não só decorar.
- **Ficha determinística** (um por disciplina) — os mesmos agentes, mas em tabela seca e
  direta, sempre nas mesmas 6 categorias. Bom para **revisão de véspera de prova**.
- **Biologia fundamental** (um para vírus, um para fungos) — os conceitos gerais que vêm
  antes de entrar em agente específico (estrutura, classificação, como se multiplicam,
  etc.), cobrindo o conteúdo das aulas introdutórias dos PDFs originais. Também tem
  cartão de Anki próprio (`Fundamentos-Microbiologia.apkg`), separado do deck por agente.

Resumindo:

```
PDF da faculdade   →   .md reescrito e organizado   →   cartão do Anki
(material-base)        (material-gerado — já e         (anki-decks/Nucleo-...apkg,
                         material de estudo completo)    por agente, e
                                                          anki-decks/Fundamentos-...apkg,
                                                          por conceito geral)
```

---

## Nível 3 — Quero achar um agente específico rápido

Se você já sabe o agente que quer revisar (ex.: "quero reler sobre HPV agora"), não
precisa abrir o documento inteiro e procurar. Abra o **[INDICE.md](INDICE.md)** — tem uma
tabela com todos os 48 agentes, e cada um tem dois links: um pra versão "historinha" e
outro pra versão "ficha seca". Clicar leva direto pro trecho certo.

---

## Nível 4 — Erros e como colaborar

Como já dito lá em cima, este material é curadoria manual de uma pessoa só — texto,
resposta ou imagem podem estar errados, incompletos ou desatualizados. As imagens
merecem um cuidado à parte: elas vêm de um processo de busca ainda experimental (foto,
diagrama ou lâmina de microscópio escolhidos manualmente), e é bem possível que alguma
não bata exatamente com o que a pergunta pede. Se notar isso estudando, vale reportar.

### Como colaborar

Encontrou um erro — de texto, de resposta ou de imagem — ou tem uma sugestão melhor?
Mande um e-mail para **lixotrashlixo@proton.me**. Para facilitar incorporar sua sugestão
rápido, inclua:

1. **No assunto do e-mail:** o nome do agente + qual parte está errada — por exemplo:
   `HPV - Achado` (pode ser o texto da resposta, a imagem, ou os dois).
2. **No corpo do e-mail:**
   - O que está errado, especificamente (ex.: "a foto é de uma lâmina de laboratório, mas
     a pergunta pede uma foto do paciente" ou "o texto diz X, mas o correto é Y").
   - Se tiver uma sugestão melhor (imagem ou texto), mande ela pronta — se for imagem,
     o **link direto** (não precisa anexar arquivo) e, se souber, a fonte/licença.

Não precisa formalidade nem justificativa longa — quanto mais direto o e-mail, mais
rápido dá pra revisar e corrigir.

---

## Quer saber mais

Este manual cobre só o essencial. Para detalhes técnicos (estrutura de pastas, scripts,
licença de uso, avisos sobre o material ter sido feito para uma grade curricular
específica), veja o **[README.md](README.md)**.
