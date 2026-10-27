"""Leke: High-performance subword tokenizer for Kwa languages."""

try:
    from leke._leke import version
except ImportError:
    def version() -> str:
        return "0.1.0 (uncompiled)"

__version__ = version()

__all__ = ["version", "__version__"]
