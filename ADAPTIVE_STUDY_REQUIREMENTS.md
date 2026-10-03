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

## Flashcards, syntheses, errors

- Flashcards must be autonomous, natural and reversible for rereading the question after revealing the answer.
- Avoid synonymous duplicate cards and support-dependent wording (“on this page”, “in the figure”, etc.).
- “Essential” is a dense pre-exam reread; “Complete” is exhaustive within the supplied corpus.
- Error notebook must be filterable and show correction, source, repetition count, timing and remediation actions.

## Release discipline

- One coherent version identity across engine, content, exercises, original corpus and service-worker cache.
- Keep private educational data out of the public repository.
- Run structural/data validation before producing an APK or updating `main`.
- Do not ship an intermediate or partially synchronized build as the current release.