"""
Gera pacotes Anki (.apkg) a partir dos CSVs de perguntas em docs/material-gerado/.

Estrutura reutilizavel/DRY: um unico modelo de nota (MODELO) e um unico template sao
usados para TODOS os decks gerados por este script -- nucleo por agente (com imagem) e
fundamentos teoricos (sem imagem por enquanto, mas com o campo Imagem ja presente no
modelo para escalonamento futuro sem precisar migrar nota). "Vinheta (agente)" no nucleo
reaproveita a mesma imagem de "Categoria" do proprio agente (por design, ja documentado
no JSON de origem). Modular: cada disciplina vira um subdeck ("Nucleo::Virologia",
"Fundamentos::Micologia" etc.), cada CSV gera seu proprio pacote .apkg, e a copia de
midia e isolada na classe BancoDeMidia.

Uso:
    python montar_deck.py              # gera os dois pacotes (nucleo + fundamentos)
    python montar_deck.py nucleo       # so o pacote de nucleo por agente
    python montar_deck.py fundamentos  # so o pacote de fundamentos teoricos
"""

import csv
import json
import re
import shutil
import unicodedata
from pathlib import Path

import genanki

def _raiz_projeto(inicio: Path) -> Path:
    """Sobe a arvore de pastas a partir de `inicio` ate achar a raiz do projeto,
    identificada pela presenca conjunta de `fila-busca-imagens-agentes.json` e da
    pasta `imagens_agentes/` (as duas peca de infraestrutura que nao mudam de lugar,
    ao contrario dos documentos de conteudo em `docs/`). Isso deixa o script robusto
    a reorganizacoes de pasta, inclusive renomear a propria pasta-raiz do projeto."""
    for candidata in (inicio, *inicio.parents):
        if (candidata / "fila-busca-imagens-agentes.json").exists() and (candidata / "imagens_agentes").is_dir():
            return candidata
    raise FileNotFoundError(
        f"nao encontrei a raiz do projeto (fila-busca-imagens-agentes.json + imagens_agentes/) subindo a partir de {inicio}"
    )


def _localizar_arquivo(nome_arquivo: str, raiz: Path) -> Path:
    """Acha `nome_arquivo` na raiz do projeto ou em qualquer subpasta dela --
    o CSV de perguntas ja mudou de lugar mais de uma vez durante reorganizacoes."""
    caminho_direto = raiz / nome_arquivo
    if caminho_direto.exists():
        return caminho_direto
    encontrados = sorted(raiz.rglob(nome_arquivo))
    if not encontrados:
        raise FileNotFoundError(f"'{nome_arquivo}' nao encontrado em nenhum lugar sob {raiz}")
    return encontrados[0]


BASE = _raiz_projeto(Path(__file__).resolve().parent)
CSV_PATH = _localizar_arquivo("perguntas-nucleo-dicionarios.csv", BASE)
CSV_FUNDAMENTOS_MICO = _localizar_arquivo("perguntas-fundamentos-fungos.csv", BASE)
CSV_FUNDAMENTOS_VIRO = _localizar_arquivo("perguntas-fundamentos-virus.csv", BASE)
IMAGENS_DIR = BASE / "imagens_agentes"
SAIDA_APKG = BASE / "anki-decks" / "Microbiologia Nucleo.apkg"
SAIDA_APKG_FUNDAMENTOS = BASE / "anki-decks" / "Fundamentos-Microbiologia.apkg"
MEDIA_TMP = BASE / "_media_apkg_tmp"

# IDs fixos (gerados uma vez, nao mudar): reimportar o mesmo .apkg atualiza os cartoes
# existentes no Anki em vez de duplicar o deck inteiro. Os IDs de fundamentos ficam numa
# faixa separada dos de nucleo para nunca colidir, mesmo que os pacotes um dia se fundam.
DECK_ID_VIRO = 1957000002
DECK_ID_MICO = 1957000003
MODEL_ID = 1957000100
DECK_ID_FUNDAMENTOS_VIRO = 1957000012
DECK_ID_FUNDAMENTOS_MICO = 1957000013

TIPO_PARA_SUBPASTA = {
    "categoria": "categoria",
    "transmissao": "transmissao",
    "achado": "achado",
    "aplicado": "tratamento",
    "vinheta": "categoria",  # reaproveita a imagem de estrutura do proprio agente
}


def normalizar(texto):
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    return sem_acento.lower()


def slugify(texto, max_len=60):
    slug = re.sub(r"[^a-z0-9]+", "_", normalizar(texto)).strip("_")
    return slug[:max_len] or "item"


def tipo_normalizado(tipo_pergunta):
    t = normalizar(tipo_pergunta)
    for prefixo, tipo in (
        ("categoria", "categoria"), ("transmiss", "transmissao"), ("achado", "achado"),
        ("vinheta", "vinheta"), ("aplicado", "aplicado"),
    ):
        if t.startswith(prefixo):
            return tipo
    raise ValueError(f"tipo_pergunta desconhecido: {tipo_pergunta!r}")


def carregar_pastas_agentes():
    """Mapeia slug(nome do agente) -> Path da pasta em imagens_agentes/."""
    mapa = {}
    for pasta in IMAGENS_DIR.iterdir():
        manifest_path = pasta / "manifest.json"
        if not pasta.is_dir() or pasta.name.startswith("_") or not manifest_path.exists():
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        mapa[slugify(manifest["agente"])] = pasta
    return mapa


def imagem_confirmada(pasta_agente, subpasta):
    """Primeiro arquivo confirmado em <pasta_agente>/<subpasta>, ou None se pendente."""
    alvo = pasta_agente / subpasta
    if not alvo.is_dir():
        return None
    arquivos = sorted(f for f in alvo.iterdir() if f.is_file())
    return arquivos[0] if arquivos else None


class BancoDeMidia:
    """Copia cada imagem uma unica vez para uma pasta temporaria com nome estavel,
    mesmo quando dois cartoes (ex.: Categoria e Vinheta) apontam pro mesmo arquivo."""

    def __init__(self, pasta_tmp):
        self.pasta_tmp = pasta_tmp
        if self.pasta_tmp.exists():
            shutil.rmtree(self.pasta_tmp)
        self.pasta_tmp.mkdir(parents=True)
        self._cache = {}

    def registrar(self, caminho_original):
        if caminho_original is None:
            return None
        chave = str(caminho_original.resolve())
        if chave in self._cache:
            return self._cache[chave]
        nome_unico = f"{len(self._cache):04d}_{caminho_original.name}"
        shutil.copy(caminho_original, self.pasta_tmp / nome_unico)
        self._cache[chave] = nome_unico
        return nome_unico

    def arquivos(self):
        return [str(self.pasta_tmp / nome) for nome in self._cache.values()]


MODELO = genanki.Model(
    MODEL_ID,
    "Nucleo Microbiologia - Pergunta e Resposta",
    fields=[
        {"name": "Pergunta"}, {"name": "Resposta"}, {"name": "Imagem"},
        {"name": "Agente"}, {"name": "Tipo"}, {"name": "Disciplina"},
    ],
    templates=[{
        "name": "Cartao Padrao",
        "qfmt": '<div class="tipo">{{Tipo}} • {{Agente}}</div><div class="pergunta">{{Pergunta}}</div>',
        "afmt": (
            '{{FrontSide}}<hr id="answer">'
            '<div class="resposta">{{Resposta}}</div>'
            '{{#Imagem}}<div class="imagem">{{Imagem}}</div>{{/Imagem}}'
        ),
    }],
    css="""
    .card { font-family: Arial, sans-serif; font-size: 18px; text-align: center; color: #1a1a1a; }
    .tipo { color: #888; font-size: 13px; text-transform: uppercase; letter-spacing: .05em; margin-bottom: 8px; }
    .pergunta { font-weight: 600; }
    .resposta { margin-top: 10px; }
    .imagem img { max-width: 90%; max-height: 320px; margin-top: 14px; border-radius: 6px; }
    """,
)


def montar_fundamentos():
    """Gera o pacote de fundamentos teoricos (micologia + virologia) a partir dos CSVs
    perguntas-fundamentos-*.csv. Reaproveita o mesmo MODELO do nucleo -- inclusive o
    campo Imagem, sempre vazio aqui porque este material ainda nao tem imagem por
    conceito (so por agente, no nucleo). Deixar o campo presente e vazio, em vez de
    omiti-lo, evita ter que migrar as notas existentes no Anki quando/se um dia
    houver imagem por conceito fundamental."""
    decks = {
        "micologia": genanki.Deck(DECK_ID_FUNDAMENTOS_MICO, "Fundamentos::Micologia"),
        "virologia": genanki.Deck(DECK_ID_FUNDAMENTOS_VIRO, "Fundamentos::Virologia"),
    }
    total_cartoes = 0

    for caminho_csv in (CSV_FUNDAMENTOS_MICO, CSV_FUNDAMENTOS_VIRO):
        with open(caminho_csv, encoding="utf-8") as f:
            for linha in csv.DictReader(f):
                disciplina = linha["disciplina"].strip().lower()
                nota = genanki.Note(
                    model=MODELO,
                    fields=[
                        linha["pergunta"].strip(), linha["resposta"].strip(), "",
                        linha["agente"].strip(), linha["tipo_pergunta"].strip(), linha["disciplina"].strip(),
                    ],
                )
                deck_alvo = decks.get(disciplina)
                if deck_alvo is None:
                    raise ValueError(f"disciplina desconhecida: {disciplina!r} em {caminho_csv.name}")
                deck_alvo.add_note(nota)
                total_cartoes += 1

    pacote = genanki.Package(list(decks.values()))
    SAIDA_APKG_FUNDAMENTOS.parent.mkdir(parents=True, exist_ok=True)
    pacote.write_to_file(SAIDA_APKG_FUNDAMENTOS)

    print(f"Deck gerado: {SAIDA_APKG_FUNDAMENTOS}")
    print(f"Total de cartoes: {total_cartoes}")


def montar_nucleo():
    pastas_por_agente = carregar_pastas_agentes()
    midia = BancoDeMidia(MEDIA_TMP)
    decks = {
        "virologia": genanki.Deck(DECK_ID_VIRO, "Nucleo::Virologia"),
        "micologia": genanki.Deck(DECK_ID_MICO, "Nucleo::Micologia"),
    }

    sem_imagem = []
    agentes_sem_pasta = set()
    total_cartoes = 0

    with open(CSV_PATH, encoding="utf-8") as f:
        for linha in csv.DictReader(f):
            disciplina = linha["disciplina"].strip().lower()
            agente_nome = linha["agente"].strip()
            tipo = tipo_normalizado(linha["tipo_pergunta"])
            pasta_agente = pastas_por_agente.get(slugify(agente_nome))

            imagem_html = ""
            if pasta_agente is None:
                agentes_sem_pasta.add(agente_nome)
            else:
                caminho_imagem = imagem_confirmada(pasta_agente, TIPO_PARA_SUBPASTA[tipo])
                if caminho_imagem is None:
                    sem_imagem.append(f"{agente_nome} / {linha['tipo_pergunta']}")
                else:
                    imagem_html = f'<img src="{midia.registrar(caminho_imagem)}">'

            nota = genanki.Note(
                model=MODELO,
                fields=[
                    linha["pergunta"].strip(), linha["resposta"].strip(), imagem_html,
                    agente_nome, linha["tipo_pergunta"].strip(), linha["disciplina"].strip(),
                ],
            )
            deck_alvo = decks.get(disciplina)
            if deck_alvo is None:
                raise ValueError(f"disciplina desconhecida: {disciplina!r} (linha do agente {agente_nome!r})")
            deck_alvo.add_note(nota)
            total_cartoes += 1

    pacote = genanki.Package(list(decks.values()))
    pacote.media_files = midia.arquivos()
    SAIDA_APKG.parent.mkdir(parents=True, exist_ok=True)
    pacote.write_to_file(SAIDA_APKG)

    print(f"Deck gerado: {SAIDA_APKG}")
    print(f"Total de cartoes: {total_cartoes}")
    print(f"Imagens anexadas: {len(midia._cache)}")
    print(f"Cartoes sem imagem confirmada ({len(sem_imagem)}):")
    for item in sem_imagem:
        print("  -", item)
    if agentes_sem_pasta:
        print("Agentes do CSV sem pasta correspondente em imagens_agentes/:")
        for nome in sorted(agentes_sem_pasta):
            print("  -", nome)


if __name__ == "__main__":
    import sys

    alvo = sys.argv[1] if len(sys.argv) > 1 else "todos"
    if alvo in ("nucleo", "todos"):
        montar_nucleo()
    if alvo in ("fundamentos", "todos"):
        montar_fundamentos()
    if alvo not in ("nucleo", "fundamentos", "todos"):
        raise SystemExit(f"argumento desconhecido: {alvo!r} (use nucleo, fundamentos ou nada)")
