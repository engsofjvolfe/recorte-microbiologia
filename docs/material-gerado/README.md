# Mecanismo de busca de imagens (fase de teste)

![Busca de imagens](https://img.shields.io/badge/Busca_de_imagens-experimental_%2F_sem_garantia-important)

Este documento explica como as imagens anexadas aos cards do núcleo de microbiologia (ver
[README.md da raiz](../../README.md)) foram obtidas. Elas não vêm de um pipeline validado
e repetível — vêm de um mecanismo de busca **ainda experimental**, formado por dois
scripts e uma etapa manual obrigatória entre eles. Do total de 136 imagens necessárias
para os 34 agentes originais, 107 já foram confirmadas manualmente. Os 14 agentes
adicionados depois ainda não entraram nesta fila de busca.

## Como funciona

1. [`buscar_imagens.py`](buscar_imagens.py) consulta a API oficial da Wikimedia Commons.
   A fonte primária é uma lista de categorias do Commons **verificadas manualmente uma a
   uma** para cada agente (ex.: categoria `Herpesviridae` para o HSV-1), com busca
   textual livre como plano B quando não há categoria conhecida. Ele baixa alguns
   candidatos por necessidade (categoria/transmissão/achado/tratamento) e grava um
   `manifest.json` com licença, autor e URL de cada um.
2. Cada candidato baixado precisa ser **aberto e conferido visualmente por uma pessoa
   (ou por um agente com leitura de imagem)** antes de virar card. O script não distingue
   sozinho um diagrama de uma foto clínica, nem confirma que a imagem mostra exatamente o
   achado descrito na resposta do CSV — essa é a parte que falha se for pulada. As regras
   dessa conferência estão em [`CRITERIOS-BUSCA-IMAGENS.md`](CRITERIOS-BUSCA-IMAGENS.md).
3. [`curar_imagens.py`](curar_imagens.py) aplica o resultado da conferência manual: apaga
   os candidatos descartados, renomeia os confirmados e atualiza o `manifest.json`.

## Por que "experimental" e não "pronto"

**Isso não é um mecanismo determinístico de garimpagem de imagens.** Duas tentativas
anteriores de automatizar mais essa busca já falharam, pelos motivos documentados em
[`CRITERIOS-BUSCA-IMAGENS.md`](CRITERIOS-BUSCA-IMAGENS.md): busca textual livre não
encontrava quase nada, e busca por categoria + palavra-chave trazia o assunto certo mas o
tipo de imagem errado (ex.: foto de lâmina de citologia aparecendo onde devia vir um
diagrama de estrutura viral). O que existe hoje funciona porque alguém revisou
manualmente cada um dos 108 arquivos confirmados — não porque o script garanta acerto
sozinho para um agente novo ou para uma necessidade ainda não coberta.

Trate como ferramenta de ponto de partida para a busca, não como solução pronta para
reaplicar sem supervisão.

## Documentos desta pasta

| Arquivo | O que é |
|---|---|
| [`buscar_imagens.py`](buscar_imagens.py) | Busca/baixa candidatos de imagem (Wikimedia Commons) |
| [`curar_imagens.py`](curar_imagens.py) | Aplica a conferência visual manual sobre os candidatos baixados |
| [`CRITERIOS-BUSCA-IMAGENS.md`](CRITERIOS-BUSCA-IMAGENS.md) | Regras de curadoria de imagens por tipo de pergunta |
| [`dicionario-gatilhos-virologia.md`](dicionario-gatilhos-virologia.md) | Cadeia causal didática (5 elos) dos 23 vírus |
| [`dicionario-gatilhos-micologia.md`](dicionario-gatilhos-micologia.md) | Cadeia causal didática (5 elos) dos 25 fungos |
| [`virologia-especial-determinismo.md`](virologia-especial-determinismo.md) | Ficha determinística (6 eixos) dos 23 vírus |
| [`micologia-especial-determinismo.md`](micologia-especial-determinismo.md) | Ficha determinística (6 eixos) dos 25 fungos |
| [`biologia-fundamental-virus.md`](biologia-fundamental-virus.md) | Base teórica geral: estrutura, taxonomia e ciclo de vida viral |
| [`biologia-fundamental-fungos.md`](biologia-fundamental-fungos.md) | Base teórica geral: biologia e fisiologia fúngica |

Para navegação agente por agente com link direto, use o [INDICE.md da raiz](../../INDICE.md).
