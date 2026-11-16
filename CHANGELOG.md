# Changelog

## v2.0: congelamento (2026-11-16)

- **Projeto congelado** e preparado para outros interessados.
- **Dados:**
  - `data/release_v1/`: todos os registros rotulados (745: 498 da inspeção e
    247 do censo) em CSV, GeoJSON e GeoPackage, com `LEIAME.md`;
  - `data/censo/area_percorrida_AOI10_fragmento.geojson`;
  - `data/raw/aois_poligonos_frag.geojson`.
- **Scripts:**
  - `05_consolidar_rotulos.py` (gera o conjunto de entrega);
  - `06_analise_fragmento.py` (por que a varredura cega falha).
- **Resultados:** `results/aoi_v1.1/`; `docs/RESULTADOS_aoi_v1.1.md`.
- **Docs:**
  - `GUIA_INTERESSADOS.md`;
  - `DECISOES` (D12 atualizada, D13, tabela de estado no congelamento);
  - README reescrito;
  - `METODOS` §6;
  - `DICIONARIO_DADOS`.
- **Outros:**
  - `CITATION.cff` (licença a definir);
  - `MANIFEST.sha256`;
  - `requirements.txt` + geopandas e rasterio.

## v1.3.1 (2026-11-16)

- **`data/censo/censo_v1_registro.csv`:**
  - tempos de borda e matriz corrigidos (estavam trocados);
  - `n_copas` preenchido;
  - observações sobre o censo da AOI10 estendido ao fragmento inteiro.
- **`docs/RESULTADOS_aoi_v1.md`:** tabela do censo e pendências atualizadas.

## v1.3 (2026-11-16)

- **Dados:**
  - exportações do script 03 (`data/gee_exports/aoi_deteccoes_v1.csv`,
    `aoi_resumo_v1.csv`, `aoi_pontos_v1.csv`);
  - subparcelas sorteadas (`data/aoi/subparcelas_censo_v1.kml`);
  - censo (`data/censo/censo_v1.kml`, `censo_v1_registro.csv`).
- **Script 04 v1.1 (etapa 3):**
  - lê o registro do censo e mantém as subparcelas sem copas;
  - calcula sensibilidade e precisão também com as detecções do placebo (nível
    do acaso) e em 10, 20 e 30 m;
  - exporta a atribuição das copas às subparcelas
    (`censo_copas_atribuidas.csv`).
- **Resultados:** `results/aoi_v1/` (etapas 1 e 3) e
  `docs/RESULTADOS_aoi_v1.md`.
- **Docs:** `DECISOES` (D6 atualizada; novas D11, validação adiada, e D12,
  amarelo); README.
- **`.gitignore`:** `*.tif` (rasters ficam no Drive) e os arquivos da amostra
  cega.

## v1.2.1 (2026-11-16)

- **Script 03:** asset do MapBiomas atualizado para a Coleção 11
  (`projects/mapbiomas-public/assets/brazil/lulc/collection11/mapbiomas_brazil_collection11_coverage_v3`).
  A banda passa a ser escolhida automaticamente (ano mais recente, impresso no
  console), com a opção de fixar o ano em `MAPBIOMAS_BANDA`.
- **Docs:** `METODOS` (limitações da seção 5).

## v1.2 (2026-11-16)

- **Dados:**
  - `data/raw/aois_poligonos.geojson` (17 AOIs, original);
  - `data/aoi/aois_v1.geojson` (normalizado: aoi_id, data ISO, classes,
    status).
- **Script 03 (GEE):**
  - varredura por pixel nas 7 AOIs aptas: z_pico do evento e do placebo,
    objetos detectados, z nos pontos registrados, rasters;
  - sorteio estratificado das subparcelas do censo (KML).
- **Script 04 (Python):**
  - etapa 1: densidades evento × placebo, detecção dos pontos registrados,
    amostra cega;
  - etapa 2: precisão;
  - etapa 3: sensibilidade e precisão com o censo.
- **Docs:**
  - novo `PROTOCOLO_CENSO.md`;
  - `METODOS` seção 5;
  - `DICIONARIO_DADOS` (AOIs, exportações, censo, resultados);
  - `DECISOES` D6 atualizada, novas D9 e D10.
- **Outros:** `requirements.txt` + shapely.
- **Ainda sem resultados:** os scripts 03 e 04 foram testados só com dados
  sintéticos (04) e verificação de sintaxe (03).

## v1.1 (2026-11-16)

- **Script 02:**
  - ruído robusto (MAD das diferenças consecutivas, −90 a −30 d), igual para
    evento e placebo;
  - nova métrica `pico` (janela − ombros) e `z_pico`;
  - nova tabela `resumo_deteccao.csv` (evento × placebo, z > 2 e z > 3);
  - nova figura `zpico_vs_placebo.png`;
  - log com `versao_script`.
- **Motivo:** a inspeção dos falsos positivos do placebo da v1 mostrou o
  desvio-padrão subestimado (baseline de ~4 imagens) e rampas lentas reais
  pré-floração.
- **Resultados:** `results/v1.1/`; docs em `docs/RESULTADOS_v1.1.md`.
- **Docs:** `METODOS` (métricas e parâmetros novos), `DICIONARIO_DADOS` (colunas
  e arquivos novos), `DECISOES` (D4, D6, D7 atualizadas; nova D8, cobertura de
  2017), aviso de revisão em `RESULTADOS_v1`.
- **Outros:** o log passa a registrar caminhos relativos à raiz do repositório.
- **Não alterados:** script 01, dados e `results/v1*` (mantidos como registro
  histórico).

## v1 (2026-11-15)

- Estrutura inicial: dados brutos, consolidados, entrada S2 e exportação GEE;
  scripts 01 (GEE) e 02 (análise); resultados v1 e exploratório ±5 d;
  documentação.
