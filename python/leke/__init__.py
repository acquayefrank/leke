"""Leke: High-performance subword tokenizer for Kwa languages.

Leke is a high-performance subword tokenization toolkit specifically engineered
for Niger-Congo languages in the Kwa branch, including Akan/Twi (Asante & Akuapem),
Ewe, Ga, and Fante.

Standard multilingual tokenizers (such as SentencePiece in NLLB-200) suffer from severe
fragmentation on Kwa languages because their vocabularies are dominated by high-resource
Indo-European languages. Leke achieves lower fertility, zero out-of-vocabulary rate,
and sub-millisecond encoding throughput by integrating:
    1. A native Rust normalization engine (`KwaNormalizer`) handling Unicode NFC
       and phonetic glyph variations (e.g., standardizing open-e / open-o).
    2. Tone-preserving orthographic processing.
    3. Byte-Level BPE segmentation with fallback guarantees.
    4. Seamless drop-in interoperability with Hugging Face transformers.

Examples:
    >>> import leke
    >>> # Step 1: Normalize raw text with canonical orthographic mappings
    >>> clean = leke.normalize("Akwaaba ba Ghana")
    >>> # Step 2: Load a trained model
    >>> tok = leke.LekeTokenizer.from_file("models/bpe-8k/tokenizer.json")
    >>> enc = tok.encode("Akwaaba ba Ghana")
    >>> print(enc.tokens)
"""

# -----------------------------------------------------------------------------
# Step 1: Attempt to import compiled Rust extensions from `leke._leke`.
# The PyO3 extension module is compiled using Maturin and provides high-speed
# C-level Rust bindings for Unicode normalization, BPE training, and inference.
# -----------------------------------------------------------------------------
try:
    # Import the native Rust structs and functions compiled into the C-extension.
    from leke._leke import KwaNormalizer, normalize, version
except ImportError:
    # -------------------------------------------------------------------------
    # Fallback Mechanism:
    # If the user has installed or cloned the repo in pure Python mode without
    # compiling the Rust extension (e.g. before running `maturin develop`),
    # provide graceful diagnostic stubs that explain how to build the binaries.
    # -------------------------------------------------------------------------

    def version() -> str:
        """Returns the fallback package version when uncompiled.

        Returns:
            str: Version string indicating that the native extension is missing.
        """
        # Return fallback indicator showing uncompiled state.
        return "0.1.0 (uncompiled)"

    def normalize(text: str, strip_accents: bool = False, collapse_whitespace: bool = True) -> str:
        """Fallback stub for native Kwa text normalization.

        Args:
            text (str): Input text in a Kwa language (Twi, Ewe, Ga, Fante).
            strip_accents (bool, optional): Whether to remove tone diacritics. Defaults to False.
            collapse_whitespace (bool, optional): Whether to collapse multiple spaces. Defaults to True.

        Returns:
            str: The normalized string.

        Raises:
            ImportError: Always raised to direct developer to compile Rust extension.
        """
        # Inform the user that native compilation is required for normalization.
        raise ImportError("Leke C-extension is not compiled. Run `maturin develop`.")

    class KwaNormalizer:  # type: ignore
        """Fallback stub for native Rust KwaNormalizer."""

        def __init__(self, *args, **kwargs) -> None:
            """Initializes the fallback normalizer stub.

            Args:
                *args: Variable length argument list.
                **kwargs: Arbitrary keyword arguments.

            Raises:
                ImportError: Directs developer to compile native Rust module.
            """
            # Raise an informative error explaining how to compile the PyO3 binary.
            raise ImportError("Leke C-extension is not compiled. Run `maturin develop`.")


# -----------------------------------------------------------------------------
# Step 2: Package version discovery.
# Expose the semantic version string at the package root level.
# -----------------------------------------------------------------------------
__version__ = version()

# -----------------------------------------------------------------------------
# Step 3: Import pure Python orchestrators and data pipeline components.
# These modules manage corpus ingestion, stratified splits, BPE/Unigram training,
# and fertility/compression evaluation metrics.
# -----------------------------------------------------------------------------
# Import dataset preprocessing, splitting, and Dirichlet upsampling utilities.
from leke.corpus import CorpusProcessor, run_pipeline, split_dataset, temperature_upsample

# Import evaluation metrics (fertility, split rate, unknown-token rate, compression).
from leke.evaluate import calculate_metrics, evaluate_all

# Import the high-level Python tokenizer wrapper with Hugging Face interop.
from leke.tokenizer import LekeTokenizer

# Import training engines for Byte-Level BPE and Unigram algorithms.
from leke.trainer import train_bpe, train_unigram

# -----------------------------------------------------------------------------
# Step 4: Import native tokenization Encoding container if compiled.
# -----------------------------------------------------------------------------
try:
    # Encoding encapsulates token IDs, tokens, byte offsets, and attention masks.
    from leke._leke import Encoding
except ImportError:
    # Set to None if the C-extension is not compiled yet.
    Encoding = None  # type: ignore

# -----------------------------------------------------------------------------
# Step 5: Define the public API export list (`__all__`).
# This cleanly defines what is exported when users run `from leke import *`.
# -----------------------------------------------------------------------------
__all__ = [
    "KwaNormalizer",
    "normalize",
    "version",
    "__version__",
    "CorpusProcessor",
    "split_dataset",
    "temperature_upsample",
    "run_pipeline",
    "train_bpe",
    "train_unigram",
    "LekeTokenizer",
    "Encoding",
    "calculate_metrics",
    "evaluate_all",
]
