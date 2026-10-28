# Leke Corpus Licensing Audit & Provenance

This document records the legal and licensing terms governing text corpora used in the training and evaluation of the Leke tokenizer models, as mandated by `specs/mission.md` and the build handoff.

---

## Audited Corpora

| Corpus | Target Languages Covered | Primary License | Commercial Use Permitted | Attribution Requirement |
| :--- | :--- | :--- | :--- | :--- |
| **Wikipedia Dumps** (`wikimedia/wikipedia` 20231101; training only, not redistributed) | Akan/Twi (`tw`), Ewe (`ee`), Fante (`fat`) | Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) | Yes | "Text from Wikipedia, licensed under CC BY-SA 4.0" |
| **NaCCA / MoE Curriculum Manuals** | Asante Twi, Ewe, Ga, Mfantse (Fante) | Open Educational Resources (Ministry of Education / NaCCA / T-TEL / GILLBT) | Educational / Transformative Subword Extraction | Cite: National Council for Curriculum and Assessment (NaCCA), Ministry of Education, Ghana (2024–2026) |
| **Peace Corps & FSI Twi Courses** | Twi (`twi`) | US Government Public Domain (17 U.S.C. § 105) | Yes | Public Domain (Peace Corps Ghana / Foreign Service Institute) |
| **Basel Mission English–Tshi Dictionary (1909)** | Asante / Akuapem Twi, Fante | Public Domain (Published 1909) | Yes | Cite: Christaller & Mohr, *English-Tshi (Asante) Dictionary*, Basel (1909) |
| **Glot500** | Akan (`aka`), Ewe (`ewe`), Ga (`gaa`), Fante (`fat`) | Mixed Open Licenses (CC BY-SA / Apache 2.0 / MIT) | Yes (per component terms) | Cite: Imani et al., "Glot500: A Base for 500+ Languages" |
| **MADLAD-400** (`clean` subset, training only; not redistributed) | Akan (`ak`, used for Twi), Ewe (`ee`) | Open Data Commons Attribution License (ODC-By v1.0) | Yes | Cite: Kudugunta et al., "MADLAD-400: A Multilingual And Diverse Dataset for 400+ Languages" |
| **FLORES+** (evaluation only; not redistributed) | Twi (Asante, Akuapem), Ewe | Creative Commons Attribution-ShareAlike 4.0 (CC BY-SA 4.0) | Yes | Cite: NLLB Team et al., "No Language Left Behind" and the OLDI FLORES+ dataset |
| **MGhana-ST / Ghana Speech-Text** | Akan/Twi, Ewe, Ga | Creative Commons Attribution 4.0 (CC BY 4.0) | Yes | Masakhane / Ghana NLP attribution |

---

## Legal & Compliance Determinations

1. **Subword Vocabulary Extraction as Derivative / Transformative Use**:
   - Extracting subword token boundaries (BPE merge rules and vocabulary tables) represents a statistical, non-expressive transformation of text. No verbatim long-form copyrightable text is stored or re-distributed within `tokenizer.json`.
2. **Derivative Works & ShareAlike (CC BY-SA)**:
   - To guarantee complete compliance with CC BY-SA 4.0 (Wikipedia) and ODC-By (MADLAD-400), all tokenizer models and vocabulary tables released under Leke are made available under terms that permit downstream reuse and modification.
3. **Redistribution of Datasets**:
   - The repository distributes only curated sample test splits for benchmark reproducibility (`data/samples/` and `data/splits/`).
   - The 13 source PDFs used by the extraction pipeline (`scripts/extract_pdf_corpora.py`) are not redistributed. Users who have obtained the PDFs place them in `data/raw/pdfs/` and rebuild all splits with:
     ```bash
     uv run --with pypdf python scripts/extract_pdf_corpora.py
     uv run python -m leke.corpus
     ```
