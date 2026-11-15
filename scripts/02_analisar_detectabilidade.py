"""
02_analisar_detectabilidade.py
Analisa as séries Sentinel-2 exportadas pelo script 01 (GEE) e responde:
  (1) DISPONIBILIDADE: há imagem limpa perto da data do evento?
  (2) SINAL: o contraste núcleo−anel do índice de flor sobe na data do evento,
      em relação ao mesmo contraste antes da floração? (diferença em diferenças)
  (3) PLACEBO: a mesma estatística calculada numa "data falsa" pré-floração
      deveria dar ~0; se não der, o "sinal" é ruído/sazonalidade.

Uso (no terminal, na pasta dos arquivos):
    python 02_analisar_detectabilidade.py ipes_eventos_s2_input.csv ipes_s2_series_v1.csv
Saídas em ./resultados/: tabela por evento, resumo por grupo, figuras, log.
Requisitos: pandas, numpy, scipy, matplotlib.
"""
import sys, json, hashlib, platform
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ----------------------------- PARÂMETROS -----------------------------------
JANELA_EVENTO = (-10, 10)     # dias: imagens consideradas "durante a floração"
JANELA_BASE   = (-90, -30)    # dias: baseline pré-floração (mesmo ano)
PLACEBO_EV    = (-60, -40)    # dias: data falsa, ainda antes da floração
PLACEBO_BASE  = (-90, -65)    # dias: baseline do placebo
MIN_LIMPO     = 0.9           # fração mínima de pixels limpos (núcleo e anel)
MIN_N_BASE    = 3             # nº mínimo de imagens na baseline para calcular z
INDICE = {"amarelo": "NDYI", "rosa": "IRS"}   # índice usado por classe de flor
SAIDA = Path("resultados")


def md5(caminho):
    """Hash do arquivo de entrada, para registrar a proveniência."""
    return hashlib.md5(Path(caminho).read_bytes()).hexdigest()


def carregar(caminho_eventos, caminho_series):
    ev = pd.read_csv(caminho_eventos)
    se = pd.read_csv(caminho_series)
    # Mesma data pode vir de dois tiles MGRS sobrepostos: fica a observação
    # com maior fração limpa no núcleo.
    se = (se.sort_values("frac_limpo_n", ascending=False)
            .drop_duplicates(["evento_id", "data_img"]))
    se = se[(se.frac_limpo_n >= MIN_LIMPO) & (se.frac_limpo_a >= MIN_LIMPO)]
    se = se.merge(ev[["evento_id", "classe_flor"]], on="evento_id", how="inner")
    # Contraste núcleo−anel do índice da classe (média e máximo do núcleo).
    se["contraste"] = np.where(se.classe_flor == "amarelo",
                               se.n_NDYI - se.a_NDYI, se.n_IRS - se.a_IRS)
    se["contraste_max"] = np.where(se.classe_flor == "amarelo",
                                   se.nmax_NDYI - se.a_NDYI, se.nmax_IRS - se.a_IRS)
    return ev, se


def dentro(s, jan):
    return s[(s.dias_rel >= jan[0]) & (s.dias_rel <= jan[1])]


def estatistica_evento(g, jan_ev, jan_base, col):
    """Delta = mediana(contraste na janela do evento) − mediana(na baseline);
    z = delta / desvio-padrão da baseline (quando há imagens suficientes)."""
    e, b = dentro(g, jan_ev)[col], dentro(g, jan_base)[col]
    if len(e) == 0 or len(b) == 0:
        return np.nan, np.nan
    delta = e.median() - b.median()
    z = delta / b.std(ddof=1) if len(b) >= MIN_N_BASE and b.std(ddof=1) > 0 else np.nan
    return delta, z


def por_evento(ev, se):
    linhas = []
    for eid, g in se.groupby("evento_id"):
        jan = dentro(g, JANELA_EVENTO)
        d, z = estatistica_evento(g, JANELA_EVENTO, JANELA_BASE, "contraste")
        dmax, _ = estatistica_evento(g, JANELA_EVENTO, JANELA_BASE, "contraste_max")
        dp, zp = estatistica_evento(g, PLACEBO_EV, PLACEBO_BASE, "contraste")
        linhas.append(dict(
            evento_id=eid,
            n_img_evento=len(jan),
            dias_img_mais_proxima=g.dias_rel.abs().min(),
            n_img_base=len(dentro(g, JANELA_BASE)),
            delta=d, z=z, delta_max=dmax, delta_placebo=dp, z_placebo=zp))
    r = ev.merge(pd.DataFrame(linhas), on="evento_id", how="left")
    r["n_img_evento"] = r.n_img_evento.fillna(0).astype(int)
    return r


def teste_por_cluster(r, grupo, col):
    """Eventos do mesmo cluster (mesma data e mesma região) não são
    independentes: agrega por cluster (mediana) antes do teste de Wilcoxon
    unilateral (H1: delta > 0)."""
    saida = []
    for k, g in r.dropna(subset=[col]).groupby(grupo):
        c = g.groupby("cluster_id")[col].median()
        p = stats.wilcoxon(c, alternative="greater").pvalue if len(c) >= 6 else np.nan
        saida.append(dict(grupo=" | ".join(map(str, np.atleast_1d(k))), metrica=col,
                          n_eventos=len(g), n_clusters=len(c),
                          mediana_eventos=g[col].median(),
                          frac_eventos_pos=(g[col] > 0).mean(),
                          mediana_clusters=c.median(), p_wilcoxon_clusters=p))
    return saida


def figuras(se, r):
    # (a) curva média do contraste em função dos dias, por classe
    fig, ax = plt.subplots(1, 2, figsize=(11, 4), sharey=False)
    for i, cl in enumerate(["rosa", "amarelo"]):
        s = se[se.classe_flor == cl].copy()
        s["bin"] = (s.dias_rel // 5) * 5
        q = s.groupby("bin").contraste.quantile([.25, .5, .75]).unstack()
        ax[i].fill_between(q.index, q[.25], q[.75], alpha=.3)
        ax[i].plot(q.index, q[.5])
        ax[i].axvspan(*JANELA_EVENTO, color="orange", alpha=.15)
        ax[i].axhline(0, lw=.5, color="k")
        ax[i].set_title(f"{cl}: contraste {INDICE[cl]} núcleo−anel")
        ax[i].set_xlabel("dias em relação ao evento GE")
    fig.tight_layout(); fig.savefig(SAIDA / "curva_contraste.png", dpi=150)
    # (b) delta real × placebo
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    for i, cl in enumerate(["rosa", "amarelo"]):
        g = r[r.classe_flor == cl]
        ax[i].hist(g.delta_placebo.dropna(), bins=30, alpha=.5, label="placebo")
        ax[i].hist(g.delta.dropna(), bins=30, alpha=.5, label="evento")
        ax[i].axvline(0, color="k", lw=.5); ax[i].legend(); ax[i].set_title(cl)
    fig.tight_layout(); fig.savefig(SAIDA / "delta_vs_placebo.png", dpi=150)


def main(caminho_eventos, caminho_series):
    SAIDA.mkdir(exist_ok=True)
    ev, se = carregar(caminho_eventos, caminho_series)
    r = por_evento(ev, se)
    r.to_csv(SAIDA / "detectabilidade_por_evento.csv", index=False)

    # Disponibilidade: fração de eventos com >=1 imagem limpa na janela.
    disp = (r.assign(tem_img=r.n_img_evento > 0)
              .groupby(["classe_flor", "contexto"])
              .agg(n=("evento_id", "size"), frac_com_img=("tem_img", "mean"),
                   mediana_dias_mais_proxima=("dias_img_mais_proxima", "median"))
              .reset_index())
    disp.to_csv(SAIDA / "disponibilidade.csv", index=False)

    # Sinal: análise principal só com confiança alta e sem casos suspeitos.
    base = r[(r.confianca == "alta") & (r.suspeito == 0)]
    res = []
    for col in ["delta", "delta_max", "delta_placebo"]:
        res += teste_por_cluster(base, "classe_flor", col)
        res += teste_por_cluster(base, ["classe_flor", "contexto"], col)
        res += teste_por_cluster(base, ["classe_flor", "oip_presente"], col)
    pd.DataFrame(res).to_csv(SAIDA / "resumo_sinal.csv", index=False)
    figuras(se, r)

    # Log de proveniência (reprodutibilidade básica).
    log = dict(entrada_eventos=caminho_eventos, md5_eventos=md5(caminho_eventos),
               entrada_series=caminho_series, md5_series=md5(caminho_series),
               parametros=dict(JANELA_EVENTO=JANELA_EVENTO, JANELA_BASE=JANELA_BASE,
                               PLACEBO_EV=PLACEBO_EV, PLACEBO_BASE=PLACEBO_BASE,
                               MIN_LIMPO=MIN_LIMPO, INDICE=INDICE),
               python=platform.python_version(), pandas=pd.__version__,
               numpy=np.__version__, n_eventos=len(ev),
               n_eventos_com_img=int((r.n_img_evento > 0).sum()))
    (SAIDA / "log_execucao.json").write_text(json.dumps(log, indent=2, ensure_ascii=False))
    print(json.dumps(log, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
