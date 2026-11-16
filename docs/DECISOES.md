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
- **Revisão v1.1 (2026-11-16):** o z da v1 usava o desvio-padrão de uma
  baseline curta (~4 imagens no placebo), que subestimava o ruído. Passa a
  valer o ruído robusto (MAD das diferenças consecutivas), igual para evento e
  placebo. Também foi adicionada a métrica de pico acima dos ombros, que separa
  floração (transitória) de rampa lenta. As métricas da v1 são mantidas para
  comparação.

## D5. Janela do evento (aberta)

- **Situação:** ±10 dias foi pré-especificada. ±5 dias melhora o amarelo, mas
  foi escolhida post hoc.
- **Decisão pendente:** adotar ±5 dias só depois de confirmar em dados
  independentes.

## D6. Critério de detecção para o histórico multianual (aberta, com candidato)

- **Problema:** z > 2 tem cerca de 6% de falso positivo por teste. Num histórico
  de ~10 anos × centenas de copas, isso gera dezenas de detecções espúrias.
- **Atualização v1.1, candidato para o rosa:** `z_pico > 3`, com sensibilidade
  de 50% e falso positivo de 0,9% no placebo. Com `z_pico > 2`, a sensibilidade
  é de 67% e o falso positivo de 5,1%.
  - **Ressalva:** essas taxas valem por teste, com a data aproximada conhecida.
    Numa varredura cega por todas as datas de um ano, o número de testes por
    ano aumenta e o falso positivo por ano cresce junto. É preciso definir a
    unidade de teste (por exemplo, um teste por janela de floração plausível).
- **Opções:**
  - limiar mais alto;
  - exigir duas ou mais imagens consecutivas acima do limiar;
  - exigir coerência de cor (B4 e B2 sobem, B3 não);
  - calibrar o limiar pela distribuição do placebo.
- **Definir antes de montar o passo 2.**
- **Atualização 2026-11-16 (resultados das AOIs):** z > 3 por pixel gera
  ~100–160 objetos espúrios por 100 ha. Na AOI10 (rosa), a precisão no censo é
  de 15%, contra uma sensibilidade de 48% (acaso: 21%). A regra precisa ser
  revisada antes do histórico. Ver `RESULTADOS_aoi_v1.md`, seção 5.
- **Atualização v1.2:** a varredura nas AOIs mede o falso positivo **por área**
  (objetos por 100 ha no placebo), não por teste. Essa é a unidade relevante
  para a varredura cega. A decisão sobre o limiar fica para depois da etapa 1.

## D7. Hipótese alternativa de desfolha (aberta)

- **Situação:** não descartada.
- **Atualização v1.1:** foram encontradas rampas lentas do contraste semanas
  antes da floração (eventos 73_1, 443_1, 77_1), compatíveis com desfolha [H]. A
  métrica de pico não responde a elas. Inspecionar visualmente essas copas para
  confirmar.
- **Teste proposto:** amostra de copas desfolhadas sem flor no GE, analisadas
  com o mesmo pipeline.

## D8. Cobertura de 2017–2018 (aberta, nova na v1.1)

- **Problema:** 98 eventos de 2017 ficam sem ruído e sem pico, porque a coleção
  L2A tem cobertura incompleta fora da Europa em 2017–2018.
- **Opção:** extrair esses anos de `S2_HARMONIZED` (L1C, topo da atmosfera).
  - **Ataque provável:** mistura de níveis de processamento. O contraste
    núcleo−anel é local, então o efeito atmosférico se cancela em boa parte [H],
    mas os índices absolutos mudam.
  - **Teste:** comparar L1C × L2A em 2019+.

## D9. AOIs como áreas de teste da varredura espacial (adotada, v1.2)

- **Justificativa:** são áreas com muitas copas floridas não marcadas e data
  conhecida. Permitem testar a detecção às cegas no espaço, o passo
  intermediário entre o teste por ponto e o histórico multianual.
- **Ataques prováveis:**
  - (a) as AOIs foram escolhidas por terem muita floração, então as taxas valem
    para paisagens densas, não para a paisagem média;
  - (b) sem censo, as detecções não marcadas não podem ser classificadas.
- **Mitigações:**
  - placebo temporal nos mesmos pixels, para o falso positivo;
  - validação cega com controles aleatórios, para a precisão;
  - censo de subparcelas sorteadas e estratificadas (fragmento, borda, matriz),
    para a sensibilidade.
- **Não resolvido:** generalização para fora das AOIs. Exigiria áreas sorteadas
  sem critério de floração.

## D10. Distância de casamento de 20 m entre censo e detecção (provisória)

- **Justificativa:** soma aproximada do erro de posição do GE e do tamanho do
  pixel/objeto.
- **Ataque provável:** valor arbitrário; distâncias maiores inflam a
  sensibilidade e a precisão.
- **Ação:** reportar a sensibilidade a 10, 20 e 30 m quando houver censo.

## D11. Validação cega adiada (adotada, 2026-11-16)

- **Motivo:** a etapa 1 mostrou densidade de falsos positivos (placebo) da
  mesma ordem das detecções do evento. Com a regra atual (z > 3 por pixel), a
  validação cega só confirmaria uma precisão baixa, já medida no censo da AOI10
  (15%), ao custo de ~450 pontos.
- **Ação:** refazer a validação cega depois de revisar a regra de detecção.
- **Sigilo:** a amostra e a chave geradas na etapa 1 ficam fora do repositório
  até lá.

## D12. Amarelo fora do escopo da detecção por Sentinel-2 (provisória)

- **Evidência:** pontos (v1.1: ~10% com z > 2), varredura (evento ≤ placebo na
  AOI12) e censo (sensibilidade ≤ acaso).
- **Proposta:** concentrar a regra de detecção e o histórico no rosa. O amarelo
  exigiria outra resolução (PlanetScope ou imagens de alta resolução).
- **Ataque provável:** o NDYI pode ser um índice ruim, não o amarelo
  indetectável. Não foram testados índices alternativos.
- **Atualização no congelamento (2026-11-16):** mesmo com a posição conhecida,
  a detecção individual do amarelo fica perto do acaso. Hipóteses abertas, não
  testadas:
  - (a) detecção na escala de população, somando dezenas de copas por data;
  - (b) janela de floração curta demais para a revisita de 5 dias
    (PlanetScope diário atacaria isso);
  - (c) outros índices (borda do vermelho, NIR), que separem flor de capim
    seco.

## D13. Objetivo: acompanhar copas conhecidas, não descobrir copas (adotada no congelamento, 2026-11-16)

- **Evidência:** `RESULTADOS_aoi_v1.1.md`.
  - Nas copas do censo, a detecção fica 4–5× acima do placebo.
  - Por pixel, evento e placebo são indistinguíveis na área de teste.
  - A precisão máxima da varredura cega é ≤ 26%, em qualquer limiar.
- **Consequência:** o uso viável é o histórico de floração de copas **rosas** de
  posição conhecida (pontos da inspeção e do censo). Mapear copas novas exigiria
  critérios adicionais ou outra resolução.
- **Ataques prováveis:**
  - (a) baseado em uma área de teste (AOI10, 200 ha, 57 copas) e numa única
    data;
  - (b) a regra de pixel testada é só z_pico; critérios espectrais e de forma
    não foram testados;
  - (c) parte das copas de teste coincide com pontos usados no teste por ponto.

## Estado no congelamento (2026-11-16)

| Decisão | Estado |
|---|---|
| D1–D4, D9 | adotadas |
| D5 (janela ±5 d) | aberta: confirmar em dados independentes |
| D6 (critério de detecção) | resolvida para copas conhecidas (z_pico > 3, ruído robusto); sem solução para varredura cega |
| D7 (desfolha) | aberta: inspecionar copas com rampa (73_1, 443_1, 77_1) |
| D8 (cobertura 2017–2018) | aberta: extrair L1C |
| D10 (20 m) | provisória: sensibilidade reportada a 10/20/30 m |
| D11 (validação cega) | adiada indefinidamente: só faz sentido com uma regra nova |
| D12 (amarelo) | provisória: fora do escopo individual |
| D13 (acompanhar, não descobrir) | adotada |
