# Resultados v1: detectabilidade no Sentinel-2

> **Revisado na v1.1:** o z e o placebo desta versão usam um desvio-padrão
> subestimado (baseline curta), e as taxas de falso positivo abaixo estão
> infladas. Ver [`RESULTADOS_v1.1.md`](RESULTADOS_v1.1.md). Os deltas e os
> testes por cluster continuam válidos.

**Execução:** 2026-11-15.

**Entradas:**
- `ipes_eventos_s2_input.csv` (md5 `be871cca…`);
- `ipes_s2_series_v1.csv` (md5 `5422ec5a…`).

**Análise principal:** confiança alta, sem suspeitos. Rosa: 295 eventos em 43
clusters. Amarelo: 161 eventos em 35 clusters.

Legenda dos níveis de evidência:
- **[E]** evidência, resultado do teste pré-especificado;
- **[X]** exploratório, decidido após ver os dados;
- **[H]** hipótese.

## 1. Disponibilidade de imagens [E]

- **Cobertura:** 473 dos 481 eventos (98%) têm 1 ou mais imagens limpas a até
  ±10 dias.
- **Proximidade:** a mediana da distância até a imagem limpa mais próxima é de
  1 a 2 dias em todos os contextos.

A cobertura de nuvens na estação seca não é limitante.

## 2. Placebo [E]

Mediana entre clusters próxima de 0 nas duas classes:
- amarelo: 0,002 (p = 0,29);
- rosa: −0,0001 (p = 0,43).

**Exceção:** rosa × pastagem, placebo = 0,011 (p = 0,009, 11 clusters). O fundo
de pastagem tem deriva própria. Nesse estrato, o sinal precisa ser lido contra
esse valor, não contra zero.

## 3. Sinal: janela de ±10 dias, pré-especificada [E]

| | Rosa (IRS) | Amarelo (NDYI) |
|---|---|---|
| Delta, mediana entre clusters | **0,038** (p < 0,0001) | 0,0025 (p = 0,027) |
| Eventos com delta > 0 | 89% | 64% |
| Eventos com z > 2 (placebo) | **61%** (6%) | 16% (4%) |
| `delta_max`, mediana entre clusters | 0,053 | −0,002 (n.s.) |

**Rosa:**
- O sinal é significativo em todos os contextos com 6 ou mais clusters:
  cerradão 0,040; borda de estrada 0,055; pastagem 0,036.
- **Isolado (sem OIP) ≥ com OIP:** delta > 0 em 88% contra 90% dos eventos;
  `delta_max` 0,057 contra 0,043. Isso contraria a expectativa prévia de que
  só agrupamentos seriam detectáveis. Explicação provável [H]: outros ipês no
  anel reduzem o contraste.

**Curva temporal do rosa:**
- o contraste sobe a partir de cerca de −15 dias;
- tem pico em 0 a 5 dias (~0,07, contra ~0,005 na baseline);
- volta à baseline perto de +20 dias.

**Amarelo:**
- A curva mediana mostra pico estreito, praticamente restrito a 0 a 5 dias
  (~0,023 contra ~0,009). A janela de ±10 dias dilui esse pico.
- Depois de +20 dias, há deriva positiva, compatível com a secagem do capim [H].

## 4. Janela de ±5 dias [X]

Testada após inspeção da curva.

| | Rosa | Amarelo |
|---|---|---|
| Delta, mediana entre clusters | 0,052 | 0,015 (p < 0,0001) |
| Eventos com z > 2 | 76% | 24% |
| Amarelo × pastagem | — | 0,014 (p < 0,001) |

**Precisa de confirmação em dados independentes** (próxima estação, revisitas)
antes de virar parâmetro.

## 5. Flor ou desfolha? Assinatura por banda [E, interpretação H]

Mudança do contraste núcleo−anel entre o evento (±10 d) e a baseline, mediana
entre clusters:

| Banda | Rosa | Amarelo |
|---|---|---|
| B2 (azul) | +0,0020 | +0,0006 |
| B3 (verde) | +0,0008 | +0,0030 |
| B4 (vermelho) | +0,0044 | +0,0021 |
| NDVI | −0,026 (pós +30 d: −0,003) | −0,016 (pós: −0,004) |

**Interpretação [H]:**
- **Rosa:** sobem o vermelho e o azul, com o verde estável. É coerente com
  pétalas rosa e menos coerente com casca e solo expostos, que tenderiam a
  elevar também o B3.
- **Amarelo:** sobem o verde e o vermelho, com o azul estável. É coerente com
  flor amarela.
- **NDVI:** cai e se recupera, o que é compatível com floração seguida de
  rebrota, mas **não exclui desfolha**.

**Pendente:** passar pela mesma análise uma amostra de copas desfolhadas sem
flor (verificadas no GE).

## 6. Conclusão operacional

- **Rosa:** detectável no Sentinel-2 em nível de evento individual em cerca de
  60–75% dos casos, com placebo baixo. É viável para relocalizar copas e
  reconstruir históricos de floração.
- **Amarelo:** sinal médio real, mas fraco no nível individual. Antes de
  qualquer uso, depende da confirmação da janela curta.
