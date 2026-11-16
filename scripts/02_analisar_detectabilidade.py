"""
02_analisar_detectabilidade.py  (v1.1)
Analisa as séries Sentinel-2 exportadas pelo script 01 (GEE) e responde:
  (1) DISPONIBILIDADE: há imagem limpa perto da data do evento?
  (2) SINAL: o contraste núcleo−anel do índice de flor sobe na data do evento?
      Duas métricas:
        - delta: evento − baseline pré-floração (diferença em diferenças, v1);
        - pico : evento − "ombros" (antes e depois do evento). Mede um aumento
                 TRANSITÓRIO; uma rampa lenta (ex.: desfolha, secagem do fundo)
                 eleva os ombros junto e não gera pico.
  (3) PLACEBO: as mesmas métricas numa data falsa pré-floração devem dar ~0.

Mudanças em relação à v1:
  - Ruído estimado de forma robusta e igual para evento e placebo: desvio
    absoluto mediano (MAD) das diferenças entre imagens consecutivas da fase
    pré-floração, dividido por √2. Diferenças removem tendências lentas; o MAD
    é pouco afetado por valores extremos. Na v1, o placebo usava o desvio-padrão
    de ~4 imagens, que subestimava o ruído e inflava o z.
  - Nova métrica de pico acima dos ombros (z_pico).
  - Taxas de detecção (z>2 e z>3) para evento × placebo em resumo_deteccao.csv.
  As colunas da v1 (delta, z, delta_placebo, z_placebo) são mantidas para
  comparação.

Uso:
    python scripts/02_analisar_detectabilidade.py \
        data/processed/ipes_eventos_s2_input.csv data/gee_exports/ipes_s2_series_v1.csv
Saídas em ./resultados/ (mover para results/vN/).
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

VERSAO = "1.1"

# ----------------------------- PARÂMETROS -----------------------------------
JANELA_EVENTO = (-10, 10)     # dias: "durante a floração" (pré-especificada)
JANELA_BASE   = (-90, -30)    # dias: baseline pré-floração, mesmo ano
PLACEBO_EV    = (-60, -40)    # dias: data falsa, ainda antes da floração
PLACEBO_BASE  = (-90, -65)    # dias: baseline do placebo (métrica delta)
# Ombros para a métrica de pico, relativos ao CENTRO da janela (0 no evento,
# −50 no placebo): um antes e um depois, sem sobrepor a janela.
OMBRO_ANTES   = (-30, -15)
OMBRO_DEPOIS  = (20, 35)
JANELA_RUIDO  = (-90, -30)    # dias: fase usada para estimar o ruído
MIN_LIMPO     = 0.9           # fração mínima de pixels limpos (núcleo e anel)
MIN_N_BASE    = 3             # nº mínimo de imagens na baseline (z da v1)
MIN_N_RUIDO   = 5             # nº mínimo de imagens para estimar o ruído robusto
LIMIARES_Z    = (2, 3)
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
    amarelo = se.classe_flor == "amarelo"
    se["contraste"] = np.where(amarelo, se.n_NDYI - se.a_NDYI, se.n_IRS - se.a_IRS)
    se["contraste_max"] = np.where(amarelo, se.nmax_NDYI - se.a_NDYI,
                                   se.nmax_IRS - se.a_IRS)
    return ev, se.sort_values(["evento_id", "dias_rel"])


def dentro(s, jan, centro=0):
    return s[(s.dias_rel >= centro + jan[0]) & (s.dias_rel <= centro + jan[1])]


def ruido_robusto(g, col):
    """Ruído imagem-a-imagem: MAD das diferenças consecutivas na fase
    pré-floração, escalado para desvio-padrão (×1,4826) e dividido por √2
    (a diferença de duas observações independentes tem variância 2σ²).
    Ressalva: se o ruído for autocorrelacionado entre imagens próximas, este
    estimador o subestima."""
    s = dentro(g, JANELA_RUIDO)[col].to_numpy()
    if len(s) < MIN_N_RUIDO:
        return np.nan
    d = np.diff(s)
    mad = np.median(np.abs(d - np.median(d)))
    sd = 1.4826 * mad / np.sqrt(2)
    return sd if sd > 0 else np.nan


def delta_v1(g, jan_ev, jan_base, col):
    """Métrica da v1: mediana(evento) − mediana(baseline); z com dp da baseline."""
    e, b = dentro(g, jan_ev)[col], dentro(g, jan_base)[col]
    if len(e) == 0 or len(b) == 0:
        return np.nan, np.nan
    delta = e.median() - b.median()
    sd = b.std(ddof=1)
    z = delta / sd if len(b) >= MIN_N_BASE and sd > 0 else np.nan
    return delta, z


def pico(g, centro, col):
    """Mediana na janela centrada − média das medianas dos dois ombros.
    Exige imagem na janela e nos dois ombros."""
    e = dentro(g, JANELA_EVENTO, centro)[col]
    oa = dentro(g, OMBRO_ANTES, centro)[col]
    od = dentro(g, OMBRO_DEPOIS, centro)[col]
    if len(e) == 0 or len(oa) == 0 or len(od) == 0:
        return np.nan
    return e.median() - (oa.median() + od.median()) / 2


def por_evento(ev, se):
    centro_placebo = int(np.mean(PLACEBO_EV))
    linhas = []
    for eid, g in se.groupby("evento_id"):
        jan = dentro(g, JANELA_EVENTO)
        d, z = delta_v1(g, JANELA_EVENTO, JANELA_BASE, "contraste")
        dmax, _ = delta_v1(g, JANELA_EVENTO, JANELA_BASE, "contraste_max")
        dp, zp = delta_v1(g, PLACEBO_EV, PLACEBO_BASE, "contraste")
        ruido = ruido_robusto(g, "contraste")
        pk = pico(g, 0, "contraste")
        pkp = pico(g, centro_placebo, "contraste")
        linhas.append(dict(
            evento_id=eid,
            n_img_evento=len(jan),
            dias_img_mais_proxima=g.dias_rel.abs().min(),
            n_img_base=len(dentro(g, JANELA_BASE)),
            # métricas v1 (mantidas para comparação)
            delta=d, z=z, delta_max=dmax, delta_placebo=dp, z_placebo=zp,
            # métricas v1.1
            ruido=ruido,
            z_rob=d / ruido, z_placebo_rob=dp / ruido,
            pico=pk, z_pico=pk / ruido,
            pico_placebo=pkp, z_pico_placebo=pkp / ruido))
    r = ev.merge(pd.DataFrame(linhas), on="evento_id", how="left")
    r["n_img_evento"] = r.n_img_evento.fillna(0).astype(int)
    return r


def teste_por_cluster(r, grupo, col):
    """Eventos do mesmo cluster não são independentes: agrega por cluster
    (mediana) antes do Wilcoxon unilateral (H1: métrica > 0)."""
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


def taxas_deteccao(base):
    """Fração de eventos acima de cada limiar: evento (sensibilidade com data
    conhecida) × placebo (taxa empírica de falso positivo)."""
    pares = {"z (v1)": ("z", "z_placebo"),
             "z_rob (delta, ruído robusto)": ("z_rob", "z_placebo_rob"),
             "z_pico (pico, ruído robusto)": ("z_pico", "z_pico_placebo")}
    saida = []
    for cl, g in base.groupby("classe_flor"):
        for nome, (ce, cp) in pares.items():
            ge, gp = g[ce].dropna(), g[cp].dropna()
            for lim in LIMIARES_Z:
                saida.append(dict(classe=cl, metrica=nome, limiar=lim,
                                  n_evento=len(ge), taxa_evento=(ge > lim).mean(),
                                  n_placebo=len(gp), taxa_placebo=(gp > lim).mean()))
    return pd.DataFrame(saida)


def figuras(se, r):
    # (a) curva do contraste em função dos dias, por classe
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
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
    plt.close(fig)
    # (b) z_pico do evento × do placebo
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    bins = np.linspace(-6, 12, 37)
    for i, cl in enumerate(["rosa", "amarelo"]):
        g = r[r.classe_flor == cl]
        ax[i].hist(g.z_pico_placebo.dropna().clip(-6, 12), bins=bins, alpha=.5, label="placebo")
        ax[i].hist(g.z_pico.dropna().clip(-6, 12), bins=bins, alpha=.5, label="evento")
        for lim in LIMIARES_Z:
            ax[i].axvline(lim, color="k", lw=.5, ls="--")
        ax[i].legend(); ax[i].set_title(f"{cl}: z_pico (valores cortados em −6 e 12)")
    fig.tight_layout(); fig.savefig(SAIDA / "zpico_vs_placebo.png", dpi=150)
    plt.close(fig)


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
    for col in ["delta", "delta_max", "delta_placebo", "pico", "pico_placebo"]:
        res += teste_por_cluster(base, "classe_flor", col)
        res += teste_por_cluster(base, ["classe_flor", "contexto"], col)
        res += teste_por_cluster(base, ["classe_flor", "oip_presente"], col)
    pd.DataFrame(res).to_csv(SAIDA / "resumo_sinal.csv", index=False)
    taxas = taxas_deteccao(base)
    taxas.to_csv(SAIDA / "resumo_deteccao.csv", index=False)
    figuras(se, r)

    # Log de proveniência (reprodutibilidade básica).
    log = dict(versao_script=VERSAO,
               entrada_eventos=caminho_eventos, md5_eventos=md5(caminho_eventos),
               entrada_series=caminho_series, md5_series=md5(caminho_series),
               parametros=dict(JANELA_EVENTO=JANELA_EVENTO, JANELA_BASE=JANELA_BASE,
                               PLACEBO_EV=PLACEBO_EV, PLACEBO_BASE=PLACEBO_BASE,
                               OMBRO_ANTES=OMBRO_ANTES, OMBRO_DEPOIS=OMBRO_DEPOIS,
                               JANELA_RUIDO=JANELA_RUIDO, MIN_LIMPO=MIN_LIMPO,
                               MIN_N_RUIDO=MIN_N_RUIDO, INDICE=INDICE),
               python=platform.python_version(), pandas=pd.__version__,
               numpy=np.__version__, n_eventos=len(ev),
               n_eventos_com_img=int((r.n_img_evento > 0).sum()))
    (SAIDA / "log_execucao.json").write_text(json.dumps(log, indent=2, ensure_ascii=False))
    print(taxas.round(3).to_string(index=False))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
