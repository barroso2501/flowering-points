# Resultados da varredura nas AOIs v1 (etapas 1 e 3)

**Execução:** 2026-11-16.

**Entradas:**
- exportações do script 03 (`data/gee_exports/aoi_*_v1.csv`);
- censo de 2026-11-16 (`data/censo/censo_v1.kml` e `censo_v1_registro.csv`).

**Regra de detecção avaliada:** pixel com `z_pico > 3`, com pixels vizinhos
agrupados em objetos.

A etapa 2 (validação cega) foi **adiada** (ver D11).

Legenda dos níveis de evidência:
- **[E]** evidência;
- **[H]** hipótese.

## 1. Falso positivo por área (placebo) [E]

| AOI | Índice | Objetos/100 ha: evento | Objetos/100 ha: placebo | Razão |
|---|---|---|---|---|
| AOI10 | IRS (rosa) | 147 | 126 | 1,16 |
| AOI11 | IRS (rosa) | 457 | 344 | 1,33 (só 30% da área avaliável) |
| AOI07–09 | IRS e NDYI | 84–177 | 77–122 | 1,08–1,64 |
| AOI12 | NDYI (amarelo) | 120 | **160** | **0,75** |
| AOI16 | NDYI | 0 | 2 | — |

Com z > 3 por pixel, o placebo gera **~100–160 objetos espúrios por 100 ha**.
Esse número é da mesma ordem das detecções do evento.

Explicação [H]: um teste por pixel (~6.000 pixels em 60 ha) com ~1% de falso
positivo por teste. A taxa por teste medida nos pontos (v1.1) é compatível com
isso.

## 2. Pontos já registrados, mesma data e cor [E]

| AOI | n | z > 3 no evento | z > 3 no placebo |
|---|---|---|---|
| AOI10 (rosa) | 14 | 50% | 7% |
| AOI12 (amarelo) | 21 | 10% | 19% |

O rosa repete a sensibilidade de ~50% do teste por pontos. O amarelo da AOI12
não tem sinal.

## 3. Censo das subparcelas [E]

Contagens:

| Subparcela | Copas (certas) | Incertas | Tempo (min) |
|---|---|---|---|
| AOI10 inteira (rosa) | 29 | 0 | 20 |
| AOI11 inteira (rosa) | 6 | 8 | 15 |
| AOI12 fragmento | 14 | 5 | 25 |
| AOI12 borda | 132 | 22 | 5 (?) |
| AOI12 matriz | **0** | 0 | 30 |

Copas marcadas **fora** das subparcelas: 30 rosas, ao norte da AOI10, até ~700 m.
Não entram no cálculo da etapa 3.

Sensibilidade e precisão (distância de casamento de 20 m), evento × placebo
(o placebo dá o nível do acaso):

| Subparcela | Sensibilidade: evento / acaso | Precisão: evento / acaso |
|---|---|---|
| **AOI10 (rosa)** | **48% / 21%** | **15% / 7%** |
| AOI11 (rosa) | 0% / 0% | 0% / 0% |
| AOI12 fragmento | 14% / 21% | 8% / 8% |
| AOI12 borda | 5% / 8% | 21% / 19% |
| AOI12 matriz (0 copas) | — | 22 detecções, todas falsas (88/100 ha) |

Sensibilidade à distância na AOI10:

| Distância | Sensibilidade: evento / acaso |
|---|---|
| 10 m | 14% / 7% |
| 20 m | 48% / 21% |
| 30 m | 62% / 34% |

O evento fica cerca de 2× acima do acaso em todas as distâncias.

## 4. Leitura

- **Rosa (AOI10):**
  - **há sinal real no nível da copa:** a sensibilidade é cerca de 2× o acaso,
    e ~50% das copas conhecidas são detectadas;
  - **a regra por pixel não serve para varredura cega:** com ~1,3 objeto
    espúrio por hectare, a precisão é de 15%. A maioria das detecções seria
    falsa.
- **Amarelo (AOI12):** nenhum sinal na varredura. Evento ≤ placebo e
  sensibilidade ≤ acaso. Isso confirma o resultado dos pontos: o amarelo não é
  detectável com este método no Sentinel-2.
- **AOI11:** inconclusiva. Só 30% da área tem ruído estimável (janela chuvosa) e
  8 das 14 copas são incertas.

## 5. Implicação para a regra de detecção (D6)

O limiar por pixel precisa ser bem mais restritivo, ou combinado com outros
critérios. Candidatos [H]:
- z mais alto;
- objeto de 2 ou mais pixels;
- máximo local;
- coerência de cor (B4 e B2 sobem, B3 não);
- persistência em 2 ou mais imagens.

Calibrar com o censo da AOI10 traz **risco de sobreajuste**: são só 29 copas.
Um teste independente está disponível: as 30 copas marcadas ao norte da AOI10
estão dentro da área do raster (AOI + 1 km).

## 6. Pendências de dados

- **Registro do censo:** a borda (154 copas) aparece com 5 min, e a matriz (0
  copas) com 30 min. Confirmar se os tempos não estão trocados.
- **As 30 copas fora da AOI10:** confirmar se foram marcadas de propósito, como
  extensão do censo, e se a busca ali foi exaustiva.
