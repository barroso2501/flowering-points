/*******************************************************************************
 * 03_gee_varredura_aoi.js
 * Varredura por pixel nas áreas de interesse (AOIs): detecção espacial às cegas
 * de copas floridas, com data conhecida (a data em que as AOIs foram anotadas).
 *
 * Para cada AOI e índice (IRS para rosa, NDYI para amarelo), por pixel de 10 m:
 *   1. contraste c(t) = índice(t) − mediana do índice num anel de 40–80 m
 *      (mesma lógica núcleo−anel do teste por pontos, aplicada a cada pixel);
 *   2. ruído = MAD das diferenças entre datas consecutivas (−90 a −30 dias)
 *      × 1,4826 / √2  (mesmo estimador do script 02 v1.1);
 *   3. pico = mediana de c em ±10 dias − média das medianas dos ombros
 *      (−30 a −15 e +20 a +35 dias);  z_pico = pico / ruído;
 *   4. o mesmo no PLACEBO (centro em −50 dias, antes da floração).
 * Pixels com z_pico > LIMIAR viram "objetos" (manchas de pixels vizinhos).
 *
 * Saídas (Google Drive, pasta PASTA_DRIVE):
 *   - aoi_deteccoes_v1.csv : um objeto por linha (centroide, nº de pixels, z máx.)
 *                            para evento e placebo, só dentro da AOI;
 *   - aoi_resumo_v1.csv    : por AOI × índice: área avaliável (ha);
 *   - aoi_pontos_v1.csv    : z máximo num raio de 15 m em torno de cada ponto
 *                            registrado a até 1 km da AOI;
 *   - aoi_z_<AOI>.tif      : raster com z_evento, z_placebo e ruído (para QGIS);
 *   - subparcelas_censo_v1.kml : subparcelas sorteadas para o censo (abrir no GE).
 ******************************************************************************/

// ----------------------------- PARÂMETROS -----------------------------------
var ASSET_PONTOS = 'users/SEU_USUARIO/ipes_eventos_s2_input'; // mesmo asset do script 01
var PASTA_DRIVE  = 'ipes_s2';
var CS_LIMIAR    = 0.60;   // Cloud Score+ (igual ao script 01)
var LIMIAR_Z     = 3;      // candidato da D6 (z_pico > 3)
var CENTRO_PLACEBO = -50;  // dias
var R_ANEL_INT_PX = 4, R_ANEL_EXT_PX = 8;   // anel de 40–80 m em pixels de 10 m
var BUFFER_PONTOS = 1000;  // m: região extra para avaliar pontos perto da AOI
// Subparcelas do censo
var LADO_SUBPARCELA = 500; // m (25 ha)
var SEMENTE = 42;          // semente fixa: o sorteio é reproduzível
// MapBiomas (estratificação das subparcelas): Coleção 11, cobertura.
// MAPBIOMAS_BANDA = null usa o ano mais recente disponível no asset (a banda
// escolhida é impressa no console). Para fixar um ano: 'classification_2024'.
var MAPBIOMAS = 'projects/mapbiomas-public/assets/brazil/lulc/collection11/mapbiomas_brazil_collection11_coverage_v3';
var MAPBIOMAS_BANDA = null;
var CLASSES_NATURAIS_LENHOSAS = [3, 4, 6];  // formação florestal, savânica, floresta alagável

// --------------------------- AOIs aptas -------------------------------------
// Geometrias embutidas (de data/aoi/aois_v1.geojson, status = apta_s2).
var AOIS = [
  ee.Feature(ee.Geometry.Polygon([[[-49.6411439, -16.8705809], [-49.645074, -16.8698963], [-49.6486947, -16.8705295], [-49.6492862, -16.8718564], [-49.6489511, -16.8734087], [-49.6491016, -16.8752617], [-49.6471327, -16.8761325], [-49.6433005, -16.8758164], [-49.6409727, -16.8750961], [-49.6395167, -16.8742716], [-49.6389059, -16.8729848], [-49.6411439, -16.8705809]]]), {aoi_id: 'AOI10', data_aoi: '2021-07-24', indices: 'IRS'}),
  ee.Feature(ee.Geometry.Polygon([[[-49.4867526, -17.0075874], [-49.4887846, -17.0095891], [-49.4910774, -17.0121043], [-49.4908913, -17.014272], [-49.4887501, -17.0155697], [-49.4849096, -17.0157382], [-49.48317, -17.015269], [-49.4830671, -17.0127883], [-49.4822917, -17.0108042], [-49.4832308, -17.0082474], [-49.4817558, -17.008161], [-49.4824171, -17.0075254], [-49.4841858, -17.007369], [-49.4867526, -17.0075874]]]), {aoi_id: 'AOI11', data_aoi: '2019-05-26', indices: 'IRS'}),
  ee.Feature(ee.Geometry.Polygon([[[-52.208098, -22.2256715], [-52.2204457, -22.2247529], [-52.2233051, -22.2263063], [-52.2213876, -22.2292875], [-52.2164846, -22.230666], [-52.2122823, -22.2318607], [-52.208673, -22.2283758], [-52.208098, -22.2256715]]]), {aoi_id: 'AOI07', data_aoi: '2021-09-08', indices: 'IRS,NDYI'}),
  ee.Feature(ee.Geometry.Polygon([[[-52.2367757, -22.2195747], [-52.2423437, -22.2231983], [-52.2444295, -22.2254611], [-52.2396986, -22.2296376], [-52.2373284, -22.2304169], [-52.2288082, -22.2278484], [-52.2297873, -22.2224309], [-52.2338303, -22.2198301], [-52.2367757, -22.2195747]]]), {aoi_id: 'AOI08', data_aoi: '2021-09-08', indices: 'IRS,NDYI'}),
  ee.Feature(ee.Geometry.Polygon([[[-52.2094211, -22.2494879], [-52.2221846, -22.2376871], [-52.229877, -22.2391891], [-52.2289499, -22.2505961], [-52.2244084, -22.2551398], [-52.2201376, -22.2563914], [-52.2149909, -22.2562263], [-52.2094211, -22.2494879]]]), {aoi_id: 'AOI09', data_aoi: '2021-09-08', indices: 'IRS,NDYI'}),
  ee.Feature(ee.Geometry.Polygon([[[-53.1301819, -19.8485979], [-53.1443274, -19.8681677], [-53.1351458, -19.8951633], [-53.163876, -19.9077169], [-53.1551925, -19.9215958], [-53.1117766, -19.9217566], [-53.0947902, -19.9186593], [-53.0528677, -19.911227], [-53.0342128, -19.9110753], [-53.0308398, -19.8960351], [-53.0311779, -19.883464], [-53.0363198, -19.8690851], [-53.0467358, -19.8496083], [-53.0684444, -19.8504997], [-53.1301819, -19.8485979]]]), {aoi_id: 'AOI12', data_aoi: '2025-09-02', indices: 'NDYI'}),
  ee.Feature(ee.Geometry.Polygon([[[-55.1043929, -14.975504], [-55.1071606, -14.977705], [-55.1084283, -14.9802419], [-55.1073317, -14.9823003], [-55.105197, -14.9833494], [-55.1036615, -14.9829404], [-55.0997988, -14.9786248], [-55.1016342, -14.9758619], [-55.1043929, -14.975504]]]), {aoi_id: 'AOI16', data_aoi: '2024-08-30', indices: 'NDYI'})
];

// ------------------------- SENTINEL-2 ---------------------------------------
var S2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
  .linkCollection(ee.ImageCollection('GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED'), ['cs_cdf']);

function preparar(img) {
  var r = img.select(['B2', 'B3', 'B4']).divide(10000);
  var ndyi = r.normalizedDifference(['B3', 'B2']).rename('NDYI');
  var irs = r.expression('(R + B - 2*G) / (R + B + 2*G)',
    {R: r.select('B4'), G: r.select('B3'), B: r.select('B2')}).rename('IRS');
  return ndyi.addBands(irs).updateMask(img.select('cs_cdf').gte(CS_LIMIAR))
    .copyProperties(img, ['system:time_start']);
}

// Kernel em anel (1 entre 4 e 8 pixels do centro, 0 fora).
var pesos = [];
for (var i = -R_ANEL_EXT_PX; i <= R_ANEL_EXT_PX; i++) {
  var linha = [];
  for (var j = -R_ANEL_EXT_PX; j <= R_ANEL_EXT_PX; j++) {
    var d = Math.sqrt(i * i + j * j);
    linha.push(d >= R_ANEL_INT_PX && d <= R_ANEL_EXT_PX ? 1 : 0);
  }
  pesos.push(linha);
}
var ANEL = ee.Kernel.fixed(2 * R_ANEL_EXT_PX + 1, 2 * R_ANEL_EXT_PX + 1, pesos,
  -R_ANEL_EXT_PX, -R_ANEL_EXT_PX, false);

// Um mosaico por dia (evita duplicar datas quando dois tiles cobrem a AOI).
function mosaicoDiario(col) {
  var dias = ee.List(col.aggregate_array('system:time_start'))
    .map(function (t) { return ee.Date(t).format('YYYY-MM-dd'); }).distinct();
  return ee.ImageCollection(dias.map(function (s) {
    var d = ee.Date.parse('YYYY-MM-dd', s);
    return col.filterDate(d, d.advance(1, 'day')).mosaic()
      .set('system:time_start', d.millis());
  }));
}

// Contraste pixel − anel para um índice.
function contraste(img, idx) {
  var x = img.select(idx);
  var fundo = x.reduceNeighborhood({reducer: ee.Reducer.median(), kernel: ANEL});
  return x.subtract(fundo).rename('c').copyProperties(img, ['system:time_start']);
}

// Mediana de c numa janela; imagem totalmente mascarada se não houver dados.
function medianaJanela(colC, centro, a, b) {
  var sub = colC.filterDate(centro.advance(a, 'day'), centro.advance(b + 1, 'day'));
  return ee.Image(ee.Algorithms.If(sub.size().gt(0), sub.median(),
    ee.Image(0).rename('c').updateMask(ee.Image(0))));
}

// Ruído robusto por pixel: MAD das diferenças entre datas consecutivas.
function ruidoRobusto(colC, d0) {
  var pre = colC.filterDate(d0.advance(-90, 'day'), d0.advance(-29, 'day'))
    .sort('system:time_start');
  var lista = pre.toList(200);
  var n = lista.size();
  var difs = ee.ImageCollection(ee.List.sequence(1, n.subtract(1).max(1)).map(function (k) {
    k = ee.Number(k);
    return ee.Image(lista.get(k)).subtract(ee.Image(lista.get(k.subtract(1))));
  }));
  var med = difs.median();
  var mad = difs.map(function (d) { return d.subtract(med).abs(); }).median();
  return mad.multiply(1.4826 / Math.sqrt(2))
    .updateMask(difs.count().gte(4)).rename('ruido');
}

function zPico(colC, d0, deslocamento, ruido) {
  var c = d0.advance(deslocamento, 'day');
  var ev = medianaJanela(colC, c, -10, 10);
  var oa = medianaJanela(colC, c, -30, -15);
  var od = medianaJanela(colC, c, 20, 35);
  return ev.subtract(oa.add(od).divide(2)).divide(ruido);
}

// Objetos detectados (centroides) dentro da AOI.
function objetos(z, aoi, props) {
  var det = z.gt(LIMIAR_Z).selfMask().rename('det');
  return det.addBands(z.rename('z')).reduceToVectors({
    geometry: aoi, scale: 10, crs: 'EPSG:4326', geometryType: 'centroid', eightConnected: true,
    labelProperty: 'det', maxPixels: 1e9,
    reducer: ee.Reducer.max().combine(ee.Reducer.count(), null, true)
  }).map(function (f) {
    var xy = f.geometry().coordinates();
    return f.set(props).set({lon: xy.get(0), lat: xy.get(1),
      z_max: f.get('max'), n_pixels: f.get('count')});
  });
}

// ------------------------------ LAÇO PRINCIPAL -------------------------------
var pontos = ee.FeatureCollection(ASSET_PONTOS).map(function (f) {
  return ee.Feature(ee.Geometry.Point([ee.Number(f.get('lon')), ee.Number(f.get('lat'))]),
    f.toDictionary());
});

var todasDeteccoes = ee.FeatureCollection([]);
var resumo = ee.FeatureCollection([]);
var amostrasPontos = ee.FeatureCollection([]);

AOIS.forEach(function (feat) {
  var aoi = feat.geometry();
  var id = feat.get('aoi_id').getInfo();
  var dataStr = feat.get('data_aoi').getInfo();
  var indices = feat.get('indices').getInfo().split(',');
  var d0 = ee.Date(dataStr);
  var regiao = aoi.buffer(BUFFER_PONTOS);

  var col = mosaicoDiario(S2.filterBounds(regiao)
    .filterDate(d0.advance(-90, 'day'), d0.advance(61, 'day')).map(preparar));

  var bandasRaster = [];
  indices.forEach(function (idx) {
    var colC = col.map(function (im) { return contraste(im, idx); });
    var ruido = ruidoRobusto(colC, d0);
    var zEv = zPico(colC, d0, 0, ruido).rename('z_evento_' + idx);
    var zPl = zPico(colC, d0, CENTRO_PLACEBO, ruido).rename('z_placebo_' + idx);
    bandasRaster.push(zEv, zPl, ruido.rename('ruido_' + idx));

    var props = {aoi_id: id, data_aoi: dataStr, indice: idx};
    todasDeteccoes = todasDeteccoes
      .merge(objetos(zEv, aoi, ee.Dictionary(props).set('tipo', 'evento')))
      .merge(objetos(zPl, aoi, ee.Dictionary(props).set('tipo', 'placebo')));

    // Área avaliável: pixels com z calculado (evento e placebo) dentro da AOI.
    var area = function (z) {
      return ee.Image.pixelArea().divide(1e4).updateMask(z.mask())
        .reduceRegion({reducer: ee.Reducer.sum(), geometry: aoi, scale: 10,
                       maxPixels: 1e9}).get('area');
    };
    resumo = resumo.merge(ee.FeatureCollection([ee.Feature(null, props).set({
      area_aoi_ha: aoi.area(1).divide(1e4),
      area_avaliavel_evento_ha: area(zEv),
      area_avaliavel_placebo_ha: area(zPl),
      n_datas: col.size()
    })]));

    // z máximo num raio de 15 m em torno dos pontos perto da AOI.
    var pts = pontos.filterBounds(regiao);
    var amostra = zEv.rename('z_evento').addBands(zPl.rename('z_placebo'))
      .reduceRegions({collection: pts.map(function (p) { return p.buffer(15); }),
                      reducer: ee.Reducer.max(), scale: 10})
      .map(function (f) { return f.set(props).setGeometry(null); });
    amostrasPontos = amostrasPontos.merge(amostra);
  });

  Export.image.toDrive({
    image: ee.Image(bandasRaster).toFloat().clip(regiao),
    description: 'aoi_z_' + id, folder: PASTA_DRIVE, region: regiao,
    scale: 10, crs: 'EPSG:4326', maxPixels: 1e9
  });
});

Export.table.toDrive({collection: todasDeteccoes, description: 'aoi_deteccoes_v1',
  folder: PASTA_DRIVE, fileFormat: 'CSV',
  selectors: ['aoi_id', 'data_aoi', 'indice', 'tipo', 'lon', 'lat', 'z_max', 'n_pixels']});
Export.table.toDrive({collection: resumo, description: 'aoi_resumo_v1',
  folder: PASTA_DRIVE, fileFormat: 'CSV',
  selectors: ['aoi_id', 'data_aoi', 'indice', 'area_aoi_ha', 'area_avaliavel_evento_ha',
              'area_avaliavel_placebo_ha', 'n_datas']});
Export.table.toDrive({collection: amostrasPontos, description: 'aoi_pontos_v1',
  folder: PASTA_DRIVE, fileFormat: 'CSV',
  selectors: ['aoi_id', 'data_aoi', 'indice', 'evento_id', 'data_evento',
              'classe_flor', 'z_evento', 'z_placebo']});

// ------------------- SUBPARCELAS PARA O CENSO -------------------------------
// AOI10 e AOI11 (~60 ha): censo da AOI inteira.
// AOI12 (8.561 ha): 3 quadrados de 500 m sorteados, um por estrato de cobertura
// lenhosa natural (MapBiomas): fragmento (>=70%), borda (30–70%), matriz (<30%).
var mbTodas = ee.Image(MAPBIOMAS);
var bandaMB = MAPBIOMAS_BANDA ? ee.String(MAPBIOMAS_BANDA)
                             : ee.String(mbTodas.bandNames().sort().get(-1));
print('MapBiomas: banda usada na estratificação', bandaMB);
var mb = mbTodas.select([bandaMB]);
var lenhosa = mb.remap(CLASSES_NATURAIS_LENHOSAS,
  CLASSES_NATURAIS_LENHOSAS.map(function () { return 1; }), 0).rename('lenhosa');

var aoi12 = ee.Feature(AOIS.filter(function (f) {
  return f.get('aoi_id').getInfo() === 'AOI12'; })[0]).geometry();
var meioLado = LADO_SUBPARCELA / 2;
var candidatos = ee.FeatureCollection.randomPoints({
    region: aoi12.buffer(-meioLado * 1.5), points: 300, seed: SEMENTE})
  .map(function (p) {
    return ee.Feature(p.geometry().buffer(meioLado).bounds(), {ordem: p.get('system:index')});
  });
candidatos = lenhosa.reduceRegions({collection: candidatos, reducer: ee.Reducer.mean(), scale: 30})
  .map(function (f) {
    var fr = ee.Number(f.get('mean'));
    var estrato = ee.Algorithms.If(fr.gte(0.7), 'fragmento',
                  ee.Algorithms.If(fr.gte(0.3), 'borda', 'matriz'));
    return f.set({frac_lenhosa: fr, estrato: estrato});
  });
var sorteadas = ee.FeatureCollection(['fragmento', 'borda', 'matriz'].map(function (e) {
  return ee.Feature(candidatos.filter(ee.Filter.eq('estrato', e)).first())
    .set('subparcela', ee.String('AOI12_').cat(e), 'aoi_id', 'AOI12');
}));
var inteiras = ee.FeatureCollection(AOIS.filter(function (f) {
  var id = f.get('aoi_id').getInfo(); return id === 'AOI10' || id === 'AOI11';
}).map(function (f) {
  return ee.Feature(f.geometry(), {subparcela: ee.String(f.get('aoi_id')).cat('_inteira'),
    aoi_id: f.get('aoi_id'), estrato: 'AOI inteira'});
}));
var subparcelas = inteiras.merge(sorteadas);
print('Subparcelas sorteadas', subparcelas);
Map.addLayer(subparcelas, {color: 'yellow'}, 'subparcelas');
Export.table.toDrive({collection: subparcelas, description: 'subparcelas_censo_v1',
  folder: PASTA_DRIVE, fileFormat: 'KML',
  selectors: ['subparcela', 'aoi_id', 'estrato', 'frac_lenhosa']});

// --------------------- INSPEÇÃO RÁPIDA (opcional) ----------------------------
Map.centerObject(AOIS[0].geometry(), 15);   // AOI10 (rosa)
AOIS.forEach(function (f) { Map.addLayer(f.geometry(), {color: 'white'}, f.get('aoi_id').getInfo(), false); });
