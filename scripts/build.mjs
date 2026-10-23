import { cp, rm } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const output = path.join(root, 'dist');
// dist is generated exclusively by this script; editable sources live in projects/alba.
await rm(output, { recursive: true, force: true });
await cp(path.join(root, 'projects/alba/dist'), output, { recursive: true });
console.log('Sitio construido: Escudo del Alba en /. Sin dependencias externas de compilación.');
await import('./check.mjs');
