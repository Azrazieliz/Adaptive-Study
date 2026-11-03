# Adaptive Study — exam-first midway release v3.32.0

**P0 source of truth:** [00_START_HERE_ADAPTIVE_STUDY.md](../00_START_HERE_ADAPTIVE_STUDY.md). This release preserves the existing native Android app and progresses the user's three immediate examination courses.

## Exam-focused curriculum added

| Course | Original FC page images | New source-linked atomic cards | Newly authored A–E practice questions | Original assessment documents | Detailed molecular/causal sections |
|---|---:|---:|---:|---:|---:|
| Première semaine embryonnaire | 18 | 91 | 13 | 4 (ACC Sujet/Corrigé and QCM Sujet/Correction) | 17 |
| Deuxième semaine embryonnaire — Partie 1 | 11 | 57 | 11 | 2 (ACC Sujet/Corrigé) | 10 |
| Fécondation | 22 | 94 retained | 8 | 4 existing | 21 |

Total: 75 chapter entries; 341 active practice questions; 1,979 active flashcards in the data. The new midway question set has 32 new multi-select A–E questions with 160 individual correction explanations. New week map assets: two overviews plus 27 readable detailed boards. The existing original mind maps remain untouched. Source file images and original PDFs were imported privately from the user's actual Android phone over ADB, not obtained from web assets.

The Android Home screen adds a three-course high-priority section with direct navigation to the original FC, Comprendre, corrected A–E practice, flashcards and original assessment PDFs. All previously implemented subject coefficients, question scoring, time tracking, progress, original maps, theme and previous courses remain present.

## Source and correctness status

The user's new original ZIP contained 29 PDFs, including week 1 and week 2 FC/ACC/QCM sources. Full unchanged source PDFs were bundled in the private Android APK; only code/metadata and source-manifest status are committed to this public GitHub repository. Individual document hashes and verifications are maintained in the private exam_midway_coverage_manifest_v3320.json.

**Academic certification limitation:** The FCs are image-based scans. All 51 FC page images for the three priority courses are included. Week 1 and Week 2 new structured notes and mechanisms were carefully assembled but **are not an independently certified 100% transcription of every table/diagram label**. Fécondation includes the prior reviewed 21-section expert module but its general source guide is still partial. The P0 requirement of fully exhaustive textual Complet/Comprendre is therefore OPEN, rather than falsely passed.

The second-week source explicitly says **Partie 1 (pages 1–11)**; no further missing part was invented.

Original annales/QCM and corrigés remain unchanged PDF documents; the 32 new A–E questions are labelled new practice, not claimed to be original annales. Exact OCR-free per-question image transcription and automated matching to original corrections remain ongoing editorial work.

## Build and integration

- Existing Android app ID and signing certificate must be preserved.
- Version: v3.32.0 native exam midway.
- Android source: native-android/app, built with the existing Gradle toolchain, signed with the same existing keystore and updated via adb install -r if device is connected.
- Build/data verification is recorded separately from true device installation and academic completeness.
- No public redistribution of original paid FCs or assessment PDFs. Private asset injection remains in the authorized recovery workspace.

## Next stage

Complete all outstanding FC page-by-page tables/figures and scientific details in Essentiel/Complet/Comprendre, expand atomic cards and verified exam-style questions to full coverage, then integrate the other new courses (Noyau, acides nucléiques, gène→protéine, prévention, acoustique, chimie) without redesign or regressions. Do not rebuild after each chapter.
