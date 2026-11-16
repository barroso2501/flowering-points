# Métodos

## 1. Origem dos registros

- **Contexto:** durante a inspeção visual de áreas em regeneração no Cerrado,
  em imagens de alta resolução do Google Earth (GE), foram registradas copas com
  floração conspícua.
- **O que é um registro:** um ponto colocado sobre a copa florida, com a data
  da imagem do GE em que a floração é visível.
- **Atributos atribuídos visualmente:** classe de cor da flor, contexto da
  paisagem, confiança visual e presença de outros indivíduos próximos (OIP).
- **Natureza amostral:** presença oportunista. Só é registrado o que estava
  florido numa data em que existe imagem de alta resolução, ao longo da rota
  de inspeção. Ausência de registro **não** é ausência da espécie.

## 2. Consolidação (raw → processed, v1)

Arquivo bruto: `ipes_ver2_revisado.csv` (495 pontos, separador `;`, decimal `,`).

Regras aplicadas para gerar `ipes_eventos_consolidados.csv`:

1. **Estrutura:** uma linha por evento de floração (`evento_id = <individuo>_<n>`).
   Indivíduos com floração registrada em duas datas geram dois eventos.
   Resultado: 490 indivíduos, 498 eventos.
2. **Datas:** convertidas para ISO (`AAAA-MM-DD`). Quando os campos `Data` e
   `data_imagem` divergiam, os dois viraram eventos distintos (IDs 142, 347, 364).
3. **Exclusões:** 5 IDs removidos.
   - 226–228: data marcada como "Ni O USAR";
   - 288–289: classe "descartar".
4. **Classe:** usada a coluna revisada `especie_grupo` (→ `classe_flor`).
   O campo `Name` (rótulo original) divergia em 13 registros.
5. **Campos derivados:** extraídos das observações em texto livre.
   - `oip_presente`;
   - `oip_multicor` (OIP de mais de uma cor);
   - `area_interesse`.

**Pendência de reprodutibilidade:** a consolidação v1 não está em script. As
regras acima a descrevem, mas não a reexecutam.

### Subconjunto para o Sentinel-2 (`ipes_eventos_s2_input.csv`, 481 eventos)

- `data_evento >= 2017-04-01`. A coleção S2 L2A harmonizada só tem cobertura
  consistente a partir de 2017; a baseline usa 90 dias antes do evento.
- `classe_flor ∈ {rosa, amarelo}`. Roxo (8 eventos, todos de 2016) e sucupira
  (1) ficaram fora.
- Removido o evento `364_2`, quase certamente o mesmo evento de `364_1`
  (24 × 25/05/2024).
- **Mantidos, mas marcados** `suspeito = 1`:
  - ID 70: único amarelo em junho, dentro de um cluster de rosas;
  - ID 438: data original "2", reclassificado de rosa para amarelo.
- `cluster_id` = data do evento + célula de ~0,05° (≈5 km). Define a unidade
  de independência nos testes.

## 3. Extração Sentinel-2 (`01_gee_extrair_series_s2.js`)

### Imagens

- **Coleção:** `COPERNICUS/S2_SR_HARMONIZED` (L2A).
- **Nuvem:** máscara **por pixel** com Cloud Score+
  (`GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED`), mantendo `cs_cdf ≥ 0,60`. Não se
  usa filtro de nebulosidade por cena.
- **Período:** para cada evento, todas as imagens de −90 a +60 dias da data do
  evento no GE.

### Geometrias por evento

| Geometria | Definição | Estatística | Função |
|---|---|---|---|
| Núcleo | buffer de 15 m em torno do ponto (~7 px) | média das bandas e índices; máximo de NDYI e IRS | sinal da copa; o máximo tolera erro de posição de alguns metros |
| Anel | coroa de 40–80 m (~150 px) | mediana | fundo local (controle espacial) |

Também é registrada a fração de pixels limpos em cada geometria.

### Índices

| Índice | Fórmula (bandas S2) | Alvo | Status |
|---|---|---|---|
| NDVI | (B8−B4)/(B8+B4) | vigor foliar | padrão |
| NDYI | (B3−B2)/(B3+B2) | flor amarela | da literatura de floração de canola; **não validado para ipê** |
| IRS | (B4+B2−2·B3)/(B4+B2+2·B3) | flor rosa/magenta (reflete R e B, absorve G) | **definido neste projeto, exploratório** |

## 4. Análise (`02_analisar_detectabilidade.py`)

### Filtros

- Por evento e data, quando dois tiles MGRS se sobrepõem, fica a observação com
  maior fração limpa no núcleo.
- Só entram observações com fração limpa ≥ 0,9 **no núcleo e no anel**.
- Análise principal: `confianca == alta` e `suspeito == 0`.

### Estatística por evento: diferença em diferenças

- **Contraste:** `c(t) = índice_núcleo(t) − índice_anel(t)`. O índice usado é o
  NDYI para amarelo e o IRS para rosa.
- **Delta:** `delta = mediana[c(t), t ∈ janela do evento] − mediana[c(t), t ∈ baseline]`.
  - Janela do evento: ±10 dias.
  - Baseline: −90 a −30 dias.
- **z:** `z = delta / dp(c na baseline)`, calculado quando há 3 ou mais imagens
  na baseline.
- **`delta_max`:** a mesma estatística, usando o máximo do índice no núcleo.

O desenho remove (a) diferenças fixas entre o ponto e o entorno e (b) variações
sazonais que afetam núcleo e anel igualmente.

### Placebo

A mesma estatística é calculada numa "data falsa" pré-floração (−60 a −40
dias, contra a baseline de −90 a −65). Placebo diferente de zero indica que o
"sinal" vem de sazonalidade ou ruído, não da flor.

### Métricas adicionadas na v1.1

- **Ruído robusto (`ruido`):** MAD das diferenças entre imagens consecutivas
  de −90 a −30 dias, × 1,4826 / √2, exigindo 5 ou mais imagens. Remove
  tendências lentas e resiste a valores extremos. É o mesmo para o evento e o
  placebo.
  - **Ressalva:** se o ruído for autocorrelacionado entre imagens próximas, o
    estimador o subestima.
- **`z_rob` e `z_placebo_rob`:** o delta (do evento ou do placebo) dividido pelo
  `ruido`.
- **Pico:** `pico = mediana[c, ±10 d] − ½·(mediana[c, −30 a −15 d] + mediana[c, +20 a +35 d])`.
  Mede um aumento transitório; uma rampa lenta eleva os ombros e não gera pico.
  - **Placebo:** as mesmas janelas centradas em −50 dias (`pico_placebo`).
  - **`z_pico`** = `pico / ruido`.
- **Taxas de detecção:** fração de eventos com z > 2 e z > 3, evento × placebo
  (`resumo_deteccao.csv`). A taxa do placebo é a estimativa empírica de falso
  positivo por teste.

### Inferência

- **Unidade:** eventos do mesmo cluster não são independentes. O delta é
  agregado por cluster (mediana) antes do teste.
- **Teste:** Wilcoxon unilateral (H1: delta > 0), quando há 6 ou mais clusters.
- **Estratificação:** por classe, por classe × contexto e por classe × OIP.

### Disponibilidade

Por evento: número de imagens limpas na janela e distância (em dias) até a
imagem limpa mais próxima.

## 5. Varredura por pixel nas AOIs (scripts 03 e 04)

### Áreas de interesse

As AOIs são polígonos desenhados durante a inspeção em torno de regiões com
muitas copas floridas, das quais só algumas foram marcadas como ponto.
- **Arquivos:** bruto em `data/raw/aois_poligonos.geojson` (17 polígonos);
  versão normalizada em `data/aoi/aois_v1.geojson`.
- **Campos normalizados:** `aoi_id`, data ISO, classes e `status`.
- **Natureza dos recortes:** amplos, podendo conter um grande fragmento e sua
  borda (predominantemente pastagem), ou vários fragmentos e matriz.

Status:
- **`apta_s2`** (7 AOIs, ~9.200 ha): AOI07–09 (amarelo e rosa, 08/09/2021),
  AOI10 (rosa, 24/07/2021), AOI11 (rosa, 26/05/2019), AOI12 (amarelo,
  02/09/2025), AOI16 (amarelo, 30/08/2024);
- `lacuna_L2A_2017` (AOI00–04): dependem da D8;
- `pre_sentinel` (AOI13–15, 2004 e 2013): fora;
- `fora_escopo` (AOI05–06, palmeiras).

### Pergunta

Com a data conhecida, mas **sem saber onde estão as copas**, quantas manchas o
método detecta por área, quantas delas são flor e quantas florações ele perde?

### Cálculo por pixel (script 03)

A mesma lógica do script 02 v1.1, aplicada a cada pixel:
- **Contraste:** `c(t) = índice(t) − mediana do índice num anel de 40–80 m`
  (kernel fixo em anel). Índice: IRS para rosa, NDYI para amarelo; nas AOIs
  mistas, os dois.
- **Ruído:** MAD das diferenças entre datas consecutivas (−90 a −30 dias,
  exigindo 4 ou mais diferenças) × 1,4826 / √2.
- **Pico e z_pico:** como no script 02, na data da AOI (evento) e em −50 dias
  (placebo).
- **Mosaico diário:** um mosaico por dia, para não duplicar datas onde dois
  tiles se sobrepõem.
- **Detecção:** `z_pico > 3`. Pixels detectados vizinhos (8-conectividade)
  formam um **objeto**; exporta-se o centroide, o número de pixels e o z
  máximo.

### Métricas (script 04)

- **Etapa 1:**
  - objetos por 100 ha no evento e no placebo; o placebo é o **falso positivo
    por área**;
  - excesso evento − placebo;
  - fração dos pontos já registrados (mesma data e cor) com z > 3 num raio de
    15 m;
  - amostra cega (30 detecções + 15 controles aleatórios por AOI × índice).
- **Etapa 2:** precisão = fração de `sim` nas detecções da amostra cega; a taxa
  de `sim` nos controles dá a base.
- **Etapa 3:** com o censo das subparcelas,
  - sensibilidade = fração das copas do censo com detecção a ≤ 20 m;
  - precisão = fração das detecções a ≤ 20 m de uma copa do censo.

### Subparcelas do censo

- AOI10 e AOI11: AOI inteira.
- AOI12: 3 quadrados de 500 m sorteados (300 candidatos, semente 42), um por
  estrato de cobertura lenhosa natural (MapBiomas, classes 3, 4 e 6).
  Estratos: fragmento (70% ou mais), borda (30–70%), matriz (menos de 30%).
- O protocolo está em [`PROTOCOLO_CENSO.md`](PROTOCOLO_CENSO.md).

### Limitações conhecidas

- **Ruído nas AOIs de 2019:** a janela pré-floração da AOI11 (fev–mai) é
  chuvosa; pode haver poucas datas limpas e ruído mal estimado.
- **MapBiomas:** usa a Coleção 9, ano 2023, como referência para todas as AOIs.
  O caminho da coleção mais recente deve ser verificado no catálogo.
- **Objetos ≠ copas:** um objeto pode conter várias copas, e uma copa grande pode
  gerar mais de um objeto se o z oscilar.
- **Distância de casamento:** os 20 m entre o censo e a detecção são uma escolha
  (erro de posição do GE mais o tamanho do pixel); não foram calibrados.

## 6. Parâmetros

| Parâmetro | Valor v1 | Onde |
|---|---|---|
| `DIAS_ANTES` / `DIAS_DEPOIS` | 90 / 60 | script 01 |
| `CS_LIMIAR` | 0,60 | script 01 |
| `R_NUCLEO` | 15 m | script 01 |
| `R_ANEL_INT` / `R_ANEL_EXT` | 40 / 80 m | script 01 |
| `JANELA_EVENTO` | (−10, 10) dias; (−5, 5) testado post hoc | script 02 |
| `JANELA_BASE` | (−90, −30) dias | script 02 |
| `PLACEBO_EV` / `PLACEBO_BASE` | (−60, −40) / (−90, −65) dias | script 02 |
| `MIN_LIMPO` | 0,9 | script 02 |
| `MIN_N_BASE` | 3 | script 02 |
| `JANELA_RUIDO` | (−90, −30) dias | script 02 (v1.1) |
| `MIN_N_RUIDO` | 5 | script 02 (v1.1) |
| `OMBRO_ANTES` / `OMBRO_DEPOIS` | (−30, −15) / (+20, +35) dias, relativos ao centro | script 02 (v1.1) |
| `LIMIARES_Z` | 2 e 3 | script 02 (v1.1) |
| `LIMIAR_Z` | 3 | scripts 03 e 04 |
| `CENTRO_PLACEBO` | −50 dias | script 03 |
| Anel por pixel | 4–8 pixels (40–80 m) | script 03 |
| `LADO_SUBPARCELA` / `SEMENTE` | 500 m / 42 | script 03 |
| `N_DETEC_AMOSTRA` / `N_CONTROLES` | 30 / 15 por AOI × índice | script 04 |
| `DIST_MATCH` | 20 m | script 04 |
