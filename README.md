# Escudo del Alba — modelo 3D interactivo

Proyecto personal de modelado 3D para web. Un escudo medieval original de silueta de punta y emblema solar, con geometría ligera, UV, cuatro materiales PBR y una página interactiva con Google model-viewer.

La página se abre directamente en `/`, con un diseño de cuaderno de armería: lámina central, anotaciones marginales y pruebas de acabado.

| Dato | Resultado |
|---|---:|
| Triángulos | 4.586 |
| Materiales | Madera, acero, bronce y cuero |
| Mapas PBR | Base Color, Roughness, Metallic y Normal |
| Resolución por mapa | 512 × 512 px |
| GLB | 1.518.884 bytes / 1,45 MiB |

## Controles

Los tres botones de materiales funcionan en tiempo real:

- **Madera:** alternar las texturas de roble y nogal.
- **Acero:** alternar acabado claro y pavonado mediante el factor de color.
- **Bronce:** activar o desactivar el normal map del grabado.

También hay vistas frontal y posterior, giro automático y restauración. La descarga GLB ofrece el archivo original, no una exportación de la personalización actual.

## Ejecutar en local

Requiere Node.js para preparar el sitio; no hay dependencias npm que instalar.

```sh
npm run build
python3 -m http.server 8080 --bind 127.0.0.1 --directory dist
```

Abrir `http://127.0.0.1:8080`. El build comprueba enlaces, controles, cabecera, tamaño y SHA-256 del GLB y el informe de validación. Para repetir esas comprobaciones sobre la salida:

```sh
npm run check
```

## Vercel

Importar este repositorio con **Root Directory: raíz del repositorio**. `vercel.json` declara:

- Framework: sin framework.
- Instalación: ninguna.
- Build: `npm run build`.
- Output Directory: `dist`.

El escudo queda en la página de inicio, sin selector de proyectos. El código está preparado para Vercel; todavía falta completar y verificar el despliegue para obtener el enlace web de revisión.

## Estructura

```text
scripts/build.mjs         Copia la página del escudo a dist/
scripts/check.mjs         Comprueba los archivos publicados
projects/alba/dist/       Página, GLB, recursos y ZIP descargable
projects/alba/source/     Generador, mapas, UV e informes de validación
docs/                     Revisión de requisitos y evidencia
vercel.json               Configuración para Vercel
```

`dist/` de la raíz es generado y no se versiona. Para editar la página, modificar `projects/alba/dist/` y ejecutar `npm run build`. El componente model-viewer y su licencia se sirven desde `vendor/`.

En `projects/alba/source/` se entregan el generador editable, los mapas individuales y combinados, la vista UV, el informe Khronos y la auditoría. Después de regenerar un GLB, ejecutar `npm run build` desde esta raíz para actualizar el sitio.

## Validación

- Khronos glTF Validator: **0 errores y 0 advertencias**.
- Todas las caras tienen UV de área distinta de cero; las piezas repetidas reutilizan textura deliberadamente.
- Base Color, Roughness, Metallic y Normal a 512 px; Metallic/Roughness empaquetados en B/G.
- Los tres controles de apariencia se probaron en navegador.
- [Revisión de requisitos](docs/REVISION-REQUISITOS.md).

Las texturas se generaron proceduralmente desde campos de altura. El proceso se documenta en `projects/alba/MEMORIA.md`; no se atribuye a Substance Painter ni se presenta un bake de high-poly a low-poly que no se haya realizado.

## Licencia y referencias

Geometría, texturas y código propios: CC0 1.0. Google model-viewer 4.4.0 conserva su licencia Apache 2.0. No se usan modelos ni texturas comerciales de terceros.

Documentación: [model-viewer](https://modelviewer.dev/), [API de materiales](https://modelviewer.dev/examples/scenegraph/) y [Vercel](https://vercel.com/docs/project-configuration/vercel-json).
