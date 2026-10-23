import { readFile, stat, readdir } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const output = path.join(root, 'dist');
const assert = (condition, message) => { if (!condition) throw new Error(message); };
let checked = 0;
async function checkFile(file) {
  const content = await readFile(file, 'utf8');
  const refs = file.endsWith('.html')
    ? [...content.matchAll(/\b(?:src|href)="([^"]+)"/g)].map(m => m[1])
    : [...content.matchAll(/url\(['"]?([^)'"\s]+)['"]?\)/g)].map(m => m[1]);
  for (const ref of refs) {
    if (/^(?:https?:|data:|#)/.test(ref)) continue;
    const target = path.resolve(path.dirname(file), ref.split('#')[0].split('?')[0]);
    assert(target === output || target.startsWith(output + path.sep), `Ruta fuera de dist: ${ref}`);
    const info = await stat(target).catch(() => null);
    assert(info, `Recurso inexistente: ${path.relative(output, file)} → ${ref}`);
    if (info.isDirectory()) await stat(path.join(target, 'index.html'));
    checked++;
  }
}
for (const route of ['', 'alba', 'bruma']) {
  const directory = path.join(output, route);
  await checkFile(path.join(directory, 'index.html'));
  await checkFile(path.join(directory, 'styles.css'));
  if (!route) continue;
  const html = await readFile(path.join(directory, 'index.html'), 'utf8');
  for (const id of ['shield', 'wood', 'steel', 'bronze', 'reset', 'front', 'back', 'rotate', 'edit-note']) {
    assert(html.includes(`id="${id}"`), `Falta el control ${id} en ${route}`);
  }
  const slug = route === 'alba' ? 'escudo-del-alba' : 'escudo-de-la-bruma';
  const model = await readFile(path.join(directory, 'assets', `${slug}.glb`));
  const stats = JSON.parse(await readFile(path.join(directory, 'assets/model-stats.json'), 'utf8'));
  assert(model.readUInt32LE(0) === 0x46546c67 && model.readUInt32LE(4) === 2, 'GLB inválido');
  assert(model.readUInt32LE(8) === model.length && stats.bytes === model.length, 'Longitud del GLB incorrecta');
  assert(createHash('sha256').update(model).digest('hex') === stats.sha256, 'El hash del GLB no coincide');
  const gltf = JSON.parse(model.subarray(20, 20 + model.readUInt32LE(12)).toString());
  assert(gltf.materials.length === 4, 'El modelo debe conservar cuatro materiales');
  assert(gltf.meshes.every(m => m.primitives.every(p => p.attributes.TEXCOORD_0 != null)), 'Faltan UV');
  const validation = JSON.parse(await readFile(path.join(root, 'projects', route, 'source/validation-gltf.json'), 'utf8'));
  assert(validation.issues.numErrors === 0 && validation.issues.numWarnings === 0, 'Validación glTF fallida');
}
const files = await readdir(path.join(output, 'vendor'));
assert(files.includes('LICENSE-model-viewer.txt'), 'Falta la licencia de model-viewer');
console.log(`Verificación completada: ${checked} rutas locales, dos GLB y todos los controles.`);
