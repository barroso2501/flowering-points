/*******************************************************************************
 * 01_gee_extrair_series_s2.js
 * Teste de detectabilidade de floração de ipês no Sentinel-2 (GEE Code Editor)
 *
 * O que faz: para cada evento de floração registrado no Google Earth, extrai a
 * série temporal Sentinel-2 (L2A harmonizado, máscara Cloud Score+) de
 * DIAS_ANTES até DIAS_DEPOIS em torno da data do evento, em duas geometrias:
 *   - NÚCLEO: buffer pequeno em torno do ponto (onde a copa deveria estar);
 *   - ANEL: coroa circular ao redor (fundo local, controle espacial).
 * A análise (script 02, Python) compara núcleo−anel na data do evento contra
 * o mesmo contraste antes da floração (desenho tipo "diferença em diferenças").
 *
 * Entrada: ipes_eventos_s2_input.csv subido como Table asset
 *   (Assets > NEW > CSV file; colunas lat/lon são lidas como números).
 * Saída: CSV no Google Drive, uma linha por evento × imagem.
 ******************************************************************************/

// ----------------------------- PARÂMETROS -----------------------------------
var ASSET        = 'users/SEU_USUARIO/ipes_eventos_s2_input'; // <- ajuste
var DIAS_ANTES   = 90;    // início da série (baseline pré-floração)
var DIAS_DEPOIS  = 60;    // fim da série (pós-floração / refolhamento)
var CS_LIMIAR    = 0.60;  // Cloud Score+ cs_cdf: >= limiar é considerado limpo
var R_NUCLEO     = 15;    // m; ~3x3 pixels de 10 m, absorve parte do erro de posição do GE
var R_ANEL_INT   = 40;    // m; raio interno do anel de fundo
var R_ANEL_EXT   = 80;    // m; raio externo do anel de fundo
var PASTA_DRIVE  = 'ipes_s2';
var DESCRICAO    = 'ipes_s2_series_v1';

// ------------------------- DADOS DE ENTRADA ---------------------------------
// Reconstrói a geometria a partir de lon/lat (evita depender da detecção
// automática de geometria no upload do CSV).
var eventos = ee.FeatureCollection(ASSET).map(function (f) {
  var pt = ee.Geometry.Point([ee.Number(f.get('lon')), ee.Number(f.get('lat'))]);
  return ee.Feature(pt, f.toDictionary());
});

// ---------------------- SENTINEL-2 + CLOUD SCORE+ ---------------------------
var s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
  .linkCollection(ee.ImageCollection('GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED'),
                  ['cs_cdf']);

// Prepara cada imagem: máscara de nuvem/sombra, reflectância 0–1 e índices.
// NDYI (amarelo) = (B3−B2)/(B3+B2): índice usado para floração amarela de
//   culturas (canola); para ipê é extrapolação, não validado.
// IRS (índice rosa, exploratório, definido aqui): flores rosa/magenta refletem
//   vermelho e azul e absorvem verde -> (B4+B2−2·B3)/(B4+B2+2·B3).
function preparar(img) {
  var limpo = img.select('cs_cdf').gte(CS_LIMIAR);
  var r = img.select(['B2', 'B3', 'B4', 'B8', 'B11']).divide(10000);
  var ndvi = r.normalizedDifference(['B8', 'B4']).rename('NDVI');
  var ndyi = r.normalizedDifference(['B3', 'B2']).rename('NDYI');
  var irs = r.expression('(R + B - 2*G) / (R + B + 2*G)',
    {R: r.select('B4'), G: r.select('B3'), B: r.select('B2')}).rename('IRS');
  return r.addBands([ndvi, ndyi, irs]).updateMask(limpo)
    .copyProperties(img, ['system:time_start', 'MGRS_TILE', 'SENSING_ORBIT_NUMBER']);
}

var BANDAS = ['B2', 'B3', 'B4', 'B8', 'B11', 'NDVI', 'NDYI', 'IRS'];
function prefixar(p) { return BANDAS.map(function (b) { return p + b; }); }

// --------------------- EXTRAÇÃO POR EVENTO ----------------------------------
function serieDoEvento(ev) {
  var pt = ev.geometry();
  var d0 = ee.Date(ev.get('data_evento'));
  var nucleo = pt.buffer(R_NUCLEO);
  var anel = pt.buffer(R_ANEL_EXT).difference(pt.buffer(R_ANEL_INT), 1);

  var col = s2.filterBounds(pt)
    .filterDate(d0.advance(-DIAS_ANTES, 'day'), d0.advance(DIAS_DEPOIS + 1, 'day'))
    .map(preparar);

  var linhas = col.map(function (im) {
    // Média no núcleo e mediana no anel (mediana é robusta a outro ipê no anel).
    var vn = im.rename(prefixar('n_')).reduceRegion({
      reducer: ee.Reducer.mean(), geometry: nucleo, scale: 10, maxPixels: 1e6});
    var va = im.rename(prefixar('a_')).reduceRegion({
      reducer: ee.Reducer.median(), geometry: anel, scale: 10, maxPixels: 1e6});
    // Máximo dos índices no núcleo: pega a copa mesmo com o ponto deslocado.
    var vx = im.select(['NDYI', 'IRS'], ['nmax_NDYI', 'nmax_IRS']).reduceRegion({
      reducer: ee.Reducer.max(), geometry: nucleo, scale: 10, maxPixels: 1e6});
    // Fração de pixels limpos em cada geometria (0–1).
    var valido = im.select('B2').mask().rename('v');
    var fn = valido.reduceRegion({reducer: ee.Reducer.mean(), geometry: nucleo,
      scale: 10, maxPixels: 1e6}).get('v');
    var fa = valido.reduceRegion({reducer: ee.Reducer.mean(), geometry: anel,
      scale: 10, maxPixels: 1e6}).get('v');
    var dImg = ee.Date(im.get('system:time_start'));
    return ee.Feature(null, vn.combine(va).combine(vx)).set({
      evento_id: ev.get('evento_id'),
      data_img: dImg.format('YYYY-MM-dd'),
      dias_rel: dImg.difference(d0, 'day').round(),
      tile: im.get('MGRS_TILE'),
      orbita: im.get('SENSING_ORBIT_NUMBER'),
      frac_limpo_n: fn,
      frac_limpo_a: fa
    });
  });
  return ee.FeatureCollection(linhas);
}

var tabela = eventos.map(serieDoEvento).flatten();

// ------------------------------ EXPORTAÇÃO ----------------------------------
var COLUNAS = ['evento_id', 'data_img', 'dias_rel', 'tile', 'orbita',
  'frac_limpo_n', 'frac_limpo_a']
  .concat(prefixar('n_')).concat(prefixar('a_')).concat(['nmax_NDYI', 'nmax_IRS']);

Export.table.toDrive({
  collection: tabela,
  description: DESCRICAO,
  folder: PASTA_DRIVE,
  fileFormat: 'CSV',
  selectors: COLUNAS
});

// --------------------- INSPEÇÃO VISUAL DE UM EVENTO --------------------------
// Troque o ID para olhar um caso no mapa (composição RGB da imagem limpa mais
// próxima da data do evento) e o gráfico da série núcleo × anel.
var ID_INSPECAO = '400_2';
var ev1 = ee.Feature(eventos.filter(ee.Filter.eq('evento_id', ID_INSPECAO)).first());
var d1 = ee.Date(ev1.get('data_evento'));
var img1 = s2.filterBounds(ev1.geometry())
  .filterDate(d1.advance(-10, 'day'), d1.advance(11, 'day'))
  .map(preparar)
  .map(function (im) {   // ordena por distância à data do evento
    return im.set('dist', ee.Number(im.get('system:time_start'))
      .subtract(d1.millis()).abs());
  }).sort('dist').first();
Map.centerObject(ev1.geometry(), 16);
Map.addLayer(ee.Image(img1), {bands: ['B4', 'B3', 'B2'], min: 0, max: 0.2},
  'S2 RGB mais próxima do evento');
Map.addLayer(ev1.geometry().buffer(R_ANEL_EXT).difference(ev1.geometry().buffer(R_ANEL_INT), 1),
  {color: 'cyan'}, 'anel', false);
Map.addLayer(ev1.geometry().buffer(R_NUCLEO), {color: 'red'}, 'núcleo');
var s1 = serieDoEvento(ev1).filter(ee.Filter.gte('frac_limpo_n', 0.9));
print(ui.Chart.feature.byFeature(s1.sort('dias_rel'), 'dias_rel', ['n_IRS', 'a_IRS', 'n_NDYI', 'a_NDYI'])
  .setOptions({title: 'Evento ' + ID_INSPECAO + ' — núcleo (n_) × anel (a_)',
    hAxis: {title: 'dias em relação ao evento'}, lineWidth: 1, pointSize: 3}));
