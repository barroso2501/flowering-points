# Conjunto de dados de entrega v1: copas floridas rotuladas

**Gerado por:** `scripts/05_consolidar_rotulos.py`, em 2026-11-16. A
proveniência está em `log_release_v1.json`.

**Conteúdo:** todos os registros de copas floridas do projeto, num único lugar.

**Arquivos:**
- `registros_floracao_v1.csv`: tabela (lon/lat em WGS84);
- `registros_floracao_v1.geojson`: a mesma tabela com geometria de ponto;
- `flowering_points_v1.gpkg`: GeoPackage com 3 camadas, para QGIS/ArcGIS:
  - `registros`: os pontos;
  - `areas_censo`: as 5 áreas de busca exaustiva (4 subparcelas + o fragmento
    da AOI10);
  - `aois`: as 17 áreas de interesse, com status.

## Duas origens, duas naturezas

| Origem | n | Natureza | Use para |
|---|---|---|---|
| `inspecao_oportunista` | 498 registros (490 copas) | Presença oportunista: copas floridas vistas ao inspecionar regenerações, em imagens do Google Earth. **Sem não-detecções.** | Rótulos positivos; testes de detecção com data conhecida; histórico de copas conhecidas |
| `censo_exaustivo` | 247 copas | Todas as copas floridas visíveis dentro de uma área de busca, numa data. **Ausência dentro da área é informativa.** | Sensibilidade e precisão; densidade de copas por área; negativos confiáveis |

A AOI12_matriz (25 ha, 02/09/2025) foi censada e tem **zero** copas. Ela existe
em `areas_censo`, mas não gera linhas em `registros`.

## Contagens

| Origem | Cor | Certeza | n |
|---|---|---|---|
| inspeção | rosa | alta / média | 302 / 5 |
| inspeção | amarelo | alta / média / baixa | 172 / 7 / 3 |
| inspeção | roxo | média | 8 |
| inspeção | sucupira | baixa | 1 |
| censo | rosa | certa / incerta | 63 / 10 |
| censo | amarelo | certa / incerta | 146 / 27 |
| censo | outra | certa | 1 |

## Colunas de `registros`

| Coluna | Descrição |
|---|---|
| registro_id | Inspeção: `I<evento_id>` (ex.: `I397_2`); censo: `C0001`… |
| copa_id | A mesma copa em datas diferentes compartilha o `copa_id` (inspeção: `I<individuo>`) |
| origem | `inspecao_oportunista` / `censo_exaustivo` |
| lon, lat | WGS84. A posição vem do Google Earth, cujo erro entre datas pode chegar a dezenas de metros |
| data_imagem | Data (ISO) da imagem do GE em que a floração foi vista |
| cor | rosa, amarelo, roxo, sucupira, outra. É **cor da flor, não espécie** |
| certeza | Inspeção: alta / media / baixa (visual, não calibrada). Censo: certa / incerta (`?` no rótulo) |
| grupo_copas | Censo: `True` quando o ponto representa um grupo de copas não separáveis (`+`) |
| contexto | Inspeção: pastagem, cerradao_savana, mata_galeria, borda_estrada, outro |
| oip_presente, oip_multicor | Inspeção: outros indivíduos floridos próximos (e de outra cor) |
| area_busca | Censo: área de busca exaustiva (ver camada `areas_censo`) |
| busca_exaustiva | `True` no censo |
| suspeito | Inspeção: inconsistência conhecida (IDs 70 e 438) |
| cluster_id | Inspeção: data + célula de ~5 km. É a unidade de independência nos testes |
| s2_elegivel | Inspeção: entrou no teste Sentinel-2 (≥ 2017-04, rosa/amarelo) |
| s2_z_pico_ponto | Inspeção: z_pico do teste por ponto (script 02 v1.1); vazio quando o ruído não foi estimável |
| s2_z_evento_pixel, s2_z_placebo_pixel | Censo (AOI10, AOI12): z_pico máximo na janela 3×3 do raster do script 03, na data e no placebo |
| possivel_duplicata_de | Censo: registro da inspeção a ≤ 20 m, com a mesma data e cor (provavelmente a mesma copa) |
| observacoes | Texto livre original |

## Cuidados

- **Duplicatas:** 14 copas do censo (no fragmento da AOI10) provavelmente são
  copas também registradas na inspeção. Para contagens de copas únicas, remova
  as linhas com `possivel_duplicata_de` preenchido.
- **Não é amostra da paisagem:** a inspeção percorreu áreas em regeneração, e as
  AOIs foram desenhadas onde havia muita floração. Densidades não se
  extrapolam.
- **Fora do Cerrado?** As AOI07–09 parecem estar no oeste paulista. Isso não
  foi verificado.
- **Excluídos da consolidação:** IDs 226–228 ("não usar") e 288–289
  ("descartar") do arquivo bruto.
