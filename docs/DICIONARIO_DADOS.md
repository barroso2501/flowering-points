# Dicionário de dados

## `data/raw/ipes_ver2_revisado.csv`

Separador `;`, decimal `,`. 495 linhas. Exportação original; **não editar**.

| Coluna | Descrição |
|---|---|
| OBJECTID | ID original do ponto (= `individuo_id` nos derivados) |
| Name | Rótulo original do placemark (não revisado) |
| FolderPath, LabelID | Metadados do KML (sem uso) |
| Data | Data anotada manualmente (esparsa; às vezes diverge de `data_imagem`) |
| POINT_X, POINT_Y | Longitude, latitude (graus decimais, WGS84) |
| data_imagem | Data da imagem GE com floração (formatos mistos) |
| especie_grupo | Classe de cor revisada: amarelo, rosa, roxo, sucupira, descartar |
| contexto | pastagem, cerradao_savana, mata_galeria, borda_estrada, outro |
| confianca_visual | alta, media, baixa (atribuição visual, não calibrada) |
| observacoes | Texto livre; "OIP" = outros indivíduos próximos |

## `data/processed/ipes_eventos_consolidados.csv`

Uma linha por evento de floração. 498 eventos, 490 indivíduos.

| Coluna | Tipo | Descrição |
|---|---|---|
| evento_id | texto | `<individuo_id>_<n>` |
| individuo_id | inteiro | = OBJECTID |
| lat, lon | real | WGS84 |
| data_evento | data ISO | Data da imagem GE com floração |
| ano, mes | inteiro | Derivados de `data_evento` |
| classe_flor | texto | amarelo, rosa, roxo, sucupira |
| contexto | texto | Como no bruto |
| confianca | texto | alta, media, baixa |
| oip_presente | booleano | Observação menciona outros indivíduos próximos |
| oip_multicor | booleano | OIP inclui outra cor de flor |
| area_interesse | booleano | Observação menciona "área de interesse" |
| observacoes_originais | texto | Texto livre original |

## `data/processed/ipes_eventos_s2_input.csv`

Subconjunto elegível para o Sentinel-2. 481 eventos, 78 clusters
(md5 `be871cca28610115b376cb3ebf5a7f4f`).

| Coluna | Descrição |
|---|---|
| evento_id, individuo_id, lat, lon, data_evento, classe_flor, contexto, confianca | Como no consolidado |
| oip_presente | 0/1 |
| suspeito | 1 = caso com inconsistência conhecida (IDs 70, 438) |
| cluster_id | `AAAAMMDD_<lat/0,05>_<lon/0,05>`: unidade de independência |

## `data/gee_exports/ipes_s2_series_v1.csv`

Saída do script 01: uma linha por evento × imagem Sentinel-2. v1: 19.397
linhas (md5 `5422ec5a2c1f1fadcde1f7eb36960e49`).

| Coluna | Descrição |
|---|---|
| evento_id | Chave para a tabela de entrada |
| data_img | Data da imagem S2 |
| dias_rel | `data_img − data_evento` (dias) |
| tile, orbita | Tile MGRS e órbita relativa |
| frac_limpo_n, frac_limpo_a | Fração de pixels limpos (Cloud Score+) no núcleo e no anel |
| n_B2 … n_B11 | Reflectância média no núcleo (0–1) |
| n_NDVI, n_NDYI, n_IRS | Índices médios no núcleo |
| a_* | Mesmas variáveis, mediana no anel |
| nmax_NDYI, nmax_IRS | Máximo do índice no núcleo |

Valores vazios = geometria totalmente mascarada naquela imagem.

## `results/vN/` (saídas do script 02)

| Arquivo | Conteúdo |
|---|---|
| `detectabilidade_por_evento.csv` | Tabela de entrada + `n_img_evento`, `dias_img_mais_proxima`, `n_img_base`, `delta`, `z`, `delta_max`, `delta_placebo`, `z_placebo` |
| `disponibilidade.csv` | Por classe × contexto: n, fração de eventos com imagem, mediana da distância até a imagem mais próxima |
| `resumo_sinal.csv` | Por grupo e métrica: n de eventos e de clusters, mediana, fração de eventos positivos, p de Wilcoxon por cluster |
| `curva_contraste.png` | Contraste núcleo−anel × dias (mediana e IQR em bins de 5 dias), por classe |
| `delta_vs_placebo.png` | (v1) Histogramas do delta do evento e do placebo |
| `zpico_vs_placebo.png` | (v1.1) Histogramas de `z_pico` do evento e do placebo, com limiares 2 e 3 |
| `resumo_deteccao.csv` | (v1.1) Por classe, métrica e limiar: n e fração acima do limiar, evento × placebo |
| `log_execucao.json` | Hashes das entradas, parâmetros, versões (v1.1 inclui `versao_script`) |

Colunas acrescentadas em `detectabilidade_por_evento.csv` na v1.1:

| Coluna | Descrição |
|---|---|
| ruido | Ruído robusto do contraste (MAD das diferenças consecutivas, −90 a −30 d) |
| z_rob, z_placebo_rob | Delta do evento e do placebo divididos por `ruido` |
| pico, pico_placebo | Janela (±10 d) menos a média dos ombros; centrado em 0 e em −50 d |
| z_pico, z_pico_placebo | `pico` e `pico_placebo` divididos por `ruido` |

## `data/aoi/aois_v1.geojson`

Normalização das 17 AOIs de `data/raw/aois_poligonos.geojson`. Geometria
original.

| Campo | Descrição |
|---|---|
| aoi_id | `AOI00`–`AOI16` (ordem do arquivo original) |
| id_kml, nome_original | Identificador e nome do placemark no GE |
| data_aoi | Primeira data da descrição, em ISO |
| datas_todas | Todas as datas da descrição |
| classes | amarelo, rosa, "amarelo,rosa", palmeira, indefinido |
| status | apta_s2, lacuna_L2A_2017, pre_sentinel, fora_escopo |

O campo original `pasta_origem` ("placas solares") foi descartado: é um rótulo
de pasta reaproveitado no GE, não informação sobre as áreas.

## Exportações do script 03 (`data/gee_exports/`)

| Arquivo | Conteúdo |
|---|---|
| `aoi_deteccoes_v1.csv` | Um objeto detectado por linha: aoi_id, data_aoi, indice (IRS/NDYI), tipo (evento/placebo), lon, lat (centroide), z_max, n_pixels |
| `aoi_resumo_v1.csv` | Por AOI × índice: área da AOI e áreas avaliáveis (ha, pixels com z calculado) no evento e no placebo; nº de datas |
| `aoi_pontos_v1.csv` | Pontos a até 1 km da AOI: evento_id, data_evento, classe_flor, z_evento e z_placebo (máximo num raio de 15 m) |
| `aoi_z_AOIxx.tif` | Raster EPSG:4326, 10 m: z_evento_IDX, z_placebo_IDX, ruido_IDX (AOI + 1 km) |
| `subparcelas_censo_v1.kml` | Subparcelas do censo (mover para `data/aoi/`) |

## Censo (`data/censo/censo_v1.kml`)

Placemarks de ponto, um por copa florida. O nome indica a cor: `r` (rosa ou
roxo), `a` (amarelo), `o` (outra); `?` = incerto; `+` = grupo. Ver
`PROTOCOLO_CENSO.md`.

## `results/aoi_v1/` (script 04)

| Arquivo | Etapa | Conteúdo |
|---|---|---|
| `densidade_deteccoes.csv` | 1 | Objetos por 100 ha no evento e no placebo, razão e excesso |
| `deteccao_pontos_registrados.csv` | 1 | Por AOI × índice: n de pontos da mesma data e cor, fração com z > 3 (evento e placebo) |
| `validacao_amostra_cega.kml`, `validacao_template.csv` | 1 | Amostra para a validação visual |
| `_chave_amostra_NAO_ABRIR.csv` | 1 | Tipo (detecção/controle) e z de cada código da amostra |
| `precisao_validacao.csv`, `respostas_validacao.csv` | 2 | Precisão e taxa de flor nos controles |
| `censo_sensibilidade_precisao.csv` | 3 | Por subparcela × índice: copas, detecções, sensibilidade, precisão |
| `log_etapaN.json` | todas | Proveniência |
