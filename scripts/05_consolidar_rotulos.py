"""
05_consolidar_rotulos.py
Junta TODOS os registros rotulados de copas floridas do projeto num único
conjunto de dados de entrega (data/release_v1/), pronto para quem quiser
continuar as análises.

Fontes:
  1. Inspeção oportunista (pontos registrados ao inspecionar regenerações):
     data/processed/ipes_eventos_consolidados.csv  — 1 linha por copa × data.
     + métricas de detecção Sentinel-2 da v1.1 (results/v1.1/), quando houver.
  2. Censo exaustivo de subparcelas (2026-11-16): data/censo/censo_v1.kml,
     com as áreas de busca (data/aoi/subparcelas_censo_v1.kml e
     data/censo/area_percorrida_AOI10_fragmento.geojson).
     + z por pixel nas copas do censo, SE os rasters do script 03 estiverem em
     data/gee_exports/aoi_z_AOIxx.tif (não versionados; regeneráveis).

Saídas (data/release_v1/):
  - registros_floracao_v1.csv / .geojson : uma linha por copa × data de imagem;
  - flowering_points_v1.gpkg : camadas 'registros', 'areas_censo', 'aois';
  - log_release_v1.json : proveniência (hashes, contagens).

Uso (na raiz do repositório):
    python scripts/05_consolidar_rotulos.py
Requisitos: pandas, numpy, shapely, geopandas (+ rasterio, opcional).
"""
import json, hashlib, platform
from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import shape, Point
import importlib.util

RAIZ = Path(".")
SAIDA = RAIZ / "data/release_v1"
DIST_DUP = 20      # m: copa do censo a <= 20 m de um ponto da inspeção, mesma data = possível duplicata
VERSAO = "1.0"

# Reaproveita o leitor de KML e a distância do script 04.
_spec = importlib.util.spec_from_file_location("s04", RAIZ / "scripts/04_analisar_varredura.py")
s04 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(s04)

ENTRADAS = dict(
    eventos="data/processed/ipes_eventos_consolidados.csv",
    s2_input="data/processed/ipes_eventos_s2_input.csv",
    det_v11="results/v1.1/detectabilidade_por_evento.csv",
    censo="data/censo/censo_v1.kml",
    registro_censo="data/censo/censo_v1_registro.csv",
    subparcelas="data/aoi/subparcelas_censo_v1.kml",
    fragmento="data/censo/area_percorrida_AOI10_fragmento.geojson",
    aois="data/aoi/aois_v1.geojson",
)
RASTERS = {"AOI10": "data/gee_exports/aoi_z_AOI10.tif", "AOI12": "data/gee_exports/aoi_z_AOI12.tif"}


def md5(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


# ------------------------- 1. INSPEÇÃO OPORTUNISTA ---------------------------
def registros_inspecao():
    ev = pd.read_csv(ENTRADAS["eventos"])
    s2 = pd.read_csv(ENTRADAS["s2_input"])[["evento_id", "suspeito", "cluster_id"]]
    det = pd.read_csv(ENTRADAS["det_v11"])[["evento_id", "n_img_evento", "z_pico", "z_rob"]]
    r = ev.merge(s2, on="evento_id", how="left").merge(det, on="evento_id", how="left")
    return pd.DataFrame(dict(
        registro_id="I" + r.evento_id.astype(str),
        copa_id="I" + r.individuo_id.astype(str),
        origem="inspecao_oportunista",
        lon=r.lon, lat=r.lat, data_imagem=r.data_evento,
        cor=r.classe_flor,
        certeza=r.confianca,                     # alta / media / baixa (visual)
        grupo_copas=False,
        contexto=r.contexto,
        oip_presente=r.oip_presente, oip_multicor=r.oip_multicor,
        area_busca="", busca_exaustiva=False,
        suspeito=r.suspeito.fillna(0).astype(bool),
        cluster_id=r.cluster_id,
        s2_elegivel=r.evento_id.isin(s2.evento_id),
        s2_z_pico_ponto=r.z_pico,               # teste por ponto (script 02 v1.1)
        s2_z_evento_pixel=np.nan, s2_z_placebo_pixel=np.nan,
        possivel_duplicata_de="",
        observacoes=r.observacoes_originais.fillna(""),
    ))


# ----------------------------- 2. CENSO --------------------------------------
def areas_censo():
    linhas = []
    for s in s04.ler_kml(ENTRADAS["subparcelas"]):
        if s["geom"] is None or isinstance(s["geom"], Point):
            continue
        d = s["dados"]
        linhas.append(dict(area_id=d["subparcela"], aoi_id=d["aoi_id"], estrato=d.get("estrato", ""),
                           geometry=s["geom"]))
    fr = json.load(open(ENTRADAS["fragmento"]))["features"][0]
    linhas.append(dict(area_id=fr["properties"]["area_id"], aoi_id="AOI10",
                       estrato="fragmento percorrido (contém AOI10_inteira)",
                       geometry=shape(fr["geometry"])))
    g = gpd.GeoDataFrame(linhas, crs="EPSG:4326")
    reg = pd.read_csv(ENTRADAS["registro_censo"]).rename(columns={"subparcela": "area_id"})
    g = g.merge(reg[["area_id", "data_imagem", "minutos", "observacao"]], on="area_id", how="left")
    g.loc[g.area_id == "AOI10_fragmento", "data_imagem"] = "2021-07-24"
    g["area_ha"] = g.to_crs(g.estimate_utm_crs()).area / 1e4
    return g


def registros_censo(areas):
    copas = [c for c in s04.ler_kml(ENTRADAS["censo"]) if isinstance(c["geom"], Point)]
    c = pd.DataFrame([dict(lon=p["geom"].x, lat=p["geom"].y, nome=p["nome"].strip()) for p in copas])
    nm = c.nome.str.lower()
    cor = np.select([nm.str.startswith("r"), nm.str.startswith("a")], ["rosa", "amarelo"], "outra")
    # Área: a subparcela que contém a copa; se nenhuma, o fragmento da AOI10.
    area = []
    for x, y in zip(c.lon, c.lat):
        p = Point(x, y)
        dentro = [a for a, g in zip(areas.area_id, areas.geometry) if g.contains(p) and a != "AOI10_fragmento"]
        area.append(dentro[0] if dentro else
                    ("AOI10_fragmento" if areas.loc[areas.area_id == "AOI10_fragmento"].geometry.iloc[0].contains(p)
                     else "FORA"))
    datas = dict(zip(areas.area_id, areas.data_imagem))
    return pd.DataFrame(dict(
        registro_id=[f"C{i+1:04d}" for i in range(len(c))],
        copa_id=[f"C{i+1:04d}" for i in range(len(c))],
        origem="censo_exaustivo",
        lon=c.lon, lat=c.lat, data_imagem=[datas.get(a, "") for a in area],
        cor=cor,
        certeza=np.where(nm.str.contains(r"\?"), "incerta", "certa"),
        grupo_copas=nm.str.contains(r"\+"),
        contexto="", oip_presente=np.nan, oip_multicor=np.nan,
        area_busca=area, busca_exaustiva=True, suspeito=False, cluster_id="",
        s2_elegivel=True, s2_z_pico_ponto=np.nan,
        s2_z_evento_pixel=np.nan, s2_z_placebo_pixel=np.nan,
        possivel_duplicata_de="",
        observacoes=np.where(cor == "outra", "nome do placemark: " + c.nome, ""),
    ))


def z_nos_rasters(df):
    """z máximo numa janela 3×3 em torno de cada copa do censo (evento e placebo),
    se o raster da AOI estiver disponível localmente."""
    try:
        import rasterio
        from scipy.ndimage import maximum_filter
    except ImportError:
        return df, []
    usados = []
    for aoi, cam in RASTERS.items():
        if not Path(cam).exists():
            continue
        usados.append(cam)
        with rasterio.open(cam) as r:
            ev, pl = r.read(1), r.read(2)
            evm = maximum_filter(np.nan_to_num(ev, nan=-99), size=3)
            plm = maximum_filter(np.nan_to_num(pl, nan=-99), size=3)
            sel = (df.origem == "censo_exaustivo") & df.area_busca.str.startswith(aoi)
            for i in df.index[sel]:
                rr, cc = r.index(df.at[i, "lon"], df.at[i, "lat"])
                if 0 <= rr < r.height and 0 <= cc < r.width and evm[rr, cc] > -99:
                    df.at[i, "s2_z_evento_pixel"] = float(evm[rr, cc])
                    df.at[i, "s2_z_placebo_pixel"] = float(plm[rr, cc])
    return df, usados


def marcar_duplicatas(df):
    """Copa do censo a <= DIST_DUP m de um ponto da inspeção com a mesma data e cor."""
    ins = df[df.origem == "inspecao_oportunista"]
    for i in df.index[df.origem == "censo_exaustivo"]:
        cand = ins[(ins.data_imagem == df.at[i, "data_imagem"]) & (ins.cor == df.at[i, "cor"])]
        if len(cand) == 0:
            continue
        d = s04.dist_m(df.at[i, "lon"], df.at[i, "lat"], cand.lon.values, cand.lat.values)
        if d.min() <= DIST_DUP:
            df.at[i, "possivel_duplicata_de"] = cand.registro_id.values[d.argmin()]
    return df


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    areas = areas_censo()
    reg = pd.concat([registros_inspecao(), registros_censo(areas)], ignore_index=True)
    reg, rasters_usados = z_nos_rasters(reg)
    reg = marcar_duplicatas(reg)
    reg.to_csv(SAIDA / "registros_floracao_v1.csv", index=False)
    g = gpd.GeoDataFrame(reg, geometry=gpd.points_from_xy(reg.lon, reg.lat), crs="EPSG:4326")
    g.to_file(SAIDA / "registros_floracao_v1.geojson", driver="GeoJSON")
    gpkg = SAIDA / "flowering_points_v1.gpkg"
    if gpkg.exists():
        gpkg.unlink()
    g.to_file(gpkg, layer="registros", driver="GPKG")
    areas.to_file(gpkg, layer="areas_censo", driver="GPKG")
    gpd.read_file(ENTRADAS["aois"]).to_file(gpkg, layer="aois", driver="GPKG")

    resumo = reg.groupby(["origem", "cor", "certeza"]).size().rename("n").reset_index()
    log = dict(versao_script=VERSAO,
               entradas={k: dict(caminho=v, md5=md5(v)) for k, v in ENTRADAS.items()},
               rasters_usados=rasters_usados,
               n_registros=len(reg), n_copas=int(reg.copa_id.nunique()),
               n_possiveis_duplicatas=int((reg.possivel_duplicata_de != "").sum()),
               resumo=resumo.to_dict(orient="records"),
               python=platform.python_version(), pandas=pd.__version__, geopandas=gpd.__version__)
    (SAIDA / "log_release_v1.json").write_text(json.dumps(log, indent=2, ensure_ascii=False))
    print(resumo.to_string(index=False))
    print("possíveis duplicatas:", log["n_possiveis_duplicatas"], "| rasters:", rasters_usados)
    print(reg.groupby(["origem", "area_busca"]).size())


if __name__ == "__main__":
    main()
