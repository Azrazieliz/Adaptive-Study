# Adaptive Study — v3.36.0 implementation state (2026-11-06)

## Canonical scope
- Existing offline Android application; preserve architecture, previous question/card IDs, progress, grading, original page assets and original mind maps.
- New examination covers all 76 existing courses across 7 subjects. Highest exhaustive memorization priority is SHS, histology, cell biology; teacher-specific chemistry/physics methods may be added later.
- Follow the original user-supplied FC. Annales/QE are FORMAT REFERENCES only, NOT practice questions to copy back into the app.
- For non-SHS exam prep, new A–E QCM with clear question stem, FIVE independent propositions, 1–4 true, individually written true/false corrections, exact FC source evidence per proposition.
- SHS: SHORT meaningful QROC corrections directly readable in ≤8 handwritten lines. Commentary plans must remain separate.
- Flashcards: ONE precise natural question, short answer; course title already displayed in UI; no generic source-label questions.

## Implemented and verified in native local working project
- 227 additional individually authored A–E QCM + 32 previously approved = 259 **new** questions across all 65 non-SHS courses. By subject: histology 82, cell biology 64, biochemistry 36, public health 36, chemistry 24, physics 17. No original annales/QE imported. 358 older QCM remain in database with original IDs, but normal practice only selects `curated35:` and `editorial26:`.
- 132 NEW precise SHS short answers, 11/11 SHS courses, max 63 words / 403 characters; 3 separate new commentary outlines with introduction, problem, 3 axes and conclusion. The 559 earlier unusable QROC chunks were replaced in active SHS data, backed up privately.
- 56 additional manually authored natural flashcards. 845 previously marked active but mechanically phrased flashcards withheld from active study, not deleted; 1,512 active cards across all 76 courses. Total historic card records 8,270, IDs and progress retained.
- 76/76 existing course source boards and 2,167 source-page references intact, 63 original mind-map entries/images intact.
- Exact source page/label/value evidence, question schema, five options/rationales, original IDs and asset existence verified by private QA scripts.
- Java native UI: separate `short-answer` and `commentary` readers; correct new-only QCM selection; filter only approved cards; prioritize manually curated cards.
- Built offline with Gradle 8.13: **BUILD SUCCESSFUL**. Signed APK verified by apksigner and binary asset inspection:
  `D:\AdaptiveStudyRecovery\AdaptiveStudy-NATIVE-v3.36.0-EDITORIAL-QCM-SHS.apk`, 319.3 MiB.

## Known incomplete items — do not misrepresent as finished
- 259 new QCM is not the requested *large* exhaustive question bank. Some courses currently have only 2 new QCM. Source drafts authored with exact FC evidence are a solid base, not full certification of all five-option propositions.
- 949 original course-page references lack indexed facts (some covers, many genuinely unreviewed). Exhaustive editorial reconstruction of all 76 courses / Complet / Essentiel / Comprendre remains incomplete.
- 6,758 historic cards are not currently approved for active questioning; 845 newly withheld questions need rewritten natural prompts, not mechanical sentence editing.
- User supplied teacher-specific chemistry/physics problem-solving approaches are not yet provided. Physics and biochemistry also require fully developed calculation exercises, not only knowledge QCM.
- Wireless ADB connection was unavailable at v3.36.0 installation attempt on 2026-11-06; **signed APK exists on PC but v3.36.0 is not installed on phone**. Last known installed v3.35.1. Do not claim on-device v3.36.0 verification.

## Private working directory and check scripts
`D:\AdaptiveStudyRecovery\source_transfer\academic_authoring_queue_20261105\authored_qcm_20261106\`
- `AUTHORIAL_QCM_PROMOTION_REPORT_20261106.json`
- `SHS_REAL_QROC_CORRECTIONS_INTEGRATED_20261106.json`
- `NATURAL_FLASHCARD_GATE_20261106.json`
- `RELEASE_V3360_SOURCE_QA_REPORT.json`
- `v3360_validate_signed_apk_assets.py` in source_transfer

No private source PDF, user course image, private question-bank JSON, academic data, or APK should be committed into public GitHub repo unless explicitly authorized.
