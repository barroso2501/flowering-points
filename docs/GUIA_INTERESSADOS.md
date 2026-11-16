# Guia para quem quiser continuar

**Situação:** projeto congelado em 2026-11-16 por Mario Barroso Ramos Neto.

**Para quem:** colegas do MapBiomas, de biodiversidade e de ciência que queiram
usar os dados ou seguir as análises.

## Em uma frase

Há 745 registros de copas floridas de ipês rotulados visualmente no Cerrado, e
a evidência de que a floração **rosa** de copas **de posição conhecida** aparece
no Sentinel-2. Mas o método não serve para descobrir copas novas, e o amarelo
não é detectável individualmente.

## O que se sabe

| Afirmação | Força | Onde está |
|---|---|---|
| A floração rosa produz um pico transitório (~3 semanas) no contraste copa−entorno do Sentinel-2 | Evidência: 295 eventos em 43 clusters, placebo nulo | `RESULTADOS_v1.md`, `RESULTADOS_v1.1.md` |
| Com a posição conhecida, z_pico > 3 detecta ~50% das florações rosas, com ~1% de falso positivo por teste no placebo | Evidência: teste por ponto (v1.1) | `RESULTADOS_v1.1.md` |
| O censo confirma: nas copas, a detecção fica 4–5× acima do placebo | Evidência: 57 copas, uma área de 200 ha, uma data | `RESULTADOS_aoi_v1.1.md` |
| A varredura às cegas por pixel tem precisão ≤ 26% em qualquer limiar | Evidência: uma área de teste | `RESULTADOS_aoi_v1.1.md` |
| O amarelo não é detectável individualmente (NDYI), nem com a posição conhecida | Evidência: pontos, varredura e censo concordam; uma área no censo | `RESULTADOS_aoi_v1.md`, D12 |
| O pico rosa vem da flor, não da desfolha pré-floração | Hipótese favorecida pela assinatura de cor (B4 e B2 sobem, B3 não); não confirmada | D7 |
| O amarelo seria detectável na escala de população | Hipótese não testada (há um sinal médio fraco, p = 0,001) | D12 |

## O que está disponível

- **`data/release_v1/`:** todos os registros em CSV, GeoJSON e GeoPackage, com
  dicionário.
  - **Inspeção oportunista (498 registros):** só presenças, viés de esforço.
  - **Censo exaustivo (247 copas, em 5 áreas de busca):** ausências
    informativas, incluindo uma subparcela com zero copas.
- **Scripts reexecutáveis** (GEE + Python): séries por ponto, varredura por
  pixel, análise com placebo, consolidação.
- **Registro de decisões** (`docs/DECISOES.md`), com o que um revisor cético
  atacaria em cada uma e o estado no congelamento.

## Caminhos para continuar

Ordenados do mais pronto ao mais exploratório.

| # | Caminho | Pergunta | Já existe | Falta | Esforço |
|---|---|---|---|---|---|
| 1 | **Histórico de floração de copas rosas conhecidas, 2017–2026** | A floração varia entre anos? Responde a seca, fogo ou ENSO? Copas sumiram (supressão)? | ~350 copas rosas georreferenciadas (300 da inspeção + 49 do censo, sem duplicatas); detector validado (z_pico, ruído robusto, placebo) | Extrair as séries multianuais por copa (adaptar o script 01); definir a unidade de teste por ano (D6) | Médio |
| 2 | **Rótulos para modelos em imagem de alta resolução** | Uma rede detecta copas floridas em imagens sub-métricas? | Positivos (inspeção + censo) e negativos confiáveis (áreas censadas, incluindo zero copas) | Recortes de imagem nas datas; delimitar as copas | Médio |
| 3 | **Amarelo na escala de população** | A soma de dezenas de copas por data revela a curva de floração anual? | Séries por ponto (v1) | Análise agregada por data e região | Baixo |
| 4 | **Descoberta com critérios adicionais** | Cor + forma + persistência tornam a varredura cega utilizável? | Varredura, censo e área de teste | Reexportar as bandas por pixel; testar as regras na AOI10 | Médio |
| 5 | **PlanetScope / revisita diária** | Revisita diária e 3 m resolvem o amarelo e a descoberta? | Censo para validação | Acesso a dados Planet | Alto |
| 6 | **Flor × desfolha (D7)** | O pico rosa é flor? | Copas com rampa identificadas (73_1, 443_1, 77_1) | Inspeção visual das copas sem folha | Baixo |
| 7 | **Cobertura de 2017–2018 (D8)** | Os eventos de 2017 (98) recuperam o sinal com L1C? | Lista de eventos | Rodar o script 01 com `S2_HARMONIZED` | Baixo |

## Cuidados com os dados

- **Cor não é espécie.** "Rosa" e "roxo" se sobrepõem (*H. impetiginosus*); o
  amarelo reúne várias espécies.
- **Os dados não são uma amostra da paisagem.** A inspeção seguiu áreas em
  regeneração, e as AOIs foram desenhadas onde havia muita floração. Não
  extrapole densidades.
- **Posição do Google Earth:** o erro entre datas pode chegar a dezenas de
  metros. Os testes usam uma tolerância de 15–20 m.
- **Duplicatas:** 14 copas do censo provavelmente são as mesmas da inspeção
  (`possivel_duplicata_de`).
- **Inferência:** pontos da mesma data e região não são independentes. Use
  `cluster_id`.
- **Um local só:** os resultados do censo vêm de uma área rosa (AOI10) e uma
  amarela (AOI12), numa data cada. Replicar é o primeiro passo de qualquer
  continuação.

## Como começar em 30 minutos

1. Abra `data/release_v1/flowering_points_v1.gpkg` no QGIS (camadas
   `registros`, `areas_censo` e `aois`).
2. Leia `docs/RESULTADOS_aoi_v1.1.md` (2 páginas): é o resultado que define o
   escopo.
3. Escolha um caminho na tabela acima. Em `docs/DECISOES.md`, veja as decisões
   abertas que ele toca.

## Contato

Mario Barroso Ramos Neto. Contato e licença a definir antes da divulgação.
