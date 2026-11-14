# Landing implementation assignment

Trabaja en `/home/sebasvelace/Breathing-Comets`. Tu responsabilidad es implementar exclusivamente la landing de Breathing Comets, paso 10 de `docs/BUILD.md`. Otro agente está implementando API, Explorer, Lab y las demás páginas EN PARALELO. No estás solo en el repositorio: conserva sus cambios y limita tus ediciones a los archivos asignados.

## Antes de implementar

1. Lee `AGENTS.md`, `docs/STATUS.md` y `docs/BUILD.md`, en particular el recuadro inicial, §10 completo, §12.3, §13 y §14. El recuadro inicial prevalece sobre cifras antiguas del documento.
2. Lee la documentación de Svelte 5 indicada por el proyecto y los componentes existentes para comprender contratos y estilo. Utiliza las habilidades de frontend pertinentes. Solo Svelte 5 con runes.
3. Revisa el estado actual antes de modificar. No reviertas cambios ajenos, no cambies pruebas para hacerlas pasar y no instales dependencias nuevas.

## Propiedad exclusiva de tus archivos

- `apps/web/src/routes/+page.svelte`.
- Componentes nuevos dentro de `apps/web/src/lib/components/landing/`.
- Traducciones nuevas en `apps/web/messages/landing/en.json` y `apps/web/messages/landing/es.json`; todas las claves deben comenzar por `landing_`. El proyecto ya tiene configuradas estas rutas adicionales en Paraglide. Usa las funciones generadas habituales de Paraglide.
- Medios reales derivados exclusivamente de los paquetes del producto en `apps/web/static/media/landing/`.
- Herramientas necesarias para esos medios en `pipelines/landing_media.py`, si hacen falta.
- Pruebas de la landing en `apps/web/e2e/landing.spec.ts` y, si corresponde, `apps/web/tests/landing.test.ts`.
- Informe final en `docs/landing-handoff.md`.

NO modifiques `src/app.css`, el layout global, configuración, dependencias, mensajes base `messages/en.json`/`es.json`, Explorer, renderizador, Workers, API, datos científicos existentes ni `docs/STATUS.md`. Reutiliza los tokens y las fuentes globales; añade estilos locales a tus componentes. No hagas commits, push, ramas, PR ni despliegues: el agente coordinador integra y publica cada paso. Si necesitas algo fuera de tu propiedad, documéntalo en el informe; no lo cambies unilateralmente.

## Producto y diseño

Construye el sistema editorial **Plate & Ink** de §10, sin reemplazarlo por otra dirección estética. Papel cálido, tinta oscura, ocre como acento; Newsreader para titulares/ensayo, IBM Plex Sans para interfaz e IBM Plex Mono para datos. Respeta la variante oscura existente. La imagen del cielo es el protagonista: placas enmarcadas, reglas finas, escala angular y procedencia verificable.

Nada de degradados, brillos, glassmorphism, tarjetas con sombra, grillas SaaS de tres tarjetas, emojis, ilustraciones espaciales, imágenes generadas ni logos de NASA. No presentes datos de NASA como propios. Composición cuidada en escritorio y móvil; contraste, foco visible, controles de pausa, teclado y prefers-reduced-motion.

Implementa las secciones y el contenido de §10.5: héroe “The sky is breathing.”, comparación de placas, LVF/Diff λ, composición espectral, cometas, validación y los cinco objetivos. Interfaz por defecto EN y español profesional completo en `/es`; conserva el punto decimal en cifras científicas. No uses toLocaleString ni CSS uppercase sobre unidades µ.

El enlace principal debe conservar el nombre accesible inglés **Open the sky** y apuntar a `/explore?target=barnard&ui=story`, usando localizeHref para español. Las otras llamadas a la acción deben llevar a rutas existentes o a secciones reales de la landing; no publiques enlaces rotos.

## Datos y medios

- Usa solamente los JSON y las imágenes reales de `apps/web/static/data/`. Las posiciones están en `targets.json`, los canales en `channels.json`, la calibración en `calibration.json` y las notas y caveats en `targets/<slug>.json`.
- Ya existen cinco paquetes completos en `targets/<slug>/`: manifest, Gaia, seis pilas `.spxf.gz` y Diff λ del detector predeterminado. Puedes leerlos para generar pósteres/miniaturas reales. No cambies esos archivos ni ejecutes scripts científicos externos.
- Al convertir una pila en imágenes, utiliza su stretch_hint común, orientación norte arriba y saturación blanca antes de tratar NaN. Conserva el mismo estirado entre épocas. No suavices ni inventes estrellas. Incluye créditos NASA/JPL-Caltech/IRSA y Gaia cuando corresponda.
- No escribas mediciones a mano en textos, componentes o traducciones. Impórtalas del JSON y pásalas como parámetros a Paraglide. Toda cifra de notas de campo debe aparecer junto con su caveat. No uses afirmaciones científicas prohibidas por la guía.
- No cargues Aladin, SpxViewer, el renderizador WebGL ni Workers del Explorer en el paquete inicial de la landing. Usa medios ligeros, imágenes con dimensiones y lazy loading bajo el héroe. Una comparación de dos imágenes reales puede implementarse sin el Explorer completo.
- No presentes una resta cruda como Diff λ. Si falta un producto necesario, muestra indisponibilidad explícita y registra el contrato pendiente.

## Contrato pendiente de 3I

El coordinador se encarga del paquete científico y de las placas reales de 3I. Todavía no debes asumir que existen. Prepara la carga diferida de `/data/comets/3i-atlas/landing.json`, cuyo contrato acordado para integración es:

```ts
{
  target: string;
  plates: {
    poster: string;
    epochs: { image: string; mjd: number; lambda_um: number; obs_id: string; credit: string }[];
  };
  measurements: { label: string; value: number; lo: number; hi: number; unit: string; caveat: string; source: string }[];
  validation: { species: string; measured: number; published_lo: number; published_hi: number; unit: string; caveat: string; source: string }[];
  credits: string[];
}
```

No inventes el archivo, sus valores, mapas de gas ni imágenes de 3I. Si aún falta, usa una placa real de Barnard claramente identificada como tal y un estado honesto para los resultados pendientes de 3I. No lo marques como cumplimiento del héroe final de 3I. Las secciones científicas se completarán automáticamente cuando llegue el paquete; informa qué falta.

## Verificación y entrega

- Ejecuta `npm run check` y `npm run build` en `apps/web`; reporta errores con su salida exacta. La suite Python tiene un fallo conocido de cobertura de R Dra: no lo modifiques ni lo ocultes.
- Verifica visualmente escritorio y móvil, EN/ES, foco y movimiento reducido. Comprueba la navegación a Barnard y las cinco entradas reales.
- Presupuestos: JS inicial menor de 90 KB gzip y Lighthouse móvil LCP menor de 1.5 s. Mide cuando tengas la herramienta disponible; no confundas build aprobado con presupuesto verificado. No instales herramientas adicionales sin autorización.
- En `docs/landing-handoff.md`, enumera archivos modificados, verificación observada, tamaño inicial medido, estado visual, contratos pendientes y dependencias de integración. Distingue claramente lo aprobado de lo pendiente. No declares terminado lo que no hayas comprobado.

Continúa hasta dejar una implementación concreta y revisable dentro de tu alcance, sin tocar el trabajo del coordinador.
