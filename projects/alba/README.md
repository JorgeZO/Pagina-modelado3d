# Escudo del Alba — proyecto 3D para web

> Rediseño actual, solo en local: cuaderno de armería: lámina central, anotaciones marginales y pruebas de acabado. Se mantienen el GLB y los tres controles de materiales. Integrado en el repositorio Pagina-modelado3d; pendiente publicar en Vercel.

Escudo medieval original de silueta de punta, cuerpo curvo de madera, borde biselado de acero, emblema solar de bronce y dos correas de cuero. La página permite explorar el frente, el canto y el reverso con Google `<model-viewer>` 4.4.0.

## Entregables

- `dist/index.html`, `styles.css` y `app.js`: página adaptable a móvil y escritorio, lista para hosting estático.
- `dist/assets/escudo-del-alba.glb`: geometría, UV, tangentes y texturas PBR integradas en un único archivo.
- `source/textures/`: mapas de cada material, incluyendo Base Color, Roughness, Metallic y Normal; también el mapa de altura usado para generar normales y la textura combinada Metallic/Roughness.
- `source/generate_shield.py`: fuente editable y reproducible del modelo y sus texturas.
- `source/uv-layout.png`: visualización de los UV por material.
- `source/validation-gltf.json`: informe del validador oficial glTF de Khronos, sin errores ni advertencias.
- `MEMORIA.md`: decisiones de modelado, UV, PBR, optimización e interacciones.

## Ficha técnica

| Dato | Resultado |
|---|---:|
| Triángulos | 4.586 |
| Vértices exportados, con costuras y tangentes | 9.981 |
| Materiales / primitivas / draw calls del objeto | 4 |
| Texturas integradas | 12 |
| Resolución por textura | 512 × 512 px |
| Peso del GLB | 1.518.884 bytes · 1,45 MiB |
| Tamaño aproximado del escudo | 0,76 × 1,12 m |
| Formato | glTF 2.0 binario / GLB |

El peso corresponde al GLB. El componente model-viewer y la segunda textura de madera se descargan aparte. No se usa Draco ni KTX2: este modelo ya tiene una descarga moderada y evita decodificadores adicionales. El número real de llamadas de una escena puede aumentar por sombras y otros pases; cuatro corresponde a las cuatro primitivas del objeto.

## Abrir localmente

No hace falta una instalación de Node ni un proceso de compilación. Desde la carpeta del proyecto:

```sh
python3 -m http.server 8080 --directory dist
```

Abrir `http://localhost:8080`. Usar un servidor HTTP en lugar de abrir el HTML directamente con `file://` para que el navegador pueda cargar el GLB y la textura alternativa.

## Controles de apariencia (los tres botones solicitados)

1. **Madera:** cambia la textura Base Color entre roble natural y nogal oscuro. Usa `createTexture()` y `baseColorTexture.setTexture()`; la textura alternativa se carga solo al solicitarla.
2. **Acero:** aplica un factor de color al acero para alternar entre acabado claro y pavonado. Usa `pbrMetallicRoughness.setBaseColorFactor()`.
3. **Bronce:** elimina y restaura el normal map. Usa `normalTexture.setTexture(null)` y después restaura el objeto de textura original.

Los cambios son combinables y no alteran la geometría. Restablecer recupera todos los acabados y la cámara originales. Hay controles adicionales de vista frontal, reverso y giro automático. Los botones se habilitan después de cargar el modelo y comunican sus estados mediante `aria-pressed`.

La descarga GLB ofrece el archivo original, no una exportación del estado personalizado en el visor.

## Regenerar el modelo y los mapas

Requiere Python 3, NumPy y Pillow. Se recomienda un entorno virtual:

```sh
python3 -m venv .venv
.venv/bin/pip install numpy pillow
.venv/bin/python source/generate_shield.py
```

El script usa una semilla fija. Escribe el GLB, sus estadísticas, los mapas y la vista UV. Las versiones usadas para esta entrega son NumPy 2.3.5 y Pillow 12.3.0. El informe glTF no se regenera automáticamente: validar de nuevo si se modifica la geometría.

Para editar manualmente, importar el GLB en Blender (`Archivo > Importar > glTF 2.0`). En esta entrega el archivo fuente editable es el generador de Python; no se incluye un archivo `.blend` ni se atribuye el trabajo a Substance Painter.

## Publicar en otro servidor

Subir todo el contenido de `dist/` a cualquier hosting estático, conservando las rutas. Netlify permite desplegar esa carpeta; GitHub Pages puede servirla como raíz de publicación; Vercel admite el mismo contenido con salida estática. El sitio no requiere claves, servicios de pago ni backend. El componente y su licencia se incluyen en `dist/vendor/`, por lo que el visor no depende de un CDN de JavaScript.

## Documentación consultada

- Google model-viewer: https://modelviewer.dev/
- Materiales y scene graph: https://modelviewer.dev/examples/scenegraph/
- API de materiales (fuente oficial): https://github.com/google/model-viewer/blob/master/packages/model-viewer/src/features/scene-graph/api.ts
- Especificación glTF 2.0: https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html
- Validador oficial: https://github.com/KhronosGroup/glTF-Validator

## Licencias

La geometría, las texturas procedurales, el diseño y el código propios se entregan bajo CC0 1.0 (ver `LICENSE.txt`). No se utilizaron modelos, escaneos ni texturas comerciales de terceros. Google model-viewer conserva su licencia Apache 2.0 en `dist/vendor/LICENSE-model-viewer.txt`.
