# Escudo de la Bruma — segundo proyecto 3D

> Rediseño actual, solo en local: mesa de inspección: visor sobre retícula, barra de vistas y panel lateral de materiales. Se mantienen el GLB y los tres controles de materiales. Integrado en el repositorio Pagina-modelado3d; pendiente publicar en Vercel.

**Estado de entrega: integrado en el repositorio Pagina-modelado3d.** La publicación web en Vercel sigue pendiente. Este proyecto es independiente del Escudo del Alba.

Objeto medieval original: escudo circular de madera de fresno con dos cuarteles azules, borde remachado y umbo de acero, cenefa entrelazada de bronce y dos correas de cuero en el reverso. Se presenta en una página estática con Google `<model-viewer>` 4.4.0.

## Archivos

- `dist/index.html`, `dist/styles.css`, `dist/app.js`: página adaptable con controles de materiales y cámara.
- `dist/assets/escudo-de-la-bruma.glb`: modelo autocontenido con cuatro materiales PBR.
- `dist/assets/fresno-*`: juego PBR alternativo de madera natural, cargado a petición.
- `dist/assets/model-stats.json`: estadísticas y SHA-256 del GLB.
- `dist/vendor/`: componente model-viewer y su licencia Apache 2.0, servidos localmente.
- `source/generate_shield.py`: fuente editable y reproducible de la geometría, UV, materiales y exportación.
- `source/textures/`: Base Color, Roughness, Metallic, Normal, altura y Metallic/Roughness combinado, por material; incluye el juego alternativo de fresno natural.
- `source/uv-layout.png`: vista de los dominios UV.
- `source/validation-gltf.json`: informe del validador oficial glTF de Khronos.
- `MEMORIA.md`: explicación de modelado, texturizado y optimización.
- `vercel.json`: configuración estática local para usar `dist` como directorio de salida. No realiza ningún despliegue.

## Ficha técnica

| Dato | Resultado |
|---|---:|
| Triángulos | 5.760 |
| Vértices exportados | 11.294 |
| Materiales y primitivas | 4 |
| Resolución de mapas | 512 × 512 px |
| Imágenes integradas en el GLB | 12 |
| Peso del GLB | 1.469.128 bytes / 1,40 MiB |
| Diámetro | 0,966 m |
| Formato | glTF 2.0 binario / GLB |
| Validación glTF | 0 errores, 0 advertencias |

El tamaño del GLB no incluye el JavaScript del visor ni los tres mapas alternativos. Las cuatro primitivas implican cuatro llamadas para dibujar el objeto en un pase normal; sombras y otros pases pueden añadir llamadas de renderizado.

## Abrir en local

Desde la raíz de este proyecto:

```sh
python3 -m http.server 8080 --bind 127.0.0.1 --directory dist
```

Abrir `http://127.0.0.1:8080`. El servidor solo escucha en el equipo local. No abrir el HTML con `file://`: el navegador necesita HTTP para cargar correctamente el GLB y los mapas alternativos.

## Los tres botones de materiales

1. **Madera:** alterna cuarteles azules y fresno natural. Cambia simultáneamente Base Color, Metallic/Roughness y Normal. El segundo juego se descarga una sola vez cuando se solicita.
2. **Acero:** alterna acero satinado claro y acabado pavonado oscuro mediante el factor Base Color del material metálico.
3. **Bronce:** desactiva o restaura el Normal Map para comparar la cenefa grabada y una superficie lisa. Su color y geometría siguen siendo los del mismo material.

Los tres cambios son combinables. Restablecer recupera los acabados y la cámara originales. Hay vistas frontal y posterior, giro automático opcional y control libre de cámara con ratón, teclado o tacto. El GLB descargado es el original, no una exportación de la personalización actual.

## Regenerar el modelo

Python 3.11 o superior con NumPy y Pillow. Entorno virtual recomendado:

```sh
python3 -m venv .venv
.venv/bin/pip install numpy==2.3.5 pillow==12.3.0
.venv/bin/python source/generate_shield.py
```

La semilla es fija. El script regenera el GLB, los mapas, las estadísticas y la vista UV. Si cambia la geometría, hay que validar de nuevo el GLB; el informe incluido corresponde a la entrega actual. No se necesita Blender para ejecutar el generador. El GLB se puede importar en Blender para edición manual. No se incluye un archivo `.blend`.

## Preparación para Vercel

El código está preparado como sitio estático, sin backend, claves, instalación npm ni proceso de compilación. La configuración `vercel.json` indica `dist` como salida. Cuando se proporcione el repositorio se podrá incorporar esta carpeta, respetando la estructura que tenga ese repositorio, y conectar Vercel. Si los dos escudos se alojan dentro de una sola página, se ajustarán las rutas y la navegación durante esa integración.

**El código está preparado para el repositorio; todavía no se confirma un despliegue web en Vercel.**

Documentación oficial de esta configuración: https://vercel.com/docs/project-configuration/vercel-json

## Documentación de referencia

- Componente: https://modelviewer.dev/
- Materiales y scene graph: https://modelviewer.dev/examples/scenegraph/
- API oficial: https://github.com/google/model-viewer/blob/master/packages/model-viewer/src/features/scene-graph/api.ts
- glTF 2.0: https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html
- Validador: https://github.com/KhronosGroup/glTF-Validator

## Licencias

Geometría, texturas procedurales, diseño y código propios: CC0 1.0 (`LICENSE.txt`). No se usan modelos ni texturas comerciales de terceros. Google model-viewer conserva su licencia Apache 2.0 en `dist/vendor/LICENSE-model-viewer.txt`.
