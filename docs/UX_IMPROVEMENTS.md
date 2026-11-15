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

## Final challenge-focused revision

Gaia recovery now has its own request lifecycle. A catalog retry preserves the
loaded stack, selected observation, comparison and share readiness. Pending
catalog data are labelled as loading, rather than prematurely claiming that the
target has no Gaia counterpart. Cancelled requests cannot replace a later field. Free-field counterpart matching
is derived from the retained catalog and position, so replacing a detector stack
does not lose its marker or trigger an unnecessary catalog query.

The API tries ESA DR3 first, then the documented ARI Heidelberg DR3 service with
the identical ADQL cone. Requests have bounded per-provider wall-clock budgets;
the selected provider URL is retained with each returned source. Invalid CSV,
HTTP-200 error documents and potentially truncated cones fail explicitly and are
not cached as an empty sky. A cache-schema bump avoids reusing older unvalidated
remote entries. Prepared target catalogs remain available independently.

Starting a guided visit comparison now magnifies the target and frames its two
predicted positions, using the retained proper motion at the actual observation
epochs. The request waits for viewer sizing, including when leaving Diff λ.
This camera framing is not a new motion measurement. Reset restores the field;
ordinary playback does not keep overriding a user's pan or zoom. Unsupported or
out-of-field predicted positions leave the camera unchanged.

Tour copy now explicitly permits color differences and artifacts in subtraction
residuals. The revised demo script, opening identity card and scientific wording
corrections are in `docs/DEMO_SCRIPT.md`; the team's video assets were not edited.

### Human validation still to perform

Automated browser checks do not establish actual learning or ease of use. Ask
three people unfamiliar with the product to complete this short observation
exercise without coaching; record their consent and only aggregate outcomes:

1. Open Explore, start the guided Barnard comparison and identify the two dates.
2. Explain what changes in the image and what the Gaia overlay predicts.
3. Open a source spectrum and identify what its axes represent.
4. Select an asteroid and find its diameter interval and single-visit caveat.
5. Share a view, reopen it and explain which observation it contains.

Record completion, elapsed time, assistance required and one concrete point of
confusion per task. Record whether each person can distinguish a prediction from
a measurement and an estimate from a confirmed discovery. No participants have
been recruited and no results are claimed by this document.

Provider documentation: https://gaia.ari.uni-heidelberg.de/help.html and
https://gaia.ari.uni-heidelberg.de/tap.html.
