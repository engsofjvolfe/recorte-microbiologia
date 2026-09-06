# Critérios de busca e verificação de imagens — deck de agentes (virologia/micologia)

Este documento é a fonte única de regras para quem for buscar, verificar e baixar as
imagens de UM agente da fila (`fila-busca-imagens-agentes.json`). Leia inteiro antes de
começar. Não invente regra diferente da que está aqui — o objetivo é que as 34 buscas
sigam exatamente o mesmo critério, pra o deck final ficar visualmente consistente.

## Por que este documento existe

Duas tentativas anteriores falharam:
1. Busca de texto livre na Wikimedia Commons não achava quase nada (frases descritivas
   longas não batem literalmente com título de arquivo real).
2. Busca por categoria do Commons + pontuação por palavra-chave achava coisas do
   assunto certo, mas do **tipo errado** (ex: uma foto de lâmina de citologia aparecendo
   onde devia vir um diagrama de estrutura viral; uma foto de rash aparecendo onde devia
   vir um esfregaço de sangue).

A causa raiz: o Commons não tem metadado de "isso é diagrama" vs "isso é foto clínica"
vs "isso é histologia" — só quem *olha* a imagem sabe dizer isso com certeza. Por isso
a etapa de verificação visual (com a ferramenta de leitura de imagem) não é opcional:
é ela que garante que a imagem é do tipo certo, não só do assunto certo.

## Fonte da verdade do conteúdo: o CSV, não o JSON

O arquivo `fila-busca-imagens-agentes.json` tem uma descrição própria de "achado" e
"tratamento" por agente, mas ela **não bate** com o conteúdo real do deck em vários
casos (ex: JSON pede "partícula de Dane" pro achado de Hepatite B, mas a pergunta real
do deck é sobre "evolução pra cirrose/carcinoma"). A fonte da verdade sobre O QUE cada
card realmente pergunta/responde é `perguntas-nucleo-dicionarios.csv`.

Portanto, **para os campos `Achado` e `Aplicado (tratamento)`, use a coluna `resposta`
do CSV para o seu agente, não a `descricao` do JSON.** Para `Categoria` e `Transmissao`
os dois arquivos coincidem, então tanto faz.

Use o JSON só para pegar `termos_de_busca` como ponto de partida de busca (em inglês) e
para resolver `tratamento_ref` no `catalogo_tratamentos` — mas se o CSV disser uma coisa
diferente do catálogo pro seu agente (isso acontece em pelo menos 2 casos, ver tabela de
exceções abaixo), **o CSV manda**.

## Regra rígida de tipo de imagem por necessidade

| Necessidade | Regra |
|---|---|
| **Categoria** (virologia) | SEMPRE diagrama/ilustração esquemática rotulada da estrutura do vírion (capsídeo, envelope, tipo de genoma). Nunca foto de paciente, nunca lâmina de histologia. |
| **Categoria** (micologia) | SEMPRE foto real de microscopia mostrando a morfologia do fungo (levedura, hifa, conídio, cápsula etc.) — não é diagrama aqui, é foto de lâmina de verdade. |
| **Transmissão** | Foto real do vetor/ambiente quando existir algo genuinamente fotografável (animal, inseto, ambiente/exposição ocupacional, objeto contaminado). Se o mecanismo for abstrato (contato sexual, saliva, gotícula respiratória), use diagrama simples. NUNCA use uma foto genérica da doença rotulada como "transmissão" — se não achar nada específico do mecanismo, deixe vazio. |
| **Achado** | SEMPRE foto real (nunca desenho/diagrama) — mas "real" pode ser foto clínica do que se vê no paciente, radiografia, ou patologia bruta, dependendo do que a resposta do CSV pede (ver tabela de exceções). Tem que ser EXATAMENTE o achado da resposta do CSV do seu agente, não outro aspecto da doença. |
| **Aplicado (tratamento)** | Foto real da embalagem/frasco/vacina citada na resposta do CSV, ou do procedimento (cirurgia, crioterapia, ventilação), ou — só nos casos documentados na tabela — foto do efeito adverso quando a resposta for um alerta de "evitar X" em vez de um remédio a favor. |

**Regra de ouro: nunca force uma imagem errada só pra preencher a vaga.** Se depois de
buscar de verdade (não só rodar o script uma vez) você não achar nada que bata com o
critério acima, deixe `"confirmado": false` nesse campo do seu `manifest.json`, com uma
`"justificativa"` curta explicando o motivo. Não crie nem edite nenhum arquivo de
relatório compartilhado entre agentes (várias buscas rodam em paralelo e vão escrever
nesse arquivo ao mesmo tempo, corrompendo o conteúdo) — a consolidação de pendências de
todos os 34 agentes é feita depois, por fora, lendo os manifests.

## Conteúdo sensível

Se a resposta do CSV envolver lesão genital/anogenital explícita (ver tabela — HSV-2 e
HPV), **não baixe automaticamente**. Em vez disso, crie/atualize
`imagens_agentes/<pasta-do-agente>/REVISAO_MANUAL.md` listando os termos de busca em
inglês sugeridos, pra revisão manual humana depois. Deixe esse campo vazio no manifest
com `"sensivel": true`.

## Não associar grupo étnico/racial identificável a texto de julgamento de valor

Se a resposta do CSV usa um adjetivo de julgamento sobre condição/ambiente (ex.: "mal
tratada", "precário", "insalubre", "sem higiene") e a imagem candidata mostra um grupo
étnico ou racial específico e identificável, **não use essa imagem**, mesmo que ela
corresponda literalmente ao termo buscado. A combinação cria uma leitura racializada que
o fato biológico (que não depende de quem está na cena) não sustenta.

Nesses casos, prefira: (a) uma imagem sem pessoas (ex.: piscina vazia, teste de cloro,
diagrama), ou (b) reformular a resposta do CSV para descrever o mecanismo técnico em vez
do juízo de valor (ex.: "cloração inadequada" em vez de "mal tratada") — o que também
tende a ser mais preciso clinicamente. Nunca resolva isso só trocando a etnia das pessoas
na foto por outra; isso não corrige o problema de fundo, só o desloca.

## Bancos sem API confirmada

CDC PHIL (phil.cdc.gov) e DermNet NZ não têm API oficial confirmada. Não baixe nada de
lá. Se quiser sugerir como opção manual, gere a URL de busca
(`https://phil.cdc.gov/Quicksearch.aspx?query=<termo>`) e anote no manifest em vez de
baixar.

## Ferramenta disponível (ponto de partida, não decisão final)

`h:/busca-imagens-agentes/buscar_imagens.py` já sabe buscar candidatos na Wikimedia
Commons (categorias curadas + busca textual como fallback, já filtrando por tipo de
arquivo). Rode assim pra baixar até 5 candidatos por necessidade na pasta certa:

```
cd h:/busca-imagens-agentes
python buscar_imagens.py --only "<nome EXATO do campo 'agente' no JSON>"
```

Isso só te dá um ponto de partida. **A decisão final é sua**, via inspeção visual (Read)
de cada candidato baixado, comparando com a regra de tipo acima e com a resposta exata
do CSV. Se nenhum candidato bater, ou se você souber (pelo seu conhecimento médico) um
termo de busca ou categoria melhor do que a que o script tentou, faça sua própria
consulta na API do Commons:

```
https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch=<termo>&gsrnamespace=6&gsrlimit=10&prop=imageinfo&iiprop=url|extmetadata|mime&iiurlwidth=1280&format=json
```

ou por categoria (troque `<categoria>` por um nome de categoria real do Commons que você
ache plausível, ex: `Category:Herpes zoster`):

```
https://commons.wikimedia.org/w/api.php?action=query&generator=categorymembers&gcmtitle=Category:<categoria>&gcmtype=file&gcmlimit=40&prop=imageinfo&iiprop=url|extmetadata|mime&iiurlwidth=1280&format=json
```

Baixe o candidato promissor (`curl` ou `python -c "import urllib.request; ..."`) pra
dentro da subpasta certa antes de confirmar com o Read.

## Processo, passo a passo, para cada uma das 4 necessidades do seu agente

1. Releia a resposta exata do CSV pro seu agente/tipo (Achado e Aplicado, especialmente).
2. Rode o script pra pegar candidatos (ou pule direto pra busca manual se achar que vai
   ser ruim, ex: transmissão endógena).
3. Abra CADA candidato baixado com a ferramenta de leitura de imagem e confirme:
   (a) é do TIPO certo (diagrama vs foto clínica vs radiografia vs micrografia)?
   (b) é do CONTEÚDO certo (mostra exatamente o que a resposta do CSV descreve)?
4. Apague os arquivos que não confirmarem. Mantenha só 1 (idealmente) ou até 2
   confirmados por necessidade.
5. Atualize `manifest.json` da pasta do agente (schema abaixo).
6. Se não confirmar nenhum, deixe `"confirmado": false` e explique o motivo em
   `"justificativa"` — não crie arquivo de relatório separado pra isso.

## Estrutura de pastas (não mude)

```
imagens_agentes/<NN>_<slug-do-agente>/
  categoria/
  transmissao/
  achado/
  tratamento/
  manifest.json
  REVISAO_MANUAL.md        (só se sensivel)
```//
`NN` é o campo `ordem` do JSON com 2 dígitos (ex: `04`). `slug-do-agente` é o nome do
campo `agente` em minúsculas, sem acento, espaços trocados por `_`.

## Schema do manifest.json

```json
{
  "ordem": 4,
  "agente": "EBV (Mononucleose)",
  "disciplina": "virologia",
  "imagens": {
    "categoria":   { "confirmado": true, "arquivo_local": "04_ebv_mononucleose/categoria/01_x.png", "justificativa": "diagrama de estrutura do Herpesviridae, capsideo icosaedrico visivel", "fonte": "categoria_commons:Herpesviridae", "licenca": "CC BY-SA 4.0", "licenca_url": "...", "autor": "...", "url_original": "..." },
    "transmissao": { "confirmado": false, "arquivo_local": null, "justificativa": "nenhum candidato mostrava contato via saliva de forma especifica", "pendente": true },
    "achado":      { "confirmado": true, "arquivo_local": "...", "justificativa": "...", "fonte": "...", "licenca": "...", "licenca_url": "...", "autor": "...", "url_original": "..." },
    "tratamento":  { "confirmado": true, "arquivo_local": "...", "justificativa": "foto do rash por amoxicilina, conforme exececao documentada (alerta, nao remedio)", "fonte": "...", "licenca": "...", "licenca_url": "...", "autor": "...", "url_original": "..." }
  },
  "observacoes": "texto livre: substituicoes, casos endogenos, sensivel, etc."
}
```

## Tabela de exceções e casos especiais (34 agentes)

Se o seu agente não aparece aqui, siga a regra rígida padrão sem exceção.

| # | Agente | Exceção / instrução específica |
|---|---|---|
| 2 | HSV-2 (Herpes Genital) | **Achado é sensível** (úlceras genitais). Não baixar — usar `REVISAO_MANUAL.md`. Categoria/Transmissão/Tratamento seguem regra normal. |
| 3 | VZV (Varicela-Zoster) | Achado do CSV cobre 2 apresentações (varicela disseminada E zoster dermatomal). Pode manter até 2 imagens confirmadas em achado; priorize a de zoster (mais icônica/cobrada). |
| 4 | EBV (Mononucleose) | **Aplicado (tratamento) não é uma foto de remédio.** A resposta real é "evitar esforço físico (risco de ruptura esplênica) e evitar amoxicilina". Use foto do rash por amoxicilina em mononucleose como imagem de alerta (existe no Commons: categoria "Infectious mononucleosis"). Justifique isso no manifest. |
| 5 | CMV (Citomegalovirus) | Achado é "microcefalia e surdez neurossensorial" (CMV congênito) — busque foto clínica de microcefalia neonatal, não histopatologia de inclusão viral. |
| 6 | HBV (Hepatite B) | Achado é "evolução para cirrose e carcinoma hepatocelular" — não é um sinal físico, use foto real de patologia bruta de fígado cirrótico/nodular (categoria Commons "Liver cirrhosis" ou similar). |
| 7 | HPV | **Achado é sensível/interno** (câncer de colo de útero) — não baixar, usar `REVISAO_MANUAL.md`. **Aplicado (tratamento) NÃO é a vacina Gardasil** (isso é prevenção, não tratamento) — a resposta real do CSV é "cauterização ou excisão das lesões", busque foto de procedimento. |
| 11 | Vírus da Raiva | Achado é "hidrofobia" (comportamental, espasmo ao tentar engolir líquido) — muito difícil de fotografar com confiança. Se não achar nada que mostre isso especificamente, é aceitável deixar pendente em vez de forçar uma foto genérica de paciente com raiva. |
| 13 | Influenza A | Achado é "febre alta súbita + mialgia intensa" — sintomas sem sinal físico único fotografável. Aceitável deixar pendente. |
| 14 | Hantavirus | Achado é "edema pulmonar agudo bilateral e choque" — use radiografia de tórax (infiltrado bilateral), não foto de pele. |
| 16 | HCV (Hepatite C) | Achado é "cronifica em 80%, evolui a cirrose e câncer de fígado" — mesma lógica do HBV, foto real de patologia bruta de fígado cirrótico (pode reaproveitar mesmo tipo de imagem, mas confirme visualmente igual). |
| 18 | Malassezia (Pitiríase Versicolor) | **Transmissão é endógena** (fungo já reside na pele, não é transmitido). Não busque imagem de "transmissão" — deixe esse campo vazio com `"observacoes": "endogeno, sem via de transmissao"`, sem contar como pendência. |
| 21 | Trichosporon (Piedra Branca) | Transmissão é "umidade e má higiene" — abstrato, sem cena fotografável específica. Aceitável deixar pendente. |
| 31 | Candida (Candidíase) | **Transmissão é endógena** (fungo já reside nas mucosas). Mesma regra do item 18: deixe vazio com observação, não conta como pendência. |
| 28 | Histoplasma (Histoplasmose) | Achado é "pneumonia leve vs. forma disseminada grave" — use radiografia de tórax, não foto de pele. |
| 29 | Coccidioides (Coccidioidomicose) | Achado é "pneumonia aguda (febre do vale)" — use radiografia de tórax. |
| 32 | Cryptococcus (Criptococose) | Achado é "meningite grave em imunodeprimido" — sem sinal físico fotografável direto. Se quiser, pode usar a micrografia de tinta da China como substituto de evidência laboratorial (deixe claro no manifest que é substituto, não achado físico), ou deixar pendente. |
| 33 | Aspergillus (Aspergilose) | Achado é explicitamente "achado RADIOLÓGICO" (aspergiloma) — use radiografia/TC de tórax mostrando bola fúngica, não foto de pele nem micrografia aqui. |
| 34 | Pneumocystis jirovecii (PCP) | Achado é "tosse seca + febre + dispneia progressiva" — sem sinal físico único. Substituto aceitável: radiografia/TC de tórax com padrão de vidro fosco (convenção médica padrão pra PCP, mesmo não estando literalmente na resposta do CSV) — deixe isso explícito no manifest. Transmissão ("ocorre em imunodeprimido") é abstrata, sem vetor fotografável — aceitável deixar pendente. |

## Ao terminar

Retorne um resumo de 4 linhas (uma por necessidade) dizendo CONFIRMADO ou PENDENTE +
motivo curto, pra eu poder consolidar o relatório final de pendências de todos os
34 agentes.
