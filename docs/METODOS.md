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

## 5. Parâmetros

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
