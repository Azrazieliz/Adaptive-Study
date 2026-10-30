# Adaptive Study — Native Android (ongoing)
This is the native Android activity, not a WebView wrapper. The source is copied from the verified local native worktree; the private PDFs, course pages, structured curriculum, exam banks, media and all user data are intentionally **excluded** from Git.

## Private, untracked inputs (required for a functional APK)
- `app/src/main/assets/study_data.json` — user-owned structured curriculum, exam questions and short flashcards.
- `app/src/main/assets/board_catalog.json` — source-page and SHS board directory.
- `app/src/main/assets/www/assets/**` — original course-page images and offline supporting imagery.
- `app/src/main/assets/legacy_flashcards_20261030.json` — original long cards archived, not active.
- `app/src/main/assets/flashcards_deferred_for_editing_20261030.json` — oversized cards excluded until individually converted.
All assets must be sourced from authorized local copies of the existing project. **Never substitute empty placeholders or web material.**

## Current behavior
- Offline native course catalog, sourced summaries, original-page viewing and PDF renderer.
- Native board memorization (original page + recall exercise, spaced scheduling).
- Native interactive concept/section navigator.
- **Atomic tap-to-flip flashcards**. One factual question on the front, one short answer on the back; no metadata beneath the answer. Four review ratings; persistent scheduling.
- Native QCM and QROC interfaces.

## Required verification before a user-facing full release
The educational audit is not complete. Do not confuse structural validation with source fidelity.
1. Reconcile every course against its current 2026–2027 FC, including all boards (especially SHS, histology and cell biology).
2. Validate every card's claim and original page against the source. Cards under editorial review must not be presented as examiner-certified.
3. Validate QCM/QROC against original annales and corrected QE.
4. Test each functional tab on a connected Android device, not just a desktop browser.
5. Do not label the corpus complete while chapters are missing or partially covered.

Build and package from the local workspace with the existing signing identity. Do not delete the original app data.
