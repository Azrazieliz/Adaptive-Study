# Concours — Adaptive Study

Public source for the **Adaptive Study v3.25.0** mobile/PWA engine.

The public repository contains the application engine, mobile interface, offline/runtime logic and Android wrapper. The user-owned medical course PDFs, page images, compiled flashcards, QCM/QROC banks and documentary originals are intentionally **not published**.

The validated private v3.25.0 package currently contains **31 active courses, 5,291 flashcards, 6,322 QCM + 420 QROC (6,742 active questions), 623 documentary original units and four Santé publique mind maps**. Those counts describe the private release, not a fresh public clone.

## v3.25.0 changes

- compact mobile dashboard with subject mastery and immediate adaptive priority;
- adaptive priority driven by score, repeated errors, active response time and recency/unseen status;
- fixed remediation/course-support logic to use the validated explicit flashcard bank instead of the empty legacy `facts` collection;
- source-linked error notebook and timing analysis;
- bidirectional flashcard review (question → answer → question before grading);
- Essential / Complete / original-PDF course views kept separate;
- validated multi-question exercise dossiers can be activated for Physics, Biochemistry and Cell Biology by the private corpus;
- strict startup build synchronization across engine, content, exercises and original corpus;
- four Santé publique course-only mind maps integrated in the private release without regressing the four 250-question SP banks.

## Private corpus restoration

The repository stays usable without private data: it starts with the seven subjects and no active private bank. To restore a matching private package locally:

```bash
python3 tools/restore_private_bundle.py /path/to/AdaptiveStudy_v3.25.0_STANDALONE_CLEAN_SOURCE.zip
python3 -m http.server 8765 --directory local_instance/app
```

Then open `http://127.0.0.1:8765/`.

`restore_private_bundle.py` copies only user-owned private content/assets into `local_instance/`, which remains ignored by Git.

## Authoritative content rules

- Course knowledge comes only from the supplied course PDFs.
- QE/annales/corrections are used for exam style, exercises and evaluation structure.
- A false option must be contradicted by positive corpus evidence; “not mentioned” never means false.
- Figures/tables keep their year, population, territory, sex/age, denominator and units.
- No external facts may be silently inserted into course summaries, flashcards or questions.
- Missing source material stays unavailable instead of being invented.

See [`ADAPTIVE_STUDY_REQUIREMENTS.md`](ADAPTIVE_STUDY_REQUIREMENTS.md) for the frozen functional requirements.