for (const viewer of document.querySelectorAll('model-viewer')) {
  const status = viewer.closest('.piece').querySelector('.preview-state');
  viewer.addEventListener('load', () => { status.textContent = 'Vista 3D'; });
  viewer.addEventListener('error', () => { status.textContent = 'Abrir ficha ↓'; });
}
