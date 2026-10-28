# Adaptive Study — Authoritative rebuild requirements (28 October 2026)

## Purpose
The app must replace inefficient rereading of long course PDFs with **complete, ultra-dense, exam-oriented learning**, many realistic questions, high-value flashcards and adaptive review with Android notifications. A PDF viewer is *not* a completed learning app.

## Exam formats (corrected)
- **SHS**: QROC and supported written/document questions, complete answer criteria. Essential must include *every* item from a required scoring board. Partial list recall can receive zero.
- **All other subjects: QCM A–E**. This includes Physics and Biochemistry.
- Histology: closely comparable A–E propositions on structure, location, morphology, techniques.
- Santé publique: A–E propositions with context, periods, population, denominator, units, graphs.
- Biologie cellulaire: A–E knowledge and experimental reasoning; whole figures and controls.
- Biochimie: **A–E in linked multi-question experimental dossiers**, not mere definition quizzes.
- Chimie: A–E calculation/reasoning; plausible near-neighbor distractors and units.
- Physique: **A–E within linked, multi-step problems**. No Physics QE at all; model from annales with corrections. Favor the ordinary operational forms of formulas; derivations are secondary.

Every generated A–E question must have one coherent topic, five relevant and believable assertions, 1–5 correct when format permits, an A/B/C/D/E justification and positive course-page evidence for each false statement. Never assemble unrelated facts in the same options. Original QE/annales and their corrections must remain separate, intact and linked.

## Lessons
- **Essential**: reorganize high-priority FC information into compact comparison boards, steps, formulas, lists, conditions and exceptions with minimal scrolling.
- **Complete**: retain every verified information unit from the course PDF, in a denser structured presentation, with page links. Do not drop secondary facts.
- SHS required boards and lists must be intact in both modes; no silent truncation.
- Physics prioritize usable final formulas, variables, units, conditions, solution methods, not routine derivations.
- No unsupported OCR facts or external additions. Audit source page and complete figures.

## Flashcards
Replace all formerly active 5,805 cards with source-based, autonomous prompts targeting indispensable knowledge, meaningful contrasts, entire SHS required lists, formulas and conditions, mechanisms, and exam traps. No generic QCM converted to cards, invented trivia or quotas.

## Adaptive behavior
- Chapter mastery recalculated after each question/card from correctness and active response time (time modulates mastery, not raw exam marks).
- Full study set only counts as working on a chapter when all planned questions or flashcards are answered and graded; opening or abandoning the session does not count.
- Default threshold 75% (configurable), with next review 1, 2, 3, 5 or 7 days as mastery varies; at most seven days after the last completed set.
- Android notification permission, daily due digest, offline alarms and reboot persistence. Prioritize weaknesses/overdue chapters and offer direct practice.

## Implementation state — NOT A RELEASE
- Private local development app at `D:\AdaptiveStudyRecovery\Adaptive-Study\local_instance\private_app\app`.
- The retired banks (2,621 questions and 5,805 cards) were backed up and disabled locally, not deleted from history; 969 original QE/annales/training units still available.
- Existing guides have been converted into compact linked dense boards (42 guides out of 50 source-page courses). SHS high/complete retains whole sections. These guides still need editorial recertification for exhaustive coverage.
- `adaptive_review.js`: live mastery, strict completed-set accounting, 7-day/dynamic due schedule, home priorities, notification payload; browser and deterministic logic tests passed.
- Native `StudyBridge.java`, `StudyReminders.java`, Manifest and Activity: offline daily reminder digests, permissions, reboot persistence. Android Java Gradle compilation passed; no real phone notification test yet.
- Original PDF questions have A–E controls (SHS written field) plus displayed original corrections and self-grading; it is temporary source-accurate practice, NOT the required new generated question bank.
- The uploaded `Courses.zip` has 122 PDFs and was audited, but has NOT been imported into the private PC build.
- No quality-certified replacement question/card bank exists yet. Do not claim the app is finished or deliver the development snapshot as a completed APK.

## Release gates
All user PDFs integrated, all lessons recertified as exhaustive and dense, substantial course-specific A–E/QROC new banks proofread with individual option explanations, high-value cards sourced, native device notifications and in-place signing/upgrade tested. Never expose private medical PDF content in this public Git repository.
