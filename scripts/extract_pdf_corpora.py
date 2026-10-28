"""Extract and clean Kwa language corpora from textbook PDFs in data/raw/pdfs/.

This script extracts text from the born-digital Ghanaian curriculum manuals and
reference books in `data/raw/pdfs/`, filters out English pedagogical boilerplate,
acknowledgement tables, and page headers/footers, normalizes lookalike glyphs via
`data/char_mappings.json`, supplements low-page-count Twi manuals with CC BY-SA 4.0
Twi Wikipedia prose (audited in `specs/corpus_licenses.md`), and writes the merged
corpora to `data/samples/{twi,ewe,gaa,fat}.txt`.

The source PDFs are not distributed with this repository. Place the files listed
in `PDF_BY_LANG` in `data/raw/pdfs/` (git-ignored) before running.

Usage:
    uv run --with pypdf python scripts/extract_pdf_corpora.py
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Dict, List, Set

import pypdf

ROOT = Path(__file__).resolve().parent.parent
PDF_DIR = ROOT / "data" / "raw" / "pdfs"
SAMPLES_DIR = ROOT / "data" / "samples"
CHAR_MAPPINGS_PATH = ROOT / "data" / "char_mappings.json"

PDF_BY_LANG: Dict[str, List[str]] = {
    "twi": [
        "Asante-Twi-Teacher-Manual-Y1-BK-2-online.pdf",
        "GH_Twi_Language_Lessons.pdf",
    ],
    "ewe": [
        "Ewe-Teacher-manual-y1-bk1_Online.pdf",
        "Ewe-Teacher-Manual-Y1-bk-2-Online.pdf",
        "Ewe-Teacher-manual.pdf",
    ],
    "gaa": [
        "Ga-Teacher-manual-y1-bk1-ONLINE.pdf",
        "Teacher-Manual_Ga-_ear-1-Book-2.pdf",
        "GA-TM_Y3_ONLINE-VERSION.pdf",
    ],
    "fat": [
        "mfantse-Teacher-Manual-Y1-bk-1-ONLINE.pdf",
        "Teacher-Manual_Fante_-Year-1-Book-2.pdf",
        "MFANTSE-LM_Year-2-TV-1.pdf",
    ],
}

# English stopwords & curriculum boilerplate terms to reject English-language instructions
ENGLISH_REJECT_WORDS: Set[str] = {
    "the",
    "and",
    "for",
    "with",
    "that",
    "this",
    "from",
    "have",
    "should",
    "would",
    "could",
    "learners",
    "learner",
    "teacher",
    "teachers",
    "curriculum",
    "section",
    "assessment",
    "pedagogical",
    "exemplars",
    "session",
    "minutes",
    "following",
    "discuss",
    "identify",
    "explain",
    "university",
    "college",
    "school",
    "ministry",
    "education",
    "strand",
    "outcome",
    "outcomes",
    "indicator",
    "indicators",
    "level",
    "source",
    "enquiries",
    "comments",
    "director",
    "national",
    "council",
    "reproduced",
    "permission",
    "publication",
    "reserved",
    "rights",
    "knowledge",
    "understanding",
    "questions",
    "question",
    "students",
    "student",
    "group",
    "groups",
    "pairs",
    "class",
    "activity",
    "activities",
    "example",
    "examples",
    "presentation",
    "presentations",
    "homework",
    "portfolio",
    "enactment",
    "reflection",
    "colleagues",
    "misconceptions",
    "handbook",
    "template",
    "rubrics",
    "senior",
    "technical",
    "department",
    "institute",
    "achimota",
    "winneba",
    "published",
    "journal",
    "press",
}

# Target-language high-frequency function words & particles
LANG_MARKERS: Dict[str, Set[str]] = {
    "twi": {
        "ne",
        "wɔ",
        "na",
        "no",
        "mu",
        "ho",
        "de",
        "yɛ",
        "bɛ",
        "kɔ",
        "ba",
        "sɛ",
        "nnipa",
        "kasa",
        "asɛm",
        "fie",
        "sukuu",
        "adwuma",
        "nyinaa",
        "bere",
        "berɛ",
        "a",
        "nso",
        "ma",
        "wo",
        "me",
        "yɛn",
        "wɔn",
        "ankasa",
        "tumi",
        "firi",
        "fi",
        "nti",
        "so",
        "yi",
        "bi",
        "kuro",
        "ɔman",
    },
    "ewe": {
        "kple",
        "le",
        "me",
        "nye",
        "si",
        "siwo",
        "wo",
        "la",
        "ɖe",
        "ƒe",
        "ŋu",
        "tso",
        "eye",
        "alo",
        "hafi",
        "nusrɔ̃lawo",
        "nuŋlɔɖi",
        "nyagbe",
        "ame",
        "gbe",
        "sia",
        "katã",
        "katã",
        "nyuie",
        "ke",
        "gake",
        "bena",
        "nenye",
        "dometɔ",
        "aɖe",
        "aɖewo",
        "woawo",
        "mía",
        "míe",
    },
    "gaa": {
        "kɛ",
        "lɛ",
        "nɔ",
        "mli",
        "he",
        "yɛ",
        "ni",
        "akɛ",
        "ji",
        "shishi",
        "gbɛi",
        "wiemɔ",
        "bii",
        "nyɛ",
        "amɛ",
        "ekome",
        "sane",
        "maŋ",
        "gbɔmɔ",
        "tsu",
        "nɛɛ",
        "pɛ",
        "ahu",
        "jogbaŋŋ",
        "nikaselɔi",
        "tsɔɔlɔ",
        "jwɛŋmɔ",
        "kusum",
    },
    "fat": {
        "na",
        "no",
        "mu",
        "wɔ",
        "ho",
        "nye",
        "hɔn",
        "dze",
        "kasa",
        "nyimpa",
        "ebusua",
        "mbofra",
        "adzesua",
        "esuafo",
        "kyerɛkyerɛnyi",
        "nsɛmfua",
        "nyina",
        "ber",
        "dɛ",
        "ma",
        "do",
        "ara",
        "bi",
        "iyi",
        "wonya",
        "mbordo",
        "mfantse",
        "kasafua",
        "nsɛntɔw",
    },
}

KWA_CHARS = set("ɛƐɔƆŋŊɖƉƒƑɣƔʋƲãẽĩõũÃẼĨÕŨ")


def load_char_mappings() -> Dict[str, str]:
    """Load lookalike character mappings from data/char_mappings.json."""
    data = json.loads(CHAR_MAPPINGS_PATH.read_text(encoding="utf-8"))
    return data["mappings"]


def normalize_text(text: str, mappings: Dict[str, str]) -> str:
    """Apply Unicode NFC + lookalike replacement + whitespace collapsing."""
    nfc = unicodedata.normalize("NFC", text)
    mapped = "".join(mappings.get(ch, ch) for ch in nfc)
    norm_nfc = unicodedata.normalize("NFC", mapped)
    return re.sub(r"\s+", " ", norm_nfc).strip()


def clean_candidate_sentence(raw: str, mappings: Dict[str, str]) -> str:
    """Strip bullets, leading enumeration, page numbers, and normalize."""
    s = raw.strip()
    s = re.sub(r"^[\•\▪\➢\-\–\—\*]+\s*", "", s)
    s = re.sub(r"^(?:[0-9]+|[a-zA-Z]|[ivxIVX]{1,4})[\.\)]\s+", "", s)
    s = re.sub(r"^\([0-9a-zA-Z]+\)\s+", "", s)
    s = re.sub(r"\|\s*\d+\s*\|", " ", s)
    s = normalize_text(s, mappings)
    return s


def is_valid_kwa_sentence(sentence: str, lang: str) -> bool:
    """Determine whether a candidate sentence is authentic Kwa text in `lang`."""
    if not sentence or len(sentence) < 12:
        return False

    if any(
        tok in sentence.lower() for tok in ("http://", "https://", "www.", "@", "doi.org", "isbn")
    ):
        return False

    alpha_chars = [c for c in sentence if c.isalpha()]
    if len(alpha_chars) < 8:
        return False
    digit_chars = [c for c in sentence if c.isdigit()]
    if len(digit_chars) > len(alpha_chars) * 0.25:
        return False

    words = sentence.split()
    if len(words) < 3 or len(words) > 120:
        return False

    word_tokens = [re.sub(r"^[^\w]+|[^\w]+$", "", w).lower() for w in words]
    word_tokens = [w for w in word_tokens if w]
    if len(word_tokens) < 3:
        return False

    eng_hits = sum(1 for w in word_tokens if w in ENGLISH_REJECT_WORDS)
    if eng_hits >= 2 or (eng_hits == 1 and len(word_tokens) < 10):
        return False

    has_kwa_char = any(c in KWA_CHARS for c in sentence)
    marker_hits = sum(1 for w in word_tokens if w in LANG_MARKERS[lang])

    if has_kwa_char and marker_hits >= 1:
        return True
    if marker_hits >= 2:
        return True

    return False


def extract_sentences_from_pdf(pdf_path: Path, lang: str, mappings: Dict[str, str]) -> List[str]:
    """Extract and segment authentic Kwa sentences from a PDF file."""
    reader = pypdf.PdfReader(str(pdf_path))
    extracted: List[str] = []

    for page in reader.pages:
        raw_page = page.extract_text() or ""
        if not raw_page.strip():
            continue

        lines = raw_page.splitlines()
        paragraphs: List[str] = []
        current: List[str] = []

        for line in lines:
            stripped = line.strip()
            if not stripped:
                if current:
                    paragraphs.append(" ".join(current))
                    current = []
                continue
            if re.fullmatch(r"\|?\s*\d+\s*\|?", stripped):
                continue
            if stripped.startswith(("SECTION ", "AKPA ", "KƆSIƉA ", "WEEK ", "MLIJAA ", "ƆFA ")):
                if current:
                    paragraphs.append(" ".join(current))
                    current = []
                continue
            if re.match(r"^([\•\▪\➢\-\*]|\d+[\.\)]|[a-z][\.\)]|[ivx]+[\.\)])\s+", stripped):
                if current:
                    paragraphs.append(" ".join(current))
                    current = []
            current.append(stripped)

        if current:
            paragraphs.append(" ".join(current))

        for para in paragraphs:
            raw_sents = re.split(r"(?<=[\.\?\!\;])\s+", para)
            for raw_sent in raw_sents:
                cleaned = clean_candidate_sentence(raw_sent, mappings)
                if is_valid_kwa_sentence(cleaned, lang):
                    extracted.append(cleaned)

    return extracted


def fetch_twi_wikipedia_sentences(mappings: Dict[str, str], target_count: int = 2500) -> List[str]:
    """Fetch authentic Asante/Akuapem Twi sentences from Twi Wikipedia (CC BY-SA 4.0)."""
    collected: List[str] = []
    seen: Set[str] = set()
    apcontinue = ""

    headers = {
        "User-Agent": "LekeTokenizerBot/0.1 (https://github.com/acquayefrank/leke; linguistic corpus research)"
    }

    while len(collected) < target_count:
        params = {
            "action": "query",
            "generator": "allpages",
            "gaplimit": "20",
            "gapfilterredir": "nonredirects",
            "prop": "extracts",
            "exintro": "1",
            "explaintext": "1",
            "exlimit": "max",
            "format": "json",
        }
        if apcontinue:
            params["gapcontinue"] = apcontinue

        url = "https://tw.wikipedia.org/w/api.php?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            print(f"  [twi-wiki] Stopped at {len(collected)} sentences ({exc})")
            break

        pages = data.get("query", {}).get("pages", {})
        for page_obj in pages.values():
            extract = page_obj.get("extract", "")
            if not extract:
                continue
            for line in extract.splitlines():
                if line.strip().startswith("=="):
                    continue
                for raw_sent in re.split(r"(?<=[\.\?\!])\s+", line):
                    cleaned = clean_candidate_sentence(raw_sent, mappings)
                    if is_valid_kwa_sentence(cleaned, "twi") and any(
                        c in KWA_CHARS for c in cleaned
                    ):
                        if cleaned not in seen:
                            seen.add(cleaned)
                            collected.append(cleaned)
                            if len(collected) >= target_count:
                                return collected

        cont = data.get("continue", {})
        apcontinue = cont.get("gapcontinue", "")
        if not apcontinue:
            break

    return collected


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract and clean Kwa language corpora from textbook PDFs in data/raw/pdfs/."
    )
    parser.parse_args()

    mappings = load_char_mappings()

    for lang, pdf_names in PDF_BY_LANG.items():
        sample_path = SAMPLES_DIR / f"{lang}.txt"
        existing_lines: List[str] = []
        if sample_path.exists():
            # Keep only the original curated seed sentences (first 30 lines) to avoid duplicating prior runs
            raw_existing = [
                normalize_text(line, mappings)
                for line in sample_path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            existing_lines = raw_existing[:30]

        seen: Set[str] = set()
        merged: List[str] = []

        for line in existing_lines:
            if line and line not in seen:
                seen.add(line)
                merged.append(line)

        seed_count = len(merged)

        for pdf_name in pdf_names:
            pdf_path = PDF_DIR / pdf_name
            if not pdf_path.exists():
                print(f"[WARN] Missing PDF: {pdf_path}")
                continue
            sents = extract_sentences_from_pdf(pdf_path, lang, mappings)
            added = 0
            for s in sents:
                if s not in seen:
                    seen.add(s)
                    merged.append(s)
                    added += 1
            print(f"  [{lang}] {pdf_name}: +{added} unique sentences")

        # Supplement Twi with CC BY-SA 4.0 Twi Wikipedia sentences (per specs/corpus_licenses.md)
        if lang == "twi" and len(merged) < 2500:
            wiki_sents = fetch_twi_wikipedia_sentences(mappings, target_count=2600)
            wiki_added = 0
            for s in wiki_sents:
                if s not in seen:
                    seen.add(s)
                    merged.append(s)
                    wiki_added += 1
            print(f"  [twi] Twi Wikipedia (CC BY-SA 4.0): +{wiki_added} unique sentences")

        sample_path.write_text("\n".join(merged) + "\n", encoding="utf-8")
        print(
            f"==> {lang}: {seed_count} seed -> {len(merged)} total unique sentences in {sample_path}\n"
        )


if __name__ == "__main__":
    main()
