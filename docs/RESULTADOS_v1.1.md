# Resultados v1.1: revisão do ruído e métrica de pico

**Execução:** 2026-11-16. Script 02 v1.1.

**Entradas:** idênticas às da v1. Hashes em `results/v1.1/log_execucao.json`.

**Análise principal:** confiança alta, sem suspeitos.

**Motivação:** na v1, o z do placebo passava de 2 em 6% (rosa) e 4% (amarelo)
dos eventos. A inspeção desses casos mostrou duas causas:

1. **Baseline do placebo curta** (25 dias, ~4 imagens): o desvio-padrão saía
   subestimado e inflava o z. Exemplo: o evento 77_1, com z de placebo = 38.
   Nos eventos com z de placebo > 2, o desvio-padrão mediano era 0,007; nos
   demais, 0,012.
2. **Rampas lentas e reais** do contraste (eventos 73_1, 443_1, 77_1): o
   contraste sobe aos poucos semanas antes da floração. Candidatos [H]:
   desfolha da copa ou secagem diferencial do fundo. Não é ruído, mas também
   não é flor.

## Mudanças no método

- **Ruído robusto:** o desvio absoluto mediano (MAD) das diferenças entre
  imagens consecutivas de −90 a −30 dias, × 1,4826 / √2, exigindo 5 ou mais
  imagens. As diferenças removem tendências lentas e o MAD resiste a valores
  extremos. O mesmo ruído é usado para o evento e para o placebo.
- **Pico:** mediana na janela (±10 dias) menos a média das medianas de dois
  "ombros", um antes (−30 a −15 dias) e um depois (+20 a +35 dias). Uma rampa
  eleva os ombros junto, então não gera pico. O placebo usa as mesmas janelas
  centradas em −50 dias.

## Taxas de detecção [E]

Sensibilidade (evento com data conhecida) × falso positivo empírico (placebo):

| Classe | Métrica | z > 2: evento / placebo | z > 3: evento / placebo |
|---|---|---|---|
| Rosa | z (v1) | 62% / 11% | 50% / 4,4% |
| Rosa | z_rob (delta, ruído robusto) | 64% / 9,3% | 52% / 1,9% |
| Rosa | **z_pico** | **67% / 5,1%** | **50% / 0,9%** |
| Amarelo | z (v1) | 17% / 4,3% | 8,7% / 1,4% |
| Amarelo | **z_pico** | **10% / 1,4%** | 2,9% / 0,7% |

Notas sobre a tabela:
- **n:** o z (v1) usa todos os eventos com baseline (rosa 293, amarelo 161). As
  métricas robustas exigem ruído estimável (rosa 214, amarelo 138). O placebo
  do z (v1) tem n menor (rosa 158, amarelo 138). As taxas não são calculadas
  sobre exatamente o mesmo conjunto.
- **Correção de uma afirmação de 2026-11-16:** eu tinha dito que o placebo cairia
  para menos de 1% com z > 2. Essa estimativa usava como ruído o desvio-padrão
  dos níveis da baseline, que inclui a variância das rampas e, portanto,
  superestima o ruído. Com o estimador por diferenças, o valor correto com
  z > 2 é 5% (rosa, z_pico). O valor abaixo de 1% vale para **z > 3**.

## Sinal médio por pico [E]

Mediana entre clusters e Wilcoxon por cluster:

| | Rosa | Amarelo |
|---|---|---|
| Pico (evento) | 0,023 (p < 0,0001; 94% dos eventos > 0) | 0,005 (p = 0,001) |
| Pico (placebo) | 0,0005 (p = 0,61) | −0,0006 (p = 0,57) |
| Rosa × pastagem | 0,017 (p < 0,0001) | — |
| Placebo rosa × pastagem | −0,002 (p = 0,62) | — |

O placebo positivo do estrato rosa × pastagem na v1 (0,011) desaparece com a
métrica de pico. Era deriva lenta do fundo, não um pico.

## Leitura

- **Rosa:**
  - z_pico > 3 detecta metade das florações conhecidas, com cerca de 1% de falso
    positivo por teste. Esse é o critério candidato para o histórico multianual
    (D6).
  - z_pico > 2 detecta dois terços, com cerca de 5% de falso positivo.
- **Amarelo:** continua fraco no nível individual. O pico médio existe, mas só
  cerca de 10% dos eventos passam de z > 2.
- **A rampa pré-floração** é um fenômeno real que o pico separa da floração. Se
  ela corresponde à desfolha, a métrica de pico também responde em parte à
  questão D7. A confirmação [H] depende de inspecionar visualmente as copas com
  rampa.

## Lacuna de cobertura em 2017 (nova)

112 eventos ficaram sem `z_pico`; 98 deles são de 2017. Na coleção
`S2_SR_HARMONIZED` (L2A), a cobertura fora da Europa em 2017–2018 é incompleta,
o que deixa esses eventos sem imagens suficientes na baseline. Remédio
possível: usar `S2_HARMONIZED` (L1C, topo da atmosfera) para 2017–2018. Para um
contraste núcleo−anel local, o efeito atmosférico se cancela em boa parte [H].
Exige reexecutar o script 01.
