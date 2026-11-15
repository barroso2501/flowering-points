# Dicionário de Dados — `ipes_eventos_consolidados.csv`

A tabela consolidada adota o modelo relacional **Evento-Observação**, onde a chave primária representa a combinação única entre um indivíduo georreferenciado e a data exata da imagem orbital em que a floração conspícua foi confirmada.

## Especificação das Colunas

| Coluna | Tipo | Descrição | Valores / Formato |
| :--- | :--- | :--- | :--- |
| `evento_id` | `string` | Identificador único do evento fenológico (`individuo_id` + sequência temporal). | Ex.: `398_1`, `398_2` |
| `individuo_id` | `integer` | Identificador físico da árvore marcada (`OBJECTID` original). Permite agrupar observações multi-ano sem dupla contagem. | Inteiro positivo |
| `lat` | `float` | Latitude em graus decimais (Datum WGS84 / EPSG:4326). | Ex.: `-17.1886293` |
| `lon` | `float` | Longitude em graus decimais (Datum WGS84 / EPSG:4326). | Ex.: `-46.1450347` |
| `data_evento` | `date` | Data exata de aquisição da cena histórica no Google Earth (ISO 8601). | `AAAA-MM-DD` |
| `ano` | `integer` | Ano da observação extraído de `data_evento`. | `2005` a `2026` |
| `mes` | `integer` | Mês da observação extraído de `data_evento`. | `1` a `12` |
| `classe_flor` | `string` | Agrupamento funcional pela síndrome de cor da florada. | `amarelo`, `rosa`, `roxo`, `sucupira` |
| `contexto` | `string` | Fisionomia ou matriz da paisagem imediata onde o indivíduo se insere. | `cerradao_savana`, `pastagem`, `borda_estrada`, `mata_galeria`, `outro` |
| `confianca` | `string` | Grau de certeza visual da detecção na cena de alta resolução. | `alta`, `media`, `baixa` |
| `oip_presente` | `boolean` | Indica presença de **Outros Indivíduos Próximos (OIP)** em floração simultânea na vizinhança imediata. | `True`, `False` |
| `oip_multicor` | `boolean` | Sinaliza cenas onde há coexistência de indivíduos floridos de cores distintas (ex.: amarelo e rosa/roxo) no entorno. | `True`, `False` |
| `area_interesse` | `boolean` | Flag indicando núcleos prioritários delimitados como polígonos de agrupamento. | `True`, `False` |
| `observacoes_originais` | `string` | Notas textuais originais registradas durante a inspeção visual. | Texto livre |

## Notas Metodológicas e Limitações

1. **Amostragem de Presença Confirmada:** A base documenta exclusivamente eventos positivos de floração detectados em janelas episódicas de satélites comerciais. A ausência de registro em determinada data ou região não implica ausência da espécie, mas sim assincronia entre a passagem orbital e o pico fenológico (3–7 dias).
2. **Variação Intraespecífica de Matiz:** A classe `rosa` abrange desde corolas recém-abertas (magenta intenso) até flores em senescência (rosa-pálido), além de variações de balanço radiométrico entre sensores comerciais distintos.
