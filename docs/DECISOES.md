# Registro de decisões

Formato: decisão, justificativa e o que um revisor cético atacaria.
Estado: **adotada**, **provisória** ou **aberta**.

## D1. Unidade de registro = evento de floração, não ponto (adotada)

- **Justificativa:** permite acumular revisitas e históricos.
- **Ataque provável:** as revisitas v1 (8 indivíduos) vêm em parte de conflitos
  de metadado, não de observação dupla confirmada (IDs 142, 347, 364).
- **Ação:** confirmar visualmente os IDs 142 e 347. O 364 já foi tratado como
  duplicado na entrada S2.

## D2. Classe por cor, não por espécie (adotada)

- **Justificativa:** a cor da flor não resolve as espécies de *Handroanthus*.
  "Roxo" e "rosa" se sobrepõem (*H. impetiginosus*).
- **Aberta:** fundir roxo com rosa (`rosa_roxo`)?
- **Hipótese a verificar:** os rosas tardios (51 eventos em agosto e setembro)
  podem ser de outro táxon.

## D3. Núcleo de 15 m e anel de 40–80 m (provisória)

- **Ataque provável:** em bordas (mata de galeria, estrada), o anel mistura
  coberturas.
- **Mitigações:** o desenho com dois tempos remove a parte fixa dessa mistura,
  e a mediana reduz a influência de vizinhos.
- **Não testado:** sensibilidade aos raios.

## D4. Diferença em diferenças + placebo + inferência por cluster (adotada)

- **Justificativa:** controla diferença local fixa e sazonalidade comum. O
  placebo verifica falso sinal. O cluster evita pseudorreplicação.
- **Limite:** o placebo cobre só uma data falsa pré-floração. Não testa
  desfolha, que pode coincidir com a floração.

## D5. Janela do evento (aberta)

- **Situação:** ±10 dias foi pré-especificada. ±5 dias melhora o amarelo, mas
  foi escolhida post hoc.
- **Decisão pendente:** adotar ±5 dias só depois de confirmar em dados
  independentes.

## D6. Critério de detecção para o histórico multianual (aberta)

- **Problema:** z > 2 tem cerca de 6% de falso positivo por teste. Num histórico
  de ~10 anos × centenas de copas, isso gera dezenas de detecções espúrias.
- **Opções:**
  - limiar mais alto;
  - exigir duas ou mais imagens consecutivas acima do limiar;
  - exigir coerência de cor (B4 e B2 sobem, B3 não);
  - calibrar o limiar pela distribuição do placebo.
- **Definir antes de montar o passo 2.**

## D7. Hipótese alternativa de desfolha (aberta)

- **Situação:** não descartada.
- **Teste proposto:** amostra de copas desfolhadas sem flor no GE, analisadas
  com o mesmo pipeline.
