const viewer = document.querySelector('#shield');
const $ = id => document.getElementById(id);
const controlIds = ['wood', 'steel', 'bronze', 'reset', 'front', 'back', 'rotate'];
const defaults = { wood: false, steel: false, bronze: true };
const originalOrbit = '-16deg 84deg 2.6m';
let state = { ...defaults };
let materials, originalWood, originalBronze, naturalSet, naturalPromise;
let ready = false, woodRequest = 0;

function refreshLabels() {
  ['wood', 'steel', 'bronze'].forEach(id => $(id).setAttribute('aria-pressed', String(state[id])));
  $('wood-value').textContent = state.wood ? 'Fresno natural' : 'Cuarteles azules';
  $('steel-value').textContent = state.steel ? 'Acero pavonado' : 'Acero satinado';
  $('bronze-value').textContent = state.bronze ? 'Cenefa grabada' : 'Superficie lisa';
  $('wood-action').textContent = state.wood ? 'Recuperar los cuarteles azules' : 'Usar fresno natural';
  $('steel-action').textContent = state.steel ? 'Recuperar el acero satinado' : 'Aplicar pavonado';
  $('bronze-action').textContent = state.bronze ? 'Desactivar normal map' : 'Activar normal map';
  $('wood').querySelector('.swatch').style.backgroundImage = state.wood
    ? "url('assets/fresno-basecolor.jpg')" : '';
  $('steel').querySelector('.swatch').style.filter = state.steel ? 'brightness(.38) sepia(.25) hue-rotate(155deg)' : '';
}
function applyMaterials() {
  const woodSet = state.wood ? naturalSet : originalWood;
  const pbr = materials.Madera.pbrMetallicRoughness;
  pbr.baseColorTexture.setTexture(woodSet.color);
  pbr.metallicRoughnessTexture.setTexture(woodSet.mr);
  materials.Madera.normalTexture.setTexture(woodSet.normal);
  materials.Acero.pbrMetallicRoughness.setBaseColorFactor(state.steel ? '#526a78' : '#ffffff');
  materials.Bronce.normalTexture.setTexture(state.bronze ? originalBronze : null);
  refreshLabels();
}
function stopRotation() {
  viewer.autoRotate = false;
  $('rotate').setAttribute('aria-pressed', 'false');
  $('rotate').setAttribute('aria-label', 'Activar giro automático');
  $('rotate').title = 'Activar giro automático';
}
function showError() {
  ready = false;
  $('loading').classList.add('loaded');
  $('model-error').hidden = false;
  $('edit-note').textContent = 'El modelo no está disponible';
  controlIds.forEach(id => $(id).disabled = true);
}
viewer.addEventListener('progress', ({ detail }) => {
  $('progress').style.width = `${detail.totalProgress * 100}%`;
});
viewer.addEventListener('load', () => {
  materials = Object.fromEntries(viewer.model.materials.map(m => [m.name, m]));
  if (!['Madera', 'Acero', 'Bronce', 'Cuero'].every(name => materials[name])) return showError();
  const wood = materials.Madera;
  originalWood = {
    color: wood.pbrMetallicRoughness.baseColorTexture.texture,
    mr: wood.pbrMetallicRoughness.metallicRoughnessTexture.texture,
    normal: wood.normalTexture.texture
  };
  originalBronze = materials.Bronce.normalTexture.texture;
  ready = true;
  $('loading').classList.add('loaded');
  controlIds.forEach(id => $(id).disabled = false);
  $('edit-note').textContent = 'Modelo cargado. Controles disponibles.';
  fetch('assets/model-stats.json').then(r => r.ok ? r.json() : null).then(stats => {
    if (stats) $('size').innerHTML = `${(stats.bytes / 1048576).toLocaleString('es-MX', {
      minimumFractionDigits: 2, maximumFractionDigits: 2
    })} <small>MiB</small>`;
  }).catch(() => {});
});
viewer.addEventListener('error', showError);

$('wood').addEventListener('click', async () => {
  if (!ready) return;
  const request = ++woodRequest;
  if (!naturalSet) {
    $('wood').disabled = true;
    $('edit-note').textContent = 'Preparando los mapas del fresno…';
    try {
      naturalPromise ??= Promise.all([
        viewer.createTexture('assets/fresno-basecolor.jpg'),
        viewer.createTexture('assets/fresno-mr.png'),
        viewer.createTexture('assets/fresno-normal.png')
      ]).then(([color, mr, normal]) => ({ color, mr, normal }));
      naturalSet = await naturalPromise;
    } catch {
      naturalPromise = undefined;
      if (request === woodRequest) $('edit-note').textContent = 'No se cargó el fresno. Vuelve a intentarlo.';
      return;
    } finally {
      $('wood').disabled = !ready;
    }
  }
  if (request !== woodRequest || !ready) return;
  state.wood = !state.wood;
  applyMaterials();
  $('edit-note').textContent = state.wood ? 'Madera: fresno natural' : 'Madera: cuarteles azules';
});
$('steel').addEventListener('click', () => {
  if (!ready) return;
  state.steel = !state.steel;
  applyMaterials();
  $('edit-note').textContent = state.steel ? 'Acero: acabado pavonado' : 'Acero: acabado satinado';
});
$('bronze').addEventListener('click', () => {
  if (!ready) return;
  state.bronze = !state.bronze;
  applyMaterials();
  $('edit-note').textContent = state.bronze ? 'Bronce: normal map activado' : 'Bronce: normal map desactivado';
});
$('reset').addEventListener('click', () => {
  if (!ready) return;
  ++woodRequest;
  state = { ...defaults };
  applyMaterials();
  stopRotation();
  viewer.cameraOrbit = originalOrbit;
  viewer.cameraTarget = '0m 0m 0m';
  $('edit-note').textContent = 'Acabados y vista originales';
});
$('front').addEventListener('click', () => {
  stopRotation(); viewer.cameraOrbit = '0deg 90deg 2.6m';
  $('edit-note').textContent = 'Vista frontal';
});
$('back').addEventListener('click', () => {
  stopRotation(); viewer.cameraOrbit = '180deg 85deg 2.6m';
  $('edit-note').textContent = 'Reverso: madera y correas de cuero';
});
$('rotate').addEventListener('click', () => {
  viewer.autoRotate = !viewer.autoRotate;
  viewer.rotationPerSecond = '12deg';
  const label = viewer.autoRotate ? 'Pausar giro automático' : 'Activar giro automático';
  $('rotate').setAttribute('aria-pressed', String(viewer.autoRotate));
  $('rotate').setAttribute('aria-label', label);
  $('rotate').title = label;
  $('edit-note').textContent = viewer.autoRotate ? 'Giro automático activado' : 'Giro automático pausado';
});
// Keep a useful download and error message if the local Web Component cannot load.
setTimeout(() => { if (!customElements.get('model-viewer')) showError(); }, 30000);
