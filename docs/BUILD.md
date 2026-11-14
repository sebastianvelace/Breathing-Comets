# BUILD.md: guía única para construir Breathing Comets

*Versión del 14 de noviembre de 2026 (con las correcciones de la auditoría, `docs/AUDIT.md`). **Este es el único documento que el agente constructor necesita.** Reemplaza a los antiguos documentos 08, 09, 10 y 11 (archivados en `docs/archive/`). La ciencia de fondo está en `docs/06-tesis-metodologia.md` y los hallazgos crudos del archivo en `docs/03-acceso-datos-spherex.md`; se citan donde hace falta, pero todo lo necesario para construir está aquí.*

**Convenciones del documento:**
- **DEBE** y **NO DEBE** son obligatorios. "Recomendado" admite criterio.
- Cada cifra marcada con ✔ fue **medida o verificada** el 11–12 nov 2026. Las marcadas con ≈ son estimaciones.
- El código, los nombres, los commits y la API van en **inglés**. Este documento está en español.

> ## ESTADO AL 13 NOV: LÉELO PRIMERO
> Si una sección más abajo contradice este recuadro, **manda este recuadro**. Las secciones marcadas como *histórico* o *superado* se conservan solo como contexto.
>
> **Datos y acceso**
> - **Versión de datos:** **DR1 + QR3** (procesamiento R7, v27). QR2 queda reemplazado por DR1.
> - **Claves S3:** índice local `data/derived/spherex_s3_keys_compact.npz`. **El datalink de IRSA no resuelve QR2** (§8, error 35).
> - **Índice de exposiciones:** `data/derived/spherex_exposures_d456_dr1_qr3.parquet` (§8.0b). D1–D3 usan la huella de su par **con margen ≥ 18 px** (las esquinas difieren 28–105″) y descartando los recortes que caigan fuera.
>
> **Fotometría** (`research/spherex_psf.py`, validada: §8.0c)
> - ePSF **muestreada** (no integrada), **sin** corrección de apertura (la calibración de SPHEREx es por ePSF), con la máscara oficial `HARD_ES21`. Lee `PSF` (cubo de QR2) o `EPSF` (tabla de v27).
> - **La malla EPSF no es igual en todos los detectores:** 21×21 (441 filas) en D1, D2, D4, D5 y D6; **11×41 (451 filas) en D3**. Usar `spherex_psf.epsf_row()` (error 49).
> - Error² = σ² + (0.03·F)².
> - Contra 2MASS/WISE, 41 estrellas en 3 campos (NEP, COSMOS, CDFS): J 0.98, H 1.01, Ks 1.01, W1 0.97, W2 1.00 (media 0.994; todas dentro de ±3%). El 0.965 inicial era solo el NEP.
>
> **Asteroides (Small-Body Lab)**
> - **28 tamaños térmicos (11 A + 17 B, 7 PHA) y 6 provisionales**, de 86 candidatos post-NEOWISE (§0.9c): `post_neowise_neo_sizes_v2.csv`.
> - Método: η = 1.48 ± 0.44 (calibrado con la fotometría ePSF final); validación contra NEOWISE en 50 NEO: dispersión fuera de muestra −33%/+36% (1σ). La mediana 1.02 sale por construcción (η se ajusta a ella): **no citarla como exactitud**. Solo estelas ≤ 3 px. 6 de los 28 (entre ellos 2025 YH5) tienen una sola visita (`single_visit`).
>
> **Objetivos del reto (§12.1b–c)**
> - **ε Indi B:** paralaje **271 ± 20 mas** (astrometría diferencial; error por bootstrap de visitas; 277–294 al quitar un control; Gaia DR3 270.7, ε Indi A 274.8), μ 4.75 ± 0.04″/año y espectro de enana T con metano.
> - **WISE 0855:** espectro separado de la estrella vecina; W2 sintética (curva RSR real) 0.45 ± 0.02 mJy, a menos de 10% de la fotometría publicada (W2 ≈ 13.9). **No decir "0.96× AllWISE":** el catálogo AllWISE da 13.70 (0.57 mJy, fuente mezclada).
> - **Barnard:** μ 10.6 ± 0.4″/año (el error formal es 0.10; dominan los sistemáticos).
> - **R Dra:** variabilidad con escala de ≈ 229 d (225–241) a 3.8–5 µm, compatible con el período catalogado (245.6 d). **No decir "período medido 247 ± 10 d":** hay 1.9 ciclos.
> - **RW Aur:** variabilidad anticorrelacionada entre el óptico y 4–5 µm.
> - **No decir "WISE 0855 desaparece en D1":** hay una estrella de fondo.
>
> **Cometas:** el censo de CO₂/CO/H₂O (Apéndice A) se midió con QR2 v20 por apertura. Con DR1, los flujos de 3I quedan iguales (v27/v20 = 0.998) y la λ de D5/D6 se corre +6.3 nm (§8.0b). Las Q siguen valiendo; en los ajustes de banda con DR1, el desplazamiento de λ queda libre.
>
> **Visor:** Aladin 3.8.2 se carga como módulo ES; el canal se elige con `setFrequency` (§9.7).
>
> **Construcción:** no recalcular nada el sábado; se copian los CSV/JSON de `data/derived/` (paso 3 de §19).
>
> **Prototipo de referencia:** `prototype/` (HTML/JS + FastAPI, ver su README). **No es el producto**; sirve para copiar lógica ya probada: espectro con ePSF (`/api/spectrum`), Diff λ, Aladin con `setFrequency` y notas de campo.
>
> **Auditoría y pendientes:** `docs/AUDIT.md` (sección 7: estado de las correcciones) y `docs/PENDIENTES.md` (qué no afirmar ni volver a ejecutar). Los scripts de `research/feasibility/historico/` no se pueden ejecutar.
>
> **Recursos oficiales y socios:** §1.1. NEOSSat (CSA) observó 3I y 8 cometas de nuestro censo.
>
> **Verificación previa al sábado (14 nov, 00:30 COT)**
> - **Repositorio:** limpio. Ganchos probados: `commit-msg` borra las líneas de atribución; `pre-push` rechaza ramas `claude/*` y otras identidades.
> - **Pruebas:** `pytest`: 14/14 (11 sin red y 3 con red; ninguna depende de archivos sin versionar).
> - **`data/export/`:** al día con `data/derived/`.
> - **Archivos citados en este documento:** todos existen, salvo los que genera el producto (`cells.parquet`, `build.json`, `docs/STATUS.md`).
> - **Dependencias:** las 25 versiones de npm y las 10 de PyPI de §3.2 existen.
> - **Servicios externos que responden:** S3 de SPHEREx, HiPS DR1 y 2MASS de IRSA, Horizons, SBDB, Gaia TAP (ESA), SIMBAD (Harvard), jsDelivr (Aladin 3.8.2), Google Fonts y MOST.
> - **IRSA TAP no respondió** (> 120 s, incluso con consulta acotada): el producto no depende de él (índice local).
> - **SIMBAD de CDS:** devuelve 404 desde aquí; usar el espejo de Harvard.
> - **Dominio `breathingcomets.org`:** activo en Cloudflare (NS carter y wren) y sin registro A todavía: se crea en el paso 2 (Pages).
> - **Pendiente de verificar el sábado:** Fly (`breathing-comets-api`) y el certificado de `api.`, que no se pueden revisar desde aquí.

---

## Índice

0. Reglas no negociables
1. El reto (texto oficial) y cómo lo cumplimos
2. Producto: tesis, prioridades y criterios de éxito
3. Arquitectura y stack (versiones exactas)
4. Infraestructura ya creada
5. Repositorio: estructura, arranque y archivos plantilla
6. Contratos de datos
7. API
8. Núcleo científico (`spxcore`)
9. Frontend
10. Sistema visual "Plate & Ink"
11. Internacionalización
12. Datos de referencia
13. Presupuestos de rendimiento
14. Pruebas de aceptación
15. Plan horario y orden de recorte
16. Entrega en Space Apps
17. Catálogo de errores (no repetirlos)
18. Pendientes y preguntas abiertas
19. Instrucciones paso a paso para el agente constructor

---

## 0. Reglas no negociables

1. **Investigación previa:** decidido por el usuario (12 nov): **se puede investigar antes del evento**.
   - El repositorio de investigación puede reutilizarse: scripts, datos derivados y resultados del censo.
   - Aun así, el código del producto vive en el repositorio nuevo y se escribe limpio en `spxcore`. Los scripts de `research/` son referencia: portarlos con tests, no copiarlos tal cual.
   - En la entrega se declara con transparencia qué se hizo antes y qué durante las 48 h (§16).
2. **Identidad de git:**
   - Todos los commits van a nombre de `sebasvelace <sebastianvelace@gmail.com>`, **solo en `main`**.
   - Sin `Co-Authored-By`, sin `Claude-Session` y sin ramas `claude/*`.
   - Hay que copiar los archivos plantilla de §5.3 **en el primer commit**.
3. **Nunca inventar datos.** Si una fuente falla, la interfaz lo dice ("Gaia DR3 unavailable — retry") y muestra lo que sí hay. Prohibido usar imágenes que no sean dato real (nada de renders o ilustraciones del espacio).
4. **Prioridad:** primero el reto cumplido (coordenadas → video de épocas → algo que se mueve → los 5 objetivos). La capa de cometas suma, pero **no puede retrasar el núcleo**.
5. **Commit y push al terminar cada bloque del plan (§15).** Al final de cada bloque el producto debe estar desplegado y funcionando.
6. **Antes de escribir Svelte,** leer `https://svelte.dev/llms-small.txt` ✔ (existe, 52 KB). Solo Svelte 5 con runes (§9.1).
7. **Ante la duda sobre una API externa** (Aladin, Paraglide, Fly), verificar en su documentación o en el código del paquete instalado. No adivinar. Este documento ya resolvió las más importantes.

---

## 1. El reto (texto oficial) y cómo lo cumplimos

**Reto:** "Planet X and SPHEREx" (NASA Space Apps 2026, nivel avanzado). Equipo **Breathing Comets**, sede virtual de Duitama.

**Resumen oficial:** *"Create a public-facing web tool to display images of the sky from SPHEREx mission, making it easy for anyone to quickly see how they change over time."*

**Contexto oficial:**
- Plutón se descubrió comparando dos imágenes del mismo cielo; el texto cita la ciencia ciudadana de backyardworlds.org.
- SPHEREx es *"uniquely sensitive to objects that are rich in hydrogen, water, carbon dioxide, carbon monoxide"*.

**Objetivos oficiales:**
- El usuario ingresa **RA/Dec**.
- La herramienta muestra **una serie de imágenes de esa región como un video corto** para detectar objetos en movimiento.
- **Objetivos de prueba:** Barnard's Star, Epsilon Indi B, WISE 0855 (`08h55m10.831s −7°14′42.53″`), RW Aurigae y R Draconis.

**Consideraciones opcionales:**
1. Fácil de actualizar con nuevas publicaciones de datos.
2. Mostrar las 102 bandas de forma creativa; **sumar los datos de cada detector** para más S/N; *extra kudos* por **espectros al vuelo**.
3. Sumar o restar épocas.
4. Campo de visión elegible.
5. Superponer Gaia y WISE.
6. Coordenadas en la URL e incrustable.
7. Metadatos, por ejemplo banderas de contaminación.
8. Usar Astropy y Aladin (CDS).

### 1.1 Recursos oficiales del reto (pestaña Resources, revisada el 13 nov 2026)

| Recurso | Qué ofrece | Uso en el producto |
|---|---|---|
| [IRSA SPHEREx](https://irsa.ipac.caltech.edu/Missions/spherex.html) | QR2 (oct 2025), QR3 (sep 2026), **DR1 (nov 2026; DOI 10.26131/IRSA678 para Spectral Images y 10.26131/IRSA679 para All-Sky Cube)**. Servicios: Data Explorer, Cutout Tool, **Spectrophotometry Tool** (espectros por fotometría forzada), Mosaic Tool, **MOST** (búsqueda de objetos en movimiento, incluye `spherex`), catálogo **SPLICES** (fuentes con hielos), página de **3I/ATLAS**, acceso S3 y Explanatory Supplement | Datos: S3 + índice canónico (§8). Citar los DOI de DR1. **Validar** nuestro espectro de un clic contra la Spectrophotometry Tool en 2–3 estrellas y nuestro cruce de NEO contra MOST en 2–3 objetos (el notebook `most-queries` muestra la interfaz). SPLICES: capa opcional "hielos" (H₂O/CO₂/CO, las moléculas del reto) |
| [Notebooks de SPHEREx](https://caltech-ipac.github.io/irsa-tutorials/spherex/) | 6 notebooks: intro, cutouts, psf (ePSF), source-discovery-tool, mosaic y hipscube | Sirven de referencia y respaldo: si S3 falla, el cutout service de IRSA. Mencionarlos en la entrega |
| [WiseView](http://byw.tools/wiseview) | Visor de parpadeo de WISE, usado por Backyard Worlds | Modelo explícito de la UI (parpadeo, contraste, épocas). Decir en la entrega: "WiseView para SPHEREx, más el espectro" |
| [Gaia en MAST](https://archive.stsci.edu/missions-and-data/gaia) | Gaia DR3 | Usamos el TAP de ESA. **Respaldo:** `astroquery.mast.Catalogs.query_region(..., catalog="Gaia", version=3)` si ESA no responde |
| CSA [NEOSSat](https://www.asc-csa.gc.ca/eng/satellites/neossat/), [CADC](https://www.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/en/), [tutorial](https://github.com/asc-csa/NEOSSAT_Tutorial), [dataset](https://data.asc-csa.gc.ca/dataset/neossat) | Telescopio espacial canadiense para NEO, cometas y satélites. Datos en CADC (`caom2`, `collection='NEOSSAT'`, TAP `argus`) | Ver abajo |

**NEOSSat × SPHEREx** (consulta TAP a CADC del 13 nov; `data/derived/neossat_targets_since_2025-04.csv`, 137 objetivos desde abr 2025):
- Observó **3I/ATLAS (12,164 cuadros, jul 2025 – ene 2026)** y **8 cometas de nuestro censo de CO₂**: 2025 A6 (Lemmon), 2024 E1, 2022 N2, 2014 UN271, 2024 T5, 2024 J3, 2022 E2, 2026 A2 y 240P. Además, 210P, 2025 K1, 2025 R2 (SWAN), 2025 T1, 161P y otros con detectabilidad SPHEREx.
- **Ninguno** de los 86 NEO post-NEOWISE. Sí observó NEO de aproximación cercana como 2025 FA22, 2025 KC, 2025 WZ3 y 2001 FF90.
- **Idea (recurso de socio, suma en Relevancia):** "gas por SPHEREx, polvo por NEOSSat". Afρ óptico en NEOSSat cerca de la fecha SPHEREx → cociente CO₂/polvo. Como mínimo, mostrar en la ficha de 3I y de los 8 cometas la imagen de NEOSSat junto a la de SPHEREx, con enlace a CADC.
- **Pendiente:** cruzar fechas (NEOSSat por día frente a visitas SPHEREx). La consulta quedó bloqueada por la red de la sesión; hacerla desde una máquina con acceso a `ws.cadc-ccda.hia-iha.nrc-cnrc.gc.ca`. Verificar en el tutorial la escala de píxel, el filtro y la calibración de NEOSSat antes de calcular Afρ.

| Requisito | Funcionalidad nuestra | Sección |
|---|---|---|
| RA/Dec | Barra de búsqueda: coordenadas, nombres (SIMBAD) y designaciones de cometa o asteroide (JPL) | §7, §9.6 |
| Serie de imágenes como video | Línea de tiempo con reproducción, parpadeo A↔B y visitas agrupadas | §9.4 |
| Detectar movimiento | Diferencia a igual λ, Gaia propagado por época con flecha, objetos de JPL, "What changed?" | §8.6, §9.4 |
| 5 objetivos | Precalculados y con recorridos guiados ("Field notes") | §12.1 |
| C1 actualizable | El índice se reconstruye solo; las colecciones nuevas (`qr4`, `dr1`…) aparecen sin cambiar código | §8.2 |
| C2 102 bandas, suma, espectro | Modo Cube (pila y HiPS DR1 en Aladin), modo Sum y espectro en un clic | §9.4, §8.5 |
| C3 sumar o restar | Modos Sum y Diff λ | §9.4 |
| C4 campo de visión | `fov` de 0.05 a 0.5° | §7 |
| C5 Gaia y WISE | Gaia DR3 propagado; HiPS AllWISE y 2MASS en Aladin | §9.7 |
| C6 URL e incrustar | Estado de la vista en la URL; `/embed` | §9.3 |
| C7 metadatos y banderas | Inspector y propiedades; máscara de banderas | §12.4 |
| C8 Astropy y Aladin | Backend con astropy y reproject; Aladin Lite 3.8.2 | §3 |
| Moléculas del enunciado | Bandas anotadas en el espectro; **cometas que respiran CO₂** | §8.9 |

**Criterios oficiales de evaluación:** Impacto, Creatividad, Validez, Relevancia y Presentación.

**Fechas:**
- Hackathon: sáb 14 – dom 15 nov 2026. Congelar el código el domingo a las 21:00 y enviar antes de las 22:00 (confirmado por el usuario).
- Juzgamiento local: 16–22 nov. Nominados: 3 dic. Finalistas: 17 dic. Ganadores: 27 ene 2027.

---

## 2. Producto: tesis, prioridades y criterios de éxito

### 2.1 Tesis

> **Decisión del usuario (12 nov): titular = "Small-Body Lab".** El nombre del equipo sigue siendo **Breathing Comets** y el núcleo del reto (el visor) no cambia. El **titular** de la landing, el video y el resumen pasa a ser: *"Asteroids and comets, seen by SPHEREx"*. Las dos tarjetas principales son:
> 1. **"After NEOWISE":** tamaños térmicos de asteroides cercanos a la Tierra descubiertos tras agosto de 2024 (Apéndice 0, método validado).
> 2. **"Who's breathing?":** actividad y gas de cometas (3I, 29P y el censo), con Activity Watch como extensión (Apéndice A).
>
> Los cometas dejan de ser la única historia: ya existe un catálogo profesional de 68 cometas (A.2).

El reto pide una herramienta **pública y fácil para cualquiera**. Los demás equipos harán, como mucho, una de dos cosas:
- un visor bonito pero superficial, o
- un clon técnico de Aladin.

**Ganamos siendo las dos cosas con revelación progresiva:**
- **modo Story** por defecto: historia guiada, 3 botones y textos de una línea;
- **modo Lab** con un interruptor: la anatomía de Aladin para técnicos.

Es el mismo motor con dos interfaces.

**Diferenciadores reales** (frente al "SPHEREx Data Explorer" de IRSA, basado en Firefly, que ya hace espectrofotometría rigurosa con The Tractor como trabajo asíncrono):
1. El tiempo como dimensión principal: video, parpadeo e indicaciones de movimiento.
2. **La diferencia a igual λ**, que resuelve el problema del filtro LVF (§8.6).
3. **Cometas que respiran:** seguimiento con efemérides vistas desde la nave y Q(CO₂) con incertidumbre. IRSA trabaja con posiciones fijas.
4. Espectro **inmediato**, sin cuenta ni espera. **No es exclusivo**: no venderlo como único.
5. Cada vista es una URL que se puede incrustar.

### 2.2 Prioridades

**Imprescindibles (F):**

| # | Funcionalidad | Criterio |
|---|---|---|
| F1 | Comparador de épocas: los 5 objetivos en < 1 s (precalculados) y cualquier coordenada en vivo | Relevancia |
| F2 | Diff λ con un deslizador antes/después | Creatividad, Validez |
| F3 | Movimiento asistido: Gaia por época con flecha, JPL y dipolo en la diferencia | Relevancia |
| F4 | Espectro en un clic con bandas anotadas: Paβ 1.282, Paα 1.875, Brα 4.052, H₂O 2.7, CH₄ 3.3, CO₂ 4.26 y CO 4.67 µm | Relevancia, Creatividad |
| F5 | Ficha de 3I/ATLAS con su halo de CO₂ y Q, y el atlas del censo | Impacto, Creatividad |
| F6 | URL = vista; `/embed`; imagen Open Graph por vista | Presentación |
| F7 | Procedencia y banderas a un clic | Validez |

**Suben la nota con poco costo (G):**

| # | Funcionalidad |
|---|---|
| G1 | Interruptor Story/Lab (§9.5) |
| G2 | Recorridos "Field notes" de los 5 objetivos (3–4 pasos cada uno; §12.1) |
| G3 | "What changed?": residuos ≥ 5σ en Diff λ cruzados con Gaia y JPL → lista de *known* o *candidate to inspect* |
| G4 | Exportar el parpadeo como video WebM (MediaRecorder) o PNG, con créditos en la imagen |
| G5 | "102 colors": deslizador de λ sobre el HiPS DR1 en Aladin |

**P2 (solo si sobra tiempo, solo en Lab):** RGB, contornos, vista múltiple de 6 detectores, regla, pins, filtro de catálogo y AllWISE como catálogo.

**Nunca:** cuentas de usuario, comentarios ni favoritos.

**Lo que no se dice:**
- "discovered" → decir "measured", "candidate" o "consistent with";
- "único con espectros";
- "Barnard se ve moverse a simple vista" (se ve con la ayuda de F3).

### 2.3 Rutas
| Ruta | Qué es | Renderizado |
|---|---|---|
| `/` y `/es` | Landing (ensayo Plate & Ink) | Prerender |
| `/explore?…` | Sky Explorer (Story/Lab) | SPA (`ssr = false`) |
| `/embed?…` | Explorer sin chrome para `<iframe>` | SPA |
| `/comets` | Atlas | Prerender |
| `/comets/[slug]` | Ficha de cometa | Prerender (`entries()`) |
| `/method` | Método, validación y limitaciones | Prerender |
| `/about` | Equipo, créditos de datos, uso de IA y licencias | Prerender |

### 2.4 Criterios de éxito (lo que el jurado logra en 60 s)
1. La landing carga en < 1.5 s (LCP en 4G).
2. Clic en "Barnard's Star" → video en < 1 s, con la cruz de Gaia y la flecha de movimiento desplazándose entre épocas.
3. Escribir `WISE 0855` (o las coordenadas del reto) → aviso de movimiento propio → en D1–D3 solo se ve una estrella de fondo (Gaia G=16.3, a 6.8″); en D6 la enana Y la supera ×4. El espectro separado (§12.1b) es ≈ 0 hasta 3.8 µm y tiene el pico de 4.5 µm.
4. Clic en un píxel → el espectro de 0.75–5 µm se arma en vivo.
5. Copiar la URL → otra pestaña muestra la misma vista.
6. 3I/ATLAS → halo de CO₂ y Q con barras 16–84%.

---

## 3. Arquitectura y stack

### 3.1 Dónde está el costo (mediciones ✔)
| Operación | Medición | Consecuencia |
|---|---|---|
| Cabecera de un L2 en S3 (23 KB) | 0.15 s | Barato |
| Recorte de 0.2° (117 filas × 2040 px), IMAGE + FLAGS | 2 × 955 KB en 0.26 s | **Cuesta lo mismo sin importar el ancho** (filas contiguas) |
| 32 lecturas de ~1 MB en paralelo (fuera de AWS) | 0.74 s (~40 MB/s) | Dentro de `us-east-1` es más rápido |
| Listar una semana del bucket (10,237 objetos) | 1.2 s | El índice completo de `qr2` (129 semanas) se lista en ~3 min |
| IRSA TAP sobre `spherex.obscore` (1.6 M filas) | 10–60 s; 503 bajo carga | **Nunca en el camino del usuario** |

**Decisiones que salen de ahí:**
1. **Recortar en el servidor junto a S3** (Fly `iad` = Virginia, igual que `us-east-1`).
2. **Índice propio** (Parquet + DuckDB + HEALPix).
3. **Binario float32** dibujado en **WebGL2**.
4. **Precálculo** de los 5 objetivos y de 3I, para que funcionen aunque la API esté caída.

El bucket S3 **sí** tiene CORS con `Range` ✔. Aun así no se lee desde el navegador: 60 épocas serían ~115 MB por objetivo.

### 3.2 Stack con versiones exactas
Todas las versiones son ≥ 2 semanas antes del sábado ✔. Se instalan **sin** `^` ni `~` (`npm i -E`).

| Capa | Paquete | Versión | Nota |
|---|---|---|---|
| Runtime | Node.js | 24.x LTS | Kit exige ≥ 22.17 |
| Framework | svelte / @sveltejs/kit / adapter-static / vite-plugin-svelte | 5.57.3 / 3.1.1 / 4.0.1 / 7.3.1 | Kit 3 |
| Build | vite | 8.3.5 | — |
| Lenguaje | typescript | **6.0.3** | **No TS 7:** Kit 3.1.1 exige `^6` y svelte-check 4.7.7 admite `^5 \|\| ^6` |
| Chequeo | svelte-check | 4.7.7 | — |
| i18n | @inlang/paraglide-js | 2.29.3 | Instalar con `npx sv add paraglide`. La 3.0 (3 nov) es muy nueva |
| Mapa de cielo | aladin-lite | **3.8.2** | La 3.9.x es beta. Desde npm o como módulo ES de jsDelivr (§9.7); **no** el CDN de CDS (404) |
| WebGL | twgl.js | 7.0.0 | Utilidades finas sobre WebGL2 |
| Gráficas | uplot | 1.6.32 | Espectros y curvas de luz |
| Workers | comlink | 4.4.2 | RPC con Workers |
| Datos | @tanstack/svelte-query | 6.3.6 | Reintentos, deduplicación y caché |
| Componentes | bits-ui | 2.20.2 | Accesibles y sin estilo |
| Animación | gsap / lenis | 3.15.0 / 1.3.27 | Solo en la landing, carga perezosa |
| Compresión | fflate | 0.8.3 | Respaldo si falta `DecompressionStream` |
| Fuentes | @fontsource-variable/newsreader / @fontsource/ibm-plex-sans / @fontsource/ibm-plex-mono | 5.3.0 / 5.3.0 / 5.3.0 | Plate & Ink |
| Pruebas | vitest / @playwright/test | 4.1.12 / 1.64.1 | Playwright con `--trace off` |
| Calidad | eslint / prettier / prettier-plugin-svelte | 10.14.0 / 3.9.10 / 4.1.1 | — |
| Python | CPython | 3.13 | numpy 2.5 exige ≥ 3.12 |
| API | fastapi / pydantic / granian | 0.162.0 / 2.14.1 / 2.8.6 | — |
| S3 | **obstore** | 0.12.1 | Rust, asíncrono, rangos concurrentes ✔ probado |
| Astronomía | astropy / reproject / astroquery / pyvo | 8.0.2 / 0.21.0 / 0.4.11 / 1.10.0 | — |
| Numérico | numpy / scipy | 2.5.4 / 1.18.1 | — |
| Índice | duckdb / pyarrow / cdshealpix | 2.0.0 / 26.0.0 / 0.9.0 | — |
| Otros | orjson / httpx | 3.13.0 / 0.28.1 | — |
| Herramientas Python | uv, pytest 9.2.0, ruff 0.17.3 | — | — |

**Por qué Svelte 5 y no React/Next:**
- **Rendimiento:** reactividad de grano fino sin DOM virtual (el inspector y la línea de tiempo se actualizan cientos de veces por segundo), runtime de pocos KB y prerender de la landing junto con SPA del Explorer en la misma app.
- **Riesgo asumido:** el agente conoce menos Svelte 5. Se mitiga leyendo `llms-small.txt` y aplicando §9.1.

### 3.3 Diagrama
```
Navegador ──(HTML/JS/datos precalculados)──► Cloudflare Pages  breathingcomets.org
    │                                          static/data/targets/*, comets/*
    │  WebGL2 (placa)  ·  Workers (decode, mediana, Diff λ, fotometría)
    │  Aladin Lite 3.8.2 ──► HiPS de IRSA (CORS *): SPHEREx DR1 cube, 2MASS, AllWISE
    │
    └──(fetch)──► API FastAPI en Fly iad  api.breathingcomets.org
                   ├─ índice DuckDB (Parquet + HEALPix) en el volumen /data
                   ├─ obstore ──► s3://nasa-irsa-spherex (us-east-1, anónimo)
                   ├─ astropy/reproject: recorte, reproyección, λ v5
                   ├─ Horizons (@-163182), SBDB, sb_ident, Gaia (ESA TAP), SIMBAD (Harvard)
                   └─ caché de disco en /data/cache (LRU, 8 GB)
```

---

## 4. Infraestructura ya creada (estado del 12 nov)

| Recurso | Estado | Detalle |
|---|---|---|
| Dominio | ✅ `breathingcomets.org` comprado en Cloudflare Registrar | El DNS está en la misma cuenta de Cloudflare |
| Fly.io | ✅ app **`breathing-comets-api`** (organización personal, estado `pending`); ✅ tarjeta agregada | `flyctl` v0.5.8 en el portátil del usuario (Linux, zsh) |
| Cloudflare Pages | ⏳ crearlo el sábado, conectado al repositorio nuevo | — |
| Repositorio del producto | ⏳ crearlo el sábado: `sebastianvelace/breathing-comets` (público) | — |

**Cloudflare Pages:**
- Build: `cd apps/web && npm ci && npm run build`.
- Directorio de salida: `apps/web/build`.
- Variable `NODE_VERSION=24`.
- Límites ✔: 25 MiB por archivo y 20,000 archivos.
- Dominio propio: `breathingcomets.org` (apex) y `www` → redirección.

**DNS de la API:**
- Registro `api` → la app de Fly (CNAME `breathing-comets-api.fly.dev`, o A/AAAA con las IP de `fly ips list`).
- **Modo "DNS only" (nube gris)**. Con proxy naranja, el certificado de Fly no valida.
- Luego `fly certs add api.breathingcomets.org`.

**`services/api/fly.toml`:**
```toml
app = "breathing-comets-api"
primary_region = "iad"

[build]
  dockerfile = "Dockerfile"

[env]
  SPX_DATA_DIR = "/data"
  SPX_ALLOWED_ORIGINS = "https://breathingcomets.org,https://www.breathingcomets.org,http://localhost:5173"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = "suspend"   # se suspende sin tráfico y despierta en < 1 s
  auto_start_machines = true
  min_machines_running = 0

[[vm]]
  size = "shared-cpu-2x"
  memory = "2gb"                    # suspend está pensado para máquinas de ≤ 2 GB ✔

[mounts]
  source = "spx_cache"
  destination = "/data"             # volumen de 5 GB: fly volumes create spx_cache -s 5 -r iad
```

**Reglas de Fly:**
- **NO** configurar swap (incompatible con suspend ✔).
- **Una sola máquina:** `fly scale count 1`.
- Fly **no tiene alertas de gasto** ✔: limitar consultas por IP en la API y revisar el panel.
- **Apagado de emergencia:** `fly scale count 0`. Lo precalculado sigue funcionando.

**Costo esperado:** 0–5 USD al mes. Fly no cobra a las cuentas personales con facturas menores de 5 USD; el dominio cuesta ~8.50 USD el primer año.

**`services/api/Dockerfile`:**
```dockerfile
FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 UV_COMPILE_BYTECODE=1
RUN pip install --no-cache-dir uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY packages/spxcore ./packages/spxcore
COPY services/api ./services/api
EXPOSE 8000
CMD ["uv","run","granian","--interface","asgi","--host","0.0.0.0","--port","8000","--workers","1","services.api.app.main:app"]
```
Una sola máquina con `--workers 1` (asíncrono). La concurrencia de S3 viene de obstore, no de procesos.

---

## 5. Repositorio: estructura, arranque y archivos plantilla

### 5.1 Estructura (monorepo)
```
breathing-comets/
├─ CLAUDE.md                      # §5.3 (reglas del agente)
├─ .claude/settings.json          # §5.3
├─ .githooks/commit-msg, pre-push # §5.3
├─ scripts/git-identity.sh        # §5.3
├─ pyproject.toml, uv.lock        # entorno Python único (uv) para spxcore, API y pipelines
├─ Makefile                       # dev | index | precompute | test | deploy-web | deploy-api
├─ packages/spxcore/spxcore/
│  ├─ __init__.py
│  ├─ s3.py          # obstore: store, rangos, listado
│  ├─ fitsio.py      # parseo de cabeceras y datLoc de cada HDU
│  ├─ index.py       # construcción y consulta del índice (DuckDB + HEALPix)
│  ├─ calib.py       # WCS espectral v5 (CWAVE/CBAND) y mapa de ángulo sólido
│  ├─ cutout.py      # recorte + reproyección + λ
│  ├─ flags.py       # remapeo de bits L2 → SPXF
│  ├─ spxf.py        # escritor SPXF
│  ├─ sky.py         # cielo estático a igual λ y Diff λ
│  ├─ spectrum.py    # fotometría de apertura y espectro
│  ├─ ephem.py       # Horizons @-163182 e interpolación
│  ├─ known.py       # sb_ident, Gaia, SIMBAD
│  └─ comets.py      # modelo de banda, Haser y Q (solo para 3I o el atlas)
│  └─ tests/
├─ services/api/app/  main.py, routes/{resolve,exposures,stack,spectrum,known,gaia,fits,health}.py, cache.py, ratelimit.py
├─ services/api/{Dockerfile, fly.toml}
├─ pipelines/ build_index.py, precompute_targets.py, precompute_comets.py
└─ apps/web/
   ├─ src/routes/  +layout.svelte, +layout.ts, +page.svelte, explore/, embed/, comets/, comets/[slug]/, method/, about/
   ├─ src/lib/state/  view.svelte.ts (URL ⇄ estado), layers.svelte.ts, mode.svelte.ts (story|lab)
   ├─ src/lib/data/   spxf.ts, api.ts, static.ts, format.ts (fmtSci)
   ├─ src/lib/gl/     renderer.ts, shaders/plate.frag.glsl, shaders/plate.vert.glsl, luts.ts
   ├─ src/lib/workers/ frames.worker.ts, photometry.worker.ts
   ├─ src/lib/astro/  coords.ts, pm.ts, flags.ts, bands.ts (líneas moleculares)
   ├─ src/lib/aladin/ AladinView.svelte
   ├─ src/lib/components/ (§9.6)
   ├─ src/app.css (tokens §10), src/app.html
   ├─ messages/en.json, messages/es.json, project.inlang/settings.json
   ├─ static/data/ targets/<slug>/…, comets/…, channels.json, targets.json, build.json
   └─ tests/e2e/*.spec.ts
```

### 5.2 Arranque (comandos exactos)
```bash
gh repo create sebastianvelace/breathing-comets --public --clone && cd breathing-comets
```
1. Primero copiar los archivos plantilla de §5.3.
2. Ejecutar:
   ```bash
   sh scripts/git-identity.sh
   ```

```bash
npx sv@latest create apps/web --template minimal --types ts --no-add-ons --install npm
```

```bash
cd apps/web && npm i -E svelte@5.57.3 @sveltejs/kit@3.1.1 @sveltejs/adapter-static@4.0.1 @sveltejs/vite-plugin-svelte@7.3.1 vite@8.3.5 typescript@6.0.3 svelte-check@4.7.7
```

```bash
npm i -E aladin-lite@3.8.2 twgl.js@7.0.0 uplot@1.6.32 comlink@4.4.2 @tanstack/svelte-query@6.3.6 bits-ui@2.20.2 gsap@3.15.0 lenis@1.3.27 fflate@0.8.3 @fontsource-variable/newsreader@5.3.0 @fontsource/ibm-plex-sans@5.3.0 @fontsource/ibm-plex-mono@5.3.0
```

```bash
npm i -DE vitest@4.1.12 @playwright/test@1.64.1 eslint@10.14.0 prettier@3.9.10 prettier-plugin-svelte@4.1.1
```

```bash
npx sv add paraglide && npm i -DE @inlang/paraglide-js@2.29.3
```

Python, desde la raíz:
```bash
uv init --python 3.13 --no-workspace && uv add fastapi==0.162.0 granian==2.8.6 pydantic==2.14.1 orjson==3.13.0 httpx==0.28.1 obstore==0.12.1 astropy==8.0.2 reproject==0.21.0 astroquery==0.4.11 pyvo==1.10.0 numpy==2.5.4 scipy==1.18.1 duckdb==2.0.0 pyarrow==26.0.0 cdshealpix==0.9.0 && uv add --dev pytest==9.2.0 ruff==0.17.3
```

**Configuración:**
- **`svelte.config.js`:** `adapter: adapter({ pages: 'build', assets: 'build', fallback: '200.html', precompress: false })`.
- **`src/routes/+layout.ts`:** `export const prerender = true; export const trailingSlash = 'never';`.
- **`src/routes/explore/+page.ts` y `embed/+page.ts`:** `export const prerender = false; export const ssr = false;`.
- **`vite.config.ts`:**
  - `worker: { format: 'es' }`;
  - `optimizeDeps: { exclude: ['aladin-lite'] }`;
  - `build: { target: 'es2022' }`;
  - el plugin `paraglideVitePlugin({ project: './project.inlang', outdir: './src/lib/paraglide', strategy: ['url', 'cookie', 'preferredLanguage', 'baseLocale'] })` que deja `sv add`. Verificar las opciones en `paraglidejs.com/sveltekit`.
- **`app.html`:** `<html lang="%paraglide.lang%">` (o lo que genere `sv add paraglide`).

### 5.3 Archivos plantilla (copiar tal cual en el primer commit)
También están en el repositorio de investigación (raíz, `.claude/`, `.githooks/`, `scripts/`).

**`CLAUDE.md`:**
```markdown
# Reglas del repositorio (prioridad máxima)

## Git
- Trabaja y haz push **solo en `main`**. Nunca crees ramas `claude/*` ni otras ramas, salvo que el usuario lo pida explícitamente.
- Autor y committer de todos los commits: `sebasvelace <sebastianvelace@gmail.com>`. Antes del primer commit de cada sesión ejecuta `sh scripts/git-identity.sh`.
- **No agregues** `Co-Authored-By`, `Claude-Session`, "Generated with Claude Code" ni ninguna otra línea de atribución en commits, PR, issues o comentarios.
- No firmes commits con llaves del entorno (`commit.gpgsign false`).
- Los hooks de `.githooks/` deben estar activos (`core.hooksPath .githooks`); no los saltes con `--no-verify`.

## Construcción
- La guía es `docs/BUILD.md`. Ante cualquier duda, manda ese documento.

## Transparencia
- El uso de IA se declara en la sección "Use of AI" de la entrega de Space Apps, no en el historial de git.
```

**`.claude/settings.json`:**
```json
{
  "attribution": { "commit": "", "pr": "", "sessionUrl": false },
  "hooks": { "SessionStart": [ { "hooks": [ { "type": "command", "command": "sh \"$CLAUDE_PROJECT_DIR\"/scripts/git-identity.sh" } ] } ] },
  "disableClaudeAiConnectors": true
}
```

**`scripts/git-identity.sh`:**
```sh
#!/bin/sh
set -e
cd "$(git rev-parse --show-toplevel)"
git config user.name  "sebasvelace"
git config user.email "sebastianvelace@gmail.com"
git config commit.gpgsign false
git config tag.gpgsign false
git config core.hooksPath .githooks
```

**`.githooks/commit-msg`:**
```sh
#!/bin/sh
grep -viE '^[[:space:]]*(Co-Authored-By:.*(claude|anthropic)|Claude-Session:|.*Generated with \[Claude Code\])' "$1" > "$1.tmp" || true
mv "$1.tmp" "$1"
```

**`.githooks/pre-push`:**
```sh
#!/bin/sh
expected="sebastianvelace@gmail.com"
zero=0000000000000000000000000000000000000000
while read lref lsha rref rsha; do
  case "$rref" in refs/heads/claude/*) echo "push rechazado: rama $rref"; exit 1;; esac
  [ "$lsha" = "$zero" ] && continue
  if [ "$rsha" = "$zero" ]; then range="$lsha --not --remotes"; else range="$rsha..$lsha"; fi
  bad=$(git log --format='%ae%n%ce' $range | grep -vxF -e "$expected" -e "noreply@github.com" | sort -u)
  [ -n "$bad" ] && { echo "push rechazado: identidad no permitida: $bad"; exit 1; }
  if git log --format=%B $range | grep -qiE '^(Co-Authored-By:.*(claude|anthropic)|Claude-Session:)'; then
    echo "push rechazado: hay líneas de atribución en los mensajes"; exit 1; fi
done
exit 0
```

Dar permisos de ejecución:
```bash
chmod +x scripts/git-identity.sh .githooks/*
```

**Copiar también:**
- `docs/BUILD.md` (este archivo) al repositorio nuevo;
- `data/derived/test_targets.json` → `apps/web/static/data/targets.json`;
- `data/derived/spherex_channels.json` → `apps/web/static/data/channels.json`.

Son datos de referencia (posiciones de SIMBAD y la tabla oficial de canales), no código.

**Verificación al final de cada día:**
- `git log --format='%an <%ae> | %cn <%ce>' | sort -u` → solo el usuario (y GitHub en commits web);
- `git log --format=%B | grep -ci claude` → `0`;
- `git ls-remote --heads origin` → solo `main`.

---

## 6. Contratos de datos

### 6.1 SPXF v1: pila de cuadros alineados (binario, little-endian)
Es el **mismo formato** para lo estático (`*.spxf.gz`) y para la API (`/v1/stack`).

```
0   char[4]  magic "SPXF"
4   uint16   version = 1
6   uint16   flags   (bit0: planos float32 con byte-shuffle)
8   uint32   header_len N (UTF-8 JSON, relleno con espacios hasta múltiplo de 8)
12  uint32   reserved = 0
16  N bytes  header JSON
16+N payload, por cada cuadro k en el orden de header.frames:
      flux  float32[ny*nx]  MJy/sr, NaN = sin dato, orden fila mayor (y luego x), y=0 abajo (convención FITS)
      var   float32[ny*nx]  solo si header.has_var
      flags uint16[ny*nx]   bits SPXF (§12.4)
    cada bloque se rellena hasta un múltiplo de 8 bytes
```

**Header (ejemplo; los valores reales salen del pipeline):**
```json
{
  "spxf": 1, "kind": "stack" ,
  "target": {"name": "Barnard's Star", "slug": "barnard", "ra": 269.446268, "dec": 4.768204, "frame": "ICRS", "track": null},
  "grid": {"ctype": ["RA---TAN","DEC--TAN"], "crval": [269.446268, 4.768204], "crpix": [74.0, 74.0],
           "cdelt_deg": [-0.0017083333, 0.0017083333], "nx": 147, "ny": 147, "north_up": true, "pixel_arcsec": 6.15},
  "units": "MJy/sr", "has_var": false, "det": 4,
  "stretch_hint": {"p_lo": 0.5, "p_hi": 99.5, "lo": 0.12, "hi": 48.3},
  "data_version": {"releases": ["dr1","qr3"], "l2": "l2b-v27", "s3_index": "spherex_s3_keys_compact.npz@2026-11-12", "spectral_wcs": "cal-swcs-v5-2026-191"},
  "frames": [
    {"k": 0, "obs_id": "2025W33_2B_0412_3", "det": 4, "collection": "spherex_dr1",
     "mjd": 60902.913, "date": "2025-08-15T21:54:43Z", "visit": 3,
     "lam_um": 2.6713, "bw_um": 0.0762, "lam_poly": [2.6713, 0.0, -0.000667, 0.0, 0.0, 0.0],
     "psf_fwhm_arcsec": 6.06, "src_pix": [1437.2, 611.8], "edge": false,
     "flag_counts": {"OUTLIER": 12, "TRANSIENT": 0, "OVERFLOW": 3},
     "s3_key": "dr1/level2/2025W33_2B/<procdir>/4/level2_2025W33_2B_0412_3D4_spx_<procdir>.fits"}
  ],
  "visits": [{"visit": 3, "mjd_min": 60902.8, "mjd_max": 60903.4, "n": 18}],
  "provenance": {"generator": "spxcore 0.1.0", "created": "2026-11-14T15:02:11Z", "astropy": "8.0.2", "reproject": "0.21.0"}
}
```

**Campos:**
- **`lam_poly`:** λ(x, y) = c0 + c1·dx + c2·dy + c3·dx² + c4·dx·dy + c5·dy², con dx = x − (crpix1 − 1) y dy = y − (crpix2 − 1), en píxeles de salida con base 0.
  - **Error máximo medido ✔ del ajuste cuadrático en 147 px:** D5 0.3–0.45 nm, D6 0.9–1.8 nm y D4 2–4 nm (en 235 px: 0.4–0.9, 0.8–1.7 y 2.4–4.9 nm). Es ≤ 5% del ancho del canal (~76 nm en D4, ~36 nm en D5–D6).
  - **Sirve para visualizar, para el modo Cube y para emparejar λ.** El espectro científico usa el mapa completo en el servidor.
- **`visit`:** exposiciones separadas por menos de 2 días.
- **`stretch_hint`:** percentiles calculados **sobre toda la pila** (nunca por cuadro).
- **`edge`:** el recorte toca un borde o está a menos de 20 px de él. Los píxeles fuera llevan NaN y el bit NODATA.

**Compresión:**
- **Estático:** gzip de nivel 9 del archivo completo, servido como `application/octet-stream` **sin** `Content-Encoding` (Cloudflare no comprime ese tipo). El cliente descomprime con `DecompressionStream('gzip')`.
- **API:** `application/x-spxf` con `GZipMiddleware` (el navegador descomprime solo).
- **Byte-shuffle** (`flags.bit0`): para cada plano float32 de n valores, se escriben primero todos los bytes 0, luego todos los 1, los 2 y los 3. Mejora gzip ~1.6–2×.

**Escritor (Python, `spxcore/spxf.py`).** ✔ Probado en ida y vuelta (gzip y *shuffle*):
```python
import json, gzip, numpy as np
MAGIC = b"SPXF"

def _shuffle(a: np.ndarray) -> bytes:
    b = np.ascontiguousarray(a, dtype="<f4").view(np.uint8).reshape(-1, 4)
    return b.T.copy().tobytes()

def _pad8(b: bytes) -> bytes:
    return b + b"\0" * ((-len(b)) % 8)

def write_spxf(path, header: dict, frames: list[dict], shuffle=True, gz=True):
    h = json.dumps(header, separators=(",", ":")).encode()
    h += b" " * ((-len(h)) % 8)
    out = [MAGIC, np.uint16(1).tobytes(), np.uint16(1 if shuffle else 0).tobytes(),
           np.uint32(len(h)).tobytes(), np.uint32(0).tobytes(), h]
    for f in frames:
        flux = f["flux"].astype("<f4")
        out.append(_pad8(_shuffle(flux) if shuffle else flux.tobytes()))
        if header.get("has_var"):
            var = f["var"].astype("<f4")
            out.append(_pad8(_shuffle(var) if shuffle else var.tobytes()))
        out.append(_pad8(f["flags"].astype("<u2").tobytes()))
    data = b"".join(out)
    with (gzip.open(path, "wb", compresslevel=9) if gz else open(path, "wb")) as fh:
        fh.write(data)
```

**Lector (TypeScript, `src/lib/data/spxf.ts`, se ejecuta dentro del Worker):**
```ts
export type SpxfFrame = { flux: Float32Array; var?: Float32Array; flags: Uint16Array };
export type Spxf = { header: any; frames: SpxfFrame[] };

export async function fetchSpxf(url: string, gz: boolean, signal?: AbortSignal): Promise<Spxf> {
  const res = await fetch(url, { signal });
  if (!res.ok) throw new Error(`SPXF ${res.status} ${url}`);
  const stream = gz ? res.body!.pipeThrough(new DecompressionStream('gzip')) : res.body!;
  return parseSpxf(await new Response(stream).arrayBuffer());
}

export function parseSpxf(buf: ArrayBuffer): Spxf {
  const dv = new DataView(buf);
  if (String.fromCharCode(...new Uint8Array(buf, 0, 4)) !== 'SPXF') throw new Error('bad magic');
  const flags = dv.getUint16(6, true), n = dv.getUint32(8, true);
  const header = JSON.parse(new TextDecoder().decode(new Uint8Array(buf, 16, n)));
  const { nx, ny } = header.grid, px = nx * ny, pad8 = (b: number) => b + ((8 - (b % 8)) % 8);
  let off = 16 + n;
  const readF32 = () => {
    const bytes = new Uint8Array(buf, off, px * 4); off += pad8(px * 4);
    if (!(flags & 1)) return new Float32Array(bytes.slice().buffer);
    const out = new Uint8Array(px * 4);
    for (let i = 0; i < px; i++) for (let b = 0; b < 4; b++) out[i * 4 + b] = bytes[b * px + i];
    return new Float32Array(out.buffer);
  };
  const frames: SpxfFrame[] = header.frames.map(() => {
    const flux = readF32(), v = header.has_var ? readF32() : undefined;
    const fl = new Uint16Array(buf.slice(off, off + px * 2)); off += pad8(px * 2);
    return { flux, var: v, flags: fl };
  });
  return { header, frames };
}
```

### 6.2 Manifiesto de objetivo (`static/data/targets/<slug>/manifest.json`)
```json
{
  "slug": "barnard", "name": "Barnard's Star", "ra": 269.446268, "dec": 4.768204,
  "pm": {"pmra_masyr": -801.551, "pmdec_masyr": 10362.394, "ref_epoch_jyear": 2000.0,
         "ra0": 269.4520769586187, "dec0": 4.693364966576667, "plx_mas": 546.9759},
  "fov_deg": 0.25, "default_det": 4, "default_mode": "blink",
  "stacks": {"1":"D1.spxf.gz","2":"D2.spxf.gz","3":"D3.spxf.gz","4":"D4.spxf.gz","5":"D5.spxf.gz","6":"D6.spxf.gz"},
  "diff":   {"4":"D4.diff.spxf.gz"},
  "sizes_bytes": {"4": 3815220},
  "spectrum": "spectrum.json", "known": "known.json", "gaia": "gaia.json",
  "field_notes": [
    {"step":1, "en":"Barnard's Star is the fastest-moving star in our sky.", "es":"La estrella de Barnard es la que más rápido se mueve en nuestro cielo.", "view":{"mode":"epoch","det":4}},
    {"step":2, "en":"Blink two dates a year apart. The cross marks where Gaia predicts it.", "es":"Alterna dos fechas con un año de diferencia. La cruz marca dónde la predice Gaia.", "view":{"mode":"blink","a":"first","b":"last","layers":["gaia"]}},
    {"step":3, "en":"Subtract the sky at the same color: what moved leaves a dipole.", "es":"Resta el cielo al mismo color: lo que se movió deja un dipolo.", "view":{"mode":"diff"}}
  ]
}
```

### 6.3 Espectro (`spectrum.json` estático o NDJSON en vivo)
Cada fila es una exposición medida en la posición del objeto propagada a su MJD:
```json
{"obs_id":"2025W33_2B_0412_3","det":4,"mjd":60902.913,"lam_um":2.6713,"bw_um":0.0762,
 "flux_mjy":12.41,"err_mjy":0.31,"ap_px":3,"ann_px":[6,10],"flags":["OUTLIER"],"visit":3,"sat":false,"edge":false}
```
- `flux_mjy` = Σ_apertura (I − fondo) · Ω_pix · 10⁹, con I en MJy/sr y Ω_pix en sr del mapa de ángulo sólido (§12.6).
- **Superado (ver recuadro y §8.0c):** `flux_mjy` es el flujo de la **ePSF forzada** (R = 4 px, fondo libre), sin corrección de apertura; `ap_px`/`ann_px` ya no aplican. La interfaz dice "ePSF forced photometry".

### 6.4 Atlas de cometas (`static/data/comets/index.json` y `<slug>.json`)
**Fuente de verdad** (en `data/derived/` del repositorio de investigación):

| Dato | Archivo | Columnas |
|---|---|---|
| CO₂ | `co2_census_physical.csv` | `QA_16/50/84`, `snr_detect`, `flux_rel_err`, `n_core`, `chi2_phys`, `T_rot`, `r_au`, `delta_au` |
| CO | `co_census_final.csv` | — |
| H₂O | `h2o_census.csv` | — |
| Q(ρ) | `q_vs_aperture.csv` | — |
| Novedad | `arxiv_novelty.csv` | — |

**NO usar** `co2_census_final.csv`: es una versión anterior. **Copiar los valores del CSV**, nunca de este documento.

```json
{"slug":"3i-atlas","name":"3I/ATLAS","class":"interstellar",
 "epochs":[{"label":"2025-12","r_au":2.15,"delta_au":1.81,
   "co2":{"q16":2.8e27,"q50":3.4e27,"q84":4.2e27,"snr_det":41.1,"flux_rel_err":0.03,"n_core":2,"chi2":185,"status":"detected"},
   "co":{"ratio_co_co2":1.5,"status":"candidate"},"h2o":null,
   "validation":{"published":"~3.0e27 (Lisse et al., arXiv:2601.06759)","agree":true}}],
 "maps":{"continuum":"3i-cont.webp","gas":"3i-co2.webp"},"stack":"3i-dec2025-D5.spxf.gz",
 "spectrum":"3i-spectrum.json","novel":false,"notes_en":"…","notes_es":"…"}
```

---

### 6.10 Paquete estático de resultados (`data/export/`, generado por `research/28_export_static.py`) ✔

Se copia tal cual a `static/data/` del producto. Todo en inglés, con unidades mJy, µm, km, mas y MJD (UTC). Total ~0.23 MB.

| Archivo | Contenido | Lo usa |
|---|---|---|
| `neo/index.json` | `method` (η, σ_η, `floor_fraction` 0.35, `cv_median`, `cv_sigma_ln`, `trail_max_px` 3, `tiers`); `counts` (652, 86 candidatos, A, B, provisional, `pha_AB`); `objects[]` con `pdes`, `slug`, `tier`, `pha`, `H`, `D_km`, `D16`, `D84`, `pV`, `D_from_H_pV014`, `snr`, `n_exp`, `n_visits`, `chi2nu`, `single_visit` y `flag` | `/neo` (tabla y gráfico D frente a H), landing §0 |
| `neo/<slug>.json` | `points[]`: `mjd`, `det`, `lam`, `f` (térmico con cielo restado), `e`, `r_au`, `delta_au`, `alpha`, `trail_px`, `obs_id`, `ra` y `dec` | Ficha del NEO y enlace al Explorer (`track`) |
| `neo/validation.json` | `cv[]` (D_SPHEREx/D_NEOWISE de 50 NEO), `eta_eff[]` y `trail[]` (flujo medido/predicho por longitud de estela) | `/method` y `/neo` |
| `targets/<slug>.json` | `notes[]` (`label`, `value`, `ref`) + según el objetivo: `astrometry` (μ, ϖ y sus errores, n, base temporal, referencia), `spectrum[]` (bins de 0.05 µm: `lam`, `f`, `e`, `n`), `lightcurve[]` (`mjd`, `lam`, `band`, `rel`) y `neighbour` | FieldNotes del Explorer y fichas de los 5 objetivos |
| `calibration.json` | Regla de fotometría, validación contra 2MASS/WISE por filtro y desplazamiento de λ v27 − v20 por detector | `/method` |

- **Regenerar** si cambia algún CSV de `data/derived/`: `python research/28_export_static.py` (< 10 s).
- **Pruebas mínimas del producto:**
  - `index.counts.A + B == 28`;
  - cada `objects[].slug` tiene su `neo/<slug>.json`, con ≥ 8 puntos en los A/B (los provisionales pueden tener 2–7);
  - `targets/wise-0855.json` tiene f < 0.1 mJy en λ < 3 µm y f > 0.3 mJy en 4.2–4.7 µm.

## 7. API (FastAPI, base `https://api.breathingcomets.org/v1`)

**Reglas:**
- Cabecera `X-SPX-Data-Version` en todas las respuestas.
- Errores con forma `{"error":{"code":"UPSTREAM_TIMEOUT","source":"jpl_sb_ident","message":"…","retry_after_s":10}}`.
- CORS desde `SPX_ALLOWED_ORIGINS` más `https://*.pages.dev`.
- Límite de 30 peticiones por minuto por IP en `/stack` y `/spectrum`; responder 429 con `Retry-After`.
- Timeouts hacia terceros: 8 s (sb_ident: 25 s, solo en el pipeline o con caché).

| Ruta | Parámetros | Respuesta | Caché HTTP |
|---|---|---|---|
| `GET /health` | — | `{ok, index_rows, index_built, collections, swcs}` | no |
| `GET /resolve` | `q` | `{ra, dec, name, kind:"fixed"\|"moving", source, pm?, epoch_warning?}` | 30 d |
| `GET /exposures` | `ra, dec, fov=0.25, det=1..6\|all, t0?, t1?` | lista de {obs_id, det, collection, mjd, lam_um, bw_um, visit, edge} | 1 h |
| `GET /stack` | `ra, dec, fov∈[0.05,0.5], det, t0?, t1?, max_frames=80, var=0\|1, track?` | SPXF | `immutable` |
| `GET /diff` | igual que `/stack` | SPXF con la diferencia a igual λ | `immutable` |
| `GET /spectrum` | `ra, dec, t0?, t1?, track?` (ePSF forzada; sin `ap`) | NDJSON en streaming | 1 d |
| `GET /known` | `ra, dec, fov, mjd` (≤ 40, separados por comas) | `{mjd:[{name,ra,dec,vmag,kind}]}` | 30 d |
| `GET /gaia` | `ra, dec, radius≤0.5, gmax=19` | lista de {source_id, ra, dec, pmra, pmdec, parallax, g, ref_epoch:2016.0} | 30 d |
| `GET /fits` | `obs_id, det, collection` | 302 a la URL de S3 del L2 completo | — |

**`/resolve`, en este orden:**
1. **Coordenadas:** decimal (`269.446 4.768`, `269.446,4.768`), sexagesimal (`17h57m47.1s +04d46m05s`, `17:57:47.1 +04:46:05`, `17 57 47.1 +04 46 05`) o galácticas (`l=… b=…`).
2. **Alias locales** de `targets.json` y del atlas. Incluye las coordenadas literales del reto para WISE 0855: devuelven la posición actual con `epoch_warning: "Proper motion applied: now ~2.1′ west of the coordinates given (epoch ~2010)"`.
3. **Cometas y asteroides** (`/^\d+[PI]\b|^[CPDAXI]\/\d{4}\s?[A-Z]/i` o nombres de `sbdb.api`): JPL SBDB → `kind:"moving"`.
4. **SIMBAD** en el espejo Harvard: `https://simbad.harvard.edu/simbad/sim-tap/sync` con `REQUEST=doQuery&LANG=ADQL&FORMAT=csv&QUERY=SELECT b.main_id,b.ra,b.dec,b.pmra,b.pmdec,b.plx_value FROM basic b JOIN ident i ON i.oidref=b.oid WHERE i.id='{q}'` ✔.
   - Los valores de SIMBAD están en ICRS a época J2000: **siempre propagar**.
   - Si falla: Sesame (`https://cds.unistra.fr/cgi-bin/nph-sesame/-oxp/SNV?{q}`).

**Gaia:**
- Endpoint `https://gea.esac.esa.int/tap-server/tap/sync` ✔ (2 s).
- Consulta: `SELECT source_id,ra,dec,pmra,pmdec,parallax,phot_g_mean_mag FROM gaiadr3.gaia_source WHERE 1=CONTAINS(POINT('ICRS',ra,dec),CIRCLE('ICRS',{ra},{dec},{r})) AND phot_g_mean_mag<{gmax}`.
- Época de referencia 2016.0.

**`sb_ident`** ✔ (18 s; geocéntrico, `mpc-code=500`):
- URL: `https://ssd-api.jpl.nasa.gov/sb_ident.api?sb-kind=a&mpc-code=500&obs-time={JD}&fov-ra-center={hh-mm-ss}&fov-dec-center={dd-mm-ss}&fov-ra-hwidth={deg}&fov-dec-hwidth={deg}`, y lo mismo con `sb-kind=c` para cometas.
- La paralaje entre el geocentro y SPHEREx es de hasta ~10″ a 1 au (~1.6 px): suficiente para marcar, no para recortar.

---

## 8. Núcleo científico (`spxcore`)

### 8.1 Archivos L2 en S3 ✔
- **Store:**
  ```python
  obstore.store.S3Store("nasa-irsa-spherex", region="us-east-1", skip_signature=True)
  ```
- **Clave:** `<rel>/level2/<semana>/<procdir>/<det>/level2_<obs_id>D<det>_spx_<procdir>.fits`, con `rel` ∈ {dr1, qr3, qr2}.
  - Ejemplo real: `dr1/level2/2026W19_2A/l2b-v27-2026-245/4/level2_2026W19_2A_1286_1D4_spx_l2b-v27-2026-245.fits`.
  - El `<procdir>` **no se deduce** (una semana puede tener varios, p. ej. `l2b-v27-2026-224` y `l2b_retry-v27-2026-225`): **usar el índice canónico** `data/derived/spherex_s3_keys_compact.npz`, generado por `research/22_s3_key_index.py` (lista el bucket entero en < 1 min).
  - **Prioridad canónica: dr1 > qr3 > qr2.** Hay 1,630,148 obs×det: 1,179,406 en dr1 (v27, 2025W17–2026W20), 448,824 en qr3 (v27, 2026W20–W40) y 1,918 solo en qr2. Las 796,665 exposiciones D4–D6 del índice TAP tienen clave.
  - **El datalink de IRSA ya no resuelve exposiciones QR2** (0/205 en una muestra del 12 nov). Cualquier código que dependa de él pierde ~75% de los datos **sin dar error**. No usar el datalink en el producto.
  - **v20 → v27 (misma exposición):** la recalibración cambia el flujo de las fuentes en −2.7% (D1), −1.7% (D2), +0.7% (D3), +2.0% (D4), +0.7% (D5) y +1.5% (D6), con dispersión < 0.3% entre exposiciones. El modelo ZODI sube ~8–15%. Impacto en los tamaños de NEO: ≤ 1%.
- **DR1 ya existe en S3** (`dr1/level2/…/l2b-v27-…`, aún no está en TAP) y **cambia el formato**: FLAGS comprimido RICE_1, EPSF en lugar de PSF y sin claves `MP_*`. Ver Apéndice A.7. **No suponer `>i4` en FLAGS sin mirar la cabecera.**
- **Equivalente HTTPS:** `https://nasa-irsa-spherex.s3.us-east-1.amazonaws.com/<clave>`. Respaldo: `https://irsa.ipac.caltech.edu/ibe/data/spherex/<clave>`.
- **Estructura** (sin compresión, big-endian; un archivo pesa ~71.6 MB):

  | HDU | Nombre | Tipo | `datLoc` típico (B) |
  |---|---|---|---|
  | 0 | PRIMARY | vacío | — |
  | 1 | IMAGE | `>f4` 2040², MJy/sr | 23,040 |
  | 2 | FLAGS | `>i4` 2040² | 16,683,840 |
  | 3 | VARIANCE | `>f4` 2040² | 33,341,760 |
  | 4 | ZODI | `>f4` 2040² | 49,999,680 |
  | 5 | PSF | `>f4` 101×101×121 | 66,689,280 |
  | 6 | WCS-WAVE | tabla (malla de λ y ancho, "solo para visualización") | 71,631,360 |

  **No fijar los offsets en el código:** calcularlos leyendo las cabeceras. La tabla sirve como test.
- **Cabecera de IMAGE** ✔:
  - `CTYPE RA---TAN-SIP`, `PC1_1…PC2_2` + `CDELT`, `A_ORDER = B_ORDER = AP_ORDER = 3` (con inversa);
  - `CRPIX ≈ 1020.5`;
  - `MJD-AVG`, `DATE-AVG`, `MJD-BEG`, `MJD-END`, `XPOSURE`, `DETECTOR` (entero), `OBSID`, `PSF_FWHM` (″, ~6.06);
  - `L2 N_*` (conteos de banderas);
  - `X_SC`, `Y_SC`, `Z_SC`, `VX_SC`… (estado de la nave).
  - En algunos archivos los CTYPE no traen `-SIP` aunque sí los coeficientes; astropy los aplica igual (con un aviso). No forzar nada.

**Lectura de cabeceras y bloque de filas** (`s3.py` + `fitsio.py`). ✔ Ejecutado el 12 nov contra S3: devuelve exactamente los `datLoc` de la tabla y un bloque de (117, 2040).
```python
import asyncio, numpy as np, obstore as obs
from obstore.store import S3Store
from astropy.io.fits import Header
STORE = S3Store("nasa-irsa-spherex", region="us-east-1", skip_signature=True)
BLOCK = 2880

async def read_hdu_layout(key: str, max_hdus=7) -> list[dict]:
    """Devuelve [{name, header, hdr_loc, dat_loc, dat_span}] leyendo solo cabeceras."""
    out, loc = [], 0
    for _ in range(max_hdus):
        nblk, end = 12, None
        while end is None:   # la cabecera del PSF tiene ~509 tarjetas (15 bloques): leer más si hace falta
            chunk = bytes(await obs.get_range_async(STORE, key, start=loc, length=BLOCK * nblk))
            end = next((i for i in range(0, len(chunk), 80) if chunk[i:i+8] == b"END     "), None)
            nblk *= 2
        hlen = ((end // BLOCK) + 1) * BLOCK
        h = Header.fromstring(chunk[:hlen].decode("ascii"), sep="")
        naxis = [h.get(f"NAXIS{i}", 0) for i in range(1, h.get("NAXIS", 0) + 1)]
        nbytes = abs(h.get("BITPIX", 8)) // 8 * (int(np.prod(naxis)) if naxis else 0) + h.get("PCOUNT", 0)
        span = ((nbytes + BLOCK - 1) // BLOCK) * BLOCK
        out.append({"name": h.get("EXTNAME", "PRIMARY"), "header": h, "hdr_loc": loc, "dat_loc": loc + hlen, "dat_span": span})
        loc += hlen + span
        if out[-1]["name"] == "WCS-WAVE": break
    return out

async def read_rows(key: str, layout: list[dict], y0: int, y1: int, names=("IMAGE", "FLAGS")) -> dict:
    """Filas [y0, y1) completas (2040 px de ancho) de cada extensión pedida, en una sola llamada."""
    hd = {d["name"]: d for d in layout}
    dt = {"IMAGE": ">f4", "FLAGS": ">i4", "VARIANCE": ">f4", "ZODI": ">f4"}
    row = 2040 * 4
    starts = [hd[n]["dat_loc"] + y0 * row for n in names]
    ends = [s + (y1 - y0) * row for s in starts]
    bufs = await obs.get_ranges_async(STORE, key, starts=starts, ends=ends)
    return {n: np.frombuffer(bytes(b), dt[n]).reshape(y1 - y0, 2040) for n, b in zip(names, bufs)}
```
Las cabeceras de las 7 HDU están en los primeros ~23 KB más una cabecera por extensión. **Cachear el layout por clave** (es idéntico en archivos de la misma versión de procesamiento).

### 8.2 Índice de exposiciones (`pipelines/build_index.py`)

> **Actualizado el 13 nov:** el índice ya está construido (`data/derived/spherex_exposures_d456_dr1_qr3.parquet` + `spherex_s3_keys_compact.npz`, §8.0b y paso 3 de §19). Lo que sigue describe cómo regenerarlo. Hoy hay que **consultar `obs_collection IN ('spherex_dr1','spherex_dr1_deep','spherex_qr3','spherex_qr3_deep')`**, no QR2 (DR1 es su reproceso), y armar las claves S3 con el índice canónico. Los conteos de abajo corresponden a QR2 y son históricos.

1. **TAP** (`https://irsa.ipac.caltech.edu/TAP/sync`, `FORMAT=csv`), por bloques de 5 días, con 4 hilos, reintentos con espera creciente y caché por bloque:
   ```sql
   SELECT obs_id, obs_collection, energy_bandpassname, t_min, t_max, s_ra, s_dec, s_region
   FROM spherex.obscore WHERE t_min >= {a} AND t_min < {b}
   ```
   - Hay ✔ 1,097,080 filas en `qr2`, 270,250 en `qr2_deep`, 192,961 en `qr3` y 47,182 en `qr3_deep` (más `*_cal`: **descartar**).
   - Rango de `qr2`: MJD 60789.75–61241.0. Rango de `qr3`: hasta 61318.0 (8 oct 2026).
   - **Deduplicar por (obs_id, energy_bandpassname, obs_collection).**
   - `s_region`: `POLYGON ICRS ra1 dec1 … ra4 dec4`, con vértices en los píxeles (0,0), (2039,0), (2039,2039) y (0,2039) ✔.
2. **Claves S3:**
   - listar `qr2/level2/` y `qr3/level2/` con `obs.list(STORE, prefix=…, chunk_size=1000)` (asíncrono, por semana, en paralelo);
   - mapear `level2_{obs_id}D{det}_…` → clave.
3. **λ central:** `lam_c` y `bw_c` en el centro del detector, desde CWAVE/CBAND (§8.4).
4. **HEALPix:** `cdshealpix.nested.polygon_search(lon, lat, depth=6)` → `cells.parquet(cell:int64, eid:int32)`.
   - Verificar la firma en la 0.9.0: `from cdshealpix.nested import polygon_search`; recibe `astropy.coordinates.Longitude/Latitude`.
5. **Archivos:** `exposures.parquet(eid, obs_id, det, collection, t_mid, ra[4], dec[4], s3_key, lam_c, bw_c)` y `meta.json(built_at, max_mjd, collections)`.
6. **Consulta:**
   - celda del punto → `eid` candidatos (y vecinos si FOV > 0.2°);
   - prueba exacta de punto dentro del polígono en el plano tangente centrado en el punto (gnomónica);
   - si el recorte entero no cabe, `edge = true`.
7. **Actualización:** `make index` incremental (semanas nuevas). Las colecciones nuevas aparecen solas.

**Campos profundos:** R Dra tiene **1,133 exposiciones** solo en D4–D6 (DR1+QR3) ✔. Con `max_frames`:
1. agrupar por visita;
2. repartir el cupo entre visitas;
3. dentro de cada visita, elegir las de λ más distintas (cubrir el rango).

**Nunca** tomar "las primeras N".

### 8.3 Recorte + reproyección (`cutout.py`)
- **Grilla de salida:** TAN, norte arriba, centrada en el objetivo (propagado a la época del cuadro si tiene movimiento propio y se pidió seguirlo); `cdelt = 6.15″ = 0.0017083333°`; `nx = ny = 2·round(fov/2/cdelt) + 1` (impar). Ejemplos: 0.25° → 147 px; 0.2° → 117 px.
- **Por exposición:**
  1. `w_in = WCS(header_IMAGE)`.
  2. Esquinas y bordes de la salida → `w_in.all_world2pix` → `y0, y1, x0, x1` con margen de 3 px, recortados a [0, 2040).
  3. `read_rows` de IMAGE y FLAGS (y VARIANCE si `var=1`).
  4. Malla: `ra, dec = w_out.wcs_pix2world(xx, yy, 0)` → `xs, ys = w_in.all_world2pix(ra, dec, 0)`. **Una sola transformación por cuadro.**
  5. Flujo: `map_coordinates(img, [ys - y0, xs - x0], order=1, cval=np.nan, prefilter=False)`.
  6. Banderas: `order=0`, más NODATA donde caiga fuera.
  7. Varianza: `order=1`.
  8. λ y ancho de banda: `map_coordinates(CWAVE, [ys, xs], order=1)` sobre el mapa **completo** → ajustar `lam_poly` por mínimos cuadrados.
- **`reproject.reproject_interp`** es equivalente (test con tolerancia de 1e-4 relativo).
- **`track=<slug>`:** el centro de la grilla de cada cuadro es la efeméride a su `MJD-AVG`.
- **No enmascarar OUTLIER (bit 19)** en la fotometría: marca lo que difiere entre visitas, es decir, lo que se mueve. La máscara de fotometría es la oficial de §8.0b (`HARD_ES21`).

### 8.4 Longitud de onda (`calib.py`) ✔
- **Archivos v5:** `qr3/spectral_wcs/cal-swcs-v5-2026-191/{d}/spectral_wcs_D{d}_spx_cal-swcs-v5-2026-191.fits`. HDU `CWAVE` y `CBAND` (2040² float32, µm) y `WCS-WAVE`. Cada archivo pesa 33.3 MB.
- **Cargar los 6 detectores a resolución completa** al arrancar la API (~200 MB). **NO submuestrear** ✔: cada 4 px el p99 queda en 0.1–0.9 nm, pero el máximo llega a **636 nm en D4** por saltos en los bordes.
- **Bordes poco fiables** ✔:
  - D4: saltos en las filas ≥ 2020 (columnas ~540–690);
  - D5: en las esquinas (filas < 15, columnas > 2018).
  - Excluir de los espectros los píxeles a < 20 px de cualquier borde.
- **Estructura:** λ varía sobre todo a lo largo de Y (D5: 4.42 µm en y = 0 → 3.81 µm en y = 2039; ~0.30 nm/px) con curvatura en X. Hay ondulaciones de ~0.1–1 nm rms.
- **Versión:** la v5 desplaza D5 y D6 en +6.4 nm respecto de la v4. En la investigación medimos λ_real = λ_v4 + 3.7 ± 0.9 nm en D5: el mismo signo. **El producto usa v5 tal cual** y lo explica en `/method`.
- **Rangos v5 ✔:** D4 2.395–3.867 µm, D5 3.798–4.446 µm y D6 4.401–5.025 µm.
- **Canales:** `channels.json` (102 filas: `frame = 17·(det − 1) + (subcanal − 1)`, λ, mínimo, máximo, R y ancho de banda).
- **Ángulo sólido:** `qr2/solid_angle_pixel_map/cal-sapm-v2-2025-164/{d}/…` (arcsec²; mediana 37.77 frente a 37.82 nominal, variación de −0.8% a +0.6%).

### 8.5 Espectro al vuelo (`spectrum.py`)
1. Exposiciones que contienen el punto (D1–D6, todas las épocas): **~300–400 en un punto típico** ≈.
2. Posición por exposición: objetos fijos con movimiento propio a `MJD-AVG`; cometas por efemérides (§8.7).
3. Píxel de origen con `all_world2pix`. Si está a < 20 px del borde, la fila sale con `edge: true` y no se dibuja por defecto.
4. Bloque de 21 filas alrededor del píxel (~171 KB por extensión), IMAGE + FLAGS (+ VARIANCE).
5. **Fotometría (vigente):** ePSF forzada de §8.0c (R = 4 px, fondo libre). *Histórico:* apertura r = 3 px con pesos por fracción de píxel (submuestreo 5×5).
   - **Fondo de objetos fijos:** mediana con recorte de 3σ en un anillo de 6–10 px.
   - **Fondo de cometas:** anillo de **40–55 px** (necesita 111 filas).
6. **Saturación:** si hay OVERFLOW en la apertura → `sat: true` (punto hueco y fuera de la curva de luz).
7. `asyncio.Semaphore(64)` y `StreamingResponse` (NDJSON, una línea por exposición).
8. ≈ 5–10 s en total, con los primeros puntos en < 1 s.

### 8.6 Diff λ: cielo estático a igual λ (`sky.py`), nuestro diferencial
**Problema:** el filtro LVF hace que cada fila del detector vea otra λ. La misma estrella cae en otra fila en otra visita, con otra λ y otro flujo, así que **restar épocas en crudo deja residuos en todas las estrellas**.

**Algoritmo**, por cuadro i (mismo detector, grilla común):
1. **Candidatos:** cuadros j de **otra visita** (|t_j − t_i| > 2 d) con |λ_j(centro) − λ_i(centro)| < 3·bw_i.
2. Se toman los **K = 8** más cercanos en λ. Si hay menos de 3 → Diff no disponible para ese cuadro (la interfaz lo dice).
3. **Referencia por píxel:**
   - si los λ_j rodean a λ_i(x, y): ajuste lineal F_j(λ) con un recorte de 3σ (una iteración), evaluado en λ_i(x, y) con `lam_poly`;
   - si no la rodean: **mediana** de los F_j (sin extrapolar).
4. **Diferencia:** D_i = F_i − R_i. Lo fijo se cancela; lo que se movió queda **positivo donde está y negativo donde estaba** (dipolo); lo que varió de brillo, con el signo del cambio.
5. **σ_i** = 1.4826 × MAD de D_i, para la escala de la LUT divergente y para "What changed?" (umbral de 5σ).
6. **Dónde se calcula:** el servidor en lo precalculado y en `/diff`; el Worker en vivo (147² × 8 operaciones por cuadro).

**Resultado medido en la investigación (3I y censo):** χ²_red de 104 → 6.5 (24P) y de 440 → 32 (C/2024 J3).

### 8.7 Efemérides (`ephem.py`)
- **Horizons** (`https://ssd.jpl.nasa.gov/api/horizons.api`, o `astroquery.jplhorizons`) con `CENTER='500@-163182'` (SPHEREx), `QUANTITIES='1'`, paso de 1 h en el intervalo pedido.
- **Designaciones que funcionaron:** 3I → `DES=1004083;`, 29P → `DES=29P;`, 240P → `240P-B`. Para los periódicos, `CAP;NOFRAG`.
- **`C/2025 N1` es 3I/ATLAS:** deduplicar.
- **Interpolar en vectores unitarios** (nunca RA en grados).
- **Tiempo:** usar `MJD-AVG` (está en **UTC**) y **convertirlo a TDB** antes de consultar Horizons o interpolar efemérides (son 69 s; a 7.5 km/s eso da 518 km de error en la posición de la nave). Equivale a `t_min + 56.79 s`.
- **Más rápido y exacto:** posición topocéntrica = vector geocéntrico del objeto (Horizons `500@399`, una vez por objeto) − `X_SC/Y_SC/Z_SC` de la cabecera. Validado a 0.01″ (Apéndice A.4).
- **Plan B:** Kepler desde SBDB (error < 0.06° frente a Horizons): sirve para buscar, **no para recortar**.

### 8.8 Caché
- **Recorte:** `sha1(f"{s3_key}|{ra:.6f}|{dec:.6f}|{fov:.4f}|{track}|{swcs}")` → `.npz` en `/data/cache`, con LRU por tiempo de acceso hasta 8 GB.
- **Pila:** hash de la lista ordenada de claves de recorte. Respuesta con `Cache-Control: public, max-age=31536000, immutable` y `ETag`.
- **Invalidación:** los L2 no cambian dentro de una versión. Si IRSA reprocesa, cambia `l2b-vNN` en la clave.

### 8.9 Cometas (`comets.py`): método resumido (detalle en el doc 06, §3)
**Fotometría:**
- 3 px de apertura, anillo de 40–55 px y Diff λ (K de 10–12 épocas lejanas, |Δt| > 2 d, polinomio de grado 2 en λ por apertura).
- Ventanas: CO₂ en D5 de 3.85–4.42 µm; CO en D6 de 4.60–4.74 µm; H₂O en D4 de 2.50–2.86 µm (±20 d).

**Modelo de banda CO₂ ν₃:**
- ν₀ = 2349.143 cm⁻¹, B = 0.3902 cm⁻¹, **solo J par**.
- R(J) = ν₀ + 2B(J + 1) con peso (J + 1)/(2J + 1); P(J) = ν₀ − 2BJ con peso J/(2J + 1).
- Población (2J + 1)·exp(−B·J(J + 1)·hc/kT).
- Cada línea se convoluciona con una gaussiana de σ = √((ancho/2.355)² + σx²).
- Continuo lineal + F_band.
- Malla: T_rot ∈ {40, 60, 80, 100, 150, 250} K, σx ∈ {0, 5, 10, 15} nm, δ ∈ {−6.7, −3.7, −0.7} nm.
- Recorte iterativo a 5σ.

**Otras moléculas:**
- **CO (1–0):** ν₀ = 2143.27 cm⁻¹, B = 1.9225 cm⁻¹, todas las J.
- **H₂O:** gaussiana en 2.69 µm con σ = 0.035 µm.

**Q por Haser (madre):**
- N_ap = Q·τ·f(x), con f(x) = x[∫ₓ^∞ K₀ + 1/x − K₁(x)] y x = ρ/(vτ).
- **Régimen x ≪ 1** (x ≈ 0.01–0.034 para CO₂): **Q ≈ 2·v·N_ap/(π·ρ)**. Q ∝ v; τ casi no influye; CO/CO₂ no depende de v.

**Constantes:**

| Constante | Valor |
|---|---|
| g(CO₂) a 1 au | 2.86e-3 s⁻¹ |
| g(CO) a 1 au | 2.46e-4 s⁻¹ |
| g(H₂O) a 1 au (2.5–3.0 µm) | 4.24e-4 s⁻¹ |
| Escalado de g | g ∝ r⁻² |
| τ₁(CO₂) | 5e5 s (Sol en calma; 3.1e5 s con Sol activo) |
| τ₁(CO) | 1.3e6 s |
| τ₁(H₂O) | 8.3e4 s |
| v | 0.85·r⁻⁰·⁵ km/s |

**Incertidumbres:**
- Monte Carlo de 4,000 realizaciones: F (estadística ⊕ dispersión del perfil), calibración ±5%, g ±5%, τ lognormal 0.3 y v lognormal 0.2. Se reportan los percentiles 16, 50 y 84.
- **Criterio de detección:** S/N_det ≥ 5 **y** χ²_red < 50 (0/79 falsos positivos en las nulas).
- **Mostrar siempre** `snr_detect`, `σ_F/F` y `n_core` (canales en 4.235–4.285 µm).

**Test dorado:** 3I en agosto de 2025 → Q(CO₂) ∈ [0.94, 1.6]e27 (publicado), y la investigación dio 1.17e27.

---

### 8.0b Lo que dice la documentación oficial (Explanatory Supplement v2.1, 10 nov 2026) ✔

- **Bits de FLAGS (tabla 16):**

| Bit | Nombre | Bit | Nombre | Bit | Nombre |
|---|---|---|---|---|---|
| 0 | TRANSIENT | 11 | COLD | 23 | GHOST_FPA |
| 1 | OVERFLOW | 12 | FULLSAMPLE | 24 | GHOST_EXT |
| 2 | SUR_ERROR | 14 | PHANMISS | 25 | STREAK |
| 6 | NONFUNC | 15 | NONLINEAR | 26 | **BLOOM** |
| 7 | DICHROIC | 17 | PERSIST | 27 | **SNOWBALL** |
| 9 | MISSING_DATA | 19 | OUTLIER | 28 | **HALO** |
| 10 | HOT | 20 | CROSSTALK | 29 | **SATELLITE_HALO** |
| | | 21 | SOURCE | | |
| | | 22 | GHOST | | |

  Queda resuelta la pregunta abierta sobre los bits 26 y 28.
- **Máscara para fotometría (recomendación oficial):** SUR_ERROR, NONFUNC, MISSING_DATA, HOT, COLD, NONLINEAR, PERSIST, BLOOM, SNOWBALL, HALO y SATELLITE_HALO. Nosotros añadimos DICHROIC. **OVERFLOW no se enmascara:** el umbral es ~½ del pozo y el ajuste SUR sigue siendo válido. En código: `spherex_psf.HARD_ES21`.
- **Máscara para estimar el fondo:** la anterior más OVERFLOW, OUTLIER, SOURCE y TRANSIENT.
- **Ángulo sólido por píxel:** la cabecera trae `OMEGA_MEDIAN` (≈ 37.95 arcsec², frente a 6.15² = 37.82 nominal: +0.3%). Usar el valor de la cabecera; existe además un mapa por píxel (Solid Angle Pixel Map).
- **Calibración absoluta:** < 1% en la mayoría de los canales.
- **Herramienta oficial de espectrofotometría** (§3.3): Tractor en modo forzado, con la ePSF por zona, un fondo global más uno local ajustado a la vez, todas las fuentes vecinas modeladas y posiciones fijas. Reporta µJy con el ángulo sólido local, error² = σ² + (0.03·F)² y una métrica de calidad del ajuste en r = 2.5 px.
  - **Nuestra metodología es la misma:** PSF/EPSF forzada con fondo, más el ajuste conjunto con estrellas Gaia (§12.1b). Decirlo así en la sección de método de la entrega.
  - **Producto:** el espectro de un clic debe usar PSF forzada (no apertura), con el 3% sistemático y la métrica de calidad.
- **Recalibración espectral v20 → v27 (medida el 13 nov, mismas exposiciones y píxeles):**
  - **D5 y D6: λ + 6.3 nm** (D5 +6.27 y D6 +6.34, uniforme ±0.4 nm); **D1–D4 sin cambio** (< 0.2 nm).
  - **Flujos de 3I/ATLAS en D5 con la misma apertura y posición:** v27/v20 = **0.998** (±3% por exposición). Las Q del censo siguen valiendo.
  - **Confirma un hallazgo propio:** con 13 cometas habíamos medido en QR2 que la banda de CO₂ caía **3.7 ± 0.9 nm antes** de su λ de laboratorio (`14_d5_wavelength_offset.py`), es decir, que las λ de D5 en v20 estaban cortas. DR1 las corrige en la misma dirección.
  - **Con DR1:** el desplazamiento residual esperado en D5 es ≈ +2.6 nm, dentro de la dispersión de ~3 nm entre cometas. El ajuste de bandas (`bandmodel.fit_physical`) mantiene el desplazamiento libre (malla de ±12 nm); en D6 (CO), donde antes se suponía δ = 0, **dejarlo libre también**.
  - En la página de método: "medimos un error de calibración de λ en D5 con cometas; DR1 lo corrigió en la misma dirección".
  - **Prueba con 3I/ATLAS (ago 2025):** ajuste físico de la banda (`bandmodel.fit_physical`) con la misma apertura y el mismo cielo.
    - v20: flujo de banda 5.40 ± 0.09 (δ = 0 nm, χ² 12.7).
    - **v27: 5.45 ± 0.09 (δ = +6 nm, χ² 11.6) → cociente 1.010: Q(CO₂) = 1.17e27 sigue valiendo.**
    - **Con δ = 0 fijo sobre DR1:** χ² = 114 y el flujo sale −8%. **Regla: con DR1, el desplazamiento de λ siempre va libre** (malla de ±12 nm, paso ≤ 3 nm).
  - **29P y CO (D6, datos v20):** el ajuste de `17_co_census.py` ya tenía δ libre (±9 nm) y eligió δ = +6 nm (χ² 53.5; con δ = 0, χ² 74 y flujo −5%). **Q(CO) = 4.5e28 es estable al 5% frente a δ.** El χ² alto indica que el perfil (T_rot = 20 K) no describe bien a 29P, y que δ absorbe parte de esa deficiencia: no usar 29P para calibrar la λ de D6. **Con DR1** (D6 +6.3 nm), usar una malla de **±15 nm** para el CO.
- **Versiones:** DR1 = reprocesado R7 (v7.0–7.2) de los surveys 1–2. QR3 = R7 del survey 3. QR2 venía de v6.4–6.5.6 y en las esquinas tenía un error de cabecera de la PSF (±5% en fotometría); con DR1 y QR3 no aplica.
- **TAP oficial al día:** `spherex.obscore` ya tiene `spherex_dr1` (945,725) + `spherex_dr1_deep` (233,681) = 1,179,406, más `spherex_qr3` + `spherex_qr3_deep` = 448,824. Coincide exactamente con nuestro índice S3. **El índice de exposiciones del producto debe salir de `spherex.obscore` (dr1 + qr3), con `s_region`.** Al índice viejo de QR2 le faltan ~13,660 exposiciones D4–D6.
- **Índice listo para el producto:** `data/derived/spherex_exposures_d456_dr1_qr3.parquet` (`research/24_obscore_index.py`).
  - Contiene 809,593 exposiciones D4–D6 de DR1 + QR3 (incluido deep), 29 MB.
  - Columnas: `obs_id`, `coll`, `det`, `t_min` y las 4 esquinas `c0..c7` en float32.
  - D1–D3 usan la huella de su par (D1↔D4, D2↔D5, D3↔D6). **Corregido (auditoría):** los centros difieren 63–76″ y las esquinas 28–105″ (hasta 17 px): usar un margen **≥ 18 px** y descartar los recortes fuera del detector. ObsCore tiene 818,637 exposiciones D1–D3 frente a 809,593 D4–D6: ~1.1% de las D1–D3 no tiene par y no aparece con este índice.
  - El script escribe los dos: el completo D1–D6 (74 MB, no se versiona) y el compacto D4–D6 del producto.
  - El datalink de IRSA **sí funciona con los ID de DR1** (`spherex_dr1?…`); el problema era solo con los de QR2.
- **MOST** (`https://irsa.ipac.caltech.edu/cgi-bin/MOST/nph-most?catalog=spherex&input_type=name_input&obj_name=…&obs_begin=yyyy+mm+dd&obs_end=…&output_mode=Brief`): validado con 2025 YH5.
  - Encuentra las 184/184 exposiciones D5/D6 de nuestro cruce (+72 de D1/D4).
  - **Sus posiciones difieren ~7.5″ (1.2 px) de la vista desde la nave.** Para fotometría, usar Horizons con `500@-163182`.
  - MOST sirve como comprobación independiente y para buscar por nombre en la UI.
- **SPLICES** (TAP `splices`, ~9 M fuentes con probable hielo, DOI 10.26131/IRSA554): **RW Aurigae está** (YSO de clase II). En su ficha: marca "objetivo de hielos de SPHEREx" y bandas de hielo de H₂O (3.0 µm) y CO (4.67 µm) en el espectro.
- **HiPS:** `data/hips/SPHEREx/spherex_allsky_cube` es el cubo de DR1 (`ivo://IPAC/P/SPHEREx/DR1/cube`, publicado el 2026-11-01). Correcto.

### 8.0c Calibración del espectro de un clic contra 2MASS y WISE ✔ (13 nov 2026)

- **Prueba** (`research/25_validate_spectra_2mass_wise.py`): 15 estrellas aisladas de AllWISE en el NEP (W1 9.5–11.5, `cc_flags=0000`, sin variabilidad), 900 recortes D1–D6 (DR1/QR3) con PSF forzada.
  - Por estrella y filtro se ajusta una ley de potencias a los puntos SPHEREx y se evalúa en λ_iso.
  - Se compara con J/H/Ks (2MASS) y W1/W2 (AllWISE).
- **Error encontrado (corregido):** la extensión PSF/EPSF es una **ePSF** (ya incluye la respuesta del píxel). Hay que **muestrearla** en el centro de cada píxel (× osamp²), no integrarla sobre el píxel.
  - Integrarla ensanchaba el modelo: el flujo salía 9–12% bajo y la separación de fuentes vecinas filtraba más (WISE 0855: −0.08 → −0.02 mJy).
  - Ahora `spherex_psf.PSF_MODE = "sample"` (por defecto).
- **Sin corrección de apertura (decisión del 13 nov, segunda iteración):** la ganancia absoluta de SPHEREx se calibró con **fotometría ePSF** de 17 estrellas CALSPEC (~54,000 medidas; Expl. Supplement §4.1.1). El flujo de la ePSF muestreada **ya es el flujo calibrado**. Multiplicar por la razón apertura/PSF cuenta dos veces las alas (error 45).
  - `spherex_psf.APPLY_APCOR = False`. El JSON `spherex_psf_aperture_correction.json` (r = 8 px / ePSF: D1 1.038 … D6 1.142) queda solo como referencia de la forma de la PSF.
  - La curva de crecimiento sigue subiendo más allá de 8 px, así que "flujo total por apertura" no está bien definido: otra razón para usar la convención ePSF del equipo.
- **Resultado final** (ePSF muestreada, sin `apcor`; mediana SPHEREx/catálogo y dispersión robusta entre estrellas):

| Filtro | J | H | Ks | W1 | W2 |
|---|---|---|---|---|---|
| Cociente | 0.969 | 0.985 | 0.943 | 0.959 | 0.970 |
| Dispersión | 0.042 | 0.047 | 0.059 | 0.018 | 0.040 |

  - En el NEP: 0.965 ± 0.016 (dispersión entre bandas, no un error).
  - **Ampliación de la auditoría (14 nov):** con 26 estrellas más en COSMOS y CDFS (elegidas con Gaia, posiciones propagadas; `spectrum_validation_stars.csv`) sale 0.999 y 0.997. **Con los tres campos (41 estrellas): J 0.982, H 1.008, Ks 1.011, W1 0.972, W2 0.996.** El −3.5% del NEP no se repite, así que no es un punto cero: citar "0.97–1.01, ±3%".
  - La referencia del Supplement para la calibración por ePSF es §3.3 + §4.2.1.
  - WISE 0855 es compatible (W2 sintética 0.45 ± 0.02 mJy, §12.1b).
  - Con `apcor` aplicada, W2 salía +10% y las bandas no eran uniformes (1.00–1.10): fue la pista del error.
- **Para el producto:** espectro de un clic = PSF forzada (ePSF muestreada, R = 4 px, fondo libre), **sin corrección de apertura**, con error² = σ² + (0.03·F)². En la página de método, mostrar `data/export/calibration.json` (tres campos) como validación ("±3% contra 2MASS/WISE en 0.75–5 µm").

## 9. Frontend

### 9.1 Reglas de Svelte 5 (obligatorias)
- **Usar:** `let x = $state(…)`, `const y = $derived(…)`, `$effect(() => …)`, `let { a } = $props()`, `{#snippet}`, `{@render}`, `onclick={…}`.
- **Prohibido:** `export let`, `$:`, `<slot>`, `on:click` y stores de `svelte/store` para estado local.
- **Estado compartido** en `*.svelte.ts`:
  ```ts
  export const view = $state({ ra: 0, dec: 0, fov: 0.25, det: 4, t: 0, mode: 'epoch' as Mode, ... })
  ```
- **Nada de lógica pesada en componentes:** decodificación, medianas, Diff λ y fotometría van en Workers (Comlink, con `ArrayBuffer` transferibles).

### 9.2 Estado de la vista ⇄ URL (fuente de verdad)
```
/explore?target=barnard&ra=269.446268&dec=4.768204&fov=0.25&det=4&ch=2.671&t=60902.913
        &mode=diff&a=60902.913&b=61118.402&layers=gaia,jpl,grid&stretch=asinh:0.5:99.5
        &lut=plate&ui=story&lang=es
```
- **Precisión:** `ra` y `dec` con 6 decimales, `t` (MJD) con 3. `mode ∈ epoch|blink|diff|sum|rgb|cube`; `ui ∈ story|lab`.
- **Prioridad:** `target` carga lo precalculado. Sin `target`, se usa la API.
- **Lectura:** desde `page.url.searchParams` al montar. **Escritura:** `replaceState(url, {})` (de `$app/navigation`), con *debounce* de 150 ms y solo al soltar los controles. Nunca dentro del bucle de animación.
- **`/embed`:** acepta lo mismo; sin cabecera ni paneles; logo pequeño que enlaza a la vista completa.

### 9.3 Renderizador WebGL2 (`gl/renderer.ts`)
**Texturas:**
- `flux`: `TEXTURE_2D_ARRAY` `R32F`, `NEAREST` (sin depender de `OES_texture_float_linear`, que falta en algunos iPhone).
- `flags`: `TEXTURE_2D_ARRAY` `R16UI`.
- `lut`: `TEXTURE_2D` RGBA8 de 256×1.
- Se suben **una vez por pila**. Cambiar de cuadro solo cambia un *uniform*.

**Geometría y dibujo:**
- Un triángulo de pantalla completa. Paneo y zoom por *uniform* (`u_view = [cx, cy, scale]`).
- Vecino más cercano en la placa: los píxeles de 6.15″ deben verse tal cual.

**Fragment shader (esqueleto):**
```glsl
#version 300 es
precision highp float; precision highp int;
precision highp sampler2DArray; precision highp usampler2DArray;
uniform sampler2DArray u_flux; uniform usampler2DArray u_flags; uniform sampler2D u_lut;
uniform int u_a, u_b, u_mode;      // 0 epoch,1 blink,2 diff(=capa diff precalculada),3 sum(capa extra)
uniform float u_mix, u_lo, u_hi, u_beta, u_sigma; uniform int u_func; // 0 lin,1 sqrt,2 log,3 asinh
uniform uint u_flagMask; uniform vec4 u_flagColor, u_nanColor, u_satColor;
uniform vec3 u_view; uniform vec2 u_size, u_canvas;
in vec2 v_uv; out vec4 o;
float stretch(float v){
  float x = clamp((v - u_lo) / (u_hi - u_lo), 0.0, 1.0);
  if (u_func==1) return sqrt(x);
  if (u_func==2) return log(1.0 + 1000.0*x)/log(1001.0);
  if (u_func==3) return asinh(u_beta*x)/asinh(u_beta);
  return x;
}
void main(){
  vec2 p = (v_uv - 0.5) * u_canvas / u_view.z + u_view.xy;   // píxel de datos (float)
  ivec2 ip = ivec2(floor(p));
  if (any(lessThan(ip, ivec2(0))) || any(greaterThanEqual(ip, ivec2(u_size)))) { o = u_nanColor; return; }
  float a = texelFetch(u_flux, ivec3(ip, u_a), 0).r;
  float b = texelFetch(u_flux, ivec3(ip, u_b), 0).r;
  uint fl = texelFetch(u_flags, ivec3(ip, u_a), 0).r;
  float v = (u_mode==1) ? mix(a, b, u_mix) : a;
  if (v != v) { o = u_nanColor; return; }
  if ((fl & 2u) != 0u) { o = u_satColor; return; }           // OVERFLOW → blanco, nunca negro
  float t = (u_mode==2) ? clamp(0.5 + 0.5 * v / (u_sigma * 5.0), 0.0, 1.0) : stretch(v);
  o = texture(u_lut, vec2(t, 0.5));
  if ((fl & u_flagMask) != 0u) o = mix(o, u_flagColor, 0.55);
}
```

**LUTs:**
- `plate`: gris cálido de `#0B0B0A` a `#ECE7DC`.
- `diff`: divergente, `--co-on-plate` (negativo) → `#0B0B0A` → `--co2-on-plate` (positivo).
- `ochre`: para el gas.

**Interacción:**
- El inspector de píxel calcula `p` en JS con la misma fórmula y lee el valor del `Float32Array` del Worker. **Nunca `readPixels`.**
- `ResizeObserver` y `devicePixelRatio` ≤ 2. Rueda o pellizco = zoom centrado en el cursor; arrastrar = paneo.

**Capa de anotaciones (SVG encima del canvas, con la misma transformación):**
- cruces de Gaia en la posición propagada **a la época del cuadro actual**;
- flecha de movimiento (vector de 1 año);
- círculos de JPL;
- apertura, regla y FWHM.

### 9.4 Modos del visor
| Modo | Qué hace | Implementación |
|---|---|---|
| Epoch | Cuadro k; reproducir de 2 a 12 fps (por defecto 4) | `u_a = k` |
| Blink A↔B | Alterna a 2 Hz con fundido de 80 ms | `u_a`, `u_b`, `u_mix` animado |
| Diff λ | D_k con LUT divergente ±5σ | Pila `diff` (precalculada o del Worker) |
| Sum | Media ponderada por 1/var de los cuadros visibles (o de los 6 detectores remuestreados) | Worker → capa extra |
| Cube | Deslizador de λ: el cuadro de λ central más cercana; en Aladin, `setFrequency` (§9.7; **no** `setSliceNumber`) | `channels.json` |
| RGB (P2) | 3 detectores a R, G y B | 3 pilas |

**Reglas:**
- **Estirado:** percentiles 0.5–99.5 **de toda la pila** (`stretch_hint`). **Nunca por cuadro**: el video "respiraría" por el estirado, no por los datos.
- `prefers-reduced-motion` → sin reproducción automática y fundidos de 0 ms.

### 9.5 Modos de interfaz: Story (por defecto) y Lab
**Story:**
- La placa ocupa ~75% del ancho, sobre papel.
- Arriba, la búsqueda grande (Newsreader cursiva: *"Search the sky — a star, a comet, or coordinates"*).
- Debajo, la línea de tiempo como regla milimetrada.
- **Columna derecha de "notas de campo"** (serifa):
  - qué estás viendo, en 2 líneas;
  - **Play**, **Compare two dates** y **What changed?**;
  - el espectro en miniatura al hacer clic;
  - los pasos de los Field notes si hay `target`.

**Lab** (interruptor arriba a la derecha):
- Los paneles pasan a papel oscuro `#1A1916`.
- Aparecen: el árbol de capas (240 px, izquierda), la barra de herramientas (40 px), el inspector (320 px, derecha), las propiedades del cuadro y Aladin en vista dividida.

**Transición:** 300 ms con `cubic-bezier(.2, .7, .2, 1)`; **la placa no se mueve** (los paneles entran desde los bordes).

**Disposición Lab (≥ 1280 px):**
```
┌───────────────────────────────────────────────────────────────────────────────────────┐
│ BREATHING COMETS  [⌘K Barnard's Star · 17h57m47.10s +04°46′05.5″]  FOV 0.25°  Share EN|ES  Story◯Lab │
├──────────┬──────────────────────────────────────────────────────────┬───┬─────────────┤
│ LAYERS   │                 PLACA (WebGL2) + tinta SVG               │ ▣ │ INSPECTOR   │
│ SPHEREx  │                                                          │ ✥ │ x,y RA Dec  │
│  D4 ch…  │        [ EPOCH | BLINK | DIFF λ | SUM | CUBE ]           │ ⌖ │ λ Δλ valor σ│
│ Ref: DR1 │                                                          │ ◎ │ banderas    │
│  2MASS…  │                                                          │ ∿ │ SPECTRUM    │
│ Gaia JPL │                                                          │ ⓘ │ LIGHT CURVE │
├──────────┴──────────────────────────────────────────────────────────┴───┴─────────────┤
│ ▶ 4 fps |2025-08 ─●─●●───│───●●●──│──●●── 2026-09|  A▲ B▲  stretch  ⇣ export          │
│ D4 · 2.671 µm · DR1 · 2025-08-15 21:54 UTC (MJD 60902.913) · visit 3 · 18/42 · OUTLIER 12 │
└───────────────────────────────────────────────────────────────────────────────────────┘
```

**Móvil (< 768 px):**
- Siempre Story.
- Placa cuadrada arriba, línea de tiempo fija abajo y notas en una hoja inferior.
- Funciones mínimas: Play, Compare, Diff y espectro con un toque. Sin desplazamiento horizontal.

### 9.6 Componentes
| Componente | Responsabilidad |
|---|---|
| `SearchBar.svelte` (Story) / `CommandBar.svelte` (Lab, ⌘K o `/`) | Parseo de coordenadas, alias, cometas, `/resolve`. Comandos en Lab: `fov 0.3`, `det 5`, `ch 4.26`, `mode diff`, `goto r-dra`, `export gif` |
| `SpxViewer.svelte` | Canvas WebGL2, paneo y zoom, `OverlaySvg` |
| `OverlaySvg.svelte` | Gaia por época, flecha de movimiento, JPL, apertura, regla, retícula y escala angular ("1′") |
| `Timeline.svelte` | Canvas 2D; ticks por cuadro y visitas; reproducir y velocidad; marcadores A y B; ←/→, Shift+←/→ |
| `FieldNotes.svelte` | Columna Story: texto, 3 botones y pasos guiados |
| `ModeSwitch.svelte` | Bits UI `ToggleGroup` |
| `LayerTree.svelte` | Capas con ojo, opacidad y color ⇄ URL `layers=` |
| `Inspector.svelte` | Píxel (del Worker), `SpectrumPlot`, `LightCurvePlot` y `FrameProps` |
| `SpectrumPlot.svelte` | uPlot: λ (µm) vs. F (mJy); color por visita; bandas moleculares sombreadas con sus colores (§10.2); puntos huecos si `sat` |
| `LightCurvePlot.svelte` | Flujo relativo vs. MJD (normalizado por la SED mediana en cada λ); para RW Aur y R Dra |
| `WhatChanged.svelte` | Lista de residuos ≥ 5σ, cruce con Gaia y JPL, etiquetas *known*/*candidate*, clic para centrar |
| `AladinView.svelte` | §9.7 |
| `ShareDialog.svelte` | URL, código `<iframe>`, PNG (`canvas.toBlob`) y **video WebM** del parpadeo con `canvas.captureStream(30)` + `MediaRecorder` (nativo, sin librerías). GIF: no |
| `StatusLine.svelte` | Estados de carga y errores por fuente (nunca modales) |

### 9.7 Aladin Lite 3.8.2 (verificado en el código del paquete)
```ts
// AladinView.svelte — solo en el cliente, con import dinámico (pesa 2.4 MB)
const { default: A } = await import('aladin-lite');
await A.init;
const aladin = A.aladin(el, { fov: view.fov * 3, target: `${view.ra} ${view.dec}`, projection: 'TAN',
  cooFrame: 'ICRSd', showCooGridControl: false, showLayersControl: false, showGotoControl: false,
  showSimbadPointerControl: false, showFrame: false, showFullscreenControl: false });
const dr1 = aladin.newImageSurvey('https://irsa.ipac.caltech.edu/data/hips/SPHEREx/spherex_allsky_cube');
aladin.setBaseImageLayer(dr1);
// NO usar setSliceNumber: el wasm de 3.8.2 indexa el cubo linealmente en FRECUENCIA (verificado en el prototipo; §0.9b)
const fmin = 299792458 / 5.009e-6, fmax = 299792458 / 7.43e-7;
dr1.setFrequency({ value: fmin + (frameIndex + 0.5) / 102 * (fmax - fmin), unit: 'Hz' });  // pide el cuadro frameIndex; etiqueta con channels.json
const twomass = aladin.newImageSurvey('https://irsa.ipac.caltech.edu/data/hips/CDS/2MASS/Color');
aladin.setOverlayImageLayer(twomass, '2mass'); twomass.setOpacity(0);
aladin.on('positionChanged', (p) => syncFromAladin(p)); aladin.on('zoomChanged', (z) => syncFov(z));
```

- **Cubo ✔:** el objeto HiPS tiene `setSliceNumber(n)` y `setFrequency({value, unit})`; **usar `setFrequency` con la fórmula de arriba** (verificado: pide los tiles `Npix*_<frame>.png` correctos). Al cargar un cubo, Aladin agrega su propio control "Slice" (`cube_displayer`): ocultarlo con CSS o con la opción correspondiente.
- **Ojo ✔ (corregido el 13 nov):** `setSliceNumber` convierte el cuadro a frecuencia suponiendo λ lineal, y el wasm luego indexa linealmente en frecuencia: el resultado es el canal equivocado (pedir el 85 trae el ~2). La fórmula en frecuencia de arriba sí trae el cuadro pedido. Etiquetar siempre con `channels.json`. Además, Aladin 3.8.2 se carga como módulo ES: `const A = (await import('https://cdn.jsdelivr.net/npm/aladin-lite@3.8.2/dist/aladin.js')).default`.
- **Términos de uso:** se puede personalizar la interfaz, pero el **logo y el enlace de Aladin deben quedar visibles** abajo a la derecha.
- **Verificar** los nombres de las opciones de `A.aladin` en `https://cds-astro.github.io/aladin-lite/` (el sitio de CDS estaba caído el 12 nov; la documentación de GitHub Pages es otro servidor).
- **Catálogos:** `A.catalog({name:'Gaia', sourceSize: 10, color: '#A85A14'})` y `cat.addSources(list.map(s => A.source(s.ra, s.dec, s)))`.
- **Huellas:** `A.graphicOverlay()` + `A.polygon([[ra, dec], …])`.

### 9.8 Estados (diseñados, no improvisados)
- **Precalculado:** se pinta el primer cuadro apenas se decodifica; el resto llega en segundo plano.
- **Modo libre:** "Querying index… 42 exposures in D4" → "Reading pixels 18/42" (barra de 1 px).
- **Sin cobertura:** "SPHEREx has not observed this position in D4 yet (data to 2026-10-08). Try another detector." + cobertura en Aladin.
- **Fuente caída:** "Gaia DR3 unavailable — retry" (línea discreta).
- **Coordenadas del reto para WISE 0855:** aviso de movimiento propio y centrado en la posición actual.

---

## 10. Sistema visual "Plate & Ink"

### 10.1 Concepto
Toma los principios de anthropic.com, que al usuario le gusta:
- papel cálido, tinta casi negra y **un solo acento cálido**;
- serifa editorial, mucho aire y tono de ensayo;
- nada de degradados.

**No copia su marca:** ni sus fuentes (propietarias), ni sus colores exactos, ni sus ilustraciones.

**Concepto propio:** Plutón se descubrió en 1930 comparando **placas fotográficas** de vidrio en un *blink comparator*.
- **Papel** para todo lo que se lee.
- **Placa** (negro, enmarcada, con escala y ficha técnica) para todo lo que es cielo.
- **Tinta** para las anotaciones sobre las placas.

### 10.2 Tokens (`src/app.css`; contraste WCAG calculado ✔)
```css
:root{
  --paper:#F5F2EA; --paper-2:#EBE6DA; --rule:#D3CCBD;
  --ink:#17160F;   /* 16.2:1 sobre paper */
  --ink-2:#4B473E; /* 8.3:1 */
  --graphite:#6F6A5E; /* 4.8:1 (AA) etiquetas, notas al pie */
  --plate:#0B0B0A; --plate-ink:#ECE7DC; /* 16.0:1 */ --plate-dim:#9A9488; /* 6.5:1 */
  --lab-panel:#1A1916;
  --co2:#A85A14; --co2-on-plate:#F2A03D;   /* acento principal (único cálido) 4.5 / 9.3 */
  --co:#1C6E73;  --co-on-plate:#7FD4E6;    /* 5.3 / 11.7 */
  --h2o:#3550C4; --h2o-on-plate:#8FA5FF;   /* 6.1 / 8.4 */
  --signal:#A8341C; --signal-on-plate:#FF6B57; /* 5.9 / 7.0 */
  --font-display:'Newsreader Variable', Georgia, serif;
  --font-ui:'IBM Plex Sans', system-ui, sans-serif;
  --font-data:'IBM Plex Mono', ui-monospace, monospace;
  --ease:cubic-bezier(.2,.7,.2,1); --t-fast:200ms; --t-med:300ms; --t-slow:500ms;
  --measure:640px; --gutter:clamp(16px,4vw,48px);
}
@media (prefers-color-scheme: dark){ :root:not([data-theme="light"]){
  --paper:#141310; --paper-2:#1C1B17; --rule:#34312A; --ink:#ECE7DC; --ink-2:#C9C2B4; --graphite:#9A9488;
  --co2:#E39A45; --co:#5FBFC7; --h2o:#8FA5FF; --signal:#FF6B57; } }
body{ background:var(--paper); color:var(--ink); font-family:var(--font-ui); }
```

**Reglas de color:**
- Los colores de molécula son **semánticos**: CO₂ = ocre, CO = verde azulado, H₂O = azul. No se usan como decoración.
- El ocre es el único acento de la interfaz: botón primario, enlace activo y lo que está seleccionado en la línea de tiempo.

### 10.3 Tipografía
| Rol | Fuente | Uso |
|---|---|---|
| Titulares y ensayo | Newsreader Variable | H1 de 56–88 px, peso 400, tracking −0.01 em; subtítulos en cursiva; ejes `opsz` automáticos |
| Interfaz y cuerpo | IBM Plex Sans | 15–17 px; botones en peso 500 |
| Datos | IBM Plex Mono | Coordenadas, λ, obs_id y fechas; `font-variant-numeric: tabular-nums` |

- **Marca "BREATHING COMETS":** Newsreader en versalitas con espaciado de 0.08 em, o Plex Mono en mayúsculas con 0.2 em. Probar las dos el sábado y elegir una.
- **Error conocido:** `text-transform: uppercase` convierte `µ` en `M`. **No usar uppercase por CSS en textos con unidades**: escribirlos ya en mayúsculas, salvo la unidad.

### 10.4 Composición
1. **Ensayo, no landing de SaaS:** columna de ~640 px, titulares grandes en serifa, párrafos cortos y **notas al margen** en Plex Mono gris (referencias, obs_id, fechas).
2. **Placas:**
   - fondo `--plate`, marco de 1 px en `--rule` y escala angular en el borde ("1′");
   - ficha debajo en mono: `SPHEREx D6 · 4.62 µm · 2025-12-17 · obs 2025W51_…`;
   - marcas de registro "+" en las esquinas.
3. **Tinta:** trazos SVG de 1.25 px; Gaia como cruces; movimiento como flecha de punta abierta; animación de "dibujado" (`stroke-dashoffset`) de 400–600 ms, **una sola vez**.
4. **Movimiento sobrio:** 200–400 ms con `--ease`. Lo único llamativo es el cielo (el parpadeo).
5. **Secciones numeradas** como en un paper: `§1 The blink`, `§2 A rainbow on a chip`…
6. **Prohibido:** degradados, brillos, *glassmorphism*, tarjetas con sombra, grillas de 3 tarjetas centradas, iconos de stock, emojis, ilustraciones o renders del espacio y titulares con palabras en degradado.
7. **Accesibilidad:** foco visible (2 px en `--co2`), `aria-label` en cada control y cada atajo con un botón equivalente.

### 10.5 Landing (secciones)
| § | Título | Contenido | Elemento |
|---|---|---|---|
| Héroe | **"The sky is breathing."** | "SPHEREx maps the whole sky in 102 colors of infrared light, every six months. We made it a time machine anyone can use — and measured what comets exhale." Botones: **Open the sky** (→ `/explore?target=barnard&ui=story`) y **Meet the comets** | Placa grande de 3I/ATLAS (pila con `track`, en bucle de 6 s, sin controles). Al hacer scroll, el halo de CO₂ se entinta en ocre (GSAP ScrollTrigger). Póster WebP mientras carga |
| §1 | "Pluto was found by blinking two plates." | 1930, Tombaugh; 3 frases | Blink real de Barnard (2 placas, botón o deslizador) con la flecha de Gaia |
| §2 | "A rainbow on a chip." | El LVF: cada fila ve otra λ; por qué restar "en crudo" falla | **Antes/después** con deslizador (resta cruda frente a Diff λ) |
| §3 | "What the sky is made of." | H, H₂O, CO₂ y CO (las moléculas del reto) | Espectro real con bandas en sus colores; clic en una banda → un objeto que la muestra |
| §4 | "Comets breathe." | 3I: continuo → gas; Q con incertidumbre | Placa con mapa de gas y cifra grande en mono |
| §5 | "Measured, then checked." | 3I CO₂ (1.17e27 frente a 0.94–1.6e27), 3I H₂O (4.0e26 frente a 3.2e26) y 29P CO (4.5e28 frente a 2.9–5.6e28) | Tabla tipográfica |
| §6 | "Five places to start." | Los 5 objetivos como Field notes | 5 mini-placas en fila con desplazamiento horizontal **dentro** del contenedor |
| Pie | — | Créditos de datos, uso de IA, `/method`, código, EN/ES | Mono gris |

**Rendimiento de la landing:** no carga Aladin ni los Workers del visor. Todo lo que está debajo del héroe carga de forma perezosa. JS inicial < 90 KB gz.

### 10.6 Atlas y ficha
- **`/comets`:**
  - gráfico de Q(CO₂) vs. r_h (log), con barras 16–84% y color por estado (detected / with systematics / marginal / not detected); anillo de tinta en los "sin publicación previa";
  - tabla filtrable;
  - al pasar el cursor, la fila resalta el punto y viceversa;
  - **leyendas de honestidad:** "29P in outburst", "UN271 at 15 au: unreliable", "Q ∝ v: ±40% systematic".
- **`/comets/[slug]`:** placa con tres modos (continuo, CO₂ y residuo de gas), espectro con el modelo P/R, diagnósticos (S/N_det, σ_F/F, n_core, χ², Q(ρ)) y procedencia.
- **`/method`:** versión corta del doc 06:
  - datos;
  - SPHEREx como observador;
  - WCS espectral v5;
  - Diff λ;
  - modelo P/R;
  - Haser y Q ∝ v;
  - validaciones;
  - nulas e inyección;
  - limitaciones;
  - `build.json`;
  - comparación de nuestro espectro con la herramienta de IRSA (si da tiempo).

---

## 11. Internacionalización (EN por defecto, ES con prefijo `/es`)
- **Mensajes:** `messages/{en,es}.json` con claves con espacio de nombres (`landing.hero.title`, `explore.mode.diff`, `notes.barnard.1`).
- **No se traduce:** nombres propios, designaciones, unidades ni códigos (D4, QR2, OUTLIER).
- **Banderas:** el nombre técnico se mantiene; el *tooltip* va traducido (`OUTLIER — píxel atípico (a menudo, algo que se movió)`).
- **Números científicos:** **siempre con punto decimal**, en notación `3.4 × 10²⁷ s⁻¹`. Función única `fmtSci(x, sig)` en `src/lib/data/format.ts`. **Prohibido `toLocaleString`** en valores científicos.
- **Fechas:** en los datos, UTC ISO (`2025-08-15 21:54 UTC`); en la narrativa, formato largo del idioma.
- **Tono:**
  - Español neutro y natural: "Explora el cielo", no "Explorar el cielo"; "Compara dos fechas", "¿Qué cambió?".
  - El usuario revisa el texto en español.
- **SEO:** `<link rel="alternate" hreflang>` en las páginas prerenderizadas.

---

## 12. Datos de referencia

### 12.1 Objetivos de prueba (`targets.json` ✔; SIMBAD Harvard + astropy `apply_space_motion`)
| Objetivo | Tipo | Posición a 2026-01-01 (°) | PM (mas/año) | Exp. D4–D6 DR1+QR3 ✔ (13 nov) | Meses con datos ✔ |
|---|---|---|---|---|---|
| Barnard's Star | M4 V | 269.446268, +4.768204 | −801.6, +10362.4 | 168 (112 dr1 + 56 qr3) | 2025-08…10, 2026-03…05, 2026-08…09 |
| ε Indi B (Ba+Bb) | T1+T6, sin resolver (~0.7″) | 331.096669, −56.800649 | +3982.0, −2466.8 | 195 (155 + 40) | 2025-04…06, 09…11, 2026-04…05, 09…10 |
| WISE 0855−0714 | Y4 (~285 K) | **133.759765, −7.242182** | **−8123.7**, +673.2 | 125 (solo dr1; QR3 aún no lo cubre) | 2025-05, 10…12, 2026-04…05 |
| RW Aurigae | T Tauri clásica (binaria de 1.4″) | 76.956587, +30.401291 | +7.2, −20.3 | 156 (103 + 53) | 2025-09, 2026-02…03, 2026-09 |
| R Draconis | Mira (P ≈ 246 d) | 248.167233, +66.755024 | −20.6, +6.1 | **1,133** (campo profundo NEP: 916 deep + 217) | todos los meses 2025-04…2026-09 |

- D1–D3 ven el mismo cielo que su par D4–D6 (D1↔D4, D2↔D5, D3↔D6; huella desplazada ~58″ por el dicroico): el total es ~2× la columna. Conteos del índice de §8.0b; con margen de 3% del borde.
- **WISE 0855:** las coordenadas del reto son de ~2010. Hoy está ~126″ (2.1′) al oeste: **sin propagar, el recorte queda vacío**.

**Visibilidad esperada (≈, a partir de fotometría publicada):**
- **WISE 0855:** W2 = 13.9 Vega = 17.2 AB ≈ **0.47 mJy** (antes decía 0.045: error ×10). Medido: S/N ≈ 2–4 por exposición en D6 y 14–22 por banda de 0.2–0.4 µm al combinar. **Una estrella Gaia G=16.3 a 6.8″ (1.1 px)** domina la apertura a < 3.8 µm (~1.3 mJy a 1 µm). Hay que separarla (§12.1b). Se mueve ~1.3 px al año: no sumar épocas sin compensar el movimiento.
- **Barnard:** K ≈ 4.5 (Vega). **Núcleo saturado** (OVERFLOW → blanco). Se mueve ~1.8 px entre 2025-08 y 2026-09. **Hay que mostrarlo con F3** (cruz de Gaia por época y flecha) y el dipolo de Diff λ.
- **ε Indi B:** K ≈ 11.2 (Vega), detección holgada. ε Indi A, muy brillante a ~6.7′, puede dejar fantasmas y halos.
- **RW Aur y R Dra:** saturación en λ cortas; la curva de luz excluye las mediciones con `sat`.

### 12.1b WISE 0855: espectro separado de la estrella vecina ✔ (medido el 12 nov 2026)

- **Problema:** en la posición de 2025–26 hay una estrella Gaia DR3 (G = 16.31, μ ≈ 6 mas/año) a **6.8″ = 1.1 px** el 2026-01-01 (11.5″ en may 2025; 4.6″ en may 2026). La apertura de r = 2.5 px mide su luz: ~1 mJy a 0.7–1.6 µm, donde la enana Y es invisible (J ≈ 25).
- **Método** (`research/23_deblend_pm_target.py`, 249 exposiciones D1–D6, píxeles nativos):
  - la posición de la enana se propaga a cada exposición (`apply_space_motion`);
  - las estrellas Gaia a ≤ 6 px se propagan con su movimiento propio;
  - se ajusta por mínimos cuadrados lineales ponderados por 1/VARIANCE una PSF (PSF o EPSF de la exposición) por fuente, más un fondo, en r ≤ 5 px.
- **Resultado** (`data/derived/wise-0855_deblended.csv`):

| λ (µm) | 0.7–1.1 | 1.1–1.65 | 1.65–2.42 | 2.42–3.0 | 3.0–3.82 | 3.82–4.2 | 4.2–4.42 | 4.42–4.7 | 4.7–5.05 |
|---|---|---|---|---|---|---|---|---|---|
| WISE 0855 (mJy) | −0.02 | −0.02 | −0.00 | 0.01 | 0.01 | **0.21** | **0.52** | **0.59** | **0.39** |
| S/N | | | | | | 14 | 23 | 18 | 11 |
| estrella vecina (mJy) | 1.22 | 1.09 | 0.70 | 0.45 | 0.30 | 0.21 | 0.25 | 0.15 | 0.16 |

- **Validación (corregida):** la W2 sintética con la **curva RSR real** de W2 (`wise_w2_rsr.csv`) es **0.45 ± 0.02 mJy**; el 14% de la banda queda más allá de 5.0 µm. Referencias: W2 ≈ 13.9 de la literatura (0.48 mJy), CatWISE2020 con movimiento propio 13.82 (0.51 mJy). El catálogo AllWISE da 13.70 (0.57 mJy) porque en 2010 la fuente estaba mezclada: no usarlo. Cociente 0.88–0.94: compatible dentro del 10%.
- **Sistemático:** −0.02 mJy a λ < 1.65 µm, ≈ 2% del flujo de la vecina. Con la ePSF integrada (modo antiguo) era −0.08 (6%). Mostrarlo como piso de error. No usar el ajuste de una sola fuente.
- **Para el producto:** precalcular este CSV y usarlo como el espectro de WISE 0855 en la ficha. Es el resultado más fuerte con un objetivo del reto: **"el objeto más frío conocido fuera del Sistema Solar, separado de una estrella de fondo con Gaia, y su pico de 4.5 µm medido por SPHEREx"**.

### 12.1c Números medidos con SPHEREx para las notas de campo ✔ (13 nov 2026)

Precalcular estos resultados y mostrarlos en cada ficha, con la fuente de referencia al lado (Gaia o la literatura).

| Objetivo | Medida SPHEREx | Referencia | Script / archivo |
|---|---|---|---|
| **ε Indi B** | **μ = 4.75 ± 0.04″/año** (diferencial, error por bootstrap de visitas; la versión absoluta da 4.716), 1.44 años | Gaia DR3 4.684″/año. El +1.5% no es significativo: los controles tratados como objetivo dan μ falso de ±30–60 mas/año. El fotocentro de la binaria Ba+Bb es una explicación posible, no necesaria | `26_pm_parallax.py` → `eps-indi-b_astrometry*.json` |
| ε Indi B | **Paralaje 271 ± 20 mas** (el error formal ±12 supone exposiciones independientes; el bootstrap por las 9 visitas da ±20 y quitar un control da 277–294) con **astrometría diferencial** (en cada exposición se resta el residuo medio de 4 estrellas Gaia lejanas del mismo campo; 194 exposiciones). La versión absoluta daba 233 ± 10: las estrellas de control mostraban una "paralaje" falsa de −0.14 ± 0.03 veces el patrón (sistemático del marco WCS por época) | Gaia DR3 270.7 mas (RUWE 4.3); ε Indi A 274.8 mas | `eps-indi-b_astrometry_differential.json`, controles en `data/derived/astrometry_controls/` |
| **Barnard** | **μ = 10.6 ± 0.4″/año** (formal ±0.10; el mismo ajuste solo recupera 0.37 de la paralaje) (173 exposiciones D1–D3, D5–D6; núcleo saturado, se ajustan las alas) | 10.39″/año | `barnard_astrometry.*` |
| Barnard | Paralaje no medible: satura (error de 0.7″ por exposición) y solo hay 3 visitas útiles | — | — |
| **R Draconis** | Núcleo saturado y con BLOOM hasta 4 px en todos los detectores, así que se usan las alas (anillo de 5–9 px). **Escala de variabilidad ≈ 229 d (225–241; 95%: 219–261) a 3.8–5 µm**; a 1.1–2.4 µm, 236 d (230–519). Rango 5–95%: 2.0 mag a 0.75–1.1 µm, 1.3 mag a 1.1–2.4 µm y 0.7 mag a 3.8–5 µm (`r-dra_lightcurve_summary.json`) | 245.6 d (Mira). Con 1.9 ciclos **no es una medida independiente del período**: el "247 ± 10" anterior dependía de la malla de frecuencias | `27_lightcurve.py r-dra 150 --wings` → `r-dra_lightcurve*` |
| **RW Aurigae** | **Variabilidad anticorrelacionada:** de 2025-09 a 2026-09, el flujo a 0.75–1.1 µm sube ×1.76 (PSF) / ×1.94 (alas) y a 3.8–5 µm baja a ×0.48 / ×0.59. Los dos métodos, independientes, coinciden | Firma conocida de RW Aur A (ocultaciones por polvo del disco interior con exceso infrarrojo, 2014–2021). **Está en SPLICES** (YSO de clase II) | `27_lightcurve.py rw-aur` → `rw-aur_lightcurve_{psf,wings}.csv` |
| **ε Indi B** | **Espectro de enana T** (`23_deblend_pm_target.py eps-indi-b`, 395 exposiciones, S/N 140–1,000 por banda): picos J (30 mJy a 1.2–1.3 µm), H (32 mJy a 1.5–1.6 µm) y K (24 mJy a 2.0–2.1 µm); agua a 1.35 µm (10 mJy) y 2.7 µm; **metano** a 1.65–1.75, 2.2–2.35 y **3.15–3.45 µm** (10.7 mJy frente a 58 mJy en el pico de 4.0 µm: 5.4×); CO/CH₄ a 4.5–5 µm | WISE W1 16.1 mJy y W2 27.5 mJy (SPHEREx 24 mJy de media a 4.1–5 µm, no ponderada por la RSR de W2) | `eps-indi-b_deblended.csv`, figura `docs/mockup/assets/browndwarfs_spherex.png` |
| **WISE 0855** | Espectro separado de la estrella vecina: ≈ 0 hasta 3.8 µm y pico de 0.59 mJy a 4.4–4.7 µm; W2 sintética (RSR real) 0.45 ± 0.02 mJy | Literatura W2 ≈ 13.9 (0.48 mJy); CatWISE2020 0.51 mJy | §12.1b |

**Frases para la demo (verificadas):**
- "SPHEREx mide la distancia de ε Indi B por paralaje desde la órbita terrestre: 271 ± 20 mas, compatible con Gaia (270.7)." (método diferencial)
- "Barnard's Star se mueve 10.5″ por año: SPHEREx lo confirma."
- "R Draconis late con un ritmo de unos 8 meses, como dice su período catalogado (246 d)."
- "RW Aurigae se ilumina en el óptico mientras se apaga a 4–5 µm: polvo caliente en su disco."
- "WISE 0855, el objeto más frío fuera del Sistema Solar, aparece solo por encima de 3.8 µm."
- "En ε Indi B se ve el metano: a 3.3 µm brilla 5 veces menos que a 4 µm." (medido: 5.4×) Mostrar la figura T frente a Y: es la imagen más fuerte para la sección de moléculas del reto.

**Lecciones:**
- **Estrellas saturadas** (Barnard en D4; R Dra, RW Aur y ε Indi A): BLOOM y SUR_ERROR cubren el núcleo. Para curvas de luz relativas usar las alas (anillo de 5–9 px menos el fondo de 13–17 px). La clave de caché de `cutout_psf` ya incluye `half` y la versión.
- **Astrometría absoluta frente a diferencial:** el WCS de cada época tiene un sistemático común a todo el campo (estrellas de control lejanas: "paralaje" falsa de −0.14 veces el patrón y μ falso de ~30–40 mas/año). **Usar siempre astrometría diferencial** contra 3–5 estrellas Gaia del campo (G 12.5–14.5, RUWE < 1.2, ϖ < 1 mas): `26_pm_parallax.py <control> --targets=<json>` y restar por exposición. Con 3–4 visitas por año, μ y ϖ siguen correlacionados.

**Field notes:** 3–4 pasos por objetivo (ver el ejemplo de §6.2). Barnard: movimiento. ε Indi B: movimiento + CH₄/CO en el espectro. WISE 0855: "invisible hasta 4 µm". RW Aur y R Dra: curva de luz.

### 12.2 Cometas destacados
| Cometa | Por qué | Cifra (docs 06 y 07) |
|---|---|---|
| **3I/ATLAS** (ago y dic 2025) | Validación interestelar; **siempre se incluye** | CO₂ 1.17e27 (ago) y 3.0–3.4e27 (dic); H₂O 4.0e26 (ago) |
| 29P (dic 2025) | Estallido: CO₂ alto y CO tranquilo | Q(CO) 4.5e28; CO/CO₂ 44 [37, 52] |
| C/2022 N2 (PANSTARRS) | La detección más fuerte | S/N 63.7; Q(CO₂) 5.3e26 |
| C/2025 A6 (Lemmon) | Rico en CO₂ | Q(CO₂) 2.1e27 (χ² 72: sistemático) |
| C/2023 R1 (PANSTARRS) | Gas extendido | Q(CO₂) 1.10e27; f8/f2 = 4.7 |
| 240P/NEAT | CO₂ + H₂O | CO₂/H₂O 0.145 |
| 24P/Schaumasse | Débil y cercano | Q(CO₂) 2.7e25; CO₂/H₂O 0.076 |

### 12.3 Bandas para anotar en el espectro (`astro/bands.ts`)
| Especie | λ (µm) | Ancho del sombreado (µm) | Color |
|---|---|---|---|
| H I Paβ | 1.282 | ±0.01 | `--ink-2` |
| H I Paα | 1.875 | ±0.01 | `--ink-2` |
| H I Brα | 4.052 | ±0.01 | `--ink-2` |
| H₂O | 2.70 | 2.55–2.85 | `--h2o` |
| CH₄ | 3.31 | 3.20–3.45 | `--graphite` |
| CO₂ ν₃ | 4.26 | 4.21–4.31 | `--co2` |
| CO (1–0) | 4.67 | 4.55–4.80 | `--co` |

### 12.4 Banderas (FLAGS L2 int32 → uint16 SPXF) — *tabla de visualización; para fotometría manda §8.0b*
> **Corregido (auditoría):** la columna "¿Se rechaza en fotometría?" de abajo es la regla antigua. La vigente es `HARD_ES21` (§8.0b): **no** se enmascaran TRANSIENT ni OVERFLOW; **sí** NONLINEAR, PERSIST, BLOOM, SNOWBALL, HALO y SATELLITE_HALO. El bit 4 no existe en la tabla 16 del Supplement, DR1 no trae las claves `MP_*`, y los bits 26–29 no caben en este remapeo: añadir un bit SPXF 14 = "BLOOM/SNOWBALL/HALO" (OR de los cuatro).
| Bit L2 | Nombre | Bit SPXF | ¿Se rechaza en fotometría? | Color en la máscara |
|---|---|---|---|---|
| 0 | TRANSIENT | 0 | sí (estelas de satélite: 73% de las imágenes, ~2.2 por exposición) | `--signal-on-plate` |
| 1 | OVERFLOW | 1 | sí | blanco `--plate-ink` |
| 2 | SUR_ERROR | 2 | sí | `--signal-on-plate` |
| 4 | PHANTOM | 3 | no | — |
| 6 | NONFUNC | 4 | sí | `--plate-dim` |
| 7 | DICHROIC | 5 | sí | `--plate-dim` |
| 9 | MISSING_DATA | 6 | sí | `--plate-dim` |
| 10 | HOT | 7 | sí | `--plate-dim` |
| 11 | COLD | 8 | sí | `--plate-dim` |
| 15 | NONLINEAR | 9 | no (avisar) | — |
| 17 | PERSIST | 10 | no (avisar) | — |
| 19 | **OUTLIER** | 11 | **no** (suele ser movimiento) | `--co-on-plate` |
| 21 | SOURCE | 12 | no | — |
| — | NODATA (fuera tras reproyectar o a < 20 px del borde) | 13 | sí | `--paper-2` al 10% |

Los bits 5 (REFERENCE), 12 (FULLSAMPLE) y 14 (PHANMISS) no se transmiten.

### 12.5 Canales y HiPS
- **`channels.json`:** 102 canales (de `qr3/spectral_channels/cal-sch-v2-2026-229`).
- **HiPS SPHEREx DR1 ✔:** `https://irsa.ipac.caltech.edu/data/hips/SPHEREx/spherex_allsky_cube`.
  - Publicado el 1 nov 2026. 102 cuadros (índice = `frame`); los cuadros 50 y 51 están en blanco (dicroico).
  - PNG con estirado asinh y corte 0–40; también `fits-cube` en orden 5.
  - 12.9″ por píxel; MJD 60789.75–61174.49.
  - **Solo para visualización:** la fotometría sale de los L2.
  - Mencionar en la entrega que el HiPS es de IRSA.
- **Otros HiPS** (IRSA, CORS `*`): 2MASS Color `…/hips/CDS/2MASS/Color` y AllWISE `…/hips/CDS/AllWISE/RGB-W4-W2-W1` (más bandas sueltas W1–W4 y J, H, K).

### 12.6 Instrumento y unidades
- **Órbita:** heliosíncrona, ~660 km, 98 min.
- **Óptica:** 20 cm f/3; 6 H2RG de 2040² útiles; **6.15″/px**; dos campos de 3.5° × 11.3° (D1–D3 y D4–D6 ven el mismo cielo).
- **Bandas:**

  | Banda | Rango (µm) | R |
  |---|---|---|
  | B1 | 0.744–1.116 | 39 |
  | B2 | 1.099–1.651 | 41 |
  | B3 | 1.636–2.421 | 41 |
  | B4 | 2.423–3.822 | 35 |
  | B5 | 3.809–4.420 | 112 |
  | B6 | 4.412–5.002 | 128 |

- **Exposición:** 113.58 s.
- **Profundidad a 5σ por exposición:** ~19.5 AB (0.7–3.8 µm) y 17.5–18.5 AB (3.8–5 µm).
- **Calibración absoluta:** ≲ 3% (B1–B4) y ≲ 5% (B5–B6).
- **Ω_pix nominal** = (6.15/206264.806)² = 8.89e-10 sr. **Usar el mapa de ángulo sólido.**
- **Conversión:** F_ν [mJy] = Σ I[MJy/sr] · Ω[sr] · 10⁹.

---

## 13. Presupuestos de rendimiento (se miden; si no se cumplen, no está terminado)
| Métrica | Objetivo | Cómo medir |
|---|---|---|
| LCP de la landing (4G, Lighthouse móvil) | < 1.5 s | Lighthouse |
| JS inicial de la landing | < 90 KB gz | Visualizador de Rollup |
| JS del Explorer sin Aladin | < 160 KB gz | ídem |
| Primer cuadro de un objetivo precalculado | < 1.0 s (CDN caliente) | `performance.mark` en Playwright |
| Reproducción | 60 fps (< 4 ms de CPU por cuadro) | DevTools |
| Modo libre de 0.25° (~40 exposiciones, caché fría) | primer cuadro < 4 s; todos < 10 s | `curl -w` contra Fly |
| Espectro al vuelo | primeros puntos < 1.5 s; completo < 12 s | ídem |
| Tamaño precalculado | ≤ 6 MB por detector; ≤ 25 MB por objetivo | `du` |
| Memoria GPU por pila | < 64 MB | — |

---

## 14. Pruebas de aceptación
**pytest:**

| Test | Qué verifica |
|---|---|
| `test_fits_layout` | `read_hdu_layout` coincide con los `datLoc` de §8.1 en un archivo real |
| `test_reproject_identity` | Error relativo < 1e-5 en el interior |
| `test_reproject_vs_pkg` | Contra `reproject_interp`, < 1e-4 |
| `test_lam_poly` | Contra CWAVE en todo el recorte: < 1 nm en D5, < 2.5 nm en D6 y < 6 nm en D4 |
| `test_flags_remap` | Ida y vuelta |
| `test_pm_barnard` | MJD 61041.0 → 269.446268, +4.768204 (± 0.1″) |
| `test_resolve_wise_challenge` | Devuelve `epoch_warning` |
| `test_spxf_roundtrip` | Con y sin *shuffle*, con y sin gzip |
| `test_index_dedupe` | Ningún (obs_id, det, colección) duplicado; ningún `*_cal` |
| `test_golden_3I_co2` (`slow`) | Q(CO₂) de agosto de 2025 en [0.94, 1.6]e27 |

**vitest:**
- `parseSpxf` (fixture escrito por Python);
- coordenadas (20 casos);
- `fmtSci`;
- movimiento propio frente a §12.1;
- serialización de la URL en ida y vuelta.

**Playwright** (`--trace off`):
1. Landing → "Open the sky" → Barnard: ≥ 10 cuadros, y la cruz de Gaia cambia de posición entre el primer y el último cuadro.
2. `/explore?target=wise-0855`: el espectro separado de §12.1b tiene S/N > 10 en 4.2–4.7 µm y |f| < 0.1 mJy en 0.75–3.0 µm. **No** probar "ausente en D1" con apertura: la estrella vecina está ahí.
3. Clic en un píxel (Lab) → ≥ 50 puntos de espectro.
4. Copiar la URL → contexto nuevo → el mismo estado serializado.
5. `/es` → textos en español y números con punto decimal.
6. iPhone 15 (emulado): Play y Compare funcionan; `scrollWidth ≤ innerWidth`.
7. Bloquear `api.*` → los 5 objetivos y 3I siguen funcionando.

---

## 15. Plan horario y orden de recorte

| Bloque | Hora | Entregable desplegado |
|---|---|---|
| S0 | Sáb 9:00–9:45 | Repositorio con plantillas (§5.3), monorepo, "hello" en Pages y Fly, DNS. 10 min mirando el Data Explorer de IRSA |
| S1 | 9:45–12:30 | `spxcore`: s3, fitsio, calib, cutout, flags y spxf + tests. **No** hace falta `build_index.py`: el índice ya está construido (paso 3 de §19) |
| S2 | 12:30–14:30 | `precompute_targets.py` → `static/data/targets`. Revisión visual: Barnard (F3) y WISE 0855 (D6) |
| S3 | 14:30–19:00 | Explorer Story: `SpxViewer`, `Timeline`, Epoch, Blink y Diff, `FieldNotes`, URL y búsqueda con los 5 objetivos |
| S4 | 19:00–22:00 | API en Fly: `/resolve`, `/exposures`, `/stack`, `/diff` y `/spectrum` + `SpectrumPlot` con bandas |
| S5 | 22:00–24:00 | Lab: `LayerTree`, `Inspector`, Aladin (DR1, Cube, 2MASS, Gaia) y "What changed?" |
| D1 | Dom 8:00–11:00 | Landing Plate & Ink + 3I (ficha) + atlas |
| D2 | 11:00–13:30 | Español completo, móvil, accesibilidad, presupuestos y E2E |
| D3 | 13:30–15:00 | G4 (exportar), Sum y pulido |
| D4 | 15:00–19:00 | Video de 30 s, resumen, capturas y textos de la entrega |
| D5 | 19:00–22:00 | Margen. **Congelar a las 21:00; enviar antes de las 22:00** |

**Orden de recorte si vamos atrasados:**
1. P2;
2. G4 (exportar);
3. el atlas (dejar solo 3I);
4. Sum;
5. Lab (Story basta para el reto);
6. "What changed?".

**Nunca se recortan:** los 5 objetivos, el parpadeo, Diff λ, la cruz de Gaia por época, el espectro, la URL, EN/ES ni el despliegue.

---

## 16. Entrega en Space Apps
> **Texto listo para pegar:** `docs/SUBMISSION_DRAFT.md` (inglés, con cifras verificadas y fuentes). El domingo solo hay que actualizar las URL, el video, la lista de lo construido en las 48 h y las cifras del catálogo NEO si se regeneró.

**Formulario:**
- **High-Level Summary** (EN, un párrafo): qué es, para quién, por qué importa, "102 colors", "time machine" y "comets breathe CO₂".
- **Demo:** video de 30 s, público (YouTube no listado o Vimeo).
- **Final Project:** URL del producto + repositorio.
- **Project Details:** funcionalidades; tabla de requisitos (§1); arquitectura; método y validación; qué se construyó durante las 48 h. **La declaración de la investigación previa la escribe el usuario a mano**: el agente no la redacta ni enlaza el repositorio de investigación en el producto, en su README ni en la entrega.
- **Use of AI:** se usó Claude Code (Anthropic) como asistente de investigación, código y redacción; los resultados se validaron contra datos independientes (§8.0c, §0.9c, §12.1c) y una auditoría (`docs/AUDIT.md`) corrigió varias cifras. No hay imágenes generadas por IA.
- **Space Agency Data:** SPHEREx L2 (NASA/IRSA), HiPS SPHEREx DR1 (IRSA), JPL Horizons, SBDB y SB Identification, Gaia DR3 (ESA), 2MASS y AllWISE (vía IRSA); imagen del equipo de ESA/Rosetta/NAVCAM (CC BY-SA IGO 3.0).
- **References:** las del doc 06 + Aladin Lite (Boch & Fernique 2014; Baumann et al. 2022) + Astropy (2022) + reproject.
- **Prohibido:** logos de NASA o imágenes de NASA presentadas como propias.

**Video (plantilla 0:00 / 0:02 / 0:05 / 0:10 / 0:20):**
- **0:00–0:02:** papel → "Breathing Comets" en Newsreader.
- **0:02–0:05:** "SPHEREx maps the whole sky in 102 colors, every six months."
- **0:05–0:10:** se escribe "Barnard's Star" → parpadeo con la cruz de Gaia y la flecha.
- **0:10–0:20:** Diff λ limpia el campo (antes/después); clic → el espectro se arma; corte a WISE 0855: en D1 solo la estrella de fondo, en D6 la enana Y la domina, y el espectro separado sube a 4.5 µm.
- **0:20–0:30:** 3I/ATLAS con el halo entintado en ocre → Q → "Any coordinates. Any time. breathingcomets.org".
- **Alternativa con las cifras medidas (§12.1c), si el tiempo de pantalla lo permite:** en 0:10–0:20, la figura T frente a Y (`docs/mockup/assets/browndwarfs_spherex.png`) con el texto "Methane, measured". En 0:20–0:25, "28 asteroids sized after NEOWISE · validated against NEOWISE" sobre el gráfico de validación.

---

## 17. Catálogo de errores (ya cometidos o detectados; no repetirlos)
| # | Error | Cómo evitarlo |
|---|---|---|
| 1 | Deduplicar por obs_id → se pierden 2/3 de las filas | (obs_id, detector, colección) |
| 2 | Servicio de recortes de IRSA → 503 en 2 de cada 3 peticiones | S3 por rangos con obstore |
| 3 | Anillo de 12–20 px para cometas dentro de la coma | 40–55 px |
| 4 | Gaussiana para CO₂ → χ² enorme | Modelo P/R (§8.9) |
| 5 | δ libre en cometas débiles → sobreajuste | Fijar δ en el desplazamiento instrumental. **Con DR1, D5: δ = +2.6 ± 1 nm** (−3.7 medido en QR2 con 13 cometas + 6.3 de la recalibración); en QR2 v20 era −3.7. Solo los cometas brillantes (S/N_phys > 15) llevan δ libre (error 47) |
| 6 | Un solo S/N (235P) | `snr_detect` + `σ_F/F` + `n_core` |
| 7 | C/2025 N1 duplicado de 3I; 240P mal designado | Deduplicar; `240P-B` |
| 8 | Interpolar RA cruzando 0/360 | Vectores unitarios |
| 9 | Restar épocas en crudo con el LVF | Diff λ (§8.6) |
| 10 | Saturación pintada de negro | Blanco |
| 11 | `uppercase` sobre `µ` → `M` | Mayúsculas escritas en el texto |
| 12 | Coordenadas del reto de WISE 0855 sin propagar → recorte vacío | Propagar siempre (§12.1) |
| 13 | Estirado por cuadro → el video "respira" | Percentiles de toda la pila |
| 14 | Enmascarar OUTLIER | No enmascarar |
| 15 | Aladin desde el CDN de CDS (404) | npm 3.8.2 empaquetado |
| 16 | TAP desde el navegador (sin CORS) | Solo el índice o la API |
| 17 | sb_ident en el camino crítico (18 s) | Caché y precálculo |
| 18 | Campos profundos sin límite (R Dra con 1,133) | Muestreo estratificado |
| 19 | Mapa de λ submuestreado (hasta 636 nm de error en D4) | Resolución completa; excluir 20 px de borde |
| 20 | Suponer `lam_poly` < 0.1 nm | Umbrales reales (§6.1) |
| 21 | Etiquetar el cubo de Aladin con su λ lineal | `channels.json` |
| 22 | TypeScript 7 con Kit 3.1.1 | TS 6.0.3 |
| 23 | `npx @inlang/paraglide-js init` (método viejo) | `npx sv add paraglide` |
| 24 | Swap en Fly con suspend | No configurar swap |
| 25 | DNS de `api` con proxy naranja | "DNS only" |
| 26 | Commits a nombre de Claude o con `Co-Authored-By` | Plantillas de §5.3 en el primer commit |
| 27 | Vender el espectro como exclusivo | "Inmediato", no "único" |
| 28 | `toLocaleString` en números científicos (coma decimal en ES) | `fmtSci` |
| 29 | `readPixels` en el bucle de dibujo | Leer del `Float32Array` del Worker |
| 30 | Copiar el código de `research/` en bloque | Reescribir limpio en `spxcore`, citando la fuente |
| 31 | Leer FLAGS de DR1 como `>i4` crudo (está comprimido RICE_1) | Mirar `ZIMAGE`/`ZCMPTYPE` en la cabecera; ver A.7 |
| 32 | Usar `MJD-AVG` (UTC) como TDB | Convertir con `Time(..., scale='utc').tdb` |
| 33 | Posiciones geocéntricas para objetos cercanos (hasta 14″ de error) | Vector geocéntrico − vector de la nave (A.4) |
| 34 | Prometer "alertas en tiempo real" | Datos con ~5–6 semanas de retraso y pocas visitas por objeto al año: es un censo por pasada |
| 35 | Resolver claves S3 con el datalink de IRSA (ya no devuelve QR2: pierde ~75% **sin error**) | Índice canónico `spherex_s3_keys_compact.npz` (dr1 > qr3 > qr2) |
| 36 | Cargar 1.6 M claves S3 como dict de Python (~1 GB; mató el proceso por memoria) | Arreglo `S20` ordenado + código de directorio (`searchsorted`, ~35 MB) |
| 37 | Suponer extensión `PSF` en todos los L2 (v27 de QR3 y DR1 traen `EPSF`) | Leer `PSF` (cubo, OVERSAMP=10, centros 1-based) **o** `EPSF` (tabla 21×21, 33×33, OVSMPX=5, centros 0-based) |
| 38 | Apertura sobre un objetivo con una estrella a ~1 px (WISE 0855) | Ajuste PSF conjunto con las estrellas Gaia propagadas (§12.1b) |
| 39 | Mezclar cachés de recortes v20 y v27 | Incluir la versión (`v20`/`v27`) en la clave de caché |
| 40 | Emparejar las filas de Horizons `TLIST` por posición: **Horizons las devuelve ordenadas por tiempo** (con pedidos desordenados se mide cielo vacío; S/N 0.8 en vez de 12) | `CAL_FORMAT=JD` y emparejar por JD (tolerancia 1e-5 d) |
| 41 | Leer la tabla EPSF entera (3.8 MB) por recorte | Calcular la fila (malla 21×21 uniforme, x-rápido) y leer 8.7 kB por rango |
| 42 | Confiar en la posición interpolada de efemérides cada 3–6 h para NEO a < 0.05 AU (errores de hasta 3°) | Posición precisa de Horizons por exposición; descartar si el recorte cae fuera del detector |
| 43 | Fotometría de apertura con anillo en λ largas (sesgo +0.08–0.18 mJy por fuentes débiles no resueltas) | Restar el cielo de otras visitas a igual λ con el mismo modelo (PSF con estela) |
| 44 | Integrar la ePSF sobre el píxel (doble convolución: flujo 9–12% bajo) | Muestrearla en el centro del píxel × osamp² (`PSF_MODE="sample"`) |
| 45 | Multiplicar el flujo ePSF por una corrección de apertura (las alas se cuentan dos veces: W2 +10%, bandas no uniformes) | La calibración absoluta de SPHEREx es por ePSF: el flujo ePSF muestreado ya es el calibrado (`APPLY_APCOR = False`) |
| 46 | Comparar con filtros de catálogo con una media ponderada por 1/σ² dentro del filtro (sesgo de hasta 17% por la pendiente espectral) | Ley de potencias en el filtro evaluada en λ_iso |
| 47 | Ajustar bandas de gas en DR1 con δλ = 0 fijo (D5/D6 se corrieron +6.3 nm; en 3I: χ² 114 y flujo −8%) | Cometas brillantes: δ libre (±12 nm). Débiles: δ fijo en +2.6 nm (D5, DR1; error 5). D6/CO: libre en los brillantes; en los débiles, +6.3 nm respecto de lo supuesto en v20 hasta medirlo |
| 48 | Astrometría absoluta con el WCS de cada exposición (paralaje −14%, μ falso de ~35 mas/año) | Diferencial: restar el residuo medio de estrellas Gaia de control por exposición |
| 49 | Suponer la malla EPSF de 21×21 en todos los detectores: **D3 es 11×41 (451 filas)** y se leía la zona equivocada en el 96% de los recortes (±3.6% de ruido, hasta 12%) | `spherex_psf.epsf_row(nfilas, x, y)`; comprobar `XCENTER/YCENTER` de la fila leída |
| 50 | Citar el error formal de un ajuste con exposiciones correlacionadas por visita (paralaje ±12 → ±20 mas; período de R Dra ±10 d con 1.9 ciclos) | Bootstrap por visita; con < 2 ciclos no se cita un período propio |
| 51 | Presentar como validación una mediana que se ajustó (η contra NEOWISE → mediana 1.02) | Citar la dispersión fuera de muestra (−33%/+36%) |
| 52 | Validar con una sola muestra y citar su cifra como universal (0.965 en el NEP; 0.998 en otros dos campos) | ≥ 3 campos y guardar la identidad de las estrellas |
| 53 | Comparar con un catálogo sin mirar si la fuente está mezclada (AllWISE W2 de WISE 0855: 13.70) y sintetizar la banda con un promedio plano | Curva RSR real y fotometría con movimiento propio (CatWISE2020) o de la literatura |
| 54 | Scripts que ejecutan código de un directorio temporal (`exec(open("/tmp/…/fit_pairs.py"))`) | Módulo versionado (`research/feasibility/neatm.py`) |

---

## 18. Pendientes y preguntas abiertas
1. **[Sábado S0]** Elegir la marca tipográfica (§10.3) y revisar el Data Explorer de IRSA (10 min).
2. **[Sábado S2]** Verificar con datos reales la visibilidad esperada (§12.1) antes de escribir los textos de los Field notes.
3. **[Antes de afirmar novedad]** Comparar el censo con el catálogo de 68 cometas de `bumhooLIM/spherex-comet` (A.2) y releer ADS.
4. ~~**[DR1]** Bits 26 y 28~~ → resuelto en §8.0b (BLOOM, SNOWBALL, HALO y SATELLITE_HALO).
5. **Compañeros:** si alguien se une, repartir (a) visor y Explorer, (b) API y pipeline, (c) landing, contenido y video.

## 19. Instrucciones paso a paso para el agente constructor (orden exacto)

> Lee §0 (reglas), §2 (producto) y §5.3 (plantillas de git) antes de empezar. Cada paso termina con **commit + push a `main`** y una verificación concreta. Si un paso falla dos veces, anótalo en `docs/STATUS.md` del repositorio nuevo y sigue con el siguiente. **No te quedes trabado.**

### Sábado
1. **(9:00) Repositorio y plantillas.**
   - Crear `sebastianvelace/breathing-comets` (§5.2) y copiar: las plantillas de §5.3 (`CLAUDE.md`, `.claude/settings.json`, `scripts/git-identity.sh`, `.githooks/`), `docs/BUILD.md`, `docs/SUBMISSION_DRAFT.md`, `data/derived/test_targets.json` (→ `targets.json`), `data/derived/spherex_channels.json` (→ `channels.json`), `data/export/` (→ `static/data/`), los índices `data/derived/spherex_exposures_d456_dr1_qr3.parquet` y `spherex_s3_keys_compact.npz`, `research/spherex_s3.py`, `research/spherex_psf.py` y `tests/test_reference.py`.
   - Ejecutar `sh scripts/git-identity.sh` y hacer el primer commit.
   - **Verificar:** `git log --format='%an <%ae>'` → `sebasvelace <sebastianvelace@gmail.com>`.
2. **(9:15) Esqueletos desplegados.**
   - SvelteKit (§5.2) → Cloudflare Pages con el dominio `breathingcomets.org`.
   - FastAPI `/v1/health` → Fly `breathing-comets-api` (§4, `fly.toml`, Dockerfile, volumen `spx_cache`).
   - DNS `api` en modo "DNS only" → `fly certs add api.breathingcomets.org`.
   - **Verificar:** `curl https://api.breathingcomets.org/v1/health` → `{ok:true}` y la home responde.
3. **(9:45) Datos: NO recalcular lo que ya está hecho.** Todo lo siguiente está en este repositorio (`data/derived/`) y se copia tal cual al repo nuevo:
   - **Índice de exposiciones:** `spherex_exposures_d456_dr1_qr3.parquet` (809,593 filas D4–D6 de DR1+QR3; D1–D3 usan la huella de su par, §8.0b). Reemplaza al `build_index.py` de 1–2 h. Si hace falta refrescarlo: `research/24_obscore_index.py` (≈ 11 min, probado el 14 nov: regenera las mismas 809,593 filas; escribe también el completo D1–D6 de 74 MB, que no se versiona).
   - **Claves S3:** `spherex_s3_keys_compact.npz` (1.63 M, dr1 > qr3 > qr2). Refrescar con `research/22_s3_key_index.py` (< 1 min). **No usar el datalink de IRSA** (error 35).
   - **Resultados ya exportados:** **copiar `data/export/` → `static/data/`** (§6.10): catálogo NEO, validación, los 5 objetivos y calibración. No hay que convertir nada. Si se toca un CSV de `data/derived/`, regenerar con `research/28_export_static.py`.
   - **Calibración del espectro:** `spherex_psf_aperture_correction.json` + `spectrum_validation_2mass_wise.csv` (§8.0c).
   - **Regenerar el catálogo NEO (< 1 min, sin red):** `python research/feasibility/neo_fit_psf.py && python research/feasibility/neo_robust_tiers.py && python research/feasibility/neo_make_catalog.py`. **Verificar:** 28 A+B y 2025 YH5 en 0.61–1.36 km. **No** volver a correr la fotometría (`neo_measure_all.py`): necesita `objects.csv`, `val_hits.parquet`, el índice viejo de QR2 y los mapas CWAVE, que no están versionados.
4. **(10:00–12:30) Paquete `spxcore`** (§8): s3 (índice compacto), fitsio (FLAGS comprimido, A.7; PSF **o** EPSF, error 37), calib (CWAVE completo), cutout, flags (máscara oficial `HARD_ES21`, §8.0b), spxf, sky (Diff λ), ephem (vector de cabecera + TDB, A.4) y photometry (**ePSF muestreada, sin corrección de apertura**, §8.0c). Portar `research/spherex_s3.py` y `research/spherex_psf.py`, que ya están validados.
   - **Verificar con pytest** (§14), incluido `test_fits_layout` en un archivo QR2 (cubo `PSF`, FLAGS sin comprimir) **y** en uno DR1/QR3 v27 (`EPSF`, FLAGS comprimido).
   - **Portar también `tests/test_reference.py`** (11 pruebas rápidas + 3 con red, `pytest -m network`). Fijan: la clave S3 canónica (DR1 > QR3), la máscara oficial (OVERFLOW y OUTLIER no se enmascaran), la ePSF muestreada y normalizada, la recuperación de flujo sin `apcor`, la conservación del flujo con estela, el paquete `data/export`, las etiquetas de los 102 canales, la lectura de una fila de EPSF (21×21 y la malla 11×41 de D3) y el +6.3 nm de D5 en DR1. **Las 14 pasan en la investigación.** Al portarlas, ajustar las rutas `data/derived/…` y `research/…`.
5. **(12:30–14:30) Precálculo de los 5 objetivos** (pilas SPXF de §6.1 y manifiesto de §6.2; las cifras ya están en `data/export/targets/`, §6.10) → `static/data/targets/…`.
   - **Verificar a ojo:** Barnard (cruz de Gaia por época) y WISE 0855 (en D6 la mancha es ~4× más brillante, relativa a la estrella G=16.3, que en D1–D3; el espectro separado coincide con `data/derived/wise-0855_deblended.csv`).
6. **(14:30–19:00) Explorer en modo Story** (§9): SpxViewer (WebGL2), Timeline, Epoch/Blink/Diff, FieldNotes, URL ⇄ estado y SearchBar con los 5 objetivos. **Pruebas E2E 1, 2 y 4.**
7. **(19:00–22:00) API en vivo:** `/resolve`, `/exposures`, `/stack`, `/diff` y `/spectrum` (NDJSON) + `SpectrumPlot` con bandas (§12.3). **Prueba E2E 3.**
8. **(22:00–24:00) Modo Lab + Aladin** (§9.5, §9.7): HiPS DR1, cargando Aladin 3.8.2 como **módulo ES** (`import()`). El canal se elige con `setFrequency` (fórmula de §0.9b; **no** `setSliceNumber`). Más 2MASS, Gaia y LayerTree.

### Domingo
9. **(8:00–10:00) Small-Body Lab: datos → páginas.**
   - **`/neo`:** tabla, gráfico D frente a H con líneas de albedo, validación contra NEOWISE (gráfico D_SPHEREx frente a D_NEOWISE en escala log con la línea 1:1) y nota de método (§0.4b).
   - **Cada NEO** enlaza al Explorer con `track=<pdes>`.
   - **Prohibido** mostrar un resultado sin su intervalo 16–84%, el piso de ±35% y el nivel (A/B/provisional).
10. **(10:00–11:30) Landing Plate & Ink** (§10.5) con el titular Small-Body Lab:
    - §0 "After NEOWISE" (cifras: 652 NEO post-NEOWISE con H < 22, ninguno con diámetro en la base de JPL; **28 tamaños térmicos (11 A + 17 B, 7 PHA)** de 86 candidatos; validación contra NEOWISE en 50 NEO, ±35% por objeto; ejemplo: 2025 YH5, PHA de 0.6–1.4 km y oscuro, *preliminar, una sola visita*);
    - "Who's breathing?" (3I, 29P);
    - Blink, Diff λ, 102 colores, Field notes y validación.
11. **(11:30–13:30) Ficha de 3I y de 29P + `/method`** (incluye las tablas de validación de NEO y cometas). Español completo y móvil.
12. **(13:30–15:00) Pruebas:** E2E 5–7, presupuestos de rendimiento (§13) y accesibilidad.
13. **(15:00–19:00) Entrega** (§16): video de 30 s (incluir 2 s del gráfico de validación contra NEOWISE y un NEO post-NEOWISE cruzando el campo), resumen y "Use of AI".
14. **(19:00–21:00) Margen y congelamiento.** Enviar antes de las 22:00.

### Orden de recorte del Small-Body Lab (si falta tiempo)
1. Activity Watch (Apéndice A) completo → solo 29P como ejemplo.
2. `/neo` con menos objetos: solo los de nivel A.
3. **Nunca recortar** la validación contra NEOWISE: sin ella no se publica ningún tamaño.

---

---

## Apéndice 0. Plan complementario principal: "After NEOWISE": tamaños de asteroides cercanos a la Tierra con SPHEREx

*Investigado y cuantificado el 12 nov 2026. Es el diferencial de nivel profesional. Se construye después del núcleo de §15. Comparte la tubería con Activity Watch (Apéndice A): los dos forman un "Small-Body Lab".*

### 0.1 La oportunidad (verificada)
- **El vacío:** **NEOWISE terminó el 8 ago 2024** y **NEO Surveyor se lanza ~sep 2027**. Mientras tanto no hay ningún observatorio espacial infrarrojo midiendo **la emisión térmica de asteroides**, que es la medida que da su **tamaño** con ~10–20% de precisión. Desde tierra, el tamaño sale del brillo (H) suponiendo un albedo, con un error de factor ~2–3.
- **SPHEREx lo hace sin proponérselo:** observa a ~90° de elongación (geometría similar a NEOWISE) y sus detectores D5 y D6 (3.8–5.0 µm) captan la emisión térmica.
- **Datos JPL SBDB ✔:** desde el 8 ago 2024 se descubrieron **652 NEO con H < 22** (D ≳ 140 m, el umbral de defensa planetaria), **93 de ellos PHA** (657 y 95 el 14 nov). **Ninguno tiene diámetro en SBDB** (verificado). No se pudo revisar la literatura: decir "none has a diameter in JPL's database", no "none has an infrared size".

### 0.2 Factibilidad medida ✔ (efemérides Horizons vistas desde SPHEREx cada 6 h + índice D5/D6 + NEATM)
- **Efemérides:** se pidieron para los 652 (107 s con 6 hilos).
- **Cobertura:** 628 caen en exposiciones D5/D6.
- **S/N térmico ≥ 5 esperado por exposición** (NEATM con pV = 0.14 y η = 1.4; 5σ de 18.5 AB en D5 y 17.5 AB en D6):
  - **104 objetos** con al menos una exposición;
  - **86** con incertidumbre de órbita (3σ, Horizons) ≤ 6″ (1 px) en ese momento → **27 PHA**;
  - **53** con ≥ 10 exposiciones de S/N ≥ 5.
- **Tamaños de la muestra:** 0.14–0.67 km (mediana 0.23 km).
- **Archivos:** `data/derived/post_neowise_neo_spherex_candidates.csv` (los 104, con S/N, Δ, ángulo de fase, tasa de movimiento, estela e incertidumbre) y `…_all.csv` (los 628).
- **Mejores casos:** 2025 NH3 (PHA, S/N ~300), 2026 NT2 (PHA, ~175), 2025 XJ (PHA, ~100), 2025 YK9 (39 exposiciones de S/N ≥ 5, estela de 1.3 px) y 2025 QR1 (PHA, **135** exposiciones de S/N ≥ 5).
- **Estela (motion trail):** mediana de 2.3 px en 113.58 s; los encuentros más cercanos llegan a 8–16 px. **Hace falta fotometría con apertura alargada** (cápsula a lo largo del vector de movimiento). Las exposiciones más lejanas, con menos estela, también suman.

### 0.3 La física (lo que lo hace profesional)
1. **NEATM** (Harris 1998):
   - T_ss = [S(1−A)/(η ε σ r²)]^{1/4}, con A = q·pV y q = 0.290 + 0.684·G;
   - emisión del hemisferio iluminado con T = T_ss·cos^{1/4}(θ), integrada hacia el observador con el ángulo de fase α;
   - ε = 0.9 y G = 0.15.
   - Implementación de referencia: el script de factibilidad (malla de 61×121 facetas). Para el producto, malla de ≥ 91×181.
2. **Parámetros:** D, η y, cuando se pueda, pV.
3. **η medido, no supuesto ✔ (≈):** el color térmico F(3.8)/F(5.0) cambia ~20% entre η = 1.0 y 1.2 (0.052 → 0.044 para un MBA de 10 km a 2.5 au). Con ~30 canales en 3.8–5.0 µm, **SPHEREx mide la pendiente de Wien y con ella η**. NEOWISE, después de agotar su criogenia (solo W1 y W2), **fijaba η = 1.4** en NEO.
4. **Albedo sin depender de H:** reflejada ∝ p_IR·D² y térmica ∝ D²·f(T). El cociente de flujo reflejado (D2 a 1.1–1.65 µm o D3 a 1.64–2.42 µm) sobre térmico (D5 o D6) da el albedo **sin usar H**, que en NEO nuevos es incierta en ±0.3–0.5 mag.
5. **Inmune a la rotación:** D1/D4, D2/D5 y D3/D6 ven **el mismo cielo al mismo tiempo** ✔ (verificado: mismo `t_min` y centros a ~0.02°). Los cocientes de una misma exposición cancelan la curva de rotación (método publicado por Ivezić et al. 2022, Icarus: **citarlo**; nosotros lo **aplicamos a datos reales**).
6. **Geometría:** posición = vector geocéntrico (Horizons `500@399`) − vector de la nave de la cabecera, con la hora en TDB (A.4). Para NEO cercanos, la paralaje Tierra–SPHEREx es grande (~10″ o más): **obligatorio**.

### 0.4 Validación (como en los cometas)
- **Catálogo NEOWISE v2 en IRSA TAP ✔:** tabla `neowisesbpropv2`, con columnas `diameter`, `diameter_err`, `v_albedo`, `ir_albedo`, `beaming_param`, `fit_code`, `type`…
  - Contenido: 1,523 NEO, 159,990 del cinturón principal, 52 centauros, 1,860 troyanos y 1,089 Hildas.
  - η ajustado en 580 NEO y 71,610 del cinturón principal.
- **Prueba:** la misma tubería sobre NEO y asteroides grandes **con** tamaño de NEOWISE que SPHEREx haya observado → comparar D, pV y η. **Meta: mediana |ΔD/D| ≤ 15%** y dispersión de ~20% (la precisión típica de NEATM).
- **Prueba piloto ✔ (12 nov; datos reales de SPHEREx, sin ajustar nada):**
  - **Muestra:** 1,182 NEO con tamaño de NEOWISE → efemérides vistas desde SPHEREx → **971 caen en exposiciones D5/D6**; 111 tienen ≥ 1 exposición con S/N esperado ≥ 10 y estela ≤ 1.5 px (**5,172 exposiciones**).
  - **Medición:** se midieron **159 exposiciones de 10 NEO** con S/N esperado de 20–600 y estela ≤ 1 px.
  - **Resultados:**

    | Medida | Resultado |
    |---|---|
    | Posición | Centroide a **0.15 px** (mediana) de la predicción: **la geometría funciona** |
    | Flujo | Medido/predicho (NEATM con D, pV y η de NEOWISE; apertura r = 4 px): **mediana 1.27**. En diámetro equivale a **D_SPHEREx/D_NEOWISE = 1.12 (mediana)**, con **7 de 10 objetos dentro de ±25%** (0.76–1.43) |
    | Dispersión dentro de una visita | **29%**, como predice la rotación (~0.2–0.3 mag, Ivezić 2022). **Justifica usar los cocientes de pares simultáneos** |
    | Bit TRANSIENT | Píxeles marcados en la apertura en 22/159 exposiciones, **sin pérdida de flujo visible** (mediana 1.33 frente a 1.23). El riesgo de que el filtro a bordo "coma" flujo **no aparece en movimientos lentos** (estela ≤ 1 px); hay que repetir la prueba con NEO rápidos |
    | Bit OUTLIER | Aparece en casi todos (marca el movimiento): confirma no enmascararlo |
    | Saturación | 1943 Anteros (S/N esperado de ~2,000) tiene dispersión enorme. **Excluir lo que pase de ~10 mJy en D5/D6** o revisar OVERFLOW |

  - **Sesgo restante (+12% en D):** puede venir de η fijo, de la parte reflejada (cociente p_IR/pV = 1.3 supuesto), de la falta de corrección de apertura o de los errores propios de NEOWISE (~10–20%).
  - **El producto debe** ajustar D y η por objeto con la pendiente térmica y con los pares simultáneos, en vez de fijarlos.
  - **Archivos:**
    - `data/derived/neo_validation_pilot_photometry.csv`;
    - scripts en `research/feasibility/neo_validation_{fetch,match,photometry}.py` (efemérides, cruce + predicción NEATM, fotometría por S3 + Horizons `TLIST` precisos).


### 0.4b Método validado (12 nov 2026, iteraciones con datos reales) ✔ — *histórico: el método vigente es el de §0.9c (PSF con estela, η = 1.48 ± 0.44)*
Esto es lo que el pipeline **debe** implementar. Sale de 6 iteraciones medidas, no de supuestos.

**Pasos por objeto:**
1. **Posiciones precisas:** Horizons `CENTER='500@-163182'` con `TLIST` en la hora media de cada exposición (`MJD-AVG` en UTC; la API acepta JD UT con `EXTRA_PREC=YES`). Error medido: centroide a 0.15 px de la predicción.
2. **Selección de exposiciones:**
   - estela ≤ 3 px (régimen validado; > 3 px es experimental);
   - sin OVERFLOW en la apertura;
   - flujo predicho < 10 mJy (por encima hay saturación: 1943 Anteros);
   - a ≥ 10 px del borde del recorte.
3. **Fotometría:** r = 3–4 px; fondo con mediana recortada en un anillo de 8–14 px que excluye TRANSIENT; Ω_pix nominal; mJy = Σ(I − fondo)·Ω·10⁹.
4. **Resta de cielo estático a igual λ** (la misma técnica Diff λ):
   - para cada exposición, K = 8 exposiciones del mismo detector, de otra visita (|Δt| > 2 d), que cubran la posición, con λ más cercana;
   - para elegirlas, λ sale del mapa CWAVE v5 en el píxel aproximado, usando la huella del detector pareado;
   - se mide la misma apertura, se ajusta una recta en λ con un recorte de 3σ y se resta.
   - **Impacto medido:** el fondo es ~6% del flujo térmico (D5/D6), pero **~48% del flujo corto** (D2/D3; hay muchas estrellas). **Sin esta resta, los pares no sirven.**
5. **Pares simultáneos:**
   - D2↔D5 y D3↔D6 (mismo `obs_id`, mismo `t_min`, mismo cielo ✔);
   - cociente y = ln(F_L/F_S), modelado con NEATM(η) + reflejada(p) en los dos λ. D se cancela, y la curva de rotación también.
   - Malla: η ∈ [0.5, 3.0] en pasos de 0.05 y p ∈ [0.03, 1] (60 valores log); χ² con un tope de 16 por punto (robusto).
   - **Se acepta η_pares** si el intervalo Δχ² ≤ χ²_min/(n−2) mide ≤ 0.5 y no toca el borde. Si no, **η = 1.25 ± 0.30** (prior calibrado con 55 NEO).
6. **Diámetro:** de la **amplitud térmica** (canal largo), con η fijo del paso 5; pV = (1329/D)²·10^(−0.4H) iterado (5–6 iteraciones); **mediana** sobre exposiciones, que promedia la rotación.
7. **Incertidumbre:** Monte Carlo (≥ 60) sobre η (σ del paso 5), bootstrap de exposiciones (rotación) y calibración (±2.5% en flujo) → percentiles 16, 50 y 84 de D.
8. **No usar el albedo del cociente de pares como resultado** (todavía): el modelo reflejado (Sol como cuerpo negro de 5778 K y p plano) **satura p** en ~1. Hay que calibrarlo con espectros solares reales (p. ej. CALSPEC) y reflectancias NIR por tipo antes de publicar albedos. El pV que se reporta sale de H y D.

**Resultados de validación contra NEOWISE (`neowisesbpropv2`):**

| Prueba | N | Resultado |
|---|---|---|
| Calibración absoluta (asteroides grandes del cinturón principal, η de NEOWISE con W3/W4, D 12–30 km) | 10 objetos, 159 exp. | flujo medido/predicho **0.93** → D ratio **0.97** |
| η efectivo (D de NEOWISE fijo) | 55 NEO | mediana **1.25**, σ robusta 0.30. En los 24 con η de NEOWISE: **correlación 0.84** y diferencia mediana **−0.06** |
| D con η constante (validación cruzada de 5 particiones) | 55 NEO | **mediana 1.005**, σ_ln robusta 0.30; 28/55 dentro de ±20%; 38/55 dentro de ±30% |
| D híbrido (η de pares con cielo restado + amplitud) | 5 NEO | 0.82, 1.18, 1.09, 1.02, 1.00 → **5/5 dentro de ±20%**. η de pares frente a NEOWISE: 0.90/0.89 y 0.70/0.75 |
| Asteroides rápidos (estela 1.5–12 px, apertura en cápsula) | 72 exp. | **0 píxeles TRANSIENT** en las cápsulas; el cociente **no cae** al alargarse la estela (0.54 → 0.68 → 1.2 → 2.0). Dispersión alta entre objetos: no concluyente, pero **no hay señal** de que el filtro a bordo "coma" flujo |
| η(α) lineal (Wolters 2008 o ajustado) | 55 NEO | **no mejora** frente a η constante; no usarlo |

**Lecciones de código (errores reales de hoy):**
- `iterrows()` convierte claves numéricas a float (`"214.0"`): leer con `dtype={"key": str}`.
- **No nombrar variables `c`, `h`, `sig`, `k`** en módulos que usan constantes físicas con esos nombres (dos bugs hoy).
- Los mapas CWAVE vienen big-endian: `.astype(np.float32)` antes de indexarlos con pandas.
- Columnas de Horizons en CSV: `R.A._(ICRF)`, `DEC_(ICRF)`, `dRA*cosD`, `d(DEC)/dt` (″/h), `r`, `delta`, `S-T-O` (ángulo de fase), `RA_3sigma` y `DEC_3sigma` (″).

**Scripts de referencia:** `research/feasibility/neo_*.py` (medición de pares, resta de cielo, ajustes y diagnóstico).
**Datos:** `data/derived/neo_validation_*.csv` y `mba_control_photometry.csv`.

### 0.9 Primeros tamaños de NEO post-NEOWISE (12 nov 2026) ✔: resultado real y lecciones — *superado por §0.9c (catálogo v2)*
**Muestra:** 11 candidatos con ≥ 10 exposiciones buenas, 308 pares medidos y cielo restado.

**Lecciones:**
- **El S/N real por exposición fue 1–5,** no ≥ 5 como predecía la selección (que suponía pV = 0.14, η = 1.4 y la profundidad nominal).
- **El cielo de fondo pesa:** 46% del flujo térmico y 87% del corto (mediana).
- **η de pares:** no se pudo en ninguno (corto dominado por el cielo) → todos usan el prior 1.25 ± 0.30.
- **Estimador correcto con S/N bajo:** **ajuste lineal ponderado de la amplitud** (D² = Σ w F M / Σ w M², con w = 1/(σ² + (0.25 F)²)). **No** la mediana de los D por exposición, que se sesga con el ruido. Bootstrap + η ~ N(1.25, 0.30) + 2.5% de calibración.
- **Criterio de publicación:**
  - **A:** S/N_total ≥ 10;
  - **B:** 5–10, con nota;
  - **C:** < 5, **no publicar**.

**Resultado** (`data/derived/post_neowise_neo_first_sizes.csv`):

| Calidad | Objeto | D (km) [16–84%] | pV | D solo con H (pV = 0.14) | Nota |
|---|---|---|---|---|---|
| **A** | **2025 YH5** (Apolo, **PHA**, descubierto el 2025-12-20; **JPL no tiene tamaño**, solo H = 19.77) | **0.79 [0.58–0.96]** | **0.035** (muy oscuro) | 0.40 | Las 5 variantes (con/sin cielo, D5/D6, poco fondo) dan 0.81–0.96 |
| B | 2025 GM1 | 0.34 [0.26–0.41] | 0.14 | 0.34 | — |
| B | 2026 KX | 0.22 [0.17–0.27] | 0.25 | 0.29 | — |
| B* | 2025 YK9 | 0.27 [0.23–0.32] | 0.73 | 0.62 | **Dudoso:** el cielo es 91% del flujo; pV alto poco físico |
| C | 2025 UZ4, 2026 JV4, 2025 UU3, 2026 GU, 2025 QR1, 2025 NT1, 2025 ST20 | — | — | — | S/N_total < 5 |

- **Lectura:** 2025 YH5 sería **la primera estimación de tamaño** de un PHA de ~0.8 km. Es **dos veces más grande** de lo que sugiere su brillo, porque es muy oscuro, y eso es relevante para defensa planetaria.
- **Presentarlo como "preliminary, single-band thermal estimate with η prior"**, nunca como descubrimiento.

**Rendimiento esperado revisado:** de los 86 candidatos, **~10–25** llegarían a S/N_total ≥ 5 con el método actual (≈ 30–35% de los 11 probados). Para subirlo el sábado:
1. usar **todas** las exposiciones, no solo ≤ 60 con estela ≤ 1.5 px: las de estela 1.5–3 px con apertura en cápsula;
2. **fotometría por ajuste de PSF** (extensión PSF/EPSF de cada L2) en vez de apertura: ganancia típica ~1.3–1.5× en S/N con señal débil;
3. sumar los 6 detectores donde haya térmico: D4 cerca de 3.5–3.8 µm aporta en NEO a r ~1 au;
4. **K = 12** referencias de cielo en vez de 8 (menos ruido en la resta).

### 0.9b Fotometría con PSF (12 nov 2026) ✔: S/N ×1.46

- **Implementación:** `research/spherex_psf.py`.
  - `cutout_psf()` lee las HDU IMAGE, FLAGS y VARIANCE junto con la zona de PSF más cercana. Hay 121 zonas (XCTR_i/YCTR_i), con OVERSAMP=10.
  - `psf_model()` desplaza la PSF sobremuestreada, la promedia a lo largo de la traza del objeto en movimiento y la rebina 10×10.
  - `psf_photometry(c, R=4.0)` ajusta por mínimos cuadrados lineales ponderados por 1/varianza la amplitud de la PSF más un fondo constante.
- **Resultado en los mismos cortes de los NEO:**
  - Mediana de S/N por exposición: 13.5 con apertura y 19.7 con PSF, es decir ×1.46.
  - Cociente de flujo PSF/apertura: 0.92.
  - Fracción de cielo residual: ≈ 0.
- **Uso:** el builder debe usar el ajuste con PSF para la amplitud térmica. Los niveles de calidad (A ≥ 10, B 5–10, C < 5) se mantienen.
- **Lecciones de construcción (prototipo local):** Aladin Lite 3.8.2 se distribuye como módulo ES y hay que cargarlo con `import()`. Su wasm indexa el cubo HiPS de SPHEREx linealmente en frecuencia. Para mostrar el cuadro *i* se usa `setFrequency({value: fmin + (i+0.5)/102·(fmax−fmin), unit:"Hz"})`, con fmin = c/5.009 µm y fmax = c/0.743 µm. `setSliceNumber` muestra el canal equivocado.

### 0.9c Catálogo v2: 28 tamaños térmicos post-NEOWISE (12–13 nov 2026) ✔

**Esto reemplaza a §0.9 como resultado principal:** `data/derived/post_neowise_neo_sizes_v2.csv`.

- **Pipeline** (`research/feasibility/neo_measure_all.py` → `neo_fit_psf.py` → `neo_robust_tiers.py`), sobre los 86 candidatos (incertidumbre orbital < 6″):
  1. Exposiciones D5/D6 con S/N predicho ≥ 3, estela ≤ 15 px y F < 10 mJy, hasta 30 por objeto: **1,497**.
  2. Posición de Horizons (observador −163182) en el inicio, centro y fin de cada exposición, **emparejada por JD** (error 40).
  3. PSF/EPSF con estela (`spherex_psf`, `nsteps` = 3·estela) y la misma PSF con estela en 8 exposiciones de otras visitas a la λ más cercana. El cielo se ajusta lineal en λ y se resta.
  4. Ajuste lineal ponderado de la amplitud térmica (NEATM + reflejada), con un término de rotación del 25%, **η = 1.48 ± 0.44** y Monte Carlo para D16–D84. Fotometría: ePSF muestreada, sin corrección de apertura (§8.0c). **Solo exposiciones con estela ≤ 3 px.**
  5. Niveles de calidad: **A** con S/N ≥ 10; **B** con S/N 5–10. Ambos requieren ≥ 8 exposiciones, χ²ν < 3 y que al quitar cualquier visita D quede dentro de ±25% (los de una sola visita no admiten esta prueba: pasan y llevan `single_visit = True`; son 6 de los 28, incluido 2025 YH5). **Provisional** para el resto con S/N ≥ 5. **C** no se publica.
- **Resultado:**
  - 1,453 exposiciones medidas, 62 objetos ajustados.
  - **28 tamaños robustos (11 A + 17 B), 7 de ellos PHA**, más 6 provisionales. El piloto (§0.9) tenía 4. Con la máscara del Explanatory Supplement (§8.0b) el resultado es igual: misma mediana de D, desviación máxima 12%, y solo un objeto cambia de nivel.
  - Ejemplos (versión final): 2025 YH5 (PHA) 0.95 km [0.61–1.36], pV 0.024; 2026 HB9 0.79 km, pV 0.016, 3 visitas; 2025 GM1 0.42 km, 7 visitas; 2024 WC15 (PHA) 0.29 km, 7 visitas. Las tres revisiones de fotometría del 13 nov movieron D +2%, +2% y +2% en mediana sin cambiar ningún nivel: el catálogo es robusto a la calibración porque η se recalibra contra NEOWISE con la misma fotometría.
- **Comprobación de población:** pV mediano 0.18 (NEOWISE NEO: 0.14). La fracción con pV < 0.03 es 10% (NEOWISE 13%) y con pV > 0.3 es 14% (19%). Los objetos oscuros son plausibles. Se marcan con "revisar H", porque el D térmico no depende de H y el pV sí.
- **Validación con PSF y cielo restado** (`neo_validation_cv50_psf.csv`, 50 NEO con D de NEOWISE, validación cruzada en 5 particiones):
  - mediana de D/D_NEOWISE **1.001**;
  - σ_ln robusta 0.36 (con apertura, 0.30);
  - 22/50 dentro de ±20%.
  - **Versión final (13 nov, ePSF muestreada sin corrección de apertura, máscara oficial):** η = 1.48 ± 0.44; mediana 1.020; σ_ln robusta 0.39; 21/50 dentro de ±20%. La apertura sin resta de cielo da 0.30 en estos NEO brillantes: la PSF con cielo restado se usa porque permite medir objetos débiles, no porque mejore cada tamaño.
  - **La PSF no mejora la exactitud por objeto** (el límite lo ponen η y la rotación); **mejora el rendimiento**: S/N por objeto ×2 en objetos débiles. El η calibrado depende del estimador y de la fotometría: 1.48 para este ajuste lineal con ePSF final (1.25 era para la mediana de log q con apertura).
- **Validación de estelas** (`neo_validation_trail_psf.csv`, NEO de NEOWISE, flujo medido/predicho con η = 1.48; fotometría final): ≤ 1.5 px: 1.04; 1.5–3 px: 1.05 (17 objetos); 3–6 px: 0.91 (5); 6–10 px: 0.64 (1). **Regla: tamaños solo con estela ≤ 3 px.** Con 3–6 px, como mucho "provisional".
- **Error que comunicar:** D16–D84 del Monte Carlo (estadístico + η), **más un piso del 35% por objeto** según la validación (σ_ln 0.39 contra NEOWISE, que a su vez tiene ~10–20% de error propio). En la ficha: "±30% (validado contra NEOWISE en 50 objetos)".
- **Scripts (reproducibles desde el repo):** `neo_fit_psf.py` → `neo_robust_tiers.py` → `neo_make_catalog.py`, sin argumentos, parten de `post_neowise_neo_meas_psf.csv` y regeneran el catálogo idéntico (< 1 min). El modelo vive en `research/feasibility/neatm.py`. Solo `neo_measure_all.py` (la fotometría) necesita insumos no versionados.
- **Lectura honesta de la validación:** la mediana ≈ 1 es por construcción; con S/N < 8 (12 de los 28) la validación tiene solo 8 objetos y salen −32%. 2025 YH5: D = 0.61 km con η = 1.0 y 1.41 km con η = 2.0 (pV 0.06–0.01): decir "0.6–1.4 km, oscuro", no "muy oscuro".
- **Para el producto:** usar `post_neowise_neo_sizes_v2.csv` tal cual en `/neo` (A, B y provisionales con su etiqueta; C oculto). Columnas: `n`, `visits`, `chi2nu`, `jk_min`, `jk_max`, `trail_med`, `tier`, `pha` y `flag`.

### 0.5 Competencia y novedad (honesto)
- **El equipo de Sistema Solar de SPHEREx** (Lisse, Bauer, Kim, Lim y otros; LPSC 2024 #2039 y LPSC 2026 #1833) planea un catálogo con tamaño, albedo y composición de ~10⁵ asteroides. A marzo de 2026 solo había resultados preliminares (3I, 171 Ophelia y la luz zodiacal). **No hay tabla de objetos del Sistema Solar en IRSA TAP ✔** (12 nov 2026).
- **Nuestro aporte:**
  1. **la primera herramienta pública y abierta** con tamaños térmicos de NEO **descubiertos después de NEOWISE** (relevancia para defensa planetaria **ahora**);
  2. η medido a partir de la pendiente térmica;
  3. albedo independiente de H con pares simultáneos;
  4. validación pública contra NEOWISE.
- **No decir "descubrimos";** decir "first openly available thermal-infrared size estimates".

### 0.6 Producto
- **Landing:** "§0 After NEOWISE." Una frase: "NEOWISE went dark in August 2024. Since then, 652 near-Earth asteroids larger than ~140 m have been found — none has an infrared size. SPHEREx saw many of them." Una placa con un NEO real cruzando el campo (pila con `track`) y su espectro reflejado + térmico.
- **`/neo`:**
  - tabla de los ~86 objetos: D (16–84%), pV, η, nº de exposiciones, PHA sí/no, comparación con el D de H suponiendo pV = 0.14;
  - gráfico de D frente a H con las líneas de albedo;
  - validación contra NEOWISE (D_SPHEREx frente a D_NEOWISE, en escala log);
  - **cada fila enlaza al Explorer** con `track=<pdes>`.
- **Explorer:** cualquier asteroide conocido → espectro reflejado + térmico con el ajuste NEATM superpuesto (bandas sombreadas por régimen).

### 0.7 Presupuesto (dos días)
- **Lecturas:** 86 objetos × ~50 exposiciones (D1–D6) × bloques de 21–41 filas (cápsula) ≈ **5–10 GB** de S3.
- **Validación:** ~200 asteroides con NEOWISE → ~20 GB.
- **Ajuste NEATM:** malla en (D, η, pV) con mínimos cuadrados (scipy `least_squares` con D y η libres, y pV del cociente) + Monte Carlo (1,000) para el intervalo 16–84%.
- **Pipeline:** `pipelines/precompute_neo.py`. Efemérides: `research/feasibility/neo_fetch_ephemerides.py` y `neo_match_spherex.py` sirven de plantilla (Horizons API, `CENTER='500@-163182'`, `STEP_SIZE='6 h'`, `QUANTITIES='1,19,20,24'`); para la incertidumbre y la tasa de movimiento: `QUANTITIES='3,36'`, columnas `dRA*cosD`, `d(DEC)/dt` (″/h), `RA_3sigma` y `DEC_3sigma` (″).

---

## Apéndice A. Plan complementario 2: "Activity Watch" (¿quién está respirando en el Sistema Solar?)

*Investigado el 12 nov 2026. Se activa solo si el núcleo de §15 está desplegado. **No cambia el plan principal.** El código se escribe durante el evento; aquí van la factibilidad medida, el diseño y los datos de entrada.*

### A.1 La idea
**Vigilar automáticamente, en cada pasada de SPHEREx, si algún objeto conocido del Sistema Solar está activo:** gas (CO₂ y CO), exceso de polvo o estallidos. Así se pueden descubrir:
- actividad en objetos que se creen inertes (centauros y asteroides activos);
- estallidos;
- cambios de química en los cometas.

El resultado es un **panel público** ("This pass: who's breathing?"), un **feed JSON** para investigadores y una **cola de candidatos para revisar**.

**Por qué cumple el reto:**
- son objetos en movimiento y el cielo cambia con el tiempo;
- llegan datos nuevos (consideración 1);
- hay espectros al vuelo (consideración 2);
- ayuda a descubrir.

**Por qué es útil para investigar:** el CO₂ y el CO no se ven desde tierra. JWST observa solo objetos elegidos, y SPHEREx ve todo el cielo, pero nadie revisa sistemáticamente sus datos con este fin.

### A.2 Limitaciones honestas (decirlas siempre)
1. **No es en tiempo real.**
   - Retraso de los datos ✔: el 12 nov 2026, lo último publicado en S3 es la semana `2026W40` (inicios de octubre) → **~5–6 semanas**.
   - **Cadencia por objeto ✔:** pocas visitas al año. Por ejemplo, 29P tiene 5 visitas en 13 meses: 2025-04-27…30, 2025-12-08, 2025-12-14…23, 2026-05-14…21 y 2026-05-26…27.
   - Es un **censo por pasada** que detecta estados de actividad que duran semanas o meses, y estallidos cuando coinciden con una visita.
2. **Gas solo para objetos cercanos o muy productivos.** El flujo de la banda escala como ∝ Q·r⁻²·Δ⁻². 29P (6.2 au, Q ~ 1e27) dio S/N 20. Chiron (~19 au) necesitaría Q ~ 1e28: **inviable**. Para centauros y asteroides lejanos, **el indicador sensible es el polvo** (exceso de brillo sobre el núcleo), no el gas.
3. **Novedad del censo de cometas: hay un trabajo profesional más completo ✔.** Repositorio público https://github.com/bumhooLIM/spherex-comet (último commit el 16 sep 2026; autor bumhooLIM). Lo leímos completo el 12 nov:
   - **Qué hace:** catálogo de Q(H₂O), Q(CO₂) y Q(CO) para **68 cometas en 192 "fases"**, con ajuste conjunto de las tres especies, perfiles de banda reconstruidos con el modelo de fluorescencia de GSFC (HITRAN 2020), contexto de polvo Afρ de ZTF, banderas de contaminación de Gaia y covarianza GLS.
   - **Resultados internos (no publicados en un artículo):** detecciones robustas ≥ 3σ de **CO₂ en 28 fases**, H₂O en 18 y CO en 4, en 37 cometas. Incluye 29P.
   - **Datos:** recortes propios de ~139,000 FITS en un disco externo; los resultados (`results/`) no están en el repositorio.
   - **Lo que NO hace:** no es una herramienta pública, no vigila centauros ni asteroides activos, no es un monitoreo por pasada, no publica una tasa de falsas alarmas y no detecta estallidos con SPHEREx (solo ve estallidos en el polvo de ZTF).
   - **Consecuencia:** **no afirmar** que nuestro censo de cometas es "el primero" ni que "14 de 20 no tienen publicación". Nuestro diferencial es **Activity Watch** (público, con centauros y asteroides activos, por pasada y con falsas alarmas calibradas) y la herramienta del reto.
   - **Lo útil de su trabajo** (citarlo si se usa):
     - **g-factors a 1 au de su base de fluorescencia:** H₂O ν₃ 3.14e-4, CO₂ ν₃ 2.71e-3 y CO 1.92e-4 s⁻¹ (los nuestros: 4.24e-4, 2.86e-3 y 2.46e-4). La diferencia en CO (~28%) y H₂O (~35%) es un sistemático a declarar;
     - g(CO) depende de la velocidad heliocéntrica (efecto Swings: +25–31% por encima de 10 km/s);
     - las bandas calientes de H₂O a 4.63 y 4.85 µm se montan sobre el CO;
     - anillo de fondo físico de 150,000 km en el cometa, con un mínimo de 15 px y un máximo de 40 px;
     - **no enmascarar** estrellas dentro de la apertura: marcarlas (enmascarar sesgó Q(CO₂) un 13% a la baja);
     - v_g = 0.8 r⁻⁰·⁵ km/s;
     - su pendiente principal es la respuesta espectral real del LVF: ver "Spectral response of SPHEREx" (arXiv:2602.09139).

### A.3 Lista de objetos (≈ 350–500), datos ✔ de JPL SBDB del 12 nov
| Grupo | Cuántos | Criterio | Indicador principal |
|---|---|---|---|
| Cometas | ~150 en la huella de SPHEREx (de 491 con perihelio 2021–2029; hay 4,088 cometas en SBDB) | `research/03`: `data/derived/comet_spherex_hits.parquet` | Gas (CO₂, CO, H₂O) + polvo |
| Centauros brillantes | **134** con H < 9.5 (de 1,088): Chiron, Pholus, Asbolus, Chariklo, Echeclus… | `sb-class=CEN` y `H<9.5` | Polvo (exceso sobre el núcleo) + gas solo si r < 8 au |
| Asteroides activos conocidos | < 60 (AJ 2024) | Tablas de Jewitt & Hsieh 2022 (arXiv:2203.01397) y de Wikipedia "Active asteroid" | Polvo |
| Controles inactivos | 100–300 asteroides brillantes del cinturón principal (H < 12) | Elegidos al azar | **Distribución nula** de los indicadores |
| Extra, solo para la landing (no es actividad) | 16 TNO con H < 3.5 (Plutón, Eris, Makemake, Haumea, Sedna…) | `sb-class=TNO` y `H<3.5` | Hielos de CH₄ y N₂ en el espectro: guiño a "Planet X" |

Consultas SBDB ✔:
```
https://ssd-api.jpl.nasa.gov/sbdb_query.api?fields=full_name,pdes,H,e,a,q,i,om,w,ma,epoch,tp&sb-class=CEN&sb-cdata={"AND":["H|LT|9.5"]}
```
(codificar en URL). Para cometas usar `sb-kind=c` con los elementos `e, q, i, om, w, tp, epoch`.

### A.4 Geometría a escala: **sin una consulta a Horizons por exposición** ✔
- **Cada cabecera L2 trae la posición de SPHEREx respecto del geocentro** en km a la mitad de la exposición: `X_SC, Y_SC, Z_SC` (`XYZ_SC_SYSTEM = GEOCENTER`, marco ICRF), además de `VX_SC…`, `*_START` y `*_END`.
- **Validado contra Horizons** (`-163182` respecto de `500@399`): **3.2 km** de diferencia, siempre que la hora se pase de **UTC (`MJD-AVG`, `TIMESYS = UTC`) a TDB**. Sin esa conversión el error es de 518 km (69 s × 7.5 km/s).
- **Posición topocéntrica:**
  1. Horizons, **una vez por objeto**: vectores geocéntricos astrométricos (`location='500@399'`, `refplane='frame'`, `aberrations='astrometric'`) con velocidades, paso de 1 día (cometas a < 1 au: 2 h).
  2. Interpolación **de Hermite cúbica** con las velocidades.
  3. **d = g(t_TDB) − sc(t)**: RA = atan2(d_y, d_x), Dec = asin(d_z/|d|).
  - **Validado ✔:** C/2025 A6 a Δ = 0.64 au → **0.01″** frente a Horizons visto desde SPHEREx; Ceres → 0.00″.
  - Usar solo el geocentro deja **14″ (2.3 px)** de error a 0.64 au: **prohibido**.
- **Costo:** ~500 objetos × 1 consulta (~1–2 s) ≈ 15 min, cacheadas. La interpolación se vectoriza con numpy para todas las exposiciones.
- **Prefiltro:** posición diaria (Kepler o Horizons) → celdas HEALPix de orden 6 → unión con `cells.parquet` del índice → candidatos (objeto, exposición) → posición precisa → prueba de punto en el polígono.

### A.5 Indicadores de actividad (por objeto y por visita)
1. **Gas:** CO₂ en D5 y CO en D6 con el modelo de banda y Diff λ (§8.9).
   - **Criterio:** S/N_det ≥ 5, χ²_red < 50 y n_core ≥ 1.
   - Reportar Q con su intervalo 16–84%.
2. **Exceso de polvo:**
   - flujo medido en el continuo (D1 cerca de 1.0 µm; D4 en 2.4–2.6 µm) frente al **núcleo esperado**:
     V = H + 5·log₁₀(r·Δ) − 2.5·log₁₀[(1 − G)Φ₁(α) + GΦ₂(α)], con G = 0.15;
   - pasar V → F_ν(1 µm) con colores solares;
   - **exceso = F_med/F_núcleo**. Activo si exceso > 3 **y** > 5σ, donde σ incluye una incertidumbre de H de ±0.3 mag.
3. **Extensión:** cociente de flujo r = 2 px / r = 5 px frente al mismo cociente del PSF a esa λ.
   - Fuente del PSF: extensión `PSF` (QR2, 101×101×121 zonas) o `EPSF` (DR1, tabla).
   - Extendido si el cociente es < PSF − 3σ.
4. **Estallido:** salto en el continuo entre visitas > 0.75 mag (factor ~2) a > 5σ, **o** dentro de una visita (varias exposiciones en días) que supere la variación por rotación esperada (≤ 0.3 mag en asteroides).
5. **Calibración de falsas alarmas:**
   - los mismos indicadores sobre **los controles inactivos** y sobre **trayectorias fantasma** desplazadas ±0.3° (como en las nulas del doc 06, §4.2);
   - **publicar la tasa de falsas alarmas** junto con cada alerta.

### A.6 Validación (casos conocidos)
| Caso | Qué debe salir | Datos SPHEREx ✔ |
|---|---|---|
| **29P, diciembre 2025** | Actividad alta después de los estallidos del 4.65 y 11.02 dic (BAA). **Dos visitas:** 2025-12-08 (después del primero) y 12-14…23 (después del segundo). Continuo de 4.65 mJy frente a 1.40–1.46 en las visitas tranquilas | Abr 2025 y may 2026 como línea base |
| 3I/ATLAS | CO₂ 1.17e27 (ago 2025); 3.0–3.4e27 (dic 2025) | §12.2 |
| Controles inactivos | Tasa de falsas alarmas ≤ 1% con los umbrales de A.5 | Por medir |
| Centauros conocidos como activos (Echeclus, Chiron) | Exceso de polvo solo si estaban activos en la fecha de la visita | Por medir |

Otros estallidos de 29P (BAA): 2025-01-02/06, 2025-02-01/02, 2025-05-13/25, febrero 2026 (el mayor desde 2022, ~167 núcleos equivalentes) y 2026-07-21/22. **Ninguno tiene una visita de SPHEREx dentro de los 30 días siguientes en el índice actual.** Revisarlo de nuevo con QR3 completo y DR1.

### A.7 DR1: ya está en S3 (sin anunciar) ✔. Hay que prepararse
- **Prefijos:** `dr1/level2/<semana>/l2b-v27-2026-196/<det>/level2_<obs_id>D<det>_spx_l2b-v27-2026-196.fits`.
  - 110 semanas: de `2025W17_4B` a `2026W20_1A`.
  - Hay carpetas `l2b_retry-v27-2026-197` (reprocesos): **preferir la versión más reciente por obs_id**.
- **Calibraciones:** `dr1/spectral_wcs/cal-swcs-v5-2026-191` (la misma v5), `dr1/sip/`, `dr1/epsf/` (v1 y v2), `dr1/l3_flux_corrections/` y `dr1/hips5_cube/hips_20261026`.
- **Ya está en IRSA TAP** (verificado el 13 nov: `spherex_dr1` + `spherex_dr1_deep` = 1,179,406 obs×det, idéntico a S3). Los obs_id coinciden con QR2 ✔ (mismas exposiciones: igual MJD-AVG y apuntado).
- **Formato distinto ✔:**
  - archivo de 65.4 MB;
  - **FLAGS es `CompImageHDU` RICE_1 con un bloque por fila** (BINTABLE `COMPRESSED_DATA 1PB`, `ZTILE = 2040×1`, `BLOCKSIZE = 32`, `BYTEPIX = 4`);
  - `PSF` pasa a **`EPSF`** (BINTABLE de 441 filas, `OVSMPX = OVSMPY = 5`);
  - `PSF_FWHM` cambia de definición (8.67″ frente a 6.10″ en QR2 para el mismo obs_id);
  - **las cabeceras no traen las claves `MP_*`**. Los bits nuevos ya están documentados (§8.0b): 26 BLOOM, 27 SNOWBALL, 28 HALO y 29 SATELLITE_HALO.
- **Leer filas de FLAGS en DR1 ✔** (verificado idéntico a `astropy ….section`; 117 filas = 630 KB y 3 ms de decodificación):
```python
import numpy as np, astropy.io.fits.hdu.compressed._codecs as C
async def read_flag_rows_dr1(key, flags_hdu, y0, y1):
    h = flags_hdu["header"]; nrow, rowlen = h["NAXIS2"], h["NAXIS1"]; theap = h.get("THEAP", rowlen * nrow)
    desc = np.frombuffer(bytes(await obs.get_range_async(STORE, key, start=flags_hdu["dat_loc"], length=rowlen * nrow)), ">i4").reshape(nrow, 2)
    n, off = desc[y0:y1, 0], desc[y0:y1, 1]
    a = flags_hdu["dat_loc"] + theap + int(off[0]); b = flags_hdu["dat_loc"] + theap + int(off[-1] + n[-1])
    heap = np.frombuffer(bytes(await obs.get_range_async(STORE, key, start=a, length=b - a)), np.uint8)
    rice = C.Rice1(blocksize=h.get("ZVAL1", 32), bytepix=h.get("ZVAL2", 4), tilesize=h.get("ZTILE1", 2040))
    return np.vstack([np.frombuffer(rice.decode(heap[o - off[0]: o - off[0] + k]), np.int32) for o, k in zip(off, n)])
```
  `_codecs` es un módulo interno de astropy 8.0.2: **fijar la versión** y tener como respaldo `fits.open(url, use_fsspec=True)["FLAGS"].section[y0:y1, :]`, que es más lento pero público.
- **Decisión (actualizada el 13 nov):** el producto lee **DR1 + QR3** (los dos en TAP y en S3, procesamiento R7 uniforme). QR2 solo para los 1,918 obs×det sin reproceso. Una nueva publicación (QR4/DR2) se incorpora regenerando los dos índices (`22_…` y `24_…`, < 10 min): cumple la consideración 1 ("easy to update").

### A.8 Producto
- **Landing:** "§7 Who's breathing?". Una placa con 29P en diciembre de 2025 (antes y después del estallido) y el contador de la pasada: "N objects watched · M active · K candidates".
- **`/watch`:** tabla por objeto con estado (active gas / dust excess / outburst / quiet / not observed), última visita, indicadores con S/N y enlace al Explorer con `track`.
  - Filtros por grupo (cometas, centauros, asteroides activos).
  - **Cada fila cita la tasa de falsas alarmas.**
- **Feed:** `static/data/watch/feed.json` (JSON Feed 1.1) y `watch/<pass>.json`, un ítem por detección:
  `{object, mjd, indicator, value, snr, far, explorer_url}`.
- **Candidatos:** lista "candidates to inspect" con botón **Report** (abre un issue prellenado en el repositorio público). **Sin cuentas ni votaciones** en el hackathon.

### A.9 Presupuesto (para que quepa en el tiempo sobrante)
- Pipeline `pipelines/precompute_watch.py`, ejecutado en Fly o en local, **nunca en la petición del usuario**.
- **Lecturas:** ~500 objetos × ~20 exposiciones relevantes por visita × 2–5 visitas × bloques de 21 filas (111 para cometas) ≈ **10–30 GB de S3**: horas, no días.
- **Si falta tiempo:** solo cometas + los 30 centauros más brillantes + controles, en la pasada más reciente (QR3).

### A.10 Plan de 3 meses (visión, para "Project Details" y el IAC 2027)
1. **Mes 1, infraestructura:**
   - índice D1–D6 con QR + DR1 y actualización semanal;
   - geometría vectorizada para ~10⁵ objetos (prefiltro Kepler + Horizons para los aciertos);
   - fotometría por objeto.
2. **Mes 2, ciencia:**
   - indicadores con falsas alarmas calibradas (nulas + inyección + controles);
   - modelo de fase y color para el núcleo;
   - validación con 29P, 3I y asteroides activos conocidos.
3. **Mes 3, producto:**
   - feed semanal automático;
   - API;
   - ciencia ciudadana (Zooniverse Project Builder);
   - integración total con el Explorer;
   - resumen para el IAC 2027 (plazo: 28 feb 2027).
4. **Métricas:** latencia publicación → alerta, falsas alarmas por pasada, recuperación de estallidos conocidos y objetos vigilados.

---

## Apéndice B. Alternativa descartada como complementaria: "Breathing Stars" (Miras de la LMC)

Ciencia sólida pero **orientada a especialistas**: no detecta objetos en movimiento ni descubre objetos nuevos. Se conserva como idea futura.
- **Factibilidad ✔:** 1,635 Miras de OGLE-III (1,188 de carbono y 447 de oxígeno), todas con ≥ 308 exposiciones D4–D6 (mediana 1,523; ~117 tramos de 3 días en 523 d).
- **Tabla:** `data/derived/lmc_miras_spherex_coverage.csv`.
- **Catálogo:** `https://www.astrouw.edu.pl/ogle/ogle3/OIII-CVS/lmc/lpv/`.
- **Saturación (≈):** ~9.7–11.7 AB según la banda; Miras de la LMC ≈ 12.3–13.9 AB (por debajo, salvo las de carbono muy polvorientas).
- **Descartadas como ciencia de la herramienta** (ya publicadas por otros): enanas marrones (6,003 ultrafrías, arXiv:2604.22012; secuencia L0–Y4, arXiv:2607.00543) y estelas de satélites (73% de las imágenes, arXiv:2605.27501).
- **Alternativa para asteroides:** hidratación a 2.7 µm validada con AKARI AcuA-spec (64 asteroides); el cociente D4/D1 de la misma exposición es inmune a la rotación.
