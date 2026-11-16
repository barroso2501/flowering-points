# Changelog

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
