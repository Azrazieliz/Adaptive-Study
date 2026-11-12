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

## Native source corrections staged after preservation (not built)

The recovery branch also contains a narrow, source-only patch to `native-android/app/src/main/java/com/azrazieliz/adaptivestudy/MainActivity.java` (commit `99a7bcc3c5a638159dfaa87bf5b3e6a68edeaf70`):

- SHS QROC displays its constraint from either legacy `lineLimit` or packaged `handwrittenLineLimit`. This fixes the proven v3.36.9 field mismatch without rewriting corrections.
- The Home flashcard progress denominator and reviewed count now use **active approved card indexes** instead of all historical inactive records. Saved review keys are unchanged.
- The native PDF cache key includes the installed application version, so a newly versioned APK no longer automatically reuses an obsolete previously cached original PDF. No deletion of user cache or study state.

Exact source snippets were inspected after the change. **Not Gradle-compiled, built, installed, or phone-verified**; these are staged code changes only. Academic content, mode diagrams, mind maps and native adaptive engine remain untouched.

## 12 November — academic-first visual learning implementation (source-staged)

**Phone evidence:** The owner-provided Android screenshots show `v3.36.9-etude` running as a native offline application and Asterion Control's listener/screen-sharing/input access active. This resolves previous uncertainty about the installed application *version shown in that screenshot*. It does not establish academic acceptance or a device-progress backup.

**Native renderer:** `MainActivity.java` now optionally loads `academic_visuals_verified_20261112.json` (separate from `study_data.json`, so no curriculum regeneration), and can render FC-linked **flow**, **comparison** and **causal feedback** boards directly in Essentiel, Complet and Comprendre. Each visual links back to original FC page(s), and Comprendre adds only concise exam-useful deductions. No map viewer panel or second application/web view. Malformed optional visual assets are disabled and logged without crashing course loading. Code latest commit `e1eabbf4b7ed188b9d52b9a6290e225b7f10834f`.

**Private provisional academic content:** `D:\AdaptiveStudyRecovery\PRIVATE_ACADEMIC_VISUALS_20261112\academic_visuals_provisional_20261112.json`, SHA-256 `c9dfe6260fbdfb8e94aec1e0d22d7af2f71891563a746a67c33f40e76c1baf4f`. Six original FC-linked visual annotations for the three existing SHS courses:
- `shs_prelevement_transplantation`: living/deceased donation consent comparison (FC pp. 10, 13); graft/immune response/immunosuppression pathway (FC pp. 2, 7).
- `shs_socio_iss`: social position to health inequality pathway (FC pp. 11, 13); obesity/social stigma feedback (FC pp. 18–19).
- `shs_sante_environnement`: danger/exposure/risk process (FC pp. 7–8); epidemiology/toxicology comparison (FC pp. 9–10).
All currently `FC_OCR_CROSSCHECKED_PENDING_IMAGE`: **NOT released and NOT marked academically reviewed**. Three original image-only PDFs were verified present within v3.36.9 (20, 28 and 21 pages); extracted PDF text was blank, so historical OCR was consulted only as preliminary source evidence. The PC screenshot of the displayed original page returned an all-black capture, therefore visual confirmation was NOT completed. No need to manufacture confidence from OCR.

**QA:** `tools/validate_academic_visuals.py` committed and exercised on the actual private 81-record curriculum. Structural test **passed** (6 boards; 3 flows, 2 comparisons, 1 causal loop; all page references valid; 0 page-image-reviewed; release_approved=false). The Java activity, including earlier QROC/flashcard/PDF cache corrections and the new renderer, **compiled successfully with Android API 36.1 `javac -source/-target 17`**, exit 0, with only standard compiler warning about module path/deprecation. **No Gradle APK build, installation, or on-phone visual acceptance.**

**Further visual formats identified, NOT yet implemented:** annotated original-course figures and compact decision trees for chemistry/physics/methods, each with source references. These should replace unnecessary prose only after rigorous source checks. Do not resurrect mind-map generation or increase Comprendre complexity beyond exam deductions.

**Next academic gate:** visually compare each of the cited FC pages, sign individual board review evidence, then enable that board by setting `PAGE_IMAGE_REVIEWED` and preserving evidence. Subsequently complete remaining incomplete chapters and incorporate teacher methods without refreshing unrelated datasets. The exact new course inventory since Nov 8 is still unresolved.

## Academic correction candidate — five fabricated courses removed non-destructively

The owner confirmed that `histo_embryo`, `biocell_cytosq`, `biocell_mec_integrine`, `biocell_dev` and `biocell_cycle` were invented during earlier assistant development, NOT five genuine missing FCs. `tools/quarantine_fabricated_courses.py` creates a separate 76-course curriculum from the **actual v3.36.9 APK's curriculum**, with source SHA guard and no source overwrite. It archives the five false chapters plus **16 associated question records, 456 associated flashcards, five guides, page registries, metadata, old map registrations and original-document mappings** in a separate private quarantine. No other reference to the false IDs remains in the new candidate. Neither the original v3.36.9 APK nor any other on-phone app data has been changed.

**Candidate** `D:\AdaptiveStudyRecovery\PRESERVATION_20261112_NO_APK_BUILD\V3369_76_REAL_COURSES_CANDIDATE.json`, SHA-256 `aa81226ec76d5a28873cac80a95fc680651311a9b50ba36cb8e40ca95cbaa6a6`. **Archive** `FIVE_INVENTED_COURSES_QUARANTINE_PRIVATE.json`, SHA-256 `0fac0443fc772d0d35bc85ea05d21a264df84fb9531435095215503454058e1a`. The v3.36.9 original source checksum was verified unchanged.

**Independent real-data comparison PASS:** The remaining 76 courses' `courseGuides`, `coursePages`, `courseMeta`, `mindMaps` and `courseSourceDocuments` entries are identical before/after. All unrelated question and flashcard records are identical. The six private academic visual drafts still pass structural validation against the cleaned 76-course candidate; **all six await original page-image review**.

**Updated structural gap report (not academic certification):** `PRESERVATION_20261112_NO_APK_BUILD\ACADEMIC_GAP_76_REAL_COURSES_20261112.json` measures current source-page fact-link coverage from the latest v3.36.9 dataset, excluding the fabricated records. It does not establish that any lesson covers every table, figure, exception or exam-important detail.

**Important:** The native viewer and actual installed APK still contain historical content until a later fully verified release is built. No APK, user-data or original source has been updated by this candidate. Do not claim the removal has been installed.

## Quantified 76-course source-index gaps after v3.36.9 academic changes

Private report `PRESERVATION_20261112_NO_APK_BUILD\ACADEMIC_GAP_76_REAL_COURSES_20261112.json`: **1,787 original FC page references in 76 genuine chapters; 423 (23.7%) have zero linked course-guide facts**. This explicitly excludes the five fabricated records. Includes 12 SHS courses after the FC Actu 12 addition.

| Subject | Course records | Page references without indexed facts |
|:--|--:|--:|
| SHS | 12 | 38 / 285 |
| Histology | 12 | 32 / 330 |
| Public health | 10 | 83 / 318 |
| Cell biology | 12 | 132 / 297 |
| Biochemistry | 10 | 91 / 325 |
| Chemistry | 11 | 31 / 144 |
| Physics | 9 | 16 / 88 |

Highest current gaps by absolute count: `bio_biomol` (62/83), `biocell_noyau` (40/50), `biocell_endo` (31/34), `sp_facteurs_env` (28/30), `biocell_endocytose_exocytose` (26/33), `sp_produits_sante` (22/32), `histo_fecondation` (19/22), `biocell_mito_perox` (17/21). Empty text-index page may be a cover, illustration, title or genuine content deficit; original source must be visually read before altering or claiming completeness. A page with one or more indexed facts is **not** a certified complete FC page.

This establishes the actual academic reconstruction priority before visual polish, major adaptive additions, or any new APK release.

## 12 November — histology figure source population (current checkpoint)

**Owner-approved formats:** original histological figures, annotated source-image identification, concise comparison boards and deduction-focused mechanisms. No anatomy course is being added; the subject is **Histology**. Old rejected mind maps are not restored.

**Original FC visual inventory, no regeneration:** `tools/inspect_histology_source_figures.py` inspected the **330 source pages across the 12 genuine histology courses** inside the existing signed v3.36.9 APK, with **zero absent page-image files**. It ranked candidate source figures and saved four private contact sheets to `PRIVATE_ACADEMIC_VISUALS_20261112\HISTO_SOURCE_REVIEW`. Heuristic rank only; original diagrams were then inspected visually rather than automatically certified.

**Implemented actual original-FC image crop renderer:** [MainActivity.java](https://github.com/Azrazieliz/Adaptive-Study/blob/work/controlled-recovery-incremental-20261112/native-android/app/src/main/java/com/azrazieliz/adaptivestudy/MainActivity.java) handles `source_figure`: verifies that the path matches a registered course FC page, requires source-review evidence, crops the real original page to the relevant schema, renders it in a pinch-to-zoom native image view and offers compact revealable identification criteria with original-page links. No giant viewer control panel, no extra standalone image download, no web app. The code was **successfully compiled by Android API 36.1 javac**, exit 0, following the new figure-mode implementation (ordinary module-path/deprecation compiler warnings only).

**Private academic content added to native working assets:** `D:\AdaptiveStudyRecovery\AdaptiveStudyNative\app\src\main\assets\academic_visuals_verified_20261112.json`, SHA-256 `c3f1dcf55b7e630229fcf0e895ede3ffca1411060eb1da191b62b1c54a5ec185`. The file provides **17 visually source-reviewed, original teacher-FC figure boards across all 12 genuine histology courses**, precisely:
- `histo_epitheliaux` — 3: basal membrane layers, electron micrograph, simple/stratified/pseudostratified tissue images.
- `histo_conjonctifs` — 2: collagen coloration and ultrastructural fibers.
- `histo_cartilage` — 1: perichondrium layers and chondroblasts.
- `histo_osseux` — 2: osteon schematic and microscope identification.
- `histo_muscles1` — 1: striated skeletal muscle longitudinal/transverse images.
- `histo_nerveux` — 1: neural tube and neural crest source schematic.
- `histo_fecondation` — 2: oocyte membrane zones and ovulation mechanism.
- `histo_methodes` — 1: HES, Masson and MGG source images.
- `histo_sanguin` — 1: hematopoietic differentiation tree.
- `histo_semaine1` — 1: tubal migration and cleavage.
- `histo_semaine2` — 1: early uteroplacental lacunar flow/villi.
- `histo_semaine3` — 1: tertiary villi, free vs anchoring villi.

Each item has a stable ID, exact original-source image path and page number, normalized crop coordinates, source image SHA-256, exam-focused recognition notes and is stored **separately** from `study_data.json`. The academic visual validator cross-checks original images against the real APK and the 76-course candidate, rejecting invented course IDs and unreviewed/fake source evidence. **17/17 passed structural, source-image hash and review-evidence checks**, `pending=0`. Earlier negative QA confirmed fake reviewed status is rejected. This certifies those specific figure references/notes, **not** full scientific completeness of their underlying courses.

**Preservation:** The 76-course academic candidate, every existing question/card, course guide and original FC page, previous APK and on-phone study data are unchanged. Previous 3/7/12/16 board versions are preserved as private archives. **No full APK built, signed, installed or tested on the phone.**

**Academic completeness is still NOT reached:** The 76 genuine courses have 1,787 page references, **423 without an indexed structured fact**, including serious deficits in Biochemistry, Cell Biology and Public Health; even an indexed page can be academically incomplete. Six provisional visual boards for the three SHS courses remain unapproved and not in the verified asset. New courses and teacher methods reported after November 8 were **not located in the recent PC input scan**; this does not establish absence on the phone or elsewhere. The question/card/QROC population, comprehensive source-page editorial pass and native adaptive learning are still open. Do not treat the 17 curated histology figures as full course completion.
