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
