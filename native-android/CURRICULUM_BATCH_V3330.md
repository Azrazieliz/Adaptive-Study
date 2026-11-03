# Adaptive Study v3.33.0 — curriculum-wide reader and exam PDF removal

## Authorized change
Removed the old original annales/QE PDF viewer, the per-question scans called "vraies questions", and all associated links FROM THE STUDENT APK. All 938 removed files (360.7 MB) are privately archived outside the Android app, with hashes, at D:/AdaptiveStudyRecovery/source_transfer/private_exam_assets_removed_from_app_v3330/manifest.json. These assets MUST NOT be pushed to public Git.

## Preserved in Android
- 75 existing chapters including weeks 1 and 2 and fertilization
- 341 original authored-source practice QCM A–E/QROC with correction rationales
- 1904 active flashcards after correction of 138 ambiguous fronts, with 75 quarantined separately in private storage
- Original FC pages, current original learning maps, 29 additional exam-focused boards, 75 course titles, course explanations, timers, coefficients, scoring and user progress

## Course reader
Complet now opens the full SOURCE-INDEXED TEXT, organized by section for each course rather than presenting only original PDF images. No arbitrary cap on facts or first pages. A full section table of contents and per-section source-page jump are available. The original pages remain accessible in the separate Pages reader. Essentiel and Comprendre retain their existing content, with expert mechanism explanations for the three priority subjects.

## Academic scope, not falsely certified
The 75 chapter entries and their original FC source images remain present, but complete transcription of all scan labels, illustrations and tables AND expert-level scientific explanations of every chapter still require editorial work. The implementation is a curriculum-wide UI and source-indexed reader improvement, NOT 100% certification of the scanned educational content. Never claim otherwise.

## Packaging
Old fallback media from previous unsigned APKs must be filtered: no /original_questions/, /new-course-preview/ or original exam PDF pages. All original FC pages and mind maps must remain. Build/sign/install and actual Android launch must be verified separately.
