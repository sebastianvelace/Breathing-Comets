// Terms of use and privacy notice. Plain data so both pages share one layout and
// both languages stay in step. Update `updated` whenever the wording changes.
export type LegalSection = { h: string; p: string[] };
export type LegalDoc = { title: string; intro: string; sections: LegalSection[] };

export const updated = "2026-11-15";
export const repo = "https://github.com/sebastianvelace/Breathing-Comets";
export const issues = repo + "/issues";

const termsEn: LegalDoc = {
  title: "Terms of use",
  intro:
    "Breathing Comets is a free, non-commercial, open-source project created by Team Breathing Comets for the NASA International Space Apps Challenge 2026. By using this website or its API you accept these terms.",
  sections: [
    {
      h: "1. Independence and no endorsement",
      p: [
        "This is an independent project. It is not operated, endorsed, sponsored or reviewed by NASA, JPL, Caltech, IPAC, ESA, CDS or any other agency or institution named on this site. Participation in the Space Apps Challenge does not imply endorsement.",
        "No agency logos, insignia or emblems are used. Mission and agency names appear only to identify the source of the data and to credit it, as their providers request.",
      ],
    },
    {
      h: "2. What the service is for",
      p: [
        "The site is an educational and quick-look research tool for viewing public SPHEREx observations and related measurements. It requires no account and has no fees.",
        "It is not a substitute for the official data products, their documentation or a full scientific analysis. Always cite and check the original archives before publishing results.",
      ],
    },
    {
      h: "3. No safety-critical use",
      p: [
        "The site issues no alerts and makes no impact predictions or planetary-defence assessments. “Potentially hazardous asteroid” (PHA) is an orbit class from the published orbit, not a risk statement. Do not use this site for navigation, safety, or any decision where an error could cause harm.",
      ],
    },
    {
      h: "4. Accuracy and availability",
      p: [
        "The site and its data are provided “as is” and “as available”, without warranties of any kind, express or implied, including accuracy, completeness, fitness for a particular purpose and non-infringement. Measurements are shown with their uncertainties and known limitations, but they may still contain errors.",
        "The live API depends on external archives and services and may be slow, change or be unavailable without notice. Prepared targets are provided as static files so that they keep working when it is.",
      ],
    },
    {
      h: "5. Data, credits and licences",
      p: [
        "Scientific data remain the property of, and subject to the terms of, their providers: SPHEREx (NASA/JPL-Caltech/IRSA), Gaia DR3 (ESA/Gaia/DPAC), 2MASS (UMass and IPAC/Caltech), WISE and NEOWISE (NASA/JPL-Caltech via IRSA), JPL Horizons and SBDB (NASA/JPL), SIMBAD and Aladin Lite (CDS, Strasbourg). If you reuse anything from this site, credit those providers as listed on the About page.",
        "The project's source code is licensed under the GNU General Public License version 3. Third-party code and fonts keep their own licences, listed in the repository. Derived measurements published here may be reused with attribution to Breathing Comets and to the original data providers.",
      ],
    },
    {
      h: "6. Acceptable use",
      p: [
        "Please do not overload, probe or disrupt the website or the API, and do not use automated tools to make large numbers of requests. We may limit or block traffic that affects other users. For bulk access, use the original archives or run the open-source code yourself.",
      ],
    },
    {
      h: "7. External links",
      p: [
        "The site links to and loads content from third-party services (for example IRSA, CDS and GitHub). We do not control them and are not responsible for their content, availability or practices.",
      ],
    },
    {
      h: "8. Limitation of liability",
      p: [
        "To the maximum extent permitted by applicable law, the team members and contributors are not liable for any direct, indirect, incidental or consequential damages arising from the use of, or inability to use, this site, its API or its data. Nothing in these terms limits liability that cannot be limited by law.",
      ],
    },
    {
      h: "9. Changes and contact",
      p: [
        "We may update these terms; the date below shows the current version. Questions, corrections and takedown requests can be sent through the project's public issue tracker on GitHub.",
      ],
    },
  ],
};

const termsEs: LegalDoc = {
  title: "Términos de uso",
  intro:
    "Breathing Comets es un proyecto gratuito, sin fines comerciales y de código abierto, creado por el equipo Breathing Comets para el NASA International Space Apps Challenge 2026. Al usar este sitio o su API aceptas estos términos.",
  sections: [
    {
      h: "1. Independencia y ausencia de respaldo",
      p: [
        "Este es un proyecto independiente. No lo operan, respaldan, patrocinan ni revisan la NASA, JPL, Caltech, IPAC, la ESA, el CDS ni ninguna otra agencia o institución mencionada en el sitio. Participar en el Space Apps Challenge no implica respaldo.",
        "No se usan logotipos, insignias ni emblemas de agencias. Los nombres de misiones y agencias aparecen solo para identificar la fuente de los datos y darles crédito, como piden sus proveedores.",
      ],
    },
    {
      h: "2. Para qué sirve el servicio",
      p: [
        "El sitio es una herramienta educativa y de consulta rápida para ver observaciones públicas de SPHEREx y mediciones relacionadas. No requiere cuenta ni tiene costo.",
        "No sustituye a los productos de datos oficiales, a su documentación ni a un análisis científico completo. Cita y verifica siempre los archivos originales antes de publicar resultados.",
      ],
    },
    {
      h: "3. Sin usos críticos para la seguridad",
      p: [
        "El sitio no emite alertas ni hace predicciones de impacto o evaluaciones de defensa planetaria. “Asteroide potencialmente peligroso” (PHA) es una clase orbital tomada de la órbita publicada, no una declaración de riesgo. No uses este sitio para navegación, seguridad ni ninguna decisión en la que un error pueda causar daño.",
      ],
    },
    {
      h: "4. Exactitud y disponibilidad",
      p: [
        "El sitio y sus datos se ofrecen “tal cual” y “según disponibilidad”, sin garantías de ningún tipo, expresas o implícitas, incluidas las de exactitud, integridad, idoneidad para un fin concreto y no infracción. Las mediciones se muestran con sus incertidumbres y limitaciones conocidas, pero aun así pueden contener errores.",
        "La API en vivo depende de archivos y servicios externos y puede ser lenta, cambiar o no estar disponible sin aviso. Los objetivos preparados se ofrecen como archivos estáticos para que sigan funcionando en ese caso.",
      ],
    },
    {
      h: "5. Datos, créditos y licencias",
      p: [
        "Los datos científicos siguen siendo propiedad de sus proveedores y se rigen por sus condiciones: SPHEREx (NASA/JPL-Caltech/IRSA), Gaia DR3 (ESA/Gaia/DPAC), 2MASS (UMass e IPAC/Caltech), WISE y NEOWISE (NASA/JPL-Caltech vía IRSA), JPL Horizons y SBDB (NASA/JPL), SIMBAD y Aladin Lite (CDS, Estrasburgo). Si reutilizas algo de este sitio, da crédito a esos proveedores como se indica en la página Acerca de.",
        "El código fuente del proyecto se publica bajo la Licencia Pública General de GNU, versión 3. El código y las fuentes tipográficas de terceros conservan sus propias licencias, listadas en el repositorio. Las mediciones derivadas publicadas aquí pueden reutilizarse citando a Breathing Comets y a los proveedores originales de los datos.",
      ],
    },
    {
      h: "6. Uso aceptable",
      p: [
        "Por favor, no sobrecargues, sondees ni interrumpas el sitio o la API, ni uses herramientas automáticas para hacer grandes cantidades de solicitudes. Podemos limitar o bloquear el tráfico que afecte a otros usuarios. Para acceso masivo, usa los archivos originales o ejecuta tú mismo el código abierto.",
      ],
    },
    {
      h: "7. Enlaces externos",
      p: [
        "El sitio enlaza y carga contenido de servicios de terceros (por ejemplo IRSA, CDS y GitHub). No los controlamos y no respondemos por su contenido, disponibilidad ni prácticas.",
      ],
    },
    {
      h: "8. Limitación de responsabilidad",
      p: [
        "En la máxima medida permitida por la ley aplicable, los integrantes del equipo y los colaboradores no son responsables de daños directos, indirectos, incidentales o consecuentes derivados del uso, o de la imposibilidad de uso, de este sitio, su API o sus datos. Nada en estos términos limita una responsabilidad que la ley no permita limitar.",
      ],
    },
    {
      h: "9. Cambios y contacto",
      p: [
        "Podemos actualizar estos términos; la fecha de abajo indica la versión vigente. Las preguntas, correcciones y solicitudes de retiro pueden enviarse por el sistema público de incidencias (issues) del proyecto en GitHub.",
      ],
    },
  ],
};

const privacyEn: LegalDoc = {
  title: "Privacy notice",
  intro:
    "Breathing Comets is designed to work without collecting personal data. This notice explains exactly what is and is not processed when you use the site.",
  sections: [
    {
      h: "1. What we do not collect",
      p: [
        "There are no accounts, sign-ups, forms, advertising, analytics, tracking pixels or third-party cookies. We do not sell, rent or share personal data, and we do not build profiles of visitors.",
      ],
    },
    {
      h: "2. Storage in your browser",
      p: [
        "The site stores one small preference in your browser's local storage (key “bc.tour.v1”) to remember that you dismissed or finished the guided tour. It never leaves your device. You can delete it at any time by clearing this site's data in your browser; the site works the same without it. The selected language and view are kept in the page address, not in cookies.",
      ],
    },
    {
      h: "3. What our servers receive",
      p: [
        "To answer a request, the API receives what you ask for: a sky position, an object name you search, a position you click, a detector and a date range. These sky queries are not linked to any identity. Responses may be cached by sky position to make later requests faster.",
        "Like any website, our hosting providers, Cloudflare (website) and Fly.io (API), process technical connection data such as IP address, browser user agent, requested address and time, in order to deliver the site and protect it from abuse. They handle these data under their own privacy policies; we do not use them to identify visitors.",
      ],
    },
    {
      h: "4. Services contacted on your behalf",
      p: [
        "To resolve names and fetch observations, our server queries public scientific services (NASA/IRSA archives, JPL Horizons and SBDB, CDS SIMBAD and Gaia archives). They receive the sky query, not your IP address.",
        "In Lab mode, the Aladin Lite viewer loads sky tiles and catalogues directly from your browser from IRSA and CDS servers, so those services receive your connection data. Following the GitHub link takes you to GitHub, which has its own privacy policy.",
      ],
    },
    {
      h: "5. Shared links",
      p: [
        "“Share this view” copies an address that contains only the view state (sky position, detector, dates, mode and language). It contains no personal information.",
      ],
    },
    {
      h: "6. Children and your rights",
      p: [
        "The site is suitable for all ages and does not knowingly collect personal data from anyone. Because we hold no personal data about you, there is nothing for us to access, correct or delete; requests about hosting logs can be directed to the providers named above.",
      ],
    },
    {
      h: "7. Changes and contact",
      p: [
        "If what the site processes ever changes, this notice will be updated first; the date below shows the current version. Questions can be sent through the project's public issue tracker on GitHub.",
      ],
    },
  ],
};

const privacyEs: LegalDoc = {
  title: "Aviso de privacidad",
  intro:
    "Breathing Comets está diseñado para funcionar sin recopilar datos personales. Este aviso explica exactamente qué se procesa y qué no cuando usas el sitio.",
  sections: [
    {
      h: "1. Lo que no recopilamos",
      p: [
        "No hay cuentas, registros, formularios, publicidad, analítica, píxeles de seguimiento ni cookies de terceros. No vendemos, alquilamos ni compartimos datos personales, ni creamos perfiles de los visitantes.",
      ],
    },
    {
      h: "2. Almacenamiento en tu navegador",
      p: [
        "El sitio guarda una pequeña preferencia en el almacenamiento local de tu navegador (clave “bc.tour.v1”) para recordar que cerraste o terminaste el recorrido guiado. Nunca sale de tu dispositivo. Puedes borrarla cuando quieras eliminando los datos de este sitio en tu navegador; el sitio funciona igual sin ella. El idioma y la vista seleccionados se guardan en la dirección de la página, no en cookies.",
      ],
    },
    {
      h: "3. Lo que reciben nuestros servidores",
      p: [
        "Para responder una solicitud, la API recibe lo que pides: una posición en el cielo, el nombre de un objeto que buscas, una posición en la que haces clic, un detector y un rango de fechas. Estas consultas del cielo no se vinculan a ninguna identidad. Las respuestas pueden guardarse en caché por posición en el cielo para que las siguientes solicitudes sean más rápidas.",
        "Como en cualquier sitio web, nuestros proveedores de alojamiento, Cloudflare (sitio web) y Fly.io (API), procesan datos técnicos de conexión como la dirección IP, el agente de usuario del navegador, la dirección solicitada y la hora, para entregar el sitio y protegerlo de abusos. Ellos tratan esos datos según sus propias políticas de privacidad; nosotros no los usamos para identificar a los visitantes.",
      ],
    },
    {
      h: "4. Servicios consultados en tu nombre",
      p: [
        "Para resolver nombres y obtener observaciones, nuestro servidor consulta servicios científicos públicos (archivos de NASA/IRSA, JPL Horizons y SBDB, SIMBAD del CDS y archivos de Gaia). Reciben la consulta del cielo, no tu dirección IP.",
        "En el modo Lab, el visor Aladin Lite carga mosaicos del cielo y catálogos directamente desde tu navegador desde servidores de IRSA y del CDS, por lo que esos servicios reciben tus datos de conexión. El enlace a GitHub te lleva a GitHub, que tiene su propia política de privacidad.",
      ],
    },
    {
      h: "5. Enlaces compartidos",
      p: [
        "“Compartir esta vista” copia una dirección que solo contiene el estado de la vista (posición en el cielo, detector, fechas, modo e idioma). No contiene información personal.",
      ],
    },
    {
      h: "6. Menores y tus derechos",
      p: [
        "El sitio es apto para todas las edades y no recopila a sabiendas datos personales de nadie. Como no guardamos datos personales tuyos, no hay nada que consultar, corregir o eliminar de nuestra parte; las solicitudes sobre los registros de alojamiento pueden dirigirse a los proveedores mencionados arriba.",
      ],
    },
    {
      h: "7. Cambios y contacto",
      p: [
        "Si alguna vez cambia lo que procesa el sitio, este aviso se actualizará primero; la fecha de abajo indica la versión vigente. Las preguntas pueden enviarse por el sistema público de incidencias (issues) del proyecto en GitHub.",
      ],
    },
  ],
};

export const legal = {
  terms: { en: termsEn, es: termsEs },
  privacy: { en: privacyEn, es: privacyEs },
} as const;
