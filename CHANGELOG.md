# Changelog

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
