"""
Auxiliar de curadoria: aplica o resultado da revisao visual manual a um agente.

Para cada tipo (categoria/transmissao/achado/tratamento), recebe a lista dos nomes de
arquivo CONFIRMADOS (na ordem final desejada; pode ter mais de um, ex.: VZV achado).
Apaga os demais candidatos da pasta, renumera os confirmados como 01_, 02_... e reescreve
o manifest.json so com as entradas confirmadas. Tipo com lista vazia = pendente (nenhum
candidato bateu com o criterio); a pasta fica vazia e o manifest registra o motivo.

Uso (dentro de outro script/REPL):
    from curar_imagens import curar
    curar("01_hsv_1_herpes_labial", {
        "categoria": ["03_herpesvirus_structure.png"],
        "transmissao": [],  # pendente
        "achado": ["01_herpes_labialis_opryszczka_wargowa.jpg"],
        "tratamento": ["01_acyclovirointment_15g_carton.jpg"],
    }, motivo_pendente={"transmissao": "candidatos eram arte/insetos, nenhum mostrava contato com saliva"})
"""

import json
import re
import unicodedata
from pathlib import Path

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


BASE = _raiz_projeto(Path(__file__).resolve().parent)
RAIZ_IMAGENS = BASE / "imagens_agentes"


def slugify(texto, max_len=40):
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "_", sem_acento.lower()).strip("_")
    return slug[:max_len] or "item"


def curar(pasta_agente, confirmados, motivo_pendente=None):
    motivo_pendente = motivo_pendente or {}
    pasta = RAIZ_IMAGENS / pasta_agente
    manifest_path = pasta / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    slug_agente = slugify(manifest.get("agente", pasta_agente))

    for tipo, nomes_confirmados in confirmados.items():
        subpasta = pasta / tipo
        entradas_antigas = {Path(e["arquivo_local"]).name: e for e in manifest["imagens"].get(tipo, []) if e.get("arquivo_local")}

        novas_entradas = []
        for i, nome in enumerate(nomes_confirmados, start=1):
            if nome not in entradas_antigas:
                raise ValueError(f"{pasta_agente}/{tipo}: '{nome}' nao esta no manifest atual")
            origem = subpasta / nome
            extensao = origem.suffix
            sufixo = f"_{i}" if len(nomes_confirmados) > 1 else ""
            destino = subpasta / f"{slug_agente}_{tipo}{sufixo}{extensao}"
            if origem != destino:
                origem.rename(destino)
            entrada = dict(entradas_antigas[nome])
            entrada["arquivo_local"] = str(destino.relative_to(RAIZ_IMAGENS))
            entrada["revisado_visualmente"] = True
            novas_entradas.append(entrada)

        # apaga tudo que nao foi confirmado
        if subpasta.exists():
            mantidos = {e["arquivo_local"].split("\\")[-1].split("/")[-1] for e in novas_entradas}
            for arquivo in subpasta.iterdir():
                if arquivo.is_file() and arquivo.name not in mantidos:
                    arquivo.unlink()

        if not nomes_confirmados:
            manifest["imagens"][tipo] = {
                "confirmado": False,
                "motivo": motivo_pendente.get(tipo, "nenhum candidato bateu com o criterio na revisao visual"),
            }
        else:
            manifest["imagens"][tipo] = novas_entradas

    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"curado: {pasta_agente}")
