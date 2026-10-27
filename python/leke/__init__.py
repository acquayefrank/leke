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

__all__ = ["KwaNormalizer", "normalize", "version", "__version__"]
