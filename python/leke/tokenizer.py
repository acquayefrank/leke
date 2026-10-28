"""High-level Python Tokenizer interface for Leke."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Union

from leke._leke import Encoding, NativeTokenizer


class LekeTokenizer:
    """High-performance Kwa subword tokenizer with Hugging Face interoperability."""

    def __init__(self, native_tokenizer: NativeTokenizer):
        self._native = native_tokenizer

    @classmethod
    def from_file(cls, path: Union[str, Path]) -> LekeTokenizer:
        """Loads a trained tokenizer from a tokenizer.json file."""
        native = NativeTokenizer.from_file(str(path))
        return cls(native)

    @property
    def vocab_size(self) -> int:
        """Returns the total vocabulary size including added/special tokens."""
        return self._native.vocab_size

    @property
    def path(self) -> str:
        """Returns the filesystem path the tokenizer was loaded from."""
        return self._native.path

    def encode(self, text: str, add_special_tokens: bool = True) -> Encoding:
        """Encodes an input string into subword tokens, IDs, and character offsets."""
        return self._native.encode(text, add_special_tokens)

    def encode_batch(self, texts: List[str], add_special_tokens: bool = True) -> List[Encoding]:
        """Encodes a batch of strings."""
        return self._native.encode_batch(texts, add_special_tokens)

    def decode(self, ids: List[int], skip_special_tokens: bool = True) -> str:
        """Decodes token IDs back into normalized text."""
        return self._native.decode(ids, skip_special_tokens)

    def decode_batch(
        self, batch_ids: List[List[int]], skip_special_tokens: bool = True
    ) -> List[str]:
        """Decodes a batch of token ID sequences."""
        return self._native.decode_batch(batch_ids, skip_special_tokens)

    def token_to_id(self, token: str) -> Optional[int]:
        """Looks up the ID for a given token string."""
        return self._native.token_to_id(token)

    def id_to_token(self, id: int) -> Optional[str]:
        """Looks up the token string for a given token ID."""
        return self._native.id_to_token(id)

    def to_transformers(self):
        """Converts to a Hugging Face transformers PreTrainedTokenizerFast instance."""
        from transformers import PreTrainedTokenizerFast

        return PreTrainedTokenizerFast(tokenizer_file=self.path)

    def __repr__(self) -> str:
        return f"LekeTokenizer(vocab_size={self.vocab_size}, path='{self.path}')"
