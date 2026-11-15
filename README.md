# flowering-points

Repositório de organização de pontos de referência georreferenciados e datados para espécies arbóreas de floração conspícua e deciduidade no bioma Cerrado (*Handroanthus* spp., *Bowdichia virgilioides*, entre outras), voltado à exploração de assinaturas espectrais e fenológicas em sensores orbitais (Sentinel-2, PlanetScope e imagens de altíssima resolução).

## Contexto e Motivação

Eventos de floração massiva e caducifolia sincronizada na estação seca do Cerrado produzem anomalias espectrais transitórias de curtíssima duração (tipicamente 3 a 7 dias). Embora a discriminação taxonômica orbital fora da janela reprodutiva seja limitada pela sobreposição estrutural e foliar no dossel, o registro sistemático de coordenadas ancoradas à **data exata do imageamento** permite:

1. Calibrar detectores de anomalias fenológicas temporais em séries densas (Sentinel-2 / PlanetScope).
2. Fornecer dados de presença de alta confiabilidade espacial e taxonômica para modelagem de nicho e distribuição.
3. Investigar padrões interanuais de alternância reprodutiva (indivíduos distintos florindo em anos distintos na mesma localidade).

## Estrutura do Repositório

```text
flowering-points/
├── data/
│   ├── raw/
│   │   └── ipes_ver2_revisado.csv            # Tabela bruta revisada a partir das inspeções no Google Earth
│   └── processed/
│       └── ipes_eventos_consolidados.csv     # Base limpa, padronizada (ISO 8601) e desdobrada por evento (ponto + data)
├── scripts/
│   ├── 01_inspecao_interativa_ge.py          # Ferramenta CLI para revisão visual sequencial no Google Earth
│   └── 02_consolidar_eventos.py              # Pipeline de limpeza, padronização de datas e extração de flags espaciais
├── docs/
│   └── dicionario_dados.md                   # Especificação dos atributos, vocabulários controlados e limitações conhecidas
├── .gitignore
├── LICENSE
└── README.md
```

## Resumo da Base Atual (`data/processed/ipes_eventos_consolidados.csv`)

* **Indivíduos físicos mapeados:** 490 (após descarte de 5 registros inconsistentes).
* **Eventos fenológicos validados (`ponto + data`):** 498 (incluindo re-observações multi-ano nos mesmos pontos).
* **Grupos funcionais de florada:**
  * `rosa`: 303 eventos (complexo *Handroanthus* rosa/magenta)
  * `amarelo`: 183 eventos (complexo *Handroanthus* amarelo)
  * `roxo`: 10 eventos
  * `sucupira`: 2 eventos (*Bowdichia virgilioides*)
* **Contextos de paisagem:** `cerradao_savana` (324), `pastagem` (121), `borda_estrada` (38), `mata_galeria` (14), `outro` (1).

## Próximos Passos

* **Módulo 03 (Google Earth Engine):** Cruzamento das coordenadas e datas (`data_evento`) com a coleção `COPERNICUS/S2_SR_HARMONIZED` para avaliar disponibilidade de cenas livres de nuvens ($\pm 5$ dias) e extrair perfis espectrais/temporais (RGB, Red-Edge, NIR, SWIR e índices fenológicos).
* **Integração de Polígonos (AOIs):** Incorporação dos polígonos de agrupamento populacional (*hotspots* de floração sincrônica).

## Licença

Dados disponibilizados sob licença CC-BY-4.0 e código sob licença MIT (ver `LICENSE`).
