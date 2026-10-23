# Escudos medievales interactivos

Proyecto personal de modelado 3D para web. Dos escudos originales con geometría ligera, UV, cuatro materiales PBR y páginas interactivas con Google model-viewer.

| Ruta | Pieza | Triángulos | GLB |
|---|---|---:|---:|
| `/` | Portada para elegir escudo | — | — |
| `/alba/` | Escudo del Alba: de punta, con emblema solar | 4.586 | 1,45 MiB |
| `/bruma/` | Escudo de la Bruma: circular, con cuarteles azules | 5.760 | 1,40 MiB |

Ambos combinan madera, acero, bronce y cuero, con mapas de 512 × 512 px. Las páginas mantienen sus diseños: cuaderno de armería para Alba y mesa de inspección para Bruma.

## Controles

Cada página tiene tres botones de materiales:

- **Madera:** alternar textura de roble/nogal en Alba o el juego PBR azul/fresno natural en Bruma.
- **Acero:** alternar acabado claro y pavonado mediante el factor de color.
- **Bronce:** activar o desactivar el normal map del grabado.

También hay vistas frontal y posterior, giro automático y restauración. Los GLB descargables son los originales, no una exportación de la personalización actual.

## Ejecutar en local

Requiere Node.js para preparar el sitio; no hay dependencias npm que instalar.

```sh
npm run build
python3 -m http.server 8080 --bind 127.0.0.1 --directory dist
```

Abrir `http://127.0.0.1:8080`. El build comprueba enlaces, controles, cabecera, tamaño y SHA-256 de los GLB y los informes de validación. Para repetir esas comprobaciones sobre la salida:

```sh
npm run check
```

## Vercel

Importar este repositorio con **Root Directory: raíz del repositorio**. `vercel.json` declara:

- Framework: sin framework.
- Instalación: ninguna.
- Build: `npm run build`.
- Output Directory: `dist`.

La portada queda en `/`, y las fichas en `/alba/` y `/bruma/`. Subir el código a GitHub no equivale a publicar la web: se debe completar y verificar el despliegue de Vercel para obtener el enlace de revisión.

## Estructura

```text
site/                     Portada y sus estilos
scripts/build.mjs         Genera el sitio en dist/
scripts/check.mjs         Comprueba los archivos publicados
projects/alba/            Fuentes, mapas y página original del Alba
projects/bruma/           Fuentes, mapas y página original de Bruma
vercel.json               Configuración del sitio completo
```

`dist/` es generado y no se versiona. El build copia las páginas originales y añade navegación de regreso a la portada. El componente model-viewer se comparte desde `/vendor/` para aprovechar la caché.

En `projects/*/source/` se entregan el generador editable, los mapas individuales y combinados, la vista UV, el informe Khronos y la auditoría. El generador conserva las rutas de su proyecto individual: después de regenerar un GLB, ejecutar `npm run build` desde esta raíz para actualizar el sitio.

## Validación

- Ambos GLB: Khronos glTF Validator con **0 errores y 0 advertencias**.
- Todas las caras tienen UV de área distinta de cero. Las piezas repetidas reutilizan textura deliberadamente.
- Base Color, Roughness, Metallic y Normal a 512 px; Metallic/Roughness empaquetados en B/G.
- Los tres controles de apariencia se probaron en navegador.
- [Revisión de requisitos](docs/REVISION-REQUISITOS.md).

Las texturas se generaron proceduralmente desde campos de altura. No se atribuye el trabajo a Substance Painter ni se presenta un bake de high-poly a low-poly que no se haya realizado.

## Licencia y referencias

Geometría, texturas y código propios: CC0 1.0. Google model-viewer 4.4.0 conserva su licencia Apache 2.0. No se usan modelos ni texturas comerciales de terceros.

Documentación: [model-viewer](https://modelviewer.dev/), [API de materiales](https://modelviewer.dev/examples/scenegraph/) y [Vercel](https://vercel.com/docs/project-configuration/vercel-json).
