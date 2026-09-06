"""
Busca e baixa imagens candidatas para a fila de agentes (fila-busca-imagens-agentes.json).

Para cada um dos 34 agentes, resolve as 4 necessidades de imagem (categoria, transmissao,
achado, tratamento -- via catalogo_tratamentos), busca as 3 primeiras imagens de cada uma
na Wikimedia Commons (API oficial) e baixa os candidatos para revisao manual, junto com um
manifest.json com licenca/autor/URL de cada arquivo.

Agentes cujo campo "observacao" mencione conteudo sensivel (ex: anogenital) NAO tem download
automatico -- so os termos de busca sao listados em relatorios/revisao_manual_sensivel.md.

CDC PHIL e DermNet nao tem API confirmada, entao nunca sao baixados: para toda necessidade de
imagem (sensivel ou nao) o script apenas gera as URLs de busca nesses dois bancos, em
relatorios/bancos_manuais.md, para abertura manual.

Uso:
    python buscar_imagens.py                  # roda tudo
    python buscar_imagens.py --dry-run         # so busca e gera relatorios, nao baixa nada
    python buscar_imagens.py --limit 3         # so os 3 primeiros agentes (teste rapido)
    python buscar_imagens.py --only "HSV"      # so agentes cujo nome contem "HSV"
    python buscar_imagens.py --force           # reprocessa agentes ja concluidos
"""

import argparse
import json
import re
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
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


BASE_DIR = _raiz_projeto(Path(__file__).resolve().parent)
JSON_PATH_PADRAO = BASE_DIR / "fila-busca-imagens-agentes.json"
SAIDA_PADRAO = BASE_DIR / "imagens_agentes"

COMMONS_API = "https://commons.wikimedia.org/w/api.php"
OPENVERSE_API = "https://api.openverse.org/v1/images/"
DAILYMED_API = "https://dailymed.nlm.nih.gov/dailymed/services/v2"
# A Wikimedia recomenda incluir um contato real no User-Agent para evitar throttling
# mais agressivo em requisicoes anonimas. Troque o e-mail abaixo se quiser.
USER_AGENT = "BuscaImagensAgentesMedicos/1.0 (uso educacional; contato: jvolfe@proton.me)"

# Termos que denunciam formula/estrutura QUIMICA (do farmaco), nao foto real de embalagem
# nem diagrama de estrutura de VIRUS -- Commons e DailyMed misturam as duas coisas na
# mesma categoria/bula, e foi isso que trouxe "composicao molecular" em vez de foto da caixa.
EXCLUSAO_QUIMICA = [
    "structural formula", "skeletal formula", "chemical structure", "molecular structure",
    "stereochemistry", "chemical diagram", "2d structure", "3d structure", "molecule of",
    "ball-and-stick", "ball and stick", "space-filling", "space filling", "chemical formula",
    "structural diagram of", "xtal", "crystal structure", "wireframe", "conformer",
]

SENSITIVE_KEYWORDS = [
    "anogenital", "genital", "genitalia", "sexual", "vulvar",
    "vaginal", "peniano", "penis", "anal",
]
SENSITIVE_PATTERN = re.compile(r"\b(" + "|".join(SENSITIVE_KEYWORDS) + r")\b")

TIPOS_NECESSIDADE = ["categoria", "transmissao", "achado", "tratamento"]

# A busca de texto livre do Commons (usada antes) so casa palavras contra titulo/descricao
# de arquivo, entao frases descritivas longas quase nunca encontram nada. As categorias do
# Commons abaixo foram verificadas manualmente (existem e tem arquivos reais) e usadas como
# fonte primaria: dentro de uma categoria de doenca, os arquivos ja sao garantidamente sobre
# aquele assunto, e so precisamos escolher quais casam melhor com cada necessidade especifica.
# Chaves de agente devem bater exatamente com o campo "agente" do JSON.
CATEGORIAS_AGENTE = {
    "HSV-1 (Herpes Labial)": {"categoria": ["Herpesviridae"], "achado": ["Herpes labialis"]},
    "HSV-2 (Herpes Genital)": {"categoria": ["Herpesviridae"], "achado": []},  # sensivel, nao usado
    "VZV (Varicela-Zoster)": {"categoria": ["Herpesviridae"], "achado": ["Herpes zoster"]},
    "EBV (Mononucleose)": {"categoria": ["Herpesviridae"], "achado": ["Atypical lymphocytes", "Infectious mononucleosis"]},
    "CMV (Citomegalovirus)": {"categoria": ["Herpesviridae"], "achado": ["Cytomegalovirus"]},
    "HBV (Hepatite B)": {"categoria": ["Hepadnaviridae", "Hepatitis B virus"], "achado": ["Hepatitis B virus"]},
    "HPV": {"categoria": ["Papillomaviridae"], "achado": []},  # sensivel, nao usado
    "Adenovirus": {"categoria": ["Adenoviridae"], "achado": ["Conjunctivitis"]},
    "Poxvirus (Variola/Mpox)": {"categoria": ["Poxviridae"], "achado": ["Mpox"]},
    "Molusco Contagioso": {"categoria": ["Poxviridae"], "achado": ["Molluscum contagiosum"]},
    "Virus da Raiva": {"categoria": ["Rhabdoviridae"], "achado": ["Rabies"]},
    "Virus do Sarampo": {"categoria": ["Paramyxoviridae"], "achado": ["Measles"]},
    "Influenza A": {"categoria": ["Orthomyxoviridae", "Influenza A virus"], "achado": ["Influenza A virus", "Influenza"]},
    "Hantavirus": {"categoria": ["Bunyavirales", "Hantaviridae"], "achado": ["Hantaviridae"]},
    "HAV (Hepatite A)": {"categoria": ["Picornaviridae"], "achado": ["Hepatitis A"]},
    "HCV (Hepatite C)": {"categoria": ["Flaviviridae"], "achado": ["Hepatitis C"]},
    "HIV/Aids": {"categoria": ["Retroviridae"], "achado": ["Kaposi's sarcoma", "HIV"]},
    "Malassezia spp. (Pitiriase Versicolor)": {"categoria": ["Malassezia"], "achado": ["Malassezia"]},
    "Hortaea werneckii (Tinea Nigra)": {"categoria": ["Tinea nigra"], "achado": ["Tinea nigra"]},
    "Piedraia hortae (Piedra Negra)": {"categoria": ["Black piedra"], "achado": ["Black piedra"]},
    "Trichosporon spp. (Piedra Branca)": {"categoria": ["White piedra"], "achado": ["White piedra"]},
    "Dermatofitos (Trichophyton, Microsporum, Epidermophyton)": {"categoria": ["Dermatophytosis"], "achado": ["Tinea corporis"]},
    "Sporothrix spp. (Esporotricose)": {"categoria": ["Sporotrichosis"], "achado": ["Sporotrichosis"]},
    "Cromoblastomicose (Fonsecaea/Cladophialophora/Phialophora)": {"categoria": ["Chromoblastomycosis"], "achado": ["Chromoblastomycosis"]},
    "Eumicetomas (Madurella, Pseudallescheria, Acremonium)": {"categoria": ["Mycetomas"], "achado": ["Mycetomas"]},
    "Lacazia loboi (Lobomicose)": {"categoria": ["Lobomycosis"], "achado": ["Lobomycosis"]},
    "Paracoccidioides brasiliensis/lutzii (Paracoccidioidomicose)": {"categoria": ["Paracoccidioidomycosis"], "achado": ["Paracoccidioidomycosis"]},
    "Histoplasma capsulatum (Histoplasmose)": {"categoria": ["Histoplasmosis", "Histoplasma capsulatum"], "achado": ["Histoplasma capsulatum"]},
    "Coccidioides immitis/posadasii (Coccidioidomicose)": {"categoria": ["Coccidioidomycosis"], "achado": ["Coccidioidomycosis"]},
    "Blastomyces dermatitidis (Blastomicose)": {"categoria": ["Blastomycosis"], "achado": ["Blastomycosis"]},
    "Candida spp./albicans (Candidiase)": {"categoria": ["Candidiasis"], "achado": ["Oral candidiasis"]},
    "Cryptococcus neoformans/gattii (Criptococose)": {"categoria": ["Cryptococcus neoformans"], "achado": ["Cryptococcosis", "Cryptococcus neoformans"]},
    "Aspergillus spp. (Aspergilose)": {"categoria": ["Aspergillosis"], "achado": ["Aspergillosis"]},
    "Pneumocystis jirovecii (PCP)": {"categoria": ["Pneumocystis jirovecii"], "achado": ["Pneumocystis jirovecii"]},
}

# Categorias de farmaco/produto por id do catalogo_tratamentos (verificadas manualmente).
# IDs sem categoria confirmada ficam de fora e caem no fallback de busca por texto.
CATEGORIAS_TRATAMENTO = {
    "aciclovir": ["Aciclovir"],
    "amoxicilina_rash_alerta": ["Infectious mononucleosis"],
    "ganciclovir": ["Ganciclovir"],
    "tenofovir_entecavir": ["Tenofovir", "Entecavir"],
    "vacina_hpv": ["Gardasil"],
    "tecovirimat": ["Tecovirimat"],
    "vacina_soro_antirrabico": ["Rabies vaccines"],
    "vitamina_a": ["Vitamin A"],
    "oseltamivir": ["Oseltamivir", "Tamiflu"],
    "vacina_hepatite_a": ["Hepatitis A vaccines"],
    "sofosbuvir": ["Sofosbuvir"],
    "tarv": ["Antiretroviral drugs"],
    "antifungico_topico_generico": ["Clotrimazole"],
    "xampu_cetoconazol": ["Ketoconazole"],
    "itraconazol": ["Itraconazole"],
    "fluconazol": ["Fluconazole"],
    "voriconazol": ["Voriconazole"],
    # sem categoria confirmada no Commons -> usam so busca por texto:
    # hidratacao_suporte, crioterapia_lesao_cutanea, suporte_uti_ventilacao,
    # cirurgia_procedimento
}

# DailyMed (NLM/FDA) tem fotos reais de bula/embalagem por nome generico em ingles (EUA).
# Usado como fonte PRIMARIA de tratamento quando existe, antes do Commons -- e uma fonte
# muito mais limpa para "foto de caixa/frasco" do que categorias genericas do Commons.
DAILYMED_DRUGS = {
    "aciclovir": "acyclovir",
    "ganciclovir": "ganciclovir",
    "tenofovir_entecavir": "entecavir",
    "tecovirimat": "tecovirimat",
    "oseltamivir": "oseltamivir",
    "sofosbuvir": "sofosbuvir",
    "antifungico_topico_generico": "clotrimazole",
    "xampu_cetoconazol": "ketoconazole",
    "itraconazol": "itraconazole",
    "fluconazol": "fluconazole",
    "voriconazol": "voriconazole",
    "anfotericina_b": "amphotericin b",
    "anfotericina_b_flucitosina": "amphotericin b",
    "sulfametoxazol_trimetoprima": "sulfamethoxazole and trimethoprim",
}

# Palavras que aparecem nos termos_de_busca so para indicar "e uma foto/ilustracao" e nao
# ajudam a diferenciar um arquivo do outro dentro de uma categoria ja filtrada por doenca.
PALAVRAS_GENERICAS = {
    "illustration", "structure", "diagram", "photo", "photograph", "image", "picture",
    "clinical", "disease", "icon", "drawing", "view", "closeup", "close", "up", "the",
    "and", "or", "of", "in", "on", "with", "a", "an",
}


def normalizar(texto):
    if not texto:
        return ""
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    return sem_acento.lower()


def contem_conteudo_sensivel(observacao):
    return bool(SENSITIVE_PATTERN.search(normalizar(observacao)))


def slugify(texto, max_len=60):
    sem_acento = normalizar(texto)
    slug = re.sub(r"[^a-z0-9]+", "_", sem_acento).strip("_")
    return slug[:max_len] or "item"


def limpar_html(valor):
    if not valor:
        return ""
    sem_tags = re.sub(r"<[^>]+>", "", valor)
    return re.sub(r"\s+", " ", sem_tags).strip()


def carregar_json(caminho):
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


def montar_catalogo(dados):
    return {item["id"]: item for item in dados["catalogo_tratamentos"]}


def montar_necessidades(agente, catalogo):
    tratamento = catalogo[agente["tratamento_ref"]]
    necessidades = {
        "categoria": agente["categoria"],
        "transmissao": agente["transmissao"],
        "achado": agente["achado"],
        "tratamento": {
            "descricao": tratamento["nome"],
            "termos_de_busca": tratamento["termos_de_busca"],
        },
    }
    return necessidades


MIMES_IMAGEM_VALIDOS = ("image/jpeg", "image/png", "image/gif", "image/webp", "image/svg+xml", "image/tiff")


def esperar_backoff(erro, tentativa, pausa_base):
    retry_after = None
    if isinstance(erro, urllib.error.HTTPError):
        retry_after = erro.headers.get("Retry-After") if erro.headers else None
    if retry_after is not None:
        try:
            time.sleep(float(retry_after) + 1)
            return
        except ValueError:
            pass
    if isinstance(erro, urllib.error.HTTPError) and erro.code == 429:
        time.sleep(10 * (tentativa + 1))
    else:
        time.sleep(pausa_base * (tentativa + 1))


def requisitar_json(url, tentativas=4, pausa=2.0):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for tentativa in range(tentativas):
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                return json.load(resp)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            if tentativa == tentativas - 1:
                print(f"    [erro] requisicao falhou ({url[:80]}...): {e}")
                return None
            print(f"    [aviso] tentativa {tentativa + 1} falhou ({e}), aguardando antes de repetir...")
            esperar_backoff(e, tentativa, pausa)
    return None


def eh_estrutura_quimica(titulo):
    t = normalizar(titulo)
    if any(chave in t for chave in EXCLUSAO_QUIMICA):
        return True
    # convencao comum de nomenclatura (ex.: DailyMed usa "<farmaco>-str.jpg" para a
    # formula quimica) que nao bate com nenhuma frase da lista acima
    base = re.sub(r"\.[a-z0-9]+$", "", t)
    return bool(re.search(r"(^|[-_])str$", base))


def extrair_resultados(dados, termo_buscado):
    if not dados:
        return []
    paginas = dados.get("query", {}).get("pages", {})
    resultados = []
    for pagina in paginas.values():
        imageinfo = pagina.get("imageinfo")
        if not imageinfo:
            continue
        info = imageinfo[0]
        mime = info.get("mime", "")
        if mime not in MIMES_IMAGEM_VALIDOS:
            # descarta PDF/DjVu/etc. (paginas de livro escaneado, nao fotos/ilustracoes)
            continue
        if eh_estrutura_quimica(pagina.get("title", "")):
            continue
        extmeta = info.get("extmetadata", {})
        resultados.append({
            "termo_buscado": termo_buscado,
            "titulo": pagina.get("title", ""),
            "url_original": info.get("url", ""),
            "url_download": info.get("thumburl") or info.get("url", ""),
            "pagina_descricao": info.get("descriptionurl", ""),
            "mime": mime,
            "autor": limpar_html(extmeta.get("Artist", {}).get("value", "")) or "Nao informado",
            "licenca": extmeta.get("LicenseShortName", {}).get("value", "Nao informada"),
            "licenca_url": extmeta.get("LicenseUrl", {}).get("value", ""),
            "credito": limpar_html(extmeta.get("Credit", {}).get("value", "")),
        })
    return resultados


def buscar_imagens_wikimedia(termo, limite=3, largura_miniatura=1280):
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": termo,
        "gsrnamespace": 6,  # namespace File:
        "gsrlimit": limite,
        "prop": "imageinfo",
        "iiprop": "url|extmetadata|mime",
        "iiurlwidth": largura_miniatura,
        "format": "json",
    }
    url = COMMONS_API + "?" + urllib.parse.urlencode(params)
    return extrair_resultados(requisitar_json(url), termo)


def buscar_membros_categoria(categoria, limite_membros=40, largura_miniatura=1280):
    """Retorna os arquivos de uma categoria do Commons (curada por humanos, portanto ja
    garantidamente sobre o assunto da categoria) junto com licenca/autor via imageinfo."""
    params = {
        "action": "query",
        "generator": "categorymembers",
        "gcmtitle": f"Category:{categoria}",
        "gcmtype": "file",
        "gcmlimit": limite_membros,
        "prop": "imageinfo",
        "iiprop": "url|extmetadata|mime",
        "iiurlwidth": largura_miniatura,
        "format": "json",
    }
    url = COMMONS_API + "?" + urllib.parse.urlencode(params)
    return extrair_resultados(requisitar_json(url), f"[categoria:{categoria}]")


MIME_POR_EXTENSAO = {
    "png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "gif": "image/gif",
    "svg": "image/svg+xml", "webp": "image/webp", "tiff": "image/tiff", "tif": "image/tiff",
}


def buscar_openverse(termo, limite=3):
    """Amplia a busca para alem do Commons: Openverse agrega Flickr, museus e outras fontes
    CC, alem do proprio Commons -- ajuda quando o Commons sozinho nao tem boa cobertura."""
    params = {"q": termo, "license_type": "all-cc", "page_size": limite * 3}
    url = OPENVERSE_API + "?" + urllib.parse.urlencode(params)
    dados = requisitar_json(url)
    if not dados:
        return []
    resultados = []
    for item in dados.get("results", []):
        titulo = item.get("title") or item.get("id", "")
        if eh_estrutura_quimica(titulo):
            continue
        mime = MIME_POR_EXTENSAO.get((item.get("filetype") or "").lower(), "")
        licenca = (item.get("license", "") + " " + (item.get("license_version") or "")).strip().upper()
        resultados.append({
            "termo_buscado": f"[openverse] {termo}",
            "titulo": titulo,
            "url_original": item.get("url", ""),
            "url_download": item.get("thumbnail") or item.get("url", ""),
            "pagina_descricao": item.get("foreign_landing_url", ""),
            "mime": mime,
            "autor": item.get("creator") or "Nao informado",
            "licenca": licenca or "Nao informada",
            "licenca_url": item.get("license_url", ""),
            "credito": item.get("attribution", ""),
        })
        if len(resultados) >= limite:
            break
    return resultados


def buscar_dailymed(nome_generico, limite=3):
    """DailyMed (NLM/FDA) publica a bula oficial de medicamentos comercializados nos EUA,
    incluindo fotos reais de embalagem/rotulo -- fonte muito mais precisa para 'tratamento'
    do que categorias genericas do Commons (que misturam foto de caixa com estrutura quimica).
    Licenca nao e Creative Commons -- e documento regulatorio publico; sinalizado para
    revisao manual em vez de uma licenca assumida."""
    params = {"drug_name": nome_generico, "pagesize": 5}
    url = f"{DAILYMED_API}/spls.json?" + urllib.parse.urlencode(params)
    dados = requisitar_json(url)
    if not dados or not dados.get("data"):
        return []
    resultados = []
    for item in dados["data"][:3]:
        setid = item.get("setid")
        if not setid:
            continue
        media_url = f"{DAILYMED_API}/spls/{setid}/media.json"
        media_dados = requisitar_json(media_url)
        if not media_dados:
            continue
        for m in media_dados.get("data", {}).get("media", []):
            nome_arquivo = m.get("name", "")
            if eh_estrutura_quimica(nome_arquivo):
                continue
            resultados.append({
                "termo_buscado": f"[dailymed] {nome_generico}",
                "titulo": nome_arquivo,
                "url_original": m.get("url", ""),
                "url_download": m.get("url", ""),
                "pagina_descricao": f"https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid={setid}",
                "mime": m.get("mime_type", "image/jpeg"),
                "autor": "Fabricante (bula regulatoria)",
                "licenca": "Documento regulatorio publico (FDA/NLM) - confirmar uso antes de publicar",
                "licenca_url": "",
                "credito": item.get("title", ""),
            })
            if len(resultados) >= limite:
                return resultados
        time.sleep(0.3)
    return resultados


def palavras_significativas(texto):
    palavras = re.findall(r"[a-zA-Z']+", normalizar(texto))
    return [p for p in palavras if len(p) > 2 and p not in PALAVRAS_GENERICAS]


def pontuar_titulo(titulo, termos, palavras_excluidas=frozenset()):
    """Pontua pela quantidade de palavras significativas dos termos_de_busca que aparecem
    no titulo do arquivo. 'palavras_excluidas' deve conter as palavras do proprio nome da
    categoria (ex.: 'infectious', 'mononucleosis'): como TODO arquivo da categoria ja tem
    essas palavras no titulo, contá-las so infla a pontuacao de forma identica para todo
    mundo e cria empates que escondem o arquivo realmente especifico (ex.: uma foto de rash
    empatando com uma foto de esfregaco de sangue so por ambas citarem 'mononucleosis')."""
    titulo_norm = normalizar(titulo)
    palavras_titulo = set(re.findall(r"[a-zA-Z']+", titulo_norm))
    pontos = 0
    for termo in termos:
        for palavra in palavras_significativas(termo):
            if palavra in palavras_excluidas:
                continue
            if palavra in palavras_titulo:
                pontos += 1
    return pontos


def buscar_por_texto_com_fallback(termos, limite=3):
    """Ultimo recurso: busca de texto livre no Commons. Tenta a frase inteira restrita a
    bitmap; se vazio, tenta sem filtro; se ainda vazio, vai cortando a ultima palavra da
    frase (perde precisao a cada corte) ate achar algo ou sobrar so 2 palavras."""
    vistos = set()
    resultados = []
    for termo in termos:
        if len(resultados) >= limite:
            break
        palavras = termo.split()
        while palavras:
            variacao = " ".join(palavras)
            for consulta in (f"{variacao} filetype:bitmap", variacao):
                if len(resultados) >= limite:
                    break
                for item in buscar_imagens_wikimedia(consulta, limite=limite):
                    if item["titulo"] in vistos:
                        continue
                    vistos.add(item["titulo"])
                    item["correspondencia_exata"] = (variacao == termo)
                    resultados.append(item)
                    if len(resultados) >= limite:
                        break
                time.sleep(0.8)
            if len(resultados) >= limite or len(palavras) <= 2:
                break
            palavras = palavras[:-1]
    return resultados[:limite]


def mimes_proibidos_para(tipo, disciplina):
    """Regra rigida (nao heuristica): desenho vetorial (SVG) nunca serve como evidencia real
    em achado/tratamento -- esses precisam ser foto/microgafia de verdade, nunca um esquema."""
    if tipo in ("achado", "tratamento"):
        return {"image/svg+xml"}
    return set()


def resolver_candidatos(termos, categorias, limite=3, permitir_generico=True, tipo=None, disciplina=None):
    """Estrategia de busca em camadas, da mais para a menos confiavel:
    1) categorias do Commons verificadas manualmente, rankeadas por quantas palavras dos
       termos_de_busca aparecem no titulo do arquivo (garante que e sobre a doenca certa;
       a pontuacao so escolhe qual foto da categoria bate melhor com a necessidade especifica);
    2) busca de texto livre (com filtro de bitmap e corte progressivo) para o que faltar;
    3) so se 'permitir_generico', preenche o resto com arquivos da categoria que nao pontuaram
       (ainda sao sobre a doenca certa, so nao confirmadamente sobre o aspecto especifico) -
       usado para categoria/achado/tratamento, mas NAO para transmissao (uma foto generica da
       doenca rotulada como "transmissao" seria enganosa)."""
    proibidos = mimes_proibidos_para(tipo, disciplina)
    vistos = set()
    escolhidos = []
    sobras_genericas = []

    for categoria in categorias:
        membros = [m for m in buscar_membros_categoria(categoria) if m["mime"] not in proibidos]
        pontuados = [(pontuar_titulo(m["titulo"], termos), m) for m in membros if m["titulo"] not in vistos]
        pontuados.sort(key=lambda par: par[0], reverse=True)
        for pontos, item in pontuados:
            if item["titulo"] in vistos:
                continue
            item["fonte"] = f"categoria_commons:{categoria}"
            item["correspondencia_generica"] = pontos == 0
            item["termo_buscado"] = f"[categoria:{categoria}] pontos={pontos}"
            if pontos > 0 and len(escolhidos) < limite:
                vistos.add(item["titulo"])
                escolhidos.append(item)
            elif pontos == 0:
                sobras_genericas.append(item)
        time.sleep(0.5)
        if len(escolhidos) >= limite:
            break

    if len(escolhidos) < limite:
        for item in buscar_openverse(termos[0], limite=limite - len(escolhidos)):
            if item["titulo"] in vistos or item["mime"] in proibidos:
                continue
            item["fonte"] = "openverse"
            item["correspondencia_generica"] = False
            vistos.add(item["titulo"])
            escolhidos.append(item)
        time.sleep(0.3)

    if len(escolhidos) < limite:
        for item in buscar_por_texto_com_fallback(termos, limite=limite - len(escolhidos)):
            if item["titulo"] in vistos:
                continue
            item["fonte"] = "busca_texto"
            item["correspondencia_generica"] = False
            vistos.add(item["titulo"])
            escolhidos.append(item)

    if permitir_generico and len(escolhidos) < limite:
        for item in sobras_genericas:
            if len(escolhidos) >= limite:
                break
            if item["titulo"] in vistos:
                continue
            vistos.add(item["titulo"])
            escolhidos.append(item)

    return escolhidos[:limite]


def baixar_arquivo(url, destino, tentativas=4, pausa=2.0):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for tentativa in range(tentativas):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                conteudo = resp.read()
            destino.write_bytes(conteudo)
            return True
        except (urllib.error.URLError, TimeoutError) as e:
            if tentativa == tentativas - 1:
                print(f"    [erro] download falhou ({url[:80]}...): {e}")
                return False
            print(f"    [aviso] download tentativa {tentativa + 1} falhou ({e}), aguardando antes de repetir...")
            esperar_backoff(e, tentativa, pausa)
    return False


MIME_PARA_EXTENSAO = {v: f".{k}" for k, v in MIME_POR_EXTENSAO.items() if k in ("png", "jpeg", "gif", "svg", "webp", "tiff")}
MIME_PARA_EXTENSAO["image/jpeg"] = ".jpg"


def parece_desenho_linha(caminho, limiar=0.92):
    """Formula quimica e pictograma de instrucao (ex.: 'engula o comprimido assim') sao
    quase sempre desenho de linha preto sobre fundo branco -- muito diferente de uma foto
    real de embalagem/comprimido, que tem cor. Filtro por nome de arquivo nao pega tudo
    (algumas bulas usam nomes tipo UUID sem nenhuma palavra-chave), entao aqui a gente
    abre o arquivo de verdade e mede a fracao de pixels sem saturacao de cor."""
    try:
        from PIL import Image
    except ImportError:
        return False
    try:
        with Image.open(caminho) as img:
            img = img.convert("RGB")
            img.thumbnail((80, 80))
            pixels = list(img.getdata())
    except Exception:
        return False
    if not pixels:
        return False
    sem_cor = sum(1 for r, g, b in pixels if max(r, g, b) - min(r, g, b) < 12)
    return (sem_cor / len(pixels)) > limiar


def nome_arquivo_local(indice, titulo, url_download, mime=""):
    nome = titulo.split(":", 1)[-1] if ":" in titulo else titulo
    base = slugify(Path(nome).stem, max_len=50)
    # prioridade pra extensao: MIME informado pela API (mais confiavel) > sufixo do path
    # da URL de download > sufixo do titulo. URLs tipo "image.cfm?...&name=foo.jpg" tem
    # a extensao real na query string, nao no path, entao nao dá pra confiar so na URL.
    # Excecao: o Commons SEMPRE serve a miniatura (thumburl, que e o que baixamos) de um
    # SVG como PNG rasterizado -- nunca manda o SVG original quando pedimos iiurlwidth.
    # Se usar ".svg" aqui o arquivo salvo fica com extensao errada (bytes de PNG).
    if mime == "image/svg+xml":
        extensao = ".png"
    else:
        extensao = MIME_PARA_EXTENSAO.get(mime, "")
    if not extensao:
        caminho_url = urllib.parse.urlparse(url_download).path
        sufixo_path = Path(caminho_url).suffix
        extensao = sufixo_path if sufixo_path in MIME_PARA_EXTENSAO.values() else (Path(nome).suffix or ".jpg")
    return f"{indice:02d}_{base}{extensao}"


def url_busca_cdc_phil(termo):
    return "https://phil.cdc.gov/Quicksearch.aspx?query=" + urllib.parse.quote(termo)


def url_busca_dermnet(termo):
    # DermNet NZ nao tem um endpoint de busca por query string confirmado e estavel;
    # usa-se busca do Google restrita ao site, que sempre funciona independente da
    # implementacao interna de busca do DermNet.
    consulta = f"site:dermnetnz.org {termo}"
    return "https://www.google.com/search?q=" + urllib.parse.quote(consulta)


def categorias_para_necessidade(tipo, nome_agente, tratamento_ref):
    info_agente = CATEGORIAS_AGENTE.get(nome_agente, {})
    if tipo == "categoria":
        return info_agente.get("categoria", []), True
    if tipo == "achado":
        return info_agente.get("achado", []), True
    if tipo == "transmissao":
        # reaproveita a categoria de achado (mesma doenca) como fonte extra, mas sem
        # preencher com sobra generica: uma foto qualquer da doenca rotulada como
        # "transmissao" sem nenhuma palavra-chave batendo seria enganosa.
        return info_agente.get("achado", []), False
    if tipo == "tratamento":
        return CATEGORIAS_TRATAMENTO.get(tratamento_ref, []), True
    return [], True


def processar_agente(agente, catalogo, pasta_saida, dry_run, delay):
    ordem = agente["ordem"]
    nome_agente = agente["agente"]
    pasta_agente = pasta_saida / f"{ordem:02d}_{slugify(nome_agente)}"
    manifest_path = pasta_agente / "manifest.json"

    observacao = agente.get("observacao", "")
    sensivel = contem_conteudo_sensivel(observacao)
    necessidades = montar_necessidades(agente, catalogo)

    manifest = {
        "ordem": ordem,
        "disciplina": agente.get("disciplina", ""),
        "agente": nome_agente,
        "observacao": observacao,
        "conteudo_sensivel_pulado": sensivel,
        "tratamento_ref": agente["tratamento_ref"],
        "imagens": {},
    }

    entradas_relatorio_bancos = []
    entrada_sensivel = None

    if sensivel:
        print(f"  [sensivel] '{nome_agente}' - observacao: {observacao!r} -> pulando download automatico")
        entrada_sensivel = {
            "ordem": ordem,
            "agente": nome_agente,
            "observacao": observacao,
            "necessidades": {
                tipo: {
                    "descricao": necessidades[tipo]["descricao"],
                    "termos_de_busca": necessidades[tipo]["termos_de_busca"],
                }
                for tipo in TIPOS_NECESSIDADE
            },
        }
        for tipo in TIPOS_NECESSIDADE:
            termo_principal = necessidades[tipo]["termos_de_busca"][0]
            entradas_relatorio_bancos.append({
                "ordem": ordem, "agente": nome_agente, "tipo": tipo,
                "termo": termo_principal,
                "cdc_phil": url_busca_cdc_phil(termo_principal),
                "dermnet": url_busca_dermnet(termo_principal),
            })
        pasta_agente.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        return entradas_relatorio_bancos, entrada_sensivel

    for tipo in TIPOS_NECESSIDADE:
        necessidade = necessidades[tipo]
        termos = necessidade["termos_de_busca"]
        termo_principal = termos[0]
        print(f"  [{tipo}] buscando: {termo_principal!r}")

        entradas_relatorio_bancos.append({
            "ordem": ordem, "agente": nome_agente, "tipo": tipo,
            "termo": termo_principal,
            "cdc_phil": url_busca_cdc_phil(termo_principal),
            "dermnet": url_busca_dermnet(termo_principal),
        })

        disciplina = agente.get("disciplina", "")
        proibidos = mimes_proibidos_para(tipo, disciplina)
        # achado/tratamento exigem foto real (nunca desenho/formula): pede um pool maior
        # do que o desejado, porque o filtro de desenho de linha (por pixel, depois do
        # download) vai descartar alguns e precisa de reserva para completar a conta.
        desejadas = 5
        pool_alvo = 10 if tipo in ("achado", "tratamento") else desejadas
        candidatos = []
        if tipo == "tratamento" and agente["tratamento_ref"] in DAILYMED_DRUGS:
            nome_farmaco = DAILYMED_DRUGS[agente["tratamento_ref"]]
            print(f"    tentando DailyMed (bula oficial): {nome_farmaco!r}")
            for item in buscar_dailymed(nome_farmaco, limite=pool_alvo):
                if item["mime"] in proibidos:
                    continue
                item["fonte"] = "dailymed"
                item["correspondencia_generica"] = False
                candidatos.append(item)

        categorias = []
        if len(candidatos) < pool_alvo:
            categorias, permitir_generico = categorias_para_necessidade(tipo, nome_agente, agente["tratamento_ref"])
            candidatos += resolver_candidatos(
                termos, categorias, limite=pool_alvo - len(candidatos), permitir_generico=permitir_generico,
                tipo=tipo, disciplina=disciplina,
            )
        if not candidatos:
            print(f"    nenhum resultado encontrado (categorias: {categorias or 'nenhuma cadastrada'})")
            manifest["imagens"][tipo] = []
            continue
        fontes = ", ".join(sorted({c.get("fonte", "?") for c in candidatos}))
        print(f"    {len(candidatos)} candidato(s) via: {fontes}")

        subpasta = pasta_agente / tipo
        entradas_manifest = []
        exige_foto_real = tipo in ("achado", "tratamento")
        indice = 0
        for item in candidatos:
            if len(entradas_manifest) >= desejadas:
                break
            indice += 1
            nome_arquivo = nome_arquivo_local(indice, item["titulo"], item["url_download"], item.get("mime", ""))
            caminho_local = subpasta / nome_arquivo
            baixado = False
            if not dry_run:
                subpasta.mkdir(parents=True, exist_ok=True)
                baixado = baixar_arquivo(item["url_download"], caminho_local)
                if baixado and exige_foto_real and parece_desenho_linha(caminho_local):
                    print(f"    [descartado] {item['titulo']!r} parece desenho/formula, nao foto real")
                    caminho_local.unlink(missing_ok=True)
                    baixado = False
                    indice -= 1
                    time.sleep(delay)
                    continue
                time.sleep(delay)

            entradas_manifest.append({
                "arquivo_local": str(caminho_local.relative_to(pasta_saida)) if baixado else None,
                "fonte": item.get("fonte", "busca_texto"),
                "correspondencia_generica": item.get("correspondencia_generica", False),
                "correspondencia_exata": item.get("correspondencia_exata"),
                "termo_buscado": item["termo_buscado"],
                "titulo_wikimedia": item["titulo"],
                "pagina_descricao": item["pagina_descricao"],
                "url_original": item["url_original"],
                "licenca": item["licenca"],
                "licenca_url": item["licenca_url"],
                "autor": item["autor"],
                "credito": item["credito"],
                "baixado": baixado,
            })
        manifest["imagens"][tipo] = entradas_manifest

    pasta_agente.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  manifest salvo em {manifest_path.relative_to(pasta_saida.parent)}")
    return entradas_relatorio_bancos, entrada_sensivel


def escrever_relatorio_bancos_manuais(caminho, entradas):
    linhas = [
        "# Bancos sem API confirmada - busca manual",
        "",
        "CDC PHIL e DermNet nao foram consultados automaticamente (sem API oficial confirmada).",
        "Abra os links abaixo manualmente para revisar candidatos nesses bancos.",
        "",
    ]
    agente_atual = None
    for e in entradas:
        if e["agente"] != agente_atual:
            agente_atual = e["agente"]
            linhas.append(f"\n## {e['ordem']:02d}. {agente_atual}")
        linhas.append(f"\n### {e['tipo']} - \"{e['termo']}\"")
        linhas.append(f"- CDC PHIL: {e['cdc_phil']}")
        linhas.append(f"- DermNet (via Google): {e['dermnet']}")
    caminho.write_text("\n".join(linhas) + "\n", encoding="utf-8")


def escrever_relatorio_sensiveis(caminho, entradas):
    if not entradas:
        caminho.write_text(
            "# Revisao manual - conteudo sensivel\n\nNenhum agente foi sinalizado como sensivel.\n",
            encoding="utf-8",
        )
        return
    linhas = [
        "# Revisao manual - conteudo sensivel",
        "",
        "Estes agentes tem campo 'observacao' mencionando conteudo sensivel (ex: anogenital).",
        "Nenhuma imagem foi baixada automaticamente. Busque manualmente pelos termos abaixo.",
        "",
    ]
    for e in entradas:
        linhas.append(f"\n## {e['ordem']:02d}. {e['agente']}")
        linhas.append(f"Observacao: {e['observacao']}")
        for tipo in TIPOS_NECESSIDADE:
            n = e["necessidades"][tipo]
            linhas.append(f"\n**{tipo}** - {n['descricao']}")
            for termo in n["termos_de_busca"]:
                linhas.append(f"- {termo}")
    caminho.write_text("\n".join(linhas) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Busca e baixa imagens candidatas para a fila de agentes.")
    parser.add_argument("--json", default=str(JSON_PATH_PADRAO), help="Caminho do fila-busca-imagens-agentes.json")
    parser.add_argument("--output", default=str(SAIDA_PADRAO), help="Pasta de saida")
    parser.add_argument("--dry-run", action="store_true", help="So busca e gera relatorios, nao baixa nada")
    parser.add_argument("--limit", type=int, default=None, help="Processa so os N primeiros agentes")
    parser.add_argument("--only", default=None, help="So processa agentes cujo nome contenha este texto")
    parser.add_argument("--force", action="store_true", help="Reprocessa agentes que ja tem manifest.json")
    parser.add_argument("--delay", type=float, default=1.0, help="Pausa (s) entre downloads (padrao: 1.0)")
    args = parser.parse_args()

    dados = carregar_json(args.json)
    catalogo = montar_catalogo(dados)
    fila = dados["fila_de_busca"]

    if args.only:
        fila = [a for a in fila if args.only.lower() in a["agente"].lower()]
    if args.limit:
        fila = fila[: args.limit]

    pasta_saida = Path(args.output)
    pasta_relatorios = pasta_saida / "_relatorios"
    pasta_saida.mkdir(parents=True, exist_ok=True)
    pasta_relatorios.mkdir(parents=True, exist_ok=True)

    todas_entradas_bancos = []
    todas_entradas_sensiveis = []

    for agente in fila:
        ordem = agente["ordem"]
        nome_agente = agente["agente"]
        pasta_agente = pasta_saida / f"{ordem:02d}_{slugify(nome_agente)}"
        manifest_existente = pasta_agente / "manifest.json"
        if manifest_existente.exists() and not args.force:
            print(f"[{ordem:02d}] '{nome_agente}' ja processado, pulando (use --force para refazer)")
            continue

        print(f"[{ordem:02d}] {nome_agente}")
        entradas_bancos, entrada_sensivel = processar_agente(
            agente, catalogo, pasta_saida, dry_run=args.dry_run, delay=args.delay
        )
        todas_entradas_bancos.extend(entradas_bancos)
        if entrada_sensivel:
            todas_entradas_sensiveis.append(entrada_sensivel)

    escrever_relatorio_bancos_manuais(pasta_relatorios / "bancos_manuais.md", todas_entradas_bancos)
    escrever_relatorio_sensiveis(pasta_relatorios / "revisao_manual_sensivel.md", todas_entradas_sensiveis)

    print(f"\nConcluido. Relatorios em {pasta_relatorios}")


if __name__ == "__main__":
    main()
