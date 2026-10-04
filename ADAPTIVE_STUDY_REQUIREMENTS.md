# Adaptive Study — frozen requirements

## Scope and authority

1. Only the user-provided course PDFs, QE, annales and corrections are authoritative content sources.
2. Course PDFs define knowledge and flashcards. QE/annales define question style and exercise structure.
3. Do not add, “complete”, normalize or correct course facts from external knowledge.
4. Preserve source file/page/version metadata. Visual questions require the complete usable figure/table context.
5. Missing source material remains unavailable rather than generated from assumptions.

## Mobile UX

- Mobile-first, compact, low-scroll interface.
- Home screen shows mastery by subject/chapter, errors, timing and the current adaptive priority.
- Fast navigation back to quiz selection and direct chapter actions.
- Images/graphs/PDF pages must be correctly placed, readable and zoomable.
- Startup must reject mixed engine/content builds instead of silently loading stale cached code.

## Adaptive behavior

- Prioritize repeated errors, low scores, excessive active response time, weak mastery and overdue/unseen work.
- Timing is diagnostic, not a raw-score penalty.
- QROC reference target: 10 minutes.
- Home mastery must be based on actual attempts, not placeholder/default content counts.

## Multi-course selection

- QCM setup must allow selecting one or multiple active courses within the chosen subject.
- Flashcard setup must allow selecting one or multiple active courses; when all subjects are selected, active courses are grouped by subject.
- Adaptive priority and session statistics must respect the exact selected course set.
- Original-PDF browsing may require a single course because source pages are course-scoped.

## Questions and exercises

- Match the observed exam style per subject/course; avoid generic placeholder wording.
- Detailed corrections must explain why options are true/false and link back to source-supported course points.
- Santé publique: contextualized A–E questions; preserve year/population/territory/age/sex/denominator/unit; do not infer causality from descriptive data.
- Histology: close A–E options in one topic; images/schematics only when the complete source visual is present.
- Cell biology: course QCM plus experimental scenarios; distinguish compatibility from proof.
- Biochemistry: multi-question experimental dossiers; not isolated definition drills as exam simulation.
- Chemistry: isolated A–E reasoning/calculation; calculator not assumed.
- Physics: linked large exercises; calculator allowed.
- SHS: QROC and text commentary only when a usable sourced task/correction exists; never fabricate unsupported commentary material.

## Mind maps

- Mind maps must use course PDFs as the factual authority.
- QE/annales may guide emphasis but must not contribute facts absent from the course.
- One landscape 16:9 map per course unless a validated course already uses sub-maps.
- Dense but readable: short fragments, strong hierarchy, no tiny prose blocks, no decorative clutter.
- A course exposes the map action only when the corresponding image asset is present in the private build.

## Course methodology reminders

- User-provided course methodologies can be stored as per-course reminders.
- Reminders appear compactly in course views and must never be invented from external knowledge.
- Methodology reminders are separate from authoritative course facts.

## Flashcards, syntheses, errors

- Flashcards must be autonomous, natural and reversible for rereading the question after revealing the answer.
- Avoid synonymous duplicate cards and support-dependent wording (“on this page”, “in the figure”, etc.).
- “Essential” is a dense pre-exam reread: compact enough to finish quickly, limited to the highest-yield repères, with no per-item source block or decorative padding that forces excessive scrolling. “Complete” is exhaustive within the supplied corpus.
- Error notebook must be filterable and show correction, source, repetition count, timing and remediation actions.

## Native APK behavior

- Native APK mode must never display PWA/browser installation controls.
- Native APK mode must not register the PWA service worker; assets are already packaged locally.
- Android system-bar insets must be respected so headers and bottom navigation are never clipped or hidden.
- The in-app bottom navigation must sit above the Android OS navigation/gesture bar, not underneath it.

## New course ingestion

- When the user supplies a course together with QE, annales, training questions or corrections, integrate the course PDF as the factual authority and preserve the supplied question/correction pages as documentary originals.
- New course pages must be readable in-app and source-linked.
- Syntheses and flashcards must be derived only from verified course-page content; OCR residue or uncertain scan fragments must never become active study facts.
- Derived questions must carry positive evidence for every true or false proposition and must remain autonomous.
- Do not label a derived item as an original QE/annale question. Original scans stay separately traceable.
- New course integration must update course inventory, source metadata, active-bank counts and release validation together.

## Release discipline

- One coherent version identity across engine, content, exercises, original corpus and service-worker cache.
- Keep private educational data out of the public repository.
- Run structural/data validation before producing an APK or updating `main`.
- Do not ship an intermediate or partially synchronized build as the current release.

## Autonomy of questions and flashcards

This is a hard release requirement.

- Every flashcard must be independently understandable without knowing which PDF, page, fiche or prior card it came from.
- Every flashcard must contain enough natural subject/context wording to be understandable on its own. The chapter may be shown as separate metadata and must not be mechanically prepended to every prompt.
- No unresolved pronouns or deictic wording such as “this experiment”, “this example”, “in this case”, or “according to the document/FC/course”.
- Mechanical chapter-name prefixes such as `Chapter — question` are prohibited; autonomy must come from the wording itself, not repeated boilerplate.
- Every question must contain all information needed to answer it. If a figure, table or page extract is required, that media must be bundled with the same question and must load in the app.
- Questions must never depend on remembering a previous question in the session.
- Source metadata remains attached for traceability, but it must never be required to understand the prompt.
- Release validation must fail if these rules are violated.
