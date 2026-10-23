import { cp, mkdir, readFile, writeFile, rm } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const output = path.join(root, 'dist');
// dist is generated exclusively by this script; editable sources live elsewhere.
await rm(output, { recursive: true, force: true });
await mkdir(output, { recursive: true });
await cp(path.join(root, 'site'), output, { recursive: true });
const vendors = [];
for (const name of ['alba', 'bruma']) {
  const source = path.join(root, 'projects', name, 'dist');
  const target = path.join(output, name);
  vendors.push(await readFile(path.join(source, 'vendor', 'model-viewer.min.js')));
  await cp(source, target, {
    recursive: true,
    filter: candidate => path.relative(source, candidate).split(path.sep)[0] !== 'vendor'
  });
  let html = await readFile(path.join(target, 'index.html'), 'utf8');
  html = html.replace('src="vendor/model-viewer.min.js"', 'src="../vendor/model-viewer.min.js"');
  if (name === 'alba') {
    html = html.replace('<span>CUADERNO DE ARMERÍA</span>', '<a href="../">← VER ESCUDOS</a>');
  } else {
    html = html.replace('Escudo circular / Proyecto 02</p>', '<a href="../">← Ver escudos</a></p>');
  }
  await writeFile(path.join(target, 'index.html'), html);
}
const digest = data => createHash('sha256').update(data).digest('hex');
if (digest(vendors[0]) !== digest(vendors[1])) throw new Error('Las versiones de model-viewer no coinciden.');
await cp(path.join(root, 'projects/alba/dist/vendor'), path.join(output, 'vendor'), { recursive: true });
console.log('Sitio construido: /, /alba/ y /bruma/. Sin dependencias externas de compilación.');
await import('./check.mjs');
