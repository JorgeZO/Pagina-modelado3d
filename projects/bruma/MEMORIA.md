# Memoria técnica — Escudo de la Bruma

La presentación actual usa un mesa de inspección: visor sobre retícula, barra de vistas y panel lateral de materiales. Los cambios de esta revisión afectan a HTML, CSS y etiquetas de interacción; el modelo y sus mapas conservan las estadísticas y la validación descritas debajo. Este rediseño no se ha publicado.

## 1. Concepto y modelado

Segundo objeto medieval del proyecto, distinto del Escudo del Alba. Se eligió una silueta circular de inspiración norteña, sin presentarla como reconstrucción histórica exacta. El cuerpo convexo es de fresno, con dos cuarteles pintados de azul. Un aro de acero remachado protege el canto; un umbo metálico sobresale en el centro. Una cenefa de bronce con grabado entrelazado y un collar central aportan contraste. El reverso muestra madera natural y dos correas de cuero con espesor.

La circunferencia tiene 64 segmentos; las superficies amplias se triangulan en anillos. El umbo usa un perfil de revolución de baja resolución. El aro exterior es un perfil cerrado de varios anillos con biseles. La cenefa usa 96 segmentos por su gran perímetro, mientras que los pequeños remaches solo usan ocho o diez segmentos. Cuatro tiras de acero dividen los cuarteles. No se modelaron las vetas, las virutas de pintura ni las líneas finas de la cenefa.

| Material | Triángulos | Vértices exportados |
|---|---:|---:|
| Madera | 1.152 | 2.252 |
| Acero | 1.832 | 3.670 |
| Bronce | 2.552 | 4.924 |
| Cuero | 224 | 448 |
| **Total** | **5.760** | **11.294** |

Los vértices se deduplican cuando coinciden posición, normal, UV y tangente. Las costuras y los cambios de dirección de las tangentes producen vértices separados. Al final, toda la geometría se agrupa en cuatro primitivas, una por material.

## 2. UV

Cada cara tiene coordenadas `TEXCOORD_0`. El frente de madera usa un dominio planar cuadrado, con las vetas paralelas al eje vertical. El reverso reutiliza una región sin pintura del mismo material, evitando una quinta primitiva y otra descarga. Los aros y el umbo tienen proyecciones planas centradas para alinear las decoraciones circulares. Los cantos de madera, las tiras y las correas usan tiras UV de área no nula. Los pequeños remaches reutilizan textura deliberadamente.

No hay un atlas universal ni un lightmap. Cada material tiene su propio juego de mapas de 512 px. El solapamiento de UV en los elementos repetidos es intencional. `source/uv-layout.png` permite ver la distribución de los cuatro dominios. Las paredes verticales de los aros usan islas planares locales con área UV no nula. Las piezas pequeñas reutilizan el dominio de su material y el GLB valida sin errores.

## 3. Texturizado PBR

Flujo metallic/roughness compatible con glTF. Todos los mapas tienen 512 × 512 píxeles. La textura de madera combina ruido anisotrópico, vetas, variaciones entre tablones y nudos. El color base tiene pintura azul en cuarteles opuestos y zonas donde el fresno queda expuesto. El acero tiene marcas suaves de forja y arañazos; el bronce, variación de pátina; el cuero, grano irregular.

Por cada juego se entregan:

- **Base Color:** JPEG RGB, interpretado como sRGB.
- **Roughness:** PNG monocanal lineal.
- **Metallic:** PNG monocanal lineal; 0 en madera/cuero y 1 en acero/bronce.
- **Normal Map:** PNG tangente RGB, convención glTF/OpenGL (+Y).
- **Metallic/Roughness combinado:** PNG RGB; G contiene Roughness y B, Metallic. R queda en 255 y no se usa como oclusión.
- **Height:** campo de altura fuente del normal map, conservado para edición y trazabilidad.

Las normales se calculan a partir del gradiente del campo de altura. En el bronce, la cenefa entrelazada y el grabado del collar residen en ese mapa. Desactivarlo elimina las ranuras aparentes manteniendo el volumen real del aro. No se hizo un bake high-poly/low-poly en Substance Painter: se usó un flujo procedural de altura a normal, y no se atribuye el modelo a otro programa.

El juego alternativo **Fresno** incluye Base Color, Metallic/Roughness y Normal sin pintura. Se cambian juntos, conservando la correspondencia entre color, relieve y rugosidad. Esos tres archivos son externos al GLB para cargarlos solo cuando el usuario los solicita.

## 4. Exportación y optimización

GLB autocontenido de **1.469.128 bytes (1,40 MiB)**, con 12 imágenes integradas, índices de 16 bits, normales y tangentes explícitas. La silueta, los biseles, el umbo y las correas usan geometría; el detalle fino, mapas. No hay animaciones, esqueletos ni morph targets. No se requieren decodificadores Draco o KTX2. Los cuatro materiales se dibujan como cuatro primitivas en el pase principal.

El JavaScript de Google model-viewer 4.4.0 se sirve desde `dist/vendor/`. El entorno neutral está integrado en el componente y no se descarga un HDR externo. La página no usa un CDN de JavaScript ni fuentes remotas.

## 5. Página e interacción

HTML/CSS/JavaScript estático con una mesa de inspección oscura: visor sobre retícula, herramientas de cámara y panel de materiales lateral. Se usa Google model-viewer, controles de cámara, sombra de contacto y tres botones de materiales:

1. Madera: `createTexture()` y `setTexture()` para el juego PBR completo.
2. Acero: `setBaseColorFactor()` para el acabado pavonado.
3. Bronce: `normalTexture.setTexture(null)` para desactivar el relieve y restauración del objeto de textura original para activarlo.

La página espera al evento `load` antes de habilitar los controles. Los estados se comunican con `aria-pressed` y un área de mensajes. Incluye foco visible, enlace de salto al modelo, carga, aviso de error y descarga directa del GLB. El giro automático está desactivado al abrir. La animación de carga respeta la preferencia de movimiento reducido. Si se pulsa Restablecer mientras se prepara el juego alternativo, una solicitud pendiente no cambia de nuevo el acabado restaurado.

## 6. Verificación y publicación pendiente

- Khronos glTF Validator 2.0.0-dev.3.10: **0 errores y 0 advertencias**; informe incluido.
- JavaScript comprobado con `node --check`.
- Vista frontal y reverso revisados visualmente en navegador local.
- Tres cambios de material combinados, restauración y controles de vista probados.
- Vista móvil revisada a 390 × 844 píxeles y sin desbordamiento horizontal. Es una prueba con viewport móvil, no un dispositivo físico.
- Configuración estática `vercel.json` preparada con `dist` como directorio de salida.

**La publicación se deja pendiente por instrucción expresa del usuario.** Este segundo proyecto se integra en el repositorio Pagina-modelado3d; no se ha publicado en Vercel. El Escudo del Alba se conserva aparte para integrarlos en este repositorio.

El rediseño se revisó en navegador de escritorio y a 390 × 844 px, sin desbordamiento horizontal. Se probaron los tres botones de material, las vistas, el giro y la restauración; no se registraron errores de JavaScript. La publicación sigue pendiente.

## Revisión de requisitos — 22 de octubre de 2026

Se corrigieron caras cuyo UV planar original se reducía a una línea. Ahora los cantos y paredes verticales reciben una proyección local en el plano de cada cara, continua sobre la diagonal del cuadrilátero y reutilizable en piezas pequeñas. La auditoría comprueba **0 triángulos con UV de área nula**. El número de triángulos y las siluetas se mantienen; cambian algunas costuras, tangentes y el número de vértices exportados. Las estadísticas y los ZIP se actualizaron.
