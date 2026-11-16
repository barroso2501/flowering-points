# Protocolo: validação cega e censo de copas floridas

São duas tarefas visuais no Google Earth Pro, com papéis diferentes:

| Tarefa | O que mede | Quando |
|---|---|---|
| A. Validação cega | **Precisão**: das manchas que o Sentinel-2 detecta, quantas são copa florida | depois da etapa 1 do script 04 |
| B. Censo de subparcelas | **Sensibilidade**: das copas floridas existentes, quantas o Sentinel-2 detecta | a qualquer momento (é independente da varredura) |

Regra comum às duas: usar **a imagem histórica da data da AOI** (`data_aoi`),
pelo controle de tempo do GE. Se essa data não estiver disponível, ou a imagem
estiver com nuvem no local, registrar `sem_imagem` e **não usar outra data**.

## A. Validação cega

**Arquivos:** `results/aoi_v1/validacao_amostra_cega.kml` e
`validacao_template.csv`.

1. **Não abrir** `_chave_amostra_NAO_ABRIR.csv`. Ele diz quais pontos são
   detecções e quais são controles aleatórios. Saber isso enviesa a resposta.
2. Abrir o KML no GE. Cada ponto tem um código (V001, V002…), e a descrição
   indica a data e a cor-alvo.
3. Em cada ponto, na imagem da data indicada, responder na planilha (coluna
   `resposta`):
   - `sim`: há copa florida da cor-alvo a até ~15 m do ponto;
   - `nao`: não há;
   - `incerto`: há algo, mas não dá para afirmar;
   - `sem_imagem`: a data não está disponível ou o local está encoberto.
4. Use `observacao` para o que ajudar a interpretar, por exemplo: "copa sem
   folha", "outra cor", "solo exposto", "estrada".
5. Salvar como `validacao_preenchida.csv` e rodar a etapa 2.

Os controles aleatórios não são desperdício. A taxa de `sim` neles mede a
densidade de base de copas floridas e a tendência do observador de ver flor
onde não há.

## B. Censo das subparcelas

**Arquivo:** `subparcelas_censo_v1.kml` (exportado pelo script 03). Contém:
- **AOI10 e AOI11:** a AOI inteira (~60 ha cada);
- **AOI12:** 3 quadrados de 500 m (25 ha), sorteados um por estrato de cobertura
  lenhosa natural do MapBiomas: `fragmento` (70% ou mais), `borda` (30–70%) e
  `matriz` (menos de 30%).

O sorteio é aleatório e tem semente fixa. **Não trocar uma subparcela por
outra "mais interessante"**: isso reintroduz o viés que o sorteio remove.

### Procedimento

1. Abrir o KML no GE e ir para a data da AOI.
2. Varrer a subparcela de forma sistemática, em faixas, de norte a sul. Usar
   altitude de visada constante (sugestão: ~300–400 m de altitude do olho). Se
   ajudar, sobrepor uma grade de 100 m.
3. Marcar **todas** as copas floridas dentro da subparcela, uma placemark por
   copa, no centro da copa. O nome da placemark indica a cor:
   - `r` = rosa ou roxo;
   - `a` = amarelo;
   - `o` = outra cor conspícua;
   - acrescentar `?` quando houver dúvida (`r?`, `a?`). As copas com `?` são
     contadas à parte e não entram no cálculo principal.
4. Copas agrupadas, com coroas que se tocam: uma placemark por copa
   distinguível. Se não der para separar, uma placemark no centro do grupo,
   com nome `r+` ou `a+`.
5. Registrar no nome da pasta do GE: subparcela, data da imagem usada e tempo
   gasto. O tempo gasto serve para planejar os próximos censos.
6. Salvar a pasta como `censo_v1.kml` (todas as subparcelas juntas) e rodar a
   etapa 3.

### Cuidados

- **Antes de terminar a subparcela:** não olhar o raster de z nem as detecções
  no QGIS. Ver as detecções antes do censo transforma o censo em validação das
  detecções.
- **Cada copa conta uma vez:** uma copa na borda da subparcela entra se o centro
  da copa estiver dentro.
- **Deslocamento do GE:** pode chegar a metros ou dezenas de metros entre
  datas. A análise aceita até 20 m entre a copa do censo e a detecção
  (`DIST_MATCH`). Se o deslocamento parecer maior naquela imagem, anote.
