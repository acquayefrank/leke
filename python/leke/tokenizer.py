"""High-level Python Tokenizer interface for Leke.

The `LekeTokenizer` class provides an idiomatic, high-level Python wrapper around
the native Rust `NativeTokenizer` engine compiled via PyO3.

In modern NLP pipelines (e.g., PyTorch, Hugging Face transformers, vLLM), tokenizers
must satisfy two critical constraints:
    1. Microsecond latency during real-time inference and high-throughput data loading.
    2. Exact alignment tracking between input characters and subword tokens.

`LekeTokenizer` accomplishes this by executing all intensive tokenization, regex splitting,
and BPE merge lookups in native compiled Rust. The Python class acts as a thin,
ergonomic facade providing:
    - Single sentence and batch encoding (`encode`, `encode_batch`).
    - Subword decoding and detokenization (`decode`, `decode_batch`).
    - Token vocabulary lookups (`token_to_id`, `id_to_token`).
    - Direct zero-copy bridge to Hugging Face `transformers.PreTrainedTokenizerFast`.

Examples:
    >>> from leke import LekeTokenizer
    >>> # 1. Instantiate from a saved tokenizer bundle
    >>> tok = LekeTokenizer.from_file("models/bpe-16k/tokenizer.json")
    >>> # 2. Encode text in Akan / Twi
    >>> enc = tok.encode("Akwaaba ba Ghana man mu.")
    >>> print(enc.tokens)
    >>> print(enc.ids)
    >>> # 3. Convert to Hugging Face AutoTokenizer compatible object
    >>> hf_tokenizer = tok.to_transformers()
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, List, Optional, Union

# Import the native PyO3 C-extension classes.
# `Encoding` holds the token IDs, string tokens, and byte offsets.
# `NativeTokenizer` is the compiled Rust struct encapsulating the Hugging Face Tokenizer core.
from leke._leke import Encoding, NativeTokenizer


class LekeTokenizer:
    """High-performance Kwa subword tokenizer with Hugging Face interoperability.

    This class wraps the native Rust tokenization core, providing an ergonomic
    interface for tokenizing text from Akan/Twi, Ewe, Ga, and Fante.

    Attributes:
        _native (NativeTokenizer): Internal reference to the compiled Rust tokenizer instance.
    """

    def __init__(self, native_tokenizer: NativeTokenizer) -> None:
        """Initializes the tokenizer with an underlying native Rust tokenizer instance.

        Args:
            native_tokenizer (NativeTokenizer): The compiled PyO3 native tokenizer object.
        """
        # Store the native PyO3 Rust tokenizer pointer in a private attribute.
        self._native = native_tokenizer

    @classmethod
    def from_file(cls, path: Union[str, Path]) -> LekeTokenizer:
        """Loads a trained tokenizer bundle from a tokenizer.json file.

        Args:
            path (Union[str, Path]): Filesystem path to the serialized `tokenizer.json`.

        Returns:
            LekeTokenizer: An initialized tokenizer ready for encoding and decoding.

        Raises:
            FileNotFoundError: If the specified file does not exist on disk.
            RuntimeError: If the JSON cannot be parsed by the native engine.

        Notes:
            When loading a tokenizer, the path is converted to a string and passed
            directly to the Rust deserializer. Rust parses the JSON structure
            (containing the normalizer, pre-tokenizer, model merges, and decoder)
            instantly into memory.

        Examples:
            >>> tok = LekeTokenizer.from_file("models/bpe-16k/tokenizer.json")
        """
        # Step 1: Normalize path to string format required by the PyO3 C-API bridge.
        path_str = str(path)

        # Step 2: Call the native Rust constructor to deserialize the model into memory.
        native = NativeTokenizer.from_file(path_str)

        # Step 3: Wrap and return the Python class instance.
        return cls(native)

    @property
    def vocab_size(self) -> int:
        """Returns the total vocabulary size including base bytes and special tokens.

        Returns:
            int: The total count of unique subwords recognized by the tokenizer.
        """
        # Query the underlying Rust vocabulary trie/hash map for total token count.
        return self._native.vocab_size

    @property
    def path(self) -> str:
        """Returns the filesystem path the tokenizer was originally loaded from.

        Returns:
            str: Filesystem path string to the tokenizer.json file.
        """
        # Retrieve the cached file path from the native Rust struct.
        return self._native.path

    def encode(self, text: str, add_special_tokens: bool = True) -> Encoding:
        """Encodes an input string into subword tokens, integer IDs, and byte offsets.

        Args:
            text (str): The raw text to tokenize.
            add_special_tokens (bool, optional): Whether to prepend/append special tokens
                like BOS/EOS if configured. Defaults to True.

        Returns:
            Encoding: Container holding token IDs, subword strings, and byte offsets.

        Notes:
            1. The input string is passed into the native Rust pipeline.
            2. `KwaNormalizer` standardizes Unicode codepoints and dialectal variants.
            3. `Metaspace` or `ByteLevel` pre-tokenizers segment words into chunks.
            4. The BPE merge graph or Unigram Viterbi path finds optimal subwords.
            5. Byte-level fallback guarantees that unseen characters never cause errors.
            6. Returns an `Encoding` object containing `.ids`, `.tokens`, and `.offsets`.

        Examples:
            >>> enc = tok.encode("Wɔfrɛ me Kofi")
            >>> print(enc.ids)
            >>> print(enc.tokens)
        """
        # Execute subword tokenization directly in the compiled Rust engine.
        return self._native.encode(text, add_special_tokens)

    def encode_batch(self, texts: List[str], add_special_tokens: bool = True) -> List[Encoding]:
        """Encodes a batch of strings in parallel with minimal Python GIL contention.

        Args:
            texts (List[str]): List of sentences or paragraphs to tokenize.
            add_special_tokens (bool, optional): Whether to add special tokens. Defaults to True.

        Returns:
            List[Encoding]: List of Encoding objects corresponding to each input text.

        Notes:
            For large datasets (thousands of sentences), looping in Python causes
            interpreter overhead. `encode_batch` delegates the full list to Rust,
            which can leverage multi-threaded CPU parallelization across batch items.
        """
        # Pass the entire list of strings into Rust for batch tokenization.
        return self._native.encode_batch(texts, add_special_tokens)

    def decode(self, ids: List[int], skip_special_tokens: bool = True) -> str:
        """Decodes a sequence of integer token IDs back into normalized text.

        Args:
            ids (List[int]): List of token IDs produced by the model.
            skip_special_tokens (bool, optional): If True, omits special tokens like
                `<pad>`, `<unk>`, `<s>`, `</s>`. Defaults to True.

        Returns:
            str: The reconstructed, human-readable string.

        Notes:
            The decoder looks up the subword bytes corresponding to each ID,
            stitches them together, resolves byte-level prefixes (like Metaspace ` `),
            and reconstructs valid UTF-8 characters.

        Examples:
            >>> text = tok.decode([12, 45, 90])
        """
        # Delegate sequence decoding to the native Rust decoder.
        return self._native.decode(ids, skip_special_tokens)

    def decode_batch(
        self, batch_ids: List[List[int]], skip_special_tokens: bool = True
    ) -> List[str]:
        """Decodes a batch of token ID sequences into a list of strings.

        Args:
            batch_ids (List[List[int]]): 2D list of token IDs (e.g. from a PyTorch batch).
            skip_special_tokens (bool, optional): Whether to omit special tokens. Defaults to True.

        Returns:
            List[str]: Reconstructed text strings for each item in the batch.
        """
        # Execute batch decoding natively in Rust.
        return self._native.decode_batch(batch_ids, skip_special_tokens)

    def token_to_id(self, token: str) -> Optional[int]:
        """Looks up the numerical ID for a given subword token string.

        Args:
            token (str): Subword token string (e.g., "Akwaaba" or "Ġmu").

        Returns:
            Optional[int]: The token's vocabulary index, or None if not found.
        """
        # Perform O(1) hash table lookup in the native vocabulary table.
        return self._native.token_to_id(token)

    def id_to_token(self, id: int) -> Optional[str]:
        """Looks up the subword token string for a given numerical token ID.

        Args:
            id (int): Numerical token index from the vocabulary.

        Returns:
            Optional[str]: The string representation of the token, or None if out of bounds.
        """
        # Perform O(1) index lookup in the native vocabulary array.
        return self._native.id_to_token(id)

    def to_transformers(self) -> Any:
        """Converts to a Hugging Face `transformers.PreTrainedTokenizerFast` instance.

        Returns:
            PreTrainedTokenizerFast: A Hugging Face fast tokenizer pointing to the model file.

        Notes:
            Because Leke generates official standard `tokenizer.json` files,
            it can be converted into Hugging Face's `PreTrainedTokenizerFast` with zero copy.
            This allows seamless integration with `AutoModelForCausalLM`, `Trainer`,
            Hugging Face Datasets, and standard PyTorch collators.

        Examples:
            >>> hf_tok = tok.to_transformers()
            >>> batch = hf_tok(["Akwaaba", "Mìedó gbe"], return_tensors="pt", padding=True)
        """
        # Lazy import transformers so downstream users only pay import time when requested.
        from transformers import PreTrainedTokenizerFast

        # Initialize Hugging Face fast tokenizer pointing to Leke's bundle.
        return PreTrainedTokenizerFast(tokenizer_file=self.path)

    def __repr__(self) -> str:
        """Returns an unambiguous string representation of the LekeTokenizer instance.

        Returns:
            str: Informative string showing vocabulary size and source file path.
        """
        # Format informative representation for interactive REPL and logging.
        return f"LekeTokenizer(vocab_size={self.vocab_size}, path='{self.path}')"
