# Memoria técnica — Escudo del Alba

La presentación actual usa un cuaderno de armería: lámina central, anotaciones marginales y pruebas de acabado. Los cambios de esta revisión afectan a HTML, CSS y etiquetas de interacción; el modelo y sus mapas conservan las estadísticas y la validación descritas debajo. Este rediseño no se ha publicado.

## Concepto y modelado

El objeto es una interpretación original de un escudo medieval de punta, con emblema solar. Las dimensiones son aproximadas y no representan una reconstrucción histórica documentada.

La silueta se define con curvas Bézier muestreadas y se triangula mediante anillos concéntricos. El frente tiene una curvatura suave; el reverso y el canto dan espesor al cuerpo. El aro de acero usa un perfil de varios anillos para formar biseles reales. El umbo, el medallón, los ocho rayos y los remaches usan perfiles de revolución o formas simples de baja resolución. Las dos correas del reverso se modelan como cintas curvas con espesor.

Se agrupa la geometría por material antes de exportar: hay una primitiva para madera, una para acero, una para bronce y una para cuero. Las costuras UV y las normales duras necesitan vértices separados; por eso el total de vértices exportados supera al de posiciones geométricas únicas.

| Material | Triángulos | Vértices exportados |
|---|---:|---:|
| Madera | 602 | 1.511 |
| Acero | 1.322 | 3.079 |
| Bronce | 2.406 | 4.879 |
| Cuero | 256 | 512 |
| **Total** | **4.586** | **9.981** |

## UV

Todas las caras exportadas tienen `TEXCOORD_0`. Las caras principales del cuerpo usan proyección planar para mantener las vetas a lo largo de la altura. Las piezas circulares usan coordenadas planas centradas, de modo que los grabados concéntricos se alinean con el medallón. El canto, el borde y las correas usan proyección adaptada a su extensión.

Se usan juegos de texturas por material en lugar de un atlas universal. Los remaches y otras piezas repetidas reutilizan coordenadas deliberadamente; el solapamiento en estas piezas no es un error. La vista `uv-layout.png` muestra los cuatro dominios por separado. Las caras verticales de cantos, aros y correas usan islas planares locales con área UV no nula; las piezas repetidas reutilizan deliberadamente el dominio del material. No hay lightmap ni necesidad de un segundo UV sin solapamientos.

## Flujo PBR

Se generan cuatro materiales distintos a 512 × 512 píxeles con un flujo metallic/roughness de glTF:

- **Base Color:** JPEG RGB, interpretado como sRGB. La madera contiene vetas, cambios entre tablones y nudos; el acero, variaciones de forja; el bronce, variaciones de pátina; el cuero, grano fino.
- **Roughness:** mapa lineal monocanal, con valores altos para madera/cuero y moderados para metales.
- **Metallic:** mapa lineal monocanal. Madera y cuero son dieléctricos (0); acero y bronce, metales (1).
- **Normal:** mapa tangente RGB PNG, convención glTF/OpenGL (+Y). Se calcula a partir del gradiente de un campo de altura; incluye vetas, marcas de superficie y grabados.
- **Metallic/Roughness combinado:** PNG RGB; R queda en 255, G almacena Roughness y B almacena Metallic. El GLB referencia ese mapa combinado. Los mapas individuales también se entregan para edición.

Los detalles finos de los grabados del bronce están en el normal map. Desactivarlo en la página deja visibles los volúmenes modelados y el color base, pero desaparecen las ranuras. Las normales y tangentes se exportan de manera explícita y pasan el validador.

El relieve se obtiene de campos de altura procedurales. No se hizo un bake high-poly/low-poly en Substance Painter ni se simula que lo hubiera. No es necesario un bake de ese tipo para este flujo; los mapas de altura se incluyen para que el proceso sea inspeccionable.

## Optimización y exportación

El GLB contiene todos los mapas necesarios para su aspecto inicial, sin rutas externas de texturas. Se emplean índices de 16 bits y se deduplican esquinas que comparten posición, normal, UV y tangente. El detalle fino lo aportan los mapas en lugar de subdivisiones.

La textura alternativa de madera es un JPEG de 512 px que se carga a petición y luego se reutiliza. No se duplican los mapas Roughness, Metallic o Normal de la madera para ese cambio cromático. El visor original y la alternativa suman sus propias descargas al GLB de 1,45 MiB.

## Página e interacción

La página es un cuaderno de armería hecho con HTML/CSS/JavaScript estático: lámina central, anotaciones marginales y controles de acabado al pie. Usa Google model-viewer 4.4.0, servido localmente desde `vendor/`. La iluminación es el entorno neutral integrado, con sombras de contacto. Los tres controles modifican materiales mediante la API documentada después del evento `load`.

Se incluyeron etiquetas accesibles, estados pulsados, foco visible, mensajes de carga/error y enlace directo al GLB. El giro es opcional, desactivado al abrir la página, y la animación decorativa de carga respeta `prefers-reduced-motion`.

## Verificación

- Validación con Khronos glTF Validator 2.0.0-dev.3.10: **0 errores, 0 advertencias**.
- Revisión visual del frente y reverso en el navegador.
- Prueba combinada de los tres controles: nogal, acero pavonado y bronce sin normal map; restauración posterior.
- Comprobación de la vista móvil a 390 × 844 y ausencia de desbordamiento horizontal.
- Sintaxis del JavaScript comprobada con `node --check`.

El informe técnico completo está en `source/validation-gltf.json`. No se presenta la prueba de un navegador de escritorio con viewport móvil como una prueba en un dispositivo físico.

El rediseño se revisó en navegador de escritorio y a 390 × 844 px, sin desbordamiento horizontal. Se probaron los tres botones de material, las vistas, el giro y la restauración; no se registraron errores de JavaScript. La publicación sigue pendiente.

## Revisión de requisitos — 22 de octubre de 2026

Se corrigieron caras cuyo UV planar original se reducía a una línea. Ahora los cantos y paredes verticales reciben una proyección local en el plano de cada cara, continua sobre la diagonal del cuadrilátero y reutilizable en piezas pequeñas. La auditoría comprueba **0 triángulos con UV de área nula**. El número de triángulos y las siluetas se mantienen; cambian algunas costuras, tangentes y el número de vértices exportados. Las estadísticas y los ZIP se actualizaron.
