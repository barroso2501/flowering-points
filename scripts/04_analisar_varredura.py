"""
04_analisar_varredura.py
Analisa as saídas do script 03 (varredura por pixel nas AOIs) em três etapas,
que podem ser rodadas em momentos diferentes:

  ETAPA 1 (logo após o export do GEE):
    - densidade de objetos detectados por 100 ha: evento × placebo
      (placebo = falso positivo por área, a métrica que faltava na D6);
    - fração dos pontos já registrados (mesma data e cor) que foram detectados;
    - amostra CEGA para validação visual: detecções do evento misturadas com
      pontos aleatórios (controles), com códigos anônimos, em KML + planilha.

  ETAPA 2 (depois que você preencher a planilha de validação):
    - precisão = fração das detecções conferidas que eram de fato copa florida;
    - taxa de "flor" nos controles aleatórios (mede o viés do observador e a
      densidade de base de copas floridas).

  ETAPA 3 (depois do censo das subparcelas):
    - sensibilidade (recall) = fração das copas do censo com detecção a ≤ d m;
    - precisão dentro das subparcelas;
    - as mesmas métricas com as detecções do PLACEBO: é o nível do acaso
      (quanto uma detecção aleatória, na mesma densidade, "acerta" copas);
    - d = 10, 20 e 30 m (sensibilidade à distância de casamento, D10).
    Subparcelas sem copas e sem detecções são mantidas (resultado válido).

Uso:
  Etapa 1:
    python scripts/04_analisar_varredura.py etapa1 \
        --deteccoes data/gee_exports/aoi_deteccoes_v1.csv \
        --resumo    data/gee_exports/aoi_resumo_v1.csv \
        --pontos    data/gee_exports/aoi_pontos_v1.csv \
        --aois      data/aoi/aois_v1.geojson
  Etapa 2:
    python scripts/04_analisar_varredura.py etapa2 \
        --validacao results/aoi_v1/validacao_preenchida.csv \
        --chave     results/aoi_v1/_chave_amostra_NAO_ABRIR.csv
  Etapa 3:
    python scripts/04_analisar_varredura.py etapa3 \
        --deteccoes data/gee_exports/aoi_deteccoes_v1.csv \
        --subparcelas data/aoi/subparcelas_censo_v1.kml \
        --censo data/censo/censo_v1.kml \
        --registro data/censo/censo_v1_registro.csv

Saídas em results/aoi_v1/. Requisitos: pandas, numpy, shapely.
"""
import argparse, json, hashlib, platform, re
import xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import pandas as pd
from shapely.geometry import shape, Point, Polygon

VERSAO = "1.1"
SAIDA = Path("results/aoi_v1")
LIMIAR_Z = 3            # o mesmo do script 03
N_DETEC_AMOSTRA = 30    # detecções do evento por AOI × índice na amostra cega
N_CONTROLES = 15        # pontos aleatórios por AOI × índice na amostra cega
DIST_MATCH = 20         # m: distância principal entre copa do censo e detecção
DISTANCIAS = (10, 20, 30)  # m: sensibilidade da métrica à distância (D10)
SEMENTE = 42
COR_DO_INDICE = {"IRS": "rosa", "NDYI": "amarelo"}


def md5(caminho):
    return hashlib.md5(Path(caminho).read_bytes()).hexdigest()


def registrar_log(nome, entradas, extra=None):
    """Proveniência: hashes das entradas, parâmetros e versões."""
    log = dict(versao_script=VERSAO, etapa=nome,
               entradas={k: dict(caminho=v, md5=md5(v)) for k, v in entradas.items() if v},
               parametros=dict(LIMIAR_Z=LIMIAR_Z, N_DETEC_AMOSTRA=N_DETEC_AMOSTRA,
                               N_CONTROLES=N_CONTROLES, DIST_MATCH=DIST_MATCH, SEMENTE=SEMENTE),
               python=platform.python_version(), pandas=pd.__version__, numpy=np.__version__)
    if extra:
        log.update(extra)
    (SAIDA / f"log_{nome}.json").write_text(json.dumps(log, indent=2, ensure_ascii=False))


def dist_m(lon1, lat1, lon2, lat2):
    """Distância aproximada em metros (haversine); suficiente para dezenas de metros."""
    lon1, lat1, lon2, lat2 = map(np.radians, (lon1, lat1, lon2, lat2))
    a = (np.sin((lat2 - lat1) / 2) ** 2
         + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2)
    return 6371000 * 2 * np.arcsin(np.sqrt(a))


# ------------------------------- KML ----------------------------------------
def _tag(e):
    return e.tag.split("}")[-1]


def ler_kml(caminho):
    """Lê Placemarks de um KML (pontos ou polígonos). Retorna lista de dicts
    com nome, dados estendidos e geometria shapely."""
    raiz = ET.parse(caminho).getroot()
    itens = []
    for pm in raiz.iter():
        if _tag(pm) != "Placemark":
            continue
        nome, dados, geom = "", {}, None
        for e in pm.iter():
            t = _tag(e)
            if t == "name" and not nome:
                nome = (e.text or "").strip()
            elif t in ("Data", "SimpleData"):
                chave = e.get("name")
                val = e.text if t == "SimpleData" else next(
                    (x.text for x in e if _tag(x) == "value"), None)
                dados[chave] = (val or "").strip()
            elif t == "coordinates" and geom is None:
                xy = [tuple(map(float, c.split(",")[:2])) for c in (e.text or "").split()]
                geom = Point(xy[0]) if len(xy) == 1 else Polygon(xy)
        itens.append(dict(nome=nome, dados=dados, geom=geom))
    return itens


def escrever_kml(df, caminho, titulo):
    """KML de pontos com nome = código anônimo e a data da imagem a conferir."""
    pms = []
    for _, r in df.iterrows():
        pms.append(f"""  <Placemark><name>{r.codigo}</name>
    <description>Conferir na imagem de {r.data_aoi}: há copa florida ({r.cor_alvo}) a até ~15 m? Responder na planilha.</description>
    <Point><coordinates>{r.lon:.7f},{r.lat:.7f},0</coordinates></Point></Placemark>""")
    Path(caminho).write_text(f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2"><Document><name>{titulo}</name>
{chr(10).join(pms)}
</Document></kml>
""", encoding="utf-8")


# ------------------------------ ETAPA 1 -------------------------------------
def pontos_aleatorios(poligono, n, rng):
    """n pontos uniformes dentro do polígono (amostragem por rejeição)."""
    minx, miny, maxx, maxy = poligono.bounds
    out = []
    while len(out) < n:
        x, y = rng.uniform(minx, maxx), rng.uniform(miny, maxy)
        if poligono.contains(Point(x, y)):
            out.append((x, y))
    return out


def etapa1(a):
    det = pd.read_csv(a.deteccoes)
    res = pd.read_csv(a.resumo)
    pts = pd.read_csv(a.pontos)
    aois = {f["properties"]["aoi_id"]: f for f in json.load(open(a.aois))["features"]}

    # (1) Densidade de objetos por 100 ha: evento × placebo.
    n = (det.groupby(["aoi_id", "indice", "tipo"]).size()
            .unstack("tipo", fill_value=0).reindex(columns=["evento", "placebo"], fill_value=0)
            .reset_index())
    dens = res.merge(n, on=["aoi_id", "indice"], how="left").fillna({"evento": 0, "placebo": 0})
    dens["obj_100ha_evento"] = 100 * dens.evento / dens.area_avaliavel_evento_ha
    dens["obj_100ha_placebo"] = 100 * dens.placebo / dens.area_avaliavel_placebo_ha
    dens["razao_evento_placebo"] = dens.obj_100ha_evento / dens.obj_100ha_placebo.replace(0, np.nan)
    # Excesso = detecções acima do nível de falso positivo (limite inferior
    # grosseiro de manchas floridas detectáveis; assume FP igual nas duas datas).
    dens["excesso_100ha"] = dens.obj_100ha_evento - dens.obj_100ha_placebo
    dens.to_csv(SAIDA / "densidade_deteccoes.csv", index=False)

    # (2) Pontos já registrados: só os da MESMA data da AOI e da cor do índice.
    pts["cor_indice"] = pts.indice.map(COR_DO_INDICE)
    ok = pts[(pts.data_evento == pts.data_aoi) & (pts.classe_flor == pts.cor_indice)].copy()
    rec = (ok.assign(det_evento=ok.z_evento > LIMIAR_Z, det_placebo=ok.z_placebo > LIMIAR_Z)
             .groupby(["aoi_id", "indice"])
             .agg(n_pontos=("evento_id", "size"), frac_det_evento=("det_evento", "mean"),
                  frac_det_placebo=("det_placebo", "mean"), z_mediano=("z_evento", "median"))
             .reset_index())
    rec.to_csv(SAIDA / "deteccao_pontos_registrados.csv", index=False)

    # (3) Amostra cega: detecções do evento + controles aleatórios, embaralhados.
    rng = np.random.default_rng(SEMENTE)
    linhas = []
    for (aoi_id, idx), g in det[det.tipo == "evento"].groupby(["aoi_id", "indice"]):
        s = g.sample(min(N_DETEC_AMOSTRA, len(g)), random_state=SEMENTE)
        for _, r in s.iterrows():
            linhas.append(dict(aoi_id=aoi_id, indice=idx, data_aoi=r.data_aoi, lon=r.lon,
                               lat=r.lat, tipo_amostra="deteccao", z_max=r.z_max))
        pol = shape(aois[aoi_id]["geometry"])
        for x, y in pontos_aleatorios(pol, N_CONTROLES, rng):
            linhas.append(dict(aoi_id=aoi_id, indice=idx, data_aoi=g.data_aoi.iloc[0], lon=x,
                               lat=y, tipo_amostra="controle", z_max=np.nan))
    am = pd.DataFrame(linhas).sample(frac=1, random_state=SEMENTE).reset_index(drop=True)
    am["codigo"] = [f"V{i+1:03d}" for i in range(len(am))]
    am["cor_alvo"] = am.indice.map(COR_DO_INDICE)
    # Chave (tipo e z) separada da planilha: abrir só depois da validação.
    am.to_csv(SAIDA / "_chave_amostra_NAO_ABRIR.csv", index=False)
    plan = am[["codigo", "aoi_id", "data_aoi", "cor_alvo", "lon", "lat"]].copy()
    plan["resposta"] = ""      # sim / nao / incerto / sem_imagem
    plan["observacao"] = ""
    plan.to_csv(SAIDA / "validacao_template.csv", index=False)
    escrever_kml(am, SAIDA / "validacao_amostra_cega.kml", "Validação cega v1")

    registrar_log("etapa1", dict(deteccoes=a.deteccoes, resumo=a.resumo, pontos=a.pontos,
                                 aois=a.aois), dict(n_amostra=len(am)))
    print(dens.round(2).to_string(index=False)); print(); print(rec.round(2).to_string(index=False))


# ------------------------------ ETAPA 2 -------------------------------------
def etapa2(a):
    val = pd.read_csv(a.validacao)
    chave = pd.read_csv(a.chave)
    m = chave.merge(val[["codigo", "resposta"]], on="codigo")
    m["resposta"] = m.resposta.str.strip().str.lower()
    validas = m[m.resposta.isin(["sim", "nao"])]
    out = (validas.assign(flor=validas.resposta == "sim")
                  .groupby(["aoi_id", "indice", "tipo_amostra"])
                  .agg(n=("codigo", "size"), frac_flor=("flor", "mean")).reset_index()
                  .pivot_table(index=["aoi_id", "indice"], columns="tipo_amostra",
                               values=["n", "frac_flor"]))
    out.columns = [f"{a_}_{b}" for a_, b in out.columns]
    out = out.reset_index().rename(columns={"frac_flor_deteccao": "precisao",
                                            "frac_flor_controle": "taxa_flor_controles"})
    out.to_csv(SAIDA / "precisao_validacao.csv", index=False)
    resumo_resp = m.groupby(["tipo_amostra", "resposta"]).size().unstack(fill_value=0)
    resumo_resp.to_csv(SAIDA / "respostas_validacao.csv")
    registrar_log("etapa2", dict(validacao=a.validacao, chave=a.chave))
    print(out.round(2).to_string(index=False)); print(); print(resumo_resp)


# ------------------------------ ETAPA 3 -------------------------------------
def _casar(c, d, dist):
    """Para copas c e detecções d: quais copas têm detecção a <= dist m e quais
    detecções têm copa a <= dist m."""
    if len(c) == 0 or len(d) == 0:
        return np.zeros(len(c), bool), np.zeros(len(d), bool)
    D = dist_m(c.lon.values[:, None], c.lat.values[:, None],
               d.lon.values[None, :], d.lat.values[None, :])
    return (D <= dist).any(axis=1), (D <= dist).any(axis=0)


def etapa3(a):
    det_all = pd.read_csv(a.deteccoes)
    subs = [s for s in ler_kml(a.subparcelas) if s["geom"] is not None
            and not isinstance(s["geom"], Point)]
    copas = [c for c in ler_kml(a.censo) if isinstance(c["geom"], Point)]
    reg = pd.read_csv(a.registro) if a.registro else None
    # Cor da copa pelo nome: "r" (rosa) ou "a" (amarelo); "?" = incerta
    # (fora do cálculo principal); "+" = grupo (conta como uma copa).
    cz = pd.DataFrame([dict(lon=c["geom"].x, lat=c["geom"].y, nome=c["nome"]) for c in copas])
    nm = cz.nome.str.strip().str.lower()
    cz["cor"] = np.where(nm.str.startswith("r"), "rosa",
                np.where(nm.str.startswith("a"), "amarelo", "outra"))
    cz["incerta"] = nm.str.contains(r"\?")
    cz["subparcela"] = "FORA"
    for s in subs:
        nome = s["dados"].get("subparcela", s["nome"])
        dentro = [s["geom"].contains(Point(x, y)) for x, y in zip(cz.lon, cz.lat)]
        cz.loc[dentro, "subparcela"] = nome
    cz.to_csv(SAIDA / "censo_copas_atribuidas.csv", index=False)

    linhas = []
    for s in subs:
        nome = s["dados"].get("subparcela", s["nome"])
        aoi_id = s["dados"].get("aoi_id", nome.split("_")[0])
        pol = s["geom"]
        area_ha = abs(_area_ha(pol))
        cs = cz[cz.subparcela == nome]
        for idx, cor in COR_DO_INDICE.items():
            dd = det_all[(det_all.aoi_id == aoi_id) & (det_all.indice == idx)]
            if len(dd) == 0 and not ((det_all.aoi_id == aoi_id) & (det_all.indice == idx)).any():
                # índice não varrido nesta AOI (ex.: NDYI na AOI10)
                if len(cs[cs.cor == cor]) == 0:
                    continue
            dd = dd[[pol.contains(Point(x, y)) for x, y in zip(dd.lon, dd.lat)]]
            c = cs[(cs.cor == cor) & ~cs.incerta]
            for tipo in ("evento", "placebo"):
                d = dd[dd.tipo == tipo]
                for dist in DISTANCIAS:
                    copa_det, det_ok = _casar(c, d, dist)
                    linhas.append(dict(
                        subparcela=nome, aoi_id=aoi_id, estrato=s["dados"].get("estrato", ""),
                        indice=idx, tipo_deteccao=tipo, dist_m=dist, area_ha=area_ha,
                        n_copas_censo=len(c),
                        n_copas_incertas=int(((cs.cor == cor) & cs.incerta).sum()),
                        n_deteccoes=len(d),
                        deteccoes_100ha=100 * len(d) / area_ha,
                        sensibilidade=copa_det.mean() if len(c) else np.nan,
                        precisao=det_ok.mean() if len(d) else np.nan))
    out = pd.DataFrame(linhas)
    if reg is not None:
        out = out.merge(reg[["subparcela", "data_imagem", "minutos"]], on="subparcela", how="left")
    out.to_csv(SAIDA / "censo_sensibilidade_precisao.csv", index=False)
    registrar_log("etapa3", dict(deteccoes=a.deteccoes, subparcelas=a.subparcelas,
                                 censo=a.censo, registro=a.registro),
                  dict(n_copas_total=len(cz), n_copas_fora=int((cz.subparcela == "FORA").sum())))
    print(cz.groupby(["subparcela", "cor", "incerta"]).size().to_string()); print()
    print(out[out.dist_m == DIST_MATCH].round(2).to_string(index=False))


def _area_ha(pol):
    """Área geodésica aproximada (ha) de um polígono em graus."""
    lat0 = np.radians(pol.centroid.y)
    x, y = np.array(pol.exterior.coords).T
    X = np.radians(x) * 6371000 * np.cos(lat0); Y = np.radians(y) * 6371000
    return 0.5 * np.sum(X[:-1] * Y[1:] - X[1:] * Y[:-1]) / 1e4


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest="etapa", required=True)
    e1 = sp.add_parser("etapa1")
    for k in ("deteccoes", "resumo", "pontos", "aois"):
        e1.add_argument(f"--{k}", required=True)
    e2 = sp.add_parser("etapa2")
    e2.add_argument("--validacao", required=True); e2.add_argument("--chave", required=True)
    e3 = sp.add_parser("etapa3")
    for k in ("deteccoes", "subparcelas", "censo"):
        e3.add_argument(f"--{k}", required=True)
    e3.add_argument("--registro", required=False,
                    help="data/censo/censo_v1_registro.csv (tempo por subparcela)")
    a = p.parse_args()
    SAIDA.mkdir(parents=True, exist_ok=True)
    {"etapa1": etapa1, "etapa2": etapa2, "etapa3": etapa3}[a.etapa](a)


if __name__ == "__main__":
    main()
