# Leke Corpus Licensing Audit & Provenance

This document records the legal and licensing terms governing text corpora used in the training and evaluation of the Leke tokenizer models, as mandated by `specs/mission.md` and the build handoff.

---

## Audited Corpora

| Corpus | Target Languages Covered | Primary License | Commercial Use Permitted | Attribution Requirement |
| :--- | :--- | :--- | :--- | :--- |
| **Wikipedia Dumps** | Akan/Twi (`tw`), Ewe (`ee`) | Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) | Yes | "Text from Wikipedia, licensed under CC BY-SA 4.0" |
| **Glot500** | Akan (`aka`), Ewe (`ewe`), Ga (`gaa`), Fante (`fat`) | Mixed Open Licenses (CC BY-SA / Apache 2.0 / MIT) | Yes (per component terms) | Cite: Imani et al., "Glot500: A Base for 500+ Languages" |
| **MADLAD-400** | Twi (`twi`), Ewe (`ewe`) | Open Data Commons Attribution License (ODC-By v1.0) | Yes | Cite: Kudugunta et al., "MADLAD-400: A Multilingual And Diverse Dataset for 400+ Languages" |
| **MGhana-ST / Ghana Speech-Text** | Akan/Twi, Ewe, Ga | Creative Commons Attribution 4.0 (CC BY 4.0) | Yes | Masakhane / Ghana NLP attribution |

---

## Legal & Compliance Determinations

1. **Subword Vocabulary Extraction as Derivative / Transformative Use**:
   - Extracting subword token boundaries (BPE merge rules and vocabulary tables) represents a statistical, non-expressive transformation of text. No verbatim long-form copyrightable text is stored or re-distributed within `tokenizer.json`.
2. **Derivative Works & ShareAlike (CC BY-SA)**:
   - To guarantee complete compliance with CC BY-SA 4.0 (Wikipedia) and ODC-By (MADLAD-400), all tokenizer models and vocabulary tables released under Leke are made available under terms that permit downstream reuse and modification.
3. **Redistribution of Datasets**:
   - The repository distributes only curated sample test splits for benchmark reproducibility (`data/samples/` and `data/splits/`). Downstream users training full billion-token vocabularies can download source corpora directly using automated ingestion scripts.
