# Adaptive Study Native v3.29.6 — recovery record (2026-10-30)

Source: `native-android/app/src/main/java/com/azrazieliz/adaptivestudy/MainActivity.java` and existing private local curriculum. **Do not replace or delete user study data.**

## Restored from original Adaptive Study logic
- QCM partial credit: 0 errors = **1**, 1 error = **0.7**, 2 errors = **0.1**, 3+ = **0**. Count omissions and incorrect selections.
- QROC SHS: self-assessed **0 or 1**; full expected board content remains mandatory. Time reference = **600 seconds**.
- Subject coefficient metadata preserved in `study_data.json`: SHS 10, histology 8, public health 8, cell biology 8, biochemistry 8, chemistry 6, physics 5.
- Time target = exam duration / approximate question count; active-time tracking is paused when Android backgrounds the quiz and when correction is revealed.
- Results and response times persist under additive SharedPreferences keys. Earlier keys continue to work.
- Flashcard rating interval restored from legacy: Again 1d, Hard 2d, Good 4d, Easy 7d.

## Native interface and curriculum corrections
- Formula numerators / denominators displayed as stacked Android views; no exam-irrelevant limit derivations.
- Formula duplicate body descriptions suppressed where the expression is already displayed. Atomic fact table remains for non-equation information.
- Native colored connected graph (hub + expandable branch nodes) instead of static hard-to-read map image. **Not yet fully equivalent** to illustrated user reference: content-specific diagrams and visual elements need further design/content work.
- Six document-processing annotations removed from active lesson data; original local data preserved at `study_data_before_20261030_content_repair.json`.
- Updated-cell-biology superseded original pages 9, 14, 17 suppressed in active source navigator and memorization catalog; replacement pages 10, 15, 18 remain accessible. Original source files remain unchanged.
- Edited trivially easy microscope-resolution conversion option in one histology QCM to a clinically relevant microscopy-fact alternative with the original correct key. 64 options had obsolete “la FC” wording removed.
- 46 generic flashcard questions rewritten to direct prompts, 836 lesson/card phrasings cleaned, source archive retained.
- 7,615 active short flashcards, 2,456 questions, 73 course entries. Existing content is **not fully certified or exhaustive**.

## Mandatory unfinished work
1. Read *all* 2026–2027 source PDFs and newly added course files; fill the 12 courses without guides and ensure each page/board is indexed.
2. Re-verify every question, option and marking key against annales, QE and source; quarantine invalid/trivial/generated questions.
3. Verify SHS, histology and cell biology boards in full. Source images remain authoritative.
4. Add genuine content-specific illustrations to concept maps, matching the user's example without zoom-to-read; current connected view is a partial implementation.
5. Test formula board, mind map and timed quiz on device when the user is not using another app.
6. Never declare finished or exam-ready based solely on counts/compilation.

## Private artifact locations on authorized PC
- `D:\AdaptiveStudyRecovery\AdaptiveStudyNative\app\src\main\assets\study_data.json`
- `D:\AdaptiveStudyRecovery\AdaptiveStudyNative\app\src\main\assets\board_catalog.json`
- `D:\AdaptiveStudyRecovery\AdaptiveStudy-NATIVE-v3.29.6-INSTALLABLE.apk` (signed)
- Old deployed versions and all assets preserved. Private PDFs/course extracts must not enter public Git.
