# Adaptive Study — controlled native recovery checkpoint (2026-11-12)

**Project continuity:** this is a continuation of the existing standalone offline Android app, not a restart and never a web/PWA migration. Academic and exam correctness take precedence over arbitrary feature counts or builds. The final ranked exam is less than one month away. [Full audited defect list: Issue #4](https://github.com/Azrazieliz/Adaptive-Study/issues/4).

## Actual environments and version evidence

- Existing authorized transport: private GitHub `Azrazieliz/Asterion-Control-Bridge` → persistent Windows worker → paired Samsung, no new connector/gateway. Phone reported SM-S948B / Android 17 and installed package `com.azrazieliz.adaptivestudy.preview`.
- Current Windows study workspace: `D:\AdaptiveStudyRecovery`; native editable files at `AdaptiveStudyNative/app/src/main/`; original working Git repository at `Adaptive-Study/`; recovery corpus repository at `AdaptiveStudy-Course-Corpus/`.
- Actual existing PC APK file: `AdaptiveStudy-NATIVE-v3.36.9-TROIS-SHS-CORRIGES-INSTALLABLE.apk`, **791,266,559 bytes**. Existing preceding versioned APK files are preserved.
- Installed phone version **not verified**. Standard Windows ADB currently returns no device; native Asterion Control is connected, but ChatGPT had an active *unsent draft* and we did **not** switch foreground apps or disturb it. No APK was installed.
- Private snapshot: `D:\AdaptiveStudyRecovery\PRESERVATION_20261112_NO_APK_BUILD`. 10 existing critical source and academic JSON/Java/Gradle files copied with SHA-256 manifest; copy command exit code 0, no missing files. The phone's saved private study progress has **not** been backed up, so this snapshot is not a device-progress guarantee.

## Existing curriculum source-of-truth snapshot

- Native working `study_data.json` and bundled v3.36.9 APK both have **81 registered chapter records**, **617 historical question records**, **8,270 historical flashcard records**, **81 course guides**, **81 course page registries**, **76 mind-map registrations**, **7 subjects**.
- Five historical *invented, non-course* IDs are still present in stored JSON and the v3.36.9 APK: `histo_embryo`, `biocell_cytosq`, `biocell_mec_integrine`, `biocell_dev`, `biocell_cycle`. The November 8 Java source explicitly excludes them from active catalogue via `INACTIVE_COURSES`. Do not confuse 81 stored entries with 81 genuine courses, or reintroduce these five as legitimate FCs.
- Live Windows `study_data.json` SHA-256 before work: `02f4ffb2c53cc2a42c6bd7f2cbfddfc85a4ec6a9d430c6131fdff9af6876807a`. v3.36.9 APK `assets/study_data.json` SHA-256: `ccb42a7ea3a2049ec9665cc8d8c9e7f08b6bc8f248a692b51f27735cd0ffb773`.
- **Precise difference:** only `courseGuides` for `shs_prelevement_transplantation`, `shs_socio_iss`, `shs_sante_environnement` differs. Chapter records, practice record lists, map registrations and page registrations were identical. Other root-level fields are also semantically identical as proven by the exact candidate reproduction test below.
- Current original private archives include `source_transfer/Courses_complete_from_phone.zip` (123 entries) and `source_transfer/Courses_20261103_new.zip` (30 entries), with full FCs plus QE/ACC/source materials. These do not establish receipt of the additional later user-reported courses; reconcile their exact files before admitting any new course.
- No source PDF content or private academic data may be committed to public GitHub.

## Implemented now — fail-closed incremental update path

Branch: `work/controlled-recovery-incremental-20261112`, based on `fix/emergency-native-study-20261108`. No merge to main, no APK build.

1. `tools/verify_incremental_study_update.py` — compares private JSON files or APK-embedded `study_data.json` and fails on unrelated course modifications, deleted records, mismatched stable IDs, unapproved new course records, unscoped root changes or duplicate IDs. Does not modify input or certify academic facts.
2. `tools/apply_incremental_study_patch.py` — explicit per-course patch, verified source SHA, stable record upserts, never removes existing records, cannot overwrite base file and creates only a separately named candidate. New courses need separately authorized `--permit-new` plus original source provenance and page registration.
3. **Positive real-data test:** The verifier passed when exactly three known SHS course guide changes were allowed. It rejected the same candidate with only `shs_socio_iss` allowed (return code 2), correctly flagging the other two.
4. **Exact reproduction test:** Generated a private patch containing only the three targeted SHS guides from real v3.36.9 APK. Applied it to the preserved original working dataset. The generated candidate was **semantically identical to all fields of the entire v3.36.9 bundled `study_data.json`**. The original working file SHA remained unchanged. Existing assets not named by the patch were preserved.
5. Private tests and outputs are under the preservation folder; keep them private. This is a structural source-level guard only. It does not certify correctness, completeness, required teaching diagrams, native UX, signing, installation or active adaptive behavior.

## Binding next priorities and blocked gates

1. **Identify the exact installed version/data and preserve its progress first.** Only inspect phone when ChatGPT unsent draft and foreground safety are assured; never uninstall or reset.
2. **Confirm the entire genuine FC and teacher-method inventory** including additional courses after November 8. Do not invent unspecified FCs; distinguish original FC, updated FC, question papers, corrections and methods. Keep source hashes and per-page provenance.
3. Correct **Essentiel** (all exam-critical facts), **Complet** (all source academic content in comprehensible structured form) and **Comprendre** (efficient mechanistic reasoning solely to support exam deductions; avoid unnecessary depth). Embed precise diagrams, comparison boards, labelled anatomy and causal flows directly inside lessons; not huge prose walls.
4. Complete realistic, adequate-volume and per-course reviewable QCM, short atomic flashcards, source-accurate SHS QROC with concise corrections and separate commentary where applicable. Preserve existing good records and IDs.
5. Finish native Android adaptive engine across QCM, cards and SHS (concept-level mastery, error and active-time feedback, spaced reviews, ranked-exam deadline planning, and persistent progress); **do not replace with old JavaScript/web app**.
6. User explicitly rejected all existing mind-map outputs; remove when safe and authorized after preservation, then only the exact user-supplied 16:9 reference style, with no oversized viewer panel. Do not regenerate mind maps as a prerequisite for academic content.
7. Validate source coverage and native UI/revisions; only then consider a coherent APK. Existing **build freeze** remains respected. No build, signing, installation or user-data migration occurred here.

**Implemented status:** PC snapshot complete; incremental gate and separate candidate creator implemented and proven on real data; academic and native release readiness NOT attained. No work is running in the background by virtue of this document.
