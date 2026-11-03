# Adaptive Study Native v3.30.0 — source-coverage report

**2026-11-03.** Data/content integration, NOT certification of the full 2026–2027 FC coverage.

## Implemented

- 73 chapter entries; 66 structured entries (61 previously indexed source guides + 5 composites).
- 73 explanatory-text entries; 6,387 source-linked fact references in 2,029 reading paragraphs.
- Source items retain stable fingerprints, original label, value, source chapter and page, alongside explanatory paragraphs.
- Original PDF pages, flashcards, and authentic assessment PDFs are retained; generated QCMs are not labeled as annales.
- Composite chapters explicitly name constituent sources and link to them and their original page images.

## Coverage status

| Status | Chapters |
|---|---:|
| SOURCE_GUIDE_INCOMPLETE_REVIEW_REQUIRED | 28 |
| SOURCE_GUIDE_NOT_EXHAUSTIVENESS_VERIFIED | 33 |
| RELATED_CONTENT_ONLY__ORIGINAL_COURSE_NOT_PROVIDED | 7 |
| COMPOSITE_EXISTING_SOURCE_COURSES__NO_INDEPENDENT_FC | 5 |

## Composite chapters — not independent FCs

- Protéines: Acides aminés et peptides, Structure des protéines, Repliement des protéines
- Atomistique et liaisons: Les atomes, Liaison chimique
- Transfert de protons et d’électrons: Équilibres acido-basiques, Réactions d’oxydo-réduction
- Énergie + électrostatique: Énergies, Électrostatique
- Fluides parfaits et visqueux: Fluides parfaits, Fluides visqueux

## Still missing an original source

- Embryologie (histo_embryo)
- Noyau (biocell_noyau)
- Cytosquelette (biocell_cytosq)
- Jonction matrice extracellulaire–intégrine (biocell_mec_integrine)
- Bases moléculaires du développement embryonnaire (biocell_dev)
- Cycle cellulaire (biocell_cycle)
- Biologie moléculaire (bio_biomol)

## Outstanding validation

- Most current FC PDFs are image-only scans; the source guides are NOT page-by-page transcripts.
- The audit flags 28 partially reviewed courses and 33 without exhaustive certification; five composites lack an independent FC.
- Figures, tables, technical details, all required course pages and exam correction keys still require direct source review.
- The seven source-less entries only reference related courses, not a replacement for their own missing original FC.
- Editorially improved prose is a learning aid, NOT a separately validated exam syllabus.

## Rebuild steps

Run the four scripts in native-android/tools in this order: compose_missing_umbrella_chapters.py, improve_textual_chapters_v2.py, polish_comprehension_prose.py, audit_comprehension_v2.py. Rebuild and sign using the existing Android project and signing identity; use ADB update only if connected.
