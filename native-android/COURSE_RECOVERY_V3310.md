# Adaptive Study Native v3.31.0 — Full-source course reader

## Source inventory
The original 2026-09-29 canonical inventory recorded 31/31 FCs for the original 31-course syllabus (including authorized early Gaz–Pression, plus the Grands problèmes addendum). Subsequent source uploads expanded the project to 73 chapter entries.

No independent original FC was found for seven additional umbrella/topic labels. The seven new reference entries are now explicitly tied to existing course pages and sections, with 575 sourced fact references from 86 sections spanning 648 linked page positions. This is a topic reference based on existing FCs, not an assertion that seven independent FC PDFs exist.

## Implementation
- 73/73 chapter entries now have existing source guides or clearly identified source-grouped related-course guides.
- Four historic NOT_RECEIVED flags were corrected where original source pages already exist: Épidémies, Mitochondrie et peroxysome, Système endomembranaire and Acoustique.
- Essentiel chooses fact references across the chapter rather than only the first source pages: 1,913 selected references.
- Complet opens a full page-by-page original-source viewer with two consecutive page images, per-page structured facts, previous/next, arbitrary page jump, and original document titles for composite chapters.
- All 6,475 source-linked guide facts can also be read in one section-based structured-facts view.
- Comprendre preserves and regenerates 1,985 reading paragraphs across the 73 entries, with per-section original-page links.
- 2,115 referenced page positions resolve to existing image assets, including reused pages for composite chapters. Unique source image count: 1,315.
- Questions and flashcards from v3.30.1 remain: 969 original question entries, 309 authored practice questions, 2,088 active concise flashcards; all 106 original maps remain.
- The barème, subject coefficients, timing, SHS recall boards and user progress storage remain unchanged.

## Explicit editorial limit
The FC PDFs checked on the recovery PC are image-only scans without a substantive selectable text layer. The original source pages are now accessible directly under Complet, but not every page has a complete paragraph-by-paragraph transcription. The 1,985 paragraphs are derived from 6,475 existing structured facts, not a certified exhaustive transcription. Do not display a false 100% textualization claim.

## Source policies
- No unrelated textbook content is invented.
- The seven secondary topic labels show exact source-course provenance and do not present linked content as an independently provided FC.
- Historic PDF/guide duplicates and original images are retained.
- All original PDFs, marks and exam question corrections remain private on the authorized PC; none are sent to the public code repository.

## Build and audit
Execute tools in sequence: link_unmapped_topic_sources_v3310.py, improve_textual_chapters_v2.py, polish_comprehension_prose.py, build_course_full_reading_indexes_v3310.py, patch_full_course_reader_v3310.py, polish_reader_ui_v3310.py, qa_full_syllabus_assets_v3310.py. Build and sign using the existing Android project.
