const viewer = document.querySelector('#shield');
const controls = ['wood', 'steel', 'bronze', 'reset', 'front', 'back', 'rotate'].map(id => document.getElementById(id));
const button = id => document.getElementById(id);
const note = button('edit-note');
const defaults = { wood: false, steel: false, bronze: true };
let state = { ...defaults };
let materials, originalWood, walnut, originalBronze, loadingWalnut, ready = false;
const changed = () => {
  for (const key of ['wood', 'steel', 'bronze']) button(key).setAttribute('aria-pressed', String(state[key]));
  button('wood-value').textContent = state.wood ? 'Nogal oscuro' : 'Roble natural';
  button('steel-value').textContent = state.steel ? 'Acero pavonado' : 'Forjado claro';
  button('bronze-value').textContent = state.bronze ? 'Relieve grabado' : 'Superficie lisa';
  button('wood-action').textContent = state.wood ? 'Volver al roble natural →' : 'Cambiar a nogal oscuro →';
  button('steel-action').textContent = state.steel ? 'Volver al acero claro →' : 'Aplicar pavonado →';
  button('bronze-action').textContent = state.bronze ? 'Quitar el grabado →' : 'Recuperar el grabado →';
  button('wood').querySelector('.swatch').style.filter = state.wood ? 'brightness(.56)' : '';
  button('steel').querySelector('.swatch').style.filter = state.steel ? 'brightness(.36) sepia(.25) hue-rotate(155deg)' : '';
};
function updateMaterials() {
  materials.Madera.pbrMetallicRoughness.baseColorTexture.setTexture(state.wood ? walnut : originalWood);
  materials.Acero.pbrMetallicRoughness.setBaseColorFactor(state.steel ? '#586e82' : '#ffffff');
  materials.Bronce.normalTexture.setTexture(state.bronze ? originalBronze : null);
  changed();
}
function stopRotation() {
  viewer.autoRotate = false;
  button('rotate').setAttribute('aria-pressed', 'false');
  button('rotate').setAttribute('aria-label', 'Activar giro automático');
  button('rotate').title = 'Activar giro automático';
}
viewer.addEventListener('progress', event => {
  button('progress').style.width = `${event.detail.totalProgress * 100}%`;
});
viewer.addEventListener('load', () => {
  materials = Object.fromEntries(viewer.model.materials.map(material => [material.name, material]));
  if (!['Madera', 'Acero', 'Bronce', 'Cuero'].every(name => materials[name])) return showError();
  originalWood = materials.Madera.pbrMetallicRoughness.baseColorTexture.texture;
  originalBronze = materials.Bronce.normalTexture.texture;
  ready = true;
  button('loading').classList.add('loaded');
  controls.forEach(control => control.disabled = false);
  note.textContent = 'Pieza lista para explorar.';
  fetch('assets/model-stats.json').then(r => r.ok ? r.json() : null).then(stats => {
    if (stats) button('size').innerHTML = `${(stats.bytes / 1048576).toLocaleString('es-MX', {minimumFractionDigits: 2, maximumFractionDigits: 2})} <small>MiB</small>`;
  }).catch(() => {});
});
function showError() {
  button('loading').classList.add('loaded');
  button('model-error').hidden = false;
  note.textContent = 'El modelo no está disponible';
  controls.forEach(control => control.disabled = true);
  ready = false;
}
viewer.addEventListener('error', showError);
button('wood').addEventListener('click', async () => {
  if (!ready) return;
  if (!walnut) {
    button('wood').disabled = true;
    note.textContent = 'Preparando el nogal…';
    try {
      loadingWalnut ??= viewer.createTexture('assets/madera-nogal.jpg');
      walnut = await loadingWalnut;
    } catch {
      loadingWalnut = null;
      note.textContent = 'No se cargó el nogal. Vuelve a intentarlo.';
      button('wood').disabled = false;
      return;
    }
    button('wood').disabled = false;
  }
  state.wood = !state.wood;
  updateMaterials();
  note.textContent = state.wood ? 'Madera: nogal oscuro' : 'Madera: roble natural';
});
button('steel').addEventListener('click', () => {
  state.steel = !state.steel;
  updateMaterials();
  note.textContent = state.steel ? 'Acero: acabado pavonado' : 'Acero: forjado claro';
});
button('bronze').addEventListener('click', () => {
  state.bronze = !state.bronze;
  updateMaterials();
  note.textContent = state.bronze ? 'Bronce: normal map activado' : 'Bronce: normal map desactivado';
});
button('reset').addEventListener('click', () => {
  state = { ...defaults };
  updateMaterials();
  stopRotation();
  viewer.cameraOrbit = '-18deg 82deg 2.6m';
  viewer.cameraTarget = '0m -0.015m 0m';
  note.textContent = 'Acabados y vista originales';
});
button('front').addEventListener('click', () => {
  stopRotation();
  viewer.cameraOrbit = '0deg 90deg 2.6m';
  viewer.cameraTarget = '0m -0.015m 0m';
  note.textContent = 'Vista frontal';
});
button('back').addEventListener('click', () => {
  stopRotation();
  viewer.cameraOrbit = '180deg 85deg 2.6m';
  viewer.cameraTarget = '0m -0.015m 0m';
  note.textContent = 'Reverso: madera y correas de cuero';
});
button('rotate').addEventListener('click', () => {
  viewer.autoRotate = !viewer.autoRotate;
  viewer.rotationPerSecond = '12deg';
  const label = viewer.autoRotate ? 'Pausar giro automático' : 'Activar giro automático';
  button('rotate').setAttribute('aria-pressed', String(viewer.autoRotate));
  button('rotate').setAttribute('aria-label', label);
  button('rotate').title = label;
  note.textContent = viewer.autoRotate ? 'Giro automático activado' : 'Giro automático pausado';
});
// Catch an unavailable Web Component module, while retaining the GLB download.
customElements.whenDefined('model-viewer').catch(showError);
