# Resultados v1.1 da varredura: por que a descoberta às cegas não funciona

**Execução:** 2026-11-16. Script `scripts/06_analise_fragmento.py`.

**Entradas:** raster `aoi_z_AOI10.tif` (script 03), registros do censo
(`data/release_v1/`) e o polígono do fragmento percorrido.

**Saídas:** `results/aoi_v1.1/`.

**Conclusão:** o sinal temporal do Sentinel-2 detecta a floração de **copas
rosas de posição conhecida**, mas **não descobre copas às cegas**. As copas
floridas ocupam menos de 1% dos pixels. Por isso, mesmo uma taxa baixa de falso
positivo por pixel produz mais detecções falsas do que verdadeiras, em qualquer
limiar.

Legenda dos níveis de evidência:
- **[E]** evidência;
- **[H]** hipótese.

## Área de teste [E]

- **Fragmento percorrido no censo da AOI10:** 200 ha, dos quais 190 ha estão
  dentro do raster. Contém 98% da AOI10.
- **Copas:** contém todas as 59 copas rosas do censo, 57 certas.
- **Divisão:**
  - **calibração** = AOI10 inteira (29 copas);
  - **teste** = fragmento fora da AOI10 (28 copas).
- **Ressalva:** as copas de teste coincidem em boa parte com os pontos da
  inspeção 458–471, usados no teste por ponto da v1.1. Não foram usadas para
  calibrar a regra por pixel.

## 1. Pixels acima do limiar: evento × placebo [E]

| Limiar | AOI10: evento / placebo | Fragmento fora da AOI10: evento / placebo |
|---|---|---|
| z > 3 | 1,69% / 1,23% | 1,63% / 1,55% |
| z > 4 | 0,75% / 0,45% | 0,67% / 0,74% |
| z > 6 | 0,26% / 0,05% | 0,23% / 0,21% |
| z > 8 | 0,10% / 0,03% | 0,07% / 0,06% |

Na área de teste, evento e placebo são indistinguíveis na escala do pixel.

## 2. Detecção nas copas do censo (máximo de z na janela 3×3) [E]

| Limiar | Calibração: evento / placebo | Teste: evento / placebo |
|---|---|---|
| z > 3 | 38% / 10% | 50% / 7% |
| z > 4 | 24% / 10% | 36% / 4% |
| z > 6 | 14% / 0% | 21% / 4% |
| z > 8 | 3% / 0% | 11% / 0% |

As copas têm sinal. No teste, a detecção fica cerca de 5× acima do placebo.

## 3. Balanço no fragmento (19.694 pixels, 57 copas) [E]

| Limiar | Pixels falsos esperados | Copas detectadas | Precisão máxima aproximada |
|---|---|---|---|
| z > 3 | 304 | 25 | 8% |
| z > 4 | 146 | 17 | 10% |
| z > 5 | 74 | 12 | 14% |
| z > 6 | 40 | 10 | 20% |
| z > 8 | 12 | 4 | 26% |

Subir o limiar reduz a sensibilidade mais rápido do que aumenta a precisão.

Esta tabela conta cada pixel falso como uma detecção. Agrupar pixels em
objetos reduz um pouco o número de falsos, mas não muda a ordem de grandeza.

## Implicações

- **Acompanhamento de copas conhecidas** (histórico de floração por indivíduo
  rosa): viável.
  - **Sensibilidade:** 40–50% por floração.
  - **Falso positivo:** 5–10% por copa testada, com z > 3.
- **Descoberta às cegas:** inviável só com z_pico. Restaria testar critérios
  independentes do z: coerência de cor (B4 e B2 sobem, B3 não), forma do
  objeto, persistência em 2 ou mais imagens. Expectativa [H]: melhora a
  precisão, mas não para níveis utilizáveis.
- **Amarelo:** não há sinal individual nem com a posição conhecida (D12). A
  hipótese aberta é detectar na escala de população, somando muitas copas por
  data.
