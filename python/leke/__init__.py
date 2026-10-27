"""Leke: High-performance subword tokenizer for Kwa languages."""

try:
    from leke._leke import KwaNormalizer, normalize, version
except ImportError:
    def version() -> str:
        return "0.1.0 (uncompiled)"

    def normalize(text: str, strip_accents: bool = False, collapse_whitespace: bool = True) -> str:
        raise ImportError("Leke C-extension is not compiled. Run `maturin develop`.")

    class KwaNormalizer:  # type: ignore
        def __init__(self, *args, **kwargs):
            raise ImportError("Leke C-extension is not compiled. Run `maturin develop`.")

__version__ = version()

from leke.corpus import CorpusProcessor, split_dataset, temperature_upsample, run_pipeline
from leke.trainer import train_bpe, train_unigram
from leke.tokenizer import LekeTokenizer
from leke.evaluate import calculate_metrics, evaluate_all

try:
    from leke._leke import Encoding
except ImportError:
    Encoding = None  # type: ignore

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
