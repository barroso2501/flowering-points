# flowering-points

Copas floridas de ipês (*Handroanthus* spp. e afins) identificadas visualmente
em imagens de alta resolução (Google Earth), e testes de detectabilidade dessa
floração no Sentinel-2.

> **Projeto congelado em 2026-11-16.** Disponível para quem quiser continuar.
> Comece pelo [`docs/GUIA_INTERESSADOS.md`](docs/GUIA_INTERESSADOS.md).

## Em três frases

- **Rosa:** a floração de copas rosas **de posição conhecida** é detectável no
  Sentinel-2 em ~40–50% das florações, com 5–10% de falso positivo por copa
  testada.
- **Descoberta às cegas:** não funciona, porque as copas floridas ocupam menos
  de 1% dos pixels; a precisão fica ≤ 26% em qualquer limiar.
- **Amarelo:** não é detectável individualmente com este método.

## O que há aqui

| Para quê | Onde |
|---|---|
| **Todos os pontos rotulados** (745 registros: inspeção + censo), prontos para uso | [`data/release_v1/`](data/release_v1/LEIAME.md) |
| Guia para quem quer continuar | [`docs/GUIA_INTERESSADOS.md`](docs/GUIA_INTERESSADOS.md) |
| Resultados, na ordem em que foram obtidos | `docs/RESULTADOS_v1.md` → `RESULTADOS_v1.1.md` → `RESULTADOS_aoi_v1.md` → `RESULTADOS_aoi_v1.1.md` |
| Métodos e parâmetros | [`docs/METODOS.md`](docs/METODOS.md) |
| Decisões, o que um revisor atacaria e o estado de cada uma no congelamento | [`docs/DECISOES.md`](docs/DECISOES.md) |
| Colunas de todos os arquivos | [`docs/DICIONARIO_DADOS.md`](docs/DICIONARIO_DADOS.md) |
| Protocolo do censo e da validação visual | [`docs/PROTOCOLO_CENSO.md`](docs/PROTOCOLO_CENSO.md) |
| Histórico de versões | [`CHANGELOG.md`](CHANGELOG.md) |

## Estrutura

```
flowering-points/
├── data/
│   ├── raw/            # originais (não editar): pontos, AOIs, polígono do fragmento
│   ├── processed/      # eventos consolidados; entrada do teste Sentinel-2
│   ├── aoi/            # AOIs normalizadas; subparcelas sorteadas para o censo
│   ├── censo/          # censo exaustivo (KML), registro de esforço, área percorrida
│   ├── gee_exports/    # exportações do GEE (CSV); rasters .tif não versionados
│   └── release_v1/     # >>> conjunto de entrega: CSV, GeoJSON, GeoPackage <<<
├── scripts/
│   ├── 01_gee_extrair_series_s2.js      # GEE: séries S2 por ponto (núcleo × anel)
│   ├── 02_analisar_detectabilidade.py   # teste por ponto: delta, z_pico, placebo
│   ├── 03_gee_varredura_aoi.js          # GEE: z_pico por pixel nas AOIs; subparcelas
│   ├── 04_analisar_varredura.py         # densidade, validação, censo
│   ├── 05_consolidar_rotulos.py         # gera data/release_v1
│   └── 06_analise_fragmento.py          # por que a varredura cega falha
├── results/            # v1, v1_exploratorio_janela5, v1.1, aoi_v1, aoi_v1.1
└── docs/
```

## Reprodução

- **Ambiente:** Python ≥ 3.10; `pip install -r requirements.txt`. GEE Code
  Editor para os scripts `.js`.
- **Ordem e comandos:** cabeçalho de cada script e `docs/METODOS.md`.
- **Caminhos:** todos os scripts Python rodam a partir da raiz do repositório.
- **Proveniência:** cada execução grava um `log_*.json` com os hashes das
  entradas, os parâmetros e as versões dos pacotes.
- **Integridade:** `MANIFEST.sha256` lista o hash de cada arquivo versionado
  (`shasum -a 256 -c MANIFEST.sha256`).
- **Nível de reprodutibilidade: básico.**
  - **O que se reproduz:** do CSV de entrada às tabelas e figuras.
  - **O que fica fora do repo:** os rasters `.tif` do script 03 ficam no Drive e
    são regeneráveis pelo script.
  - **O que não é congelável:** as coleções do GEE são reprocessadas ao longo do
    tempo; por isso, as exportações CSV estão versionadas.
  - **O que não é reexecutável:** a consolidação manual raw → processed (v1)
    está descrita, mas não automatizada.

## Licença e citação

**A definir pelo autor antes da divulgação.** Ver `CITATION.cff`.

## Autoria

Mario Barroso Ramos Neto: registro dos pontos, censo, desenho das perguntas e
das decisões.

Scripts e análises desenvolvidos com assistência de IA (Claude, Anthropic).
