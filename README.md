# flowering-points

Registros de copas floridas de ipês (*Handroanthus* spp. e afins) identificadas
visualmente em imagens de alta resolução (Google Earth) durante a inspeção de
áreas em regeneração no Cerrado, e teste de **detectabilidade dessa floração
no Sentinel-2**.

> **Status (2026-11-16, v1.1):** teste de detectabilidade revisado, com ruído
> robusto e métrica de pico.
> - **Rosa:** com `z_pico > 3`, detecta 50% das florações conhecidas, com ~1%
>   de falso positivo no placebo.
> - **Amarelo:** sinal médio real, mas fraco no nível individual.
>
> Ver [`docs/RESULTADOS_v1.1.md`](docs/RESULTADOS_v1.1.md) e o
> [`CHANGELOG.md`](CHANGELOG.md).
>
> **Varredura nas AOIs (2026-11-16):**
> - **Rosa:** detecta copas acima do acaso (sensibilidade de 48% contra 21% na
>   AOI10), mas a regra por pixel gera ~1 falso positivo por hectare (precisão
>   de 15%). A regra precisa ser revisada antes do histórico.
> - **Amarelo:** sem sinal.
>
> Ver [`docs/RESULTADOS_aoi_v1.md`](docs/RESULTADOS_aoi_v1.md).

## Pergunta

1. Os pontos registrados oportunisticamente no Google Earth (GE) correspondem a
   um sinal espectral detectável no Sentinel-2 (10 m) na data da floração?
2. Se sim, é possível usar o Sentinel-2 para (a) relocalizar a copa e (b)
   reconstruir o histórico de floração de cada indivíduo entre 2017 e o presente,
   sem depender do GE (cujo mosaico desloca a posição das copas entre datas)?

A pergunta 1 foi respondida na v1. A pergunta 2 é o próximo passo.

## Estrutura do repositório (proposta)

```
flowering-points/
├── README.md
├── data/
│   ├── raw/                         # originais (não editar)
│   │   ├── ipes_ver2_revisado.csv
│   │   └── aois_poligonos.geojson
│   ├── aoi/
│   │   ├── aois_v1.geojson               # AOIs normalizadas (aoi_id, data, status)
│   │   └── subparcelas_censo_v1.kml      # (gerado pelo script 03)
│   ├── censo/
│   │   └── censo_v1.kml                  # (a produzir: protocolo em docs/)
│   ├── processed/
│   │   ├── ipes_eventos_consolidados.csv   # 1 linha por evento de floração
│   │   └── ipes_eventos_s2_input.csv       # subconjunto elegível para o S2
│   └── gee_exports/
│       ├── ipes_s2_series_v1.csv           # séries S2 por ponto (versão congelada)
│       └── aoi_*_v1.*                      # exportações do script 03 (a produzir)
├── scripts/
│   ├── 01_gee_extrair_series_s2.js   # GEE Code Editor
│   ├── 02_analisar_detectabilidade.py
│   ├── 03_gee_varredura_aoi.js       # GEE: varredura por pixel nas AOIs + subparcelas
│   └── 04_analisar_varredura.py      # etapas 1–3: densidade, precisão, sensibilidade
├── results/
│   ├── v1/                           # saídas do script 02 v1
│   ├── v1_exploratorio_janela5/      # janela ±5 d (post hoc)
│   ├── v1.1/                         # saídas do script 02 v1.1 (ruído robusto + pico)
│   └── aoi_v1/                       # saídas do script 04 (a produzir)
└── docs/
    ├── METODOS.md
    ├── DICIONARIO_DADOS.md
    ├── RESULTADOS_v1.md
    ├── RESULTADOS_v1.1.md
    ├── RESULTADOS_aoi_v1.md          # varredura nas AOIs + censo
    ├── PROTOCOLO_CENSO.md            # validação cega e censo no GE
    └── DECISOES.md                   # registro de decisões e questões abertas
```

## Como reproduzir

1. **Entrada:** `data/processed/ipes_eventos_s2_input.csv`
   (md5 `be871cca28610115b376cb3ebf5a7f4f`).
2. **Extração (GEE):** subir o CSV como *Table asset*; ajustar `ASSET` no topo de
   `scripts/01_gee_extrair_series_s2.js`; rodar no Code Editor e disparar o
   Export para o Drive. Na v1: 21 min, ~895 EECU-s, 19.397 linhas.
3. **Congelar a exportação:** copiar o CSV para `data/gee_exports/` com sufixo de
   versão. As coleções do GEE são reprocessadas ao longo do tempo; rerodar o
   script 01 não garante o mesmo resultado bit a bit.
4. **Análise (Python ≥3.10, pandas, numpy, scipy, matplotlib):**
   ```bash
   python scripts/02_analisar_detectabilidade.py \
       data/processed/ipes_eventos_s2_input.csv \
       data/gee_exports/ipes_s2_series_v1.csv
   ```
   Saída em `resultados/` (mover para `results/vN/`), incluindo
   `log_execucao.json` com hashes das entradas, parâmetros e versões.

### Varredura nas AOIs (v1.2)

1. Rodar `scripts/03_gee_varredura_aoi.js` (as geometrias estão embutidas;
   só ajustar `ASSET_PONTOS`). Disparar os exports e salvar os CSVs em
   `data/gee_exports/` e o KML das subparcelas em `data/aoi/`.
2. Etapa 1: `python scripts/04_analisar_varredura.py etapa1 --deteccoes ... --resumo ... --pontos ... --aois data/aoi/aois_v1.geojson`.
3. Validação cega e censo no GE, conforme `docs/PROTOCOLO_CENSO.md`.
4. Etapas 2 e 3 do script 04 (comandos no cabeçalho do script).

## Nível de reprodutibilidade

**Básico.** Parâmetros declarados no topo dos scripts; hashes de entrada e
versões de pacotes registrados no log; pipeline reexecutável do CSV de entrada
até as figuras.

Dependências mínimas em `requirements.txt` (sem versões fixadas; as versões
efetivamente usadas ficam no log de cada execução).

**Faltando:** ambiente congelado (versões fixadas);
versão congelada da coleção Sentinel-2 (mitigado guardando a exportação);
script de consolidação `raw → processed` (a consolidação v1 foi feita fora do
pipeline e está descrita em `docs/METODOS.md`, mas não é reexecutável).

## Limitações principais

- Dados de **presença oportunista**: sem não-detecções, esforço não controlado,
  pontos agrupados (78 clusters de data × região).
- **Classe = cor da flor**, não espécie.
- O sinal "rosa" ainda tem uma explicação alternativa não descartada:
  **desfolha** pré-floração (ver `docs/RESULTADOS_v1.md`, seção 5).
- **Lacuna de 2017:** 98 eventos de 2017 ficam sem as métricas da v1.1, por
  cobertura incompleta da coleção L2A (D8).
- A janela de ±5 dias que melhora o sinal amarelo foi escolhida **após** ver os
  dados (exploratória).

## Autoria

Mario Barroso — registro dos pontos, consolidação e desenho da pergunta.
Scripts e análise desenvolvidos com assistência de IA (Claude, Anthropic).
