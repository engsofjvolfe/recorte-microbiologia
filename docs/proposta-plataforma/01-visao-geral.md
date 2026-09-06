# Visão Geral

**Proposta:** generalizar o mecanismo deste repositório (hoje específico de
microbiologia) para uma plataforma de material de estudo colaborativo, capaz de
cobrir qualquer disciplina, com busca por IA "determinística" e auditável.

> Este documento reúne contexto, motivação, princípios, objetivos e um esboço de
> requisitos — ainda misturados, sem o rigor formal de um documento de Requisitos
> de modelo V (ver [seção 1](#1-sobre-o-modelo-v-e-o-papel-deste-documento)). É
> matéria-prima: serve para gerar, depois, o documento de Requisitos propriamente
> dito. A cadeia de documentos que viria a seguir (Requisitos, Arquitetura, Design,
> Planos de Teste) ainda não está fechada, de propósito — ver
> [seção 13](#13-relação-com-este-repositório).
>
> **Este documento é intencionalmente genérico, modular e agnóstico de
> tecnologia e de disciplina.** Qualquer ferramenta, formato de arquivo ou
> linguagem citada aqui é **ilustrativa do protótipo atual** (este repositório de
> microbiologia) — não um requisito de que a plataforma final use a mesma
> tecnologia. Decisões de "como" ficam para o futuro documento de Arquitetura e
> Design, ainda não escrito.

---

## 1. Sobre o modelo V e o papel deste documento

O modelo V liga cada nível de especificação a um nível de verificação correspondente:

```
            Requisitos  <——————————————————>  Testes de Aceitação
Requisitos de Sistema    <————————————————>  Testes de Sistema
      Arquitetura        <——————————>  Testes de Integração
          Design         <——>  Testes de Unidade
                  Implementação
```

Quando formalizado, cada nível de especificação vira rastreável até um nível de
verificação correspondente. É isso que torna uma proposta pequena, feita por poucas
pessoas, "academicamente aceitável" desde o início: existe como provar depois que o
que foi prometido foi, de fato, verificado.

Este documento **não é** esse "Requisitos" formal do modelo V — ele mistura
contexto, motivação, princípios e um esboço de requisitos (seções 7 e 8) porque,
nesta fase, o objetivo é alinhar a ideia, não formalizar. O documento de Requisitos
propriamente dito, com o rigor que o modelo V exige, é extraído deste depois, como
passo seguinte — e é ele, não este aqui, que ocupa a primeira posição do diagrama
acima.

---

## 2. Contexto e motivação

Este repositório já prova um formato que funciona: um professor disponibiliza
material de aula → alguém reescreve isso em fichas estruturadas → um gerador
produz um deck de estudo a partir dessas fichas (ver
[MANUAL.md](../../MANUAL.md)). O resultado, hoje, cobre uma única disciplina
(microbiologia), com um schema fixo, e foi feito por uma pessoa só, manualmente.

Duas limitações motivam esta proposta:

1. **O formato está amarrado à disciplina e à implementação.** O schema de
   "agente" (vírus/fungo) com 5 eixos fixos, e a ferramenta usada para produzir o
   deck, não generalizam para outras matérias ou outros formatos de saída sem
   reescrever o mecanismo inteiro.
2. **A colaboração exige saber programar.** Editar arquivos de dados direto e rodar
   scripts via terminal afasta o público-alvo real (colegas de outras disciplinas
   que não são da área de exatas).

Ao mesmo tempo, existe uma oportunidade que vai além de "organizar matéria":
**ensinar uso ético e verificável de IA na graduação**, área hoje negligenciada pela
maioria dos alunos, que usam IA generativa para estudar sem qualquer critério de
verificação. Hoje, a "ficha determinística" e o "dicionário de gatilhos" deste
repositório são resultado de curadoria **manual**, sem uso de IA e sem citação de
fonte por afirmação (ver [MANUAL.md](../../MANUAL.md), que é explícito: "não foi
gerado por um processo automatizado e determinístico"). "Determinístico", ali,
descreve só o formato — sempre os mesmos eixos, não um processo de verificação.

Os seis eixos usados nesse guia de micologia (ou os cinco do deck por agente) não
são universais — são um recorte subjetivo, ponto. Outra matéria, ou até a mesma
matéria com outro recorte, pode pedir eixos completamente diferentes, e isso é
esperado, não um problema a corrigir (é por isso que a seção
[3](#3-princípios-de-design-genérico-modular-agnóstico) trata eixo como algo
configurável, não fixo). O que vale generalizar não é o conjunto de eixos em si,
mas a prática por trás dele: **obrigar quem organiza o material a decidir, de
forma explícita e limitada, o que realmente precisa ser registrado** — em vez de
deixar o material crescer sem corte. É essa mesma disciplina de recorte, aplicada
a um conjunto de eixos definido caso a caso, que depois torna viável exigir que
cada eixo preenchido aponte para o trecho da fonte que o sustenta — inclusive
quando o rascunho for produzido com apoio de IA.

Vale registrar uma direção futura, exploratória e fora do escopo do MVP: essa
mesma prática de recorte, se usada por quem prepara a aula — não só por quem
estuda depois —, tem potencial para ajudar a separar o que é essencial do que é
acessório também na hora de ensinar, não só na hora de revisar.

---

## 3. Princípios de design: genérico, modular, agnóstico

Estes três princípios governam todo requisito deste documento e devem ser
herdados por todos os documentos seguintes da cadeia:

- **Genérico** — nenhum requisito pode presumir uma disciplina específica.
  Onde este repositório usa "agente" (vírus/fungo), a proposta usa "tópico" ou
  "item de estudo": um conceito neutro, com eixos de conteúdo configuráveis por
  disciplina, não fixos em número ou nome.
- **Modular** — a plataforma é composta por módulos independentes e substituíveis,
  sem acoplamento entre eles:
  - **definição de disciplina** (schema: quais eixos, quais tipos de card);
  - **geração de material** (transforma dados estruturados em deck/documento);
  - **apresentação/busca** (navegação do conteúdo já gerado);
  - **assistência de IA** (roteiro determinístico de apoio à criação de conteúdo).

  Cada módulo deve poder ser revisado, testado ou substituído sem exigir mudança
  nos demais. Isso inclui poder trocar a ferramenta de geração de deck, o formato
  de arquivo de dados, ou o método de hospedagem, sem tocar nos outros módulos.
- **Agnóstico de tecnologia** — este documento e os requisitos abaixo não fixam
  linguagem, formato de arquivo, ferramenta de deck ou provedor de hospedagem.
  Essas escolhas são deliberadamente adiadas para o futuro documento de
  Arquitetura, onde podem mudar conforme restrições reais (custo, manutenção, o
  que a equipe souber operar) sem invalidar este documento.

---

## 4. Objetivo geral

Criar uma plataforma simples, modular e agnóstica de disciplina, para transformar
material de aula em conteúdo de estudo estruturado e colaborativo — com um método
de busca/IA determinístico e auditável — começando por um MVP sem infraestrutura
de servidor.

## 5. Objetivos específicos

1. Generalizar o mecanismo atual (fonte de verdade estruturada → geração de
   material de estudo) para qualquer disciplina, não só microbiologia, via um
   schema configurável em vez de um formato fixo por código.
2. Permitir colaboração de múltiplos alunos sem exigir conhecimento técnico.
3. Definir e documentar, como processo repetível e independente de disciplina, um
   método de apoio por IA que ajude quem organiza o material a fixar um recorte
   explícito e limitado (o conjunto de eixos é definido caso a caso, não herdado
   deste repositório) — exigindo, diferente do que é feito hoje de forma manual,
   citação auditável da fonte para cada eixo preenchido.
4. Entregar um MVP **sem backend robusto**: o mínimo de infraestrutura possível —
   sofisticação vem depois, com uso real validando o que de fato falta.
5. Manter a arquitetura modular o suficiente para que módulos possam ser
   adicionados, trocados ou aposentados sem reescrever a plataforma inteira.
6. Preparar a base para que o projeto saia deste repositório e vire um repositório
   próprio, com identidade e validação acadêmica independentes deste material de
   microbiologia.

---

## 6. Escopo do MVP

### Dentro do escopo (v1)

- Schema de conteúdo genérico por disciplina: eixos de conteúdo e tipos de card
  configuráveis, não fixos em código.
- Um meio de apresentação/navegação do conteúdo gerado, utilizável por quem não
  programa — sem servidor de aplicação nem banco de dados (a forma concreta de
  hospedagem/apresentação fica a critério do futuro documento de Arquitetura).
- Um gerador de material de estudo que leia qualquer disciplina cadastrada no
  schema e produza a saída (deck ou equivalente) — generalização do mecanismo já
  existente neste repositório, mas não obrigatoriamente a mesma ferramenta.
- Processo documentado de "busca determinística por IA": um roteiro/prompt
  versionado que qualquer aluno pode seguir para gerar rascunho de ficha, sempre
  citando a fonte (trecho do material original) usada pela IA — sem resposta de IA
  sem rastro verificável.
- Fluxo de colaboração via controle de versão (ou mecanismo equivalente de
  revisão), com um roteiro simples para quem quiser contribuir conteúdo novo sem
  familiaridade técnica prévia.

### Fora do escopo (por agora)

- Servidor de aplicação, banco de dados, autenticação de usuários.
- Upload de material de aula original diretamente pela interface (esse material
  continua sendo tratado por fora, manualmente, por questão de direito autoral —
  ver [NOTICE.md](../../NOTICE.md)).
- Publicação automática de conteúdo sem revisão humana.
- Suporte simultâneo a múltiplas instituições/idiomas.

Essas exclusões não são permanentes — são o que fica para depois da validação do
MVP em campo (ver [Objetivos específicos](#5-objetivos-específicos), item 4).

---

## 7. Requisitos funcionais (RF)

| ID | Requisito |
|---|---|
| RF01 | O sistema deve permitir descrever uma disciplina nova (nome, eixos de conteúdo, tipos de card) sem alterar o código dos demais módulos. |
| RF02 | O sistema deve gerar material de estudo a partir dos dados estruturados de qualquer disciplina cadastrada, independente do formato final escolhido. |
| RF03 | O sistema deve prover navegação/busca por tópico, legível por quem não programa, cobrindo múltiplas disciplinas ao mesmo tempo. |
| RF04 | O sistema deve documentar um método reprodutível de uso de IA para gerar rascunho de ficha, exigindo citação da fonte usada, independente da disciplina. |
| RF05 | O sistema deve permitir que uma contribuição de conteúdo seja revisada por um humano antes de entrar no material publicado. |
| RF06 | O sistema deve continuar funcionando sem os componentes de IA — a geração assistida por IA é um acelerador de rascunho, não uma dependência. |
| RF07 | O sistema deve ser dividido em módulos independentes (schema de disciplina, geração, apresentação, assistência de IA), cada um substituível sem exigir mudança nos demais. |
| RF08 | O sistema deve permitir que uma pessoa sem conhecimento técnico submeta conteúdo novo, seguindo um roteiro guiado — sem exigir que ela mesma edite arquivo de dados, use terminal ou opere controle de versão diretamente. |

## 8. Requisitos não funcionais (RNF)

| ID | Requisito |
|---|---|
| RNF01 | Custo de operação próximo de zero, sem depender de infraestrutura de servidor dedicada. |
| RNF02 | Manutenção viável por uma pessoa ou um pequeno grupo de voluntários, sem equipe dedicada de infraestrutura. |
| RNF03 | Licenciamento claro e separado entre código e conteúdo, como já praticado neste repositório (ver [NOTICE.md](../../NOTICE.md)). |
| RNF04 | Toda saída de IA usada no conteúdo final deve ser rastreável até a fonte original (trecho do material de aula), qualquer que seja a disciplina. |
| RNF05 | A interface de consulta deve ser usável por alguém sem conhecimento técnico, sem precisar editar arquivo de dados, terminal ou controle de versão diretamente. |
| RNF06 | Nenhum requisito funcional deve depender de uma tecnologia, formato de arquivo ou fornecedor específico — a escolha concreta é responsabilidade do Documento 3 (Arquitetura), não deste documento. |

---

## 9. Stakeholders

| Papel | Interesse |
|---|---|
| Aluno-mantenedor (atual) | Evoluir o projeto e submetê-lo como pré-projeto validável academicamente. |
| Alunos colaboradores | Contribuir conteúdo de outras disciplinas sem precisar programar. |
| Alunos consumidores | Só estudar — usar o material pronto, com confiança na procedência do conteúdo. |
| Professor/banca avaliadora | Avaliar se a proposta tem rigor metodológico suficiente para virar projeto validado. |

---

## 10. Restrições

- Material de aula de terceiros não pode ser redistribuído — qualquer design de
  contribuição precisa respeitar isso (ver [NOTICE.md](../../NOTICE.md)).
- Uso de IA deve ser auxiliar e auditável, nunca uma "resposta pronta" sem
  verificação — é um objetivo pedagógico do projeto, não só uma preferência técnica.
- Sem orçamento e sem equipe fixa: qualquer decisão de arquitetura no MVP precisa
  favorecer simplicidade de manutenção sobre robustez/escala.
- Nenhuma decisão de tecnologia deve ser tratada como definitiva neste estágio —
  este documento descreve comportamento esperado, não implementação.

---

## 11. Critérios de aceitação preliminares

Versão inicial e ainda não formal — servirão de base para o futuro documento de
Testes de Aceitação, quando a cadeia de documentos for formalizada:

- É possível cadastrar uma disciplina nova e gerar material de estudo a partir
  dela sem editar código-fonte dos demais módulos.
- Uma pessoa sem conhecimento técnico consegue navegar/buscar conteúdo de mais de
  uma disciplina pela interface, sem instruções além de um guia curto (padrão do
  [MANUAL.md](../../MANUAL.md) atual).
- Toda ficha gerada com apoio de IA tem, junto, a fonte (trecho do material
  original) que a originou.
- O MVP roda sem servidor de aplicação dedicado.
- Um módulo (por exemplo, o gerador de material) pode ser trocado por outra
  implementação sem exigir mudança no schema de disciplina ou na apresentação.
- Nenhuma contribuição de conteúdo entra no material publicado sem antes passar
  por uma revisão humana registrada.
- O fluxo de estudo/consulta funciona integralmente mesmo que nenhuma ficha tenha
  sido gerada com apoio de IA.
- Uma pessoa sem conhecimento técnico consegue submeter conteúdo novo seguindo um
  roteiro guiado, sem precisar editar arquivo de dados, usar terminal ou operar
  controle de versão diretamente.

---

## 12. Riscos

| Risco | Mitigação prevista |
|---|---|
| IA "alucinar" e virar fonte de erro sistemático no material | RF04/RNF04 — exigir citação de fonte para toda ficha assistida por IA. |
| Escopo crescer antes de validar o MVP mais simples | Escopo do MVP (seção 6) definido para excluir backend/auth desde já. |
| Baixa adesão de colaboradores externos | Fluxo de contribuição com roteiro simples e sem exigência técnica (RF08), testado primeiro dentro do próprio curso. |
| Acoplamento acidental a uma disciplina ou tecnologia específica | Princípios da seção 3 (genérico/modular/agnóstico) e RNF06, revisados a cada documento novo da cadeia. |
| Projeto sair deste repositório e perder rastreabilidade do histórico | Este documento e os seguintes migram junto quando o repositório próprio for criado. |

---

## 13. Relação com este repositório

Este documento vive aqui, em `docs/proposta-plataforma/`, como planejamento — o
núcleo de microbiologia deste repositório continua sendo o protótipo concreto que
valida a proposta na prática, mas nenhum requisito acima depende dele
especificamente. Quando a direção estiver mais madura, o conteúdo desta pasta
migra para um repositório próprio da plataforma; este repositório permanece como
o material de microbiologia que a originou.

