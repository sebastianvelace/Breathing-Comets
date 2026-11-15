# Experience revision

The revision addresses the production walkthrough findings and preserves the existing scientific values and acceptance thresholds.

## View integrity

Language changes reload the localized document and capture the actual Explorer state, including the current target, detector, observation and comparison. A completed acquisition key must match the requested field before sharing becomes available. Superseded name requests are aborted. The clipboard failure path exposes the URL for manual copying.

## Navigation and guidance

The same Explore, Comets and Asteroids navigation is available across product pages, including phones. Landing chapter links remain available below the hero. Each prepared field explains what to observe; the guide is collapsible on mobile. Visit comparison chooses the longest baseline within one band width when possible, and always explains the residual color difference. Diff λ distinguishes loading from insufficient reference frames and offers a valid comparison or a return to the observation.

## Laboratory layout

Layers occupy normal document flow in a collapsible panel, so they cannot cover playback. Lab is available on mobile. The spectrum leads the Inspector, with pixel values and observation properties behind explicit details. The first-visit tour invitation sits beside help instead of floating over image controls. Returning from the cube to Story selects Epoch.

## Reading measurements

The asteroid catalog uses adjacent selection details on desktop and a focused detail section on mobile. Diameter, interval, evidence tier, systematic floor and single-visit warnings remain together. Catalog chart links are keyboard-accessible and small-screen axes have larger labels. Empty filters have a clear reset. Comet pages offer direct access to the two real plate examples; interpretation notes remain available and unreliable selected results repeat their caveats. WISE uses the approved brown-dwarf description in both languages.

## Tradeoffs

Locale switches perform a complete navigation so static translated content and runtime locale agree. Sharing waits for acquisition completion; image display and playback remain progressive. Advanced metadata are one disclosure away, while uncertainties and limitations stay with results. No dependencies were added and no scientific data were recalculated for this revision.

## Verification

The browser suite covers live spectra, Aladin, offline prepared fields, view restoration, language transitions, delayed requests, sharing, navigation, keyboard operation and mobile layouts. Explicit pointer-hit checks exercise Lab with expanded layers at 390, 1024, 1280 and 1440 pixels. First-visit invitations are checked on narrow English and Spanish views. See STATUS.md for final observed counts and deployment evidence.

Final observed results on application commit 4c8e4c0: production E2E 62 passed (1.8m), local E2E 62 passed (1.1m), frontend unit tests 50 passed, type check 0 errors/0 warnings, build passed, data/submission checks 101 passed. Mobile landing Lighthouse: performance 98, accessibility/best-practices/SEO 100, LCP 1.170 s. This observed audit does not establish a latency percentile. The general cold-field and scientific-data limitations remain listed in STATUS.md.
