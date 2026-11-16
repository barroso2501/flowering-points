"""
06_analise_fragmento.py
Reproduz a análise que levou à conclusão "acompanhar copas conhecidas, não
descobrir copas às cegas" (docs/RESULTADOS_aoi_v1.1.md):

  (1) fração de PIXELS com z_pico acima de cada limiar, evento × placebo,
      dentro da AOI10 e no fragmento fora da AOI10 (área de teste);
  (2) z_pico (máximo numa janela 3×3) nas COPAS do censo, evento × placebo,
      separando calibração (AOI10_inteira) e teste (AOI10_fragmento);
  (3) balanço esperado no fragmento: detecções falsas × copas detectadas.

Entradas (na raiz do repositório):
  data/gee_exports/aoi_z_AOI10.tif   (raster do script 03; não versionado)
  data/release_v1/registros_floracao_v1.csv   (script 05)
  data/aoi/aois_v1.geojson, data/censo/area_percorrida_AOI10_fragmento.geojson
Saída: results/aoi_v1.1/ (tabelas CSV + log).
Requisitos: numpy, pandas, shapely, rasterio, scipy.
"""
import json, hashlib, platform
from pathlib import Path
import numpy as np
import pandas as pd
import rasterio
from rasterio.features import geometry_mask
from scipy.ndimage import maximum_filter
from shapely.geometry import shape, mapping

LIMIARES = (3, 4, 5, 6, 8)
SAIDA = Path("results/aoi_v1.1")
ENT = dict(raster="data/gee_exports/aoi_z_AOI10.tif",
           registros="data/release_v1/registros_floracao_v1.csv",
           aois="data/aoi/aois_v1.geojson",
           fragmento="data/censo/area_percorrida_AOI10_fragmento.geojson")


def md5(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    aoi = shape([f for f in json.load(open(ENT["aois"]))["features"]
                 if f["properties"]["aoi_id"] == "AOI10"][0]["geometry"])
    frag = shape(json.load(open(ENT["fragmento"]))["features"][0]["geometry"])
    with rasterio.open(ENT["raster"]) as r:
        ev, pl = r.read(1), r.read(2)
        m_aoi = ~geometry_mask([mapping(aoi)], r.shape, r.transform)
        m_frag = ~geometry_mask([mapping(frag)], r.shape, r.transform)
        transform, shape_ = r.transform, r.shape
        res = r.res

    # (1) Fração de pixels acima do limiar.
    linhas = []
    for nome, m in [("AOI10", m_aoi), ("fragmento_fora_AOI10", m_frag & ~m_aoi)]:
        e, p = ev[m & np.isfinite(ev)], pl[m & np.isfinite(pl)]
        for t in LIMIARES:
            linhas.append(dict(area=nome, n_pixels=e.size, limiar=t,
                               frac_pixels_evento=np.mean(e > t), frac_pixels_placebo=np.mean(p > t)))
    px = pd.DataFrame(linhas)
    px.to_csv(SAIDA / "excedencia_pixels.csv", index=False)

    # (2) z nas copas do censo (rosa, certas).
    reg = pd.read_csv(ENT["registros"])
    c = reg[(reg.origem == "censo_exaustivo") & (reg.cor == "rosa") & (reg.certeza == "certa")
            & reg.area_busca.isin(["AOI10_inteira", "AOI10_fragmento"])].copy()
    evm = maximum_filter(np.nan_to_num(ev, nan=-99), size=3)
    plm = maximum_filter(np.nan_to_num(pl, nan=-99), size=3)
    inv = ~transform
    idx = [tuple(int(v) for v in (inv * (x, y))[::-1]) for x, y in zip(c.lon, c.lat)]
    c["z_ev"] = [evm[i, j] for i, j in idx]
    c["z_pl"] = [plm[i, j] for i, j in idx]
    c["grupo"] = c.area_busca.map({"AOI10_inteira": "calibracao_AOI10",
                                   "AOI10_fragmento": "teste_fragmento_norte"})
    copas = pd.DataFrame([dict(grupo=g, limiar=t, n_copas=len(d),
                               frac_copas_evento=np.mean(d.z_ev > t),
                               frac_copas_placebo=np.mean(d.z_pl > t))
                          for g, d in c.groupby("grupo") for t in LIMIARES])
    copas.to_csv(SAIDA / "deteccao_copas_censo.csv", index=False)

    # (3) Balanço no fragmento inteiro coberto pelo raster: pixels falsos
    # esperados (taxa do placebo) × copas detectadas (taxa nas copas).
    n_px_frag = int((m_frag & np.isfinite(ev)).sum())
    n_copas_frag = len(c)
    bal = []
    for t in LIMIARES:
        fp = px[(px.area == "fragmento_fora_AOI10") & (px.limiar == t)].frac_pixels_placebo.iloc[0]
        sens = np.mean(c.z_ev > t)
        bal.append(dict(limiar=t, n_pixels_fragmento=n_px_frag, pixels_falsos_esperados=fp * n_px_frag,
                        copas_censo=n_copas_frag, copas_detectadas=sens * n_copas_frag,
                        precisao_maxima_aprox=(sens * n_copas_frag) / (sens * n_copas_frag + fp * n_px_frag)))
    pd.DataFrame(bal).to_csv(SAIDA / "balanco_fragmento.csv", index=False)

    log = dict(entradas={k: dict(caminho=v, md5=md5(v)) for k, v in ENT.items()},
               limiares=LIMIARES, resolucao_graus=res,
               nota=("precisao_maxima_aprox conta cada pixel falso como uma detecção; "
                     "agrupar pixels em objetos reduz um pouco o número de falsos"),
               python=platform.python_version(), numpy=np.__version__, pandas=pd.__version__)
    (SAIDA / "log_analise_fragmento.json").write_text(json.dumps(log, indent=2, ensure_ascii=False))
    print(px.round(4).to_string(index=False)); print()
    print(copas.round(2).to_string(index=False)); print()
    print(pd.DataFrame(bal).round(2).to_string(index=False))


if __name__ == "__main__":
    main()
