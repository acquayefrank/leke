//! PyO3 interface bridge exposing native Rust tokenization routines to Python.
//!
//! # Architecture & Runtime Mechanics
//! High-throughput tokenization requires zero-copy or minimal-copy transitions across
//! the Python C-API boundary:
//!
//! 1. **Underlying Engine**: Wraps Hugging Face's multi-threaded Rust `tokenizers::Tokenizer`.
//! 2. **Token Container**: Returns [`PyEncoding`] holding integer token IDs, string subwords,
//!    and character slice span offsets (`(start, end)`).
//! 3. **Batch Operations**: Employs Rayon-backed parallel encoding in Rust when processing
//!    batches, releasing GIL bottlenecks.
//!
//! # Safety & Memory Invariants
//! Memory is safely managed via PyO3's ownership tracking and Rust's RAII semantics.

use pyo3::prelude::*;

/// Python-exposed subword encoding container.
///
/// # Fields
/// * `ids`: Vector of integer token vocabulary IDs.
/// * `tokens`: Vector of subword unit strings.
/// * `offsets`: Vector of character slice spans `(start, end)` in the original text.
#[pyclass(name = "Encoding")]
#[derive(Clone, Debug)]
pub struct PyEncoding {
    #[pyo3(get)]
    pub ids: Vec<u32>,
    #[pyo3(get)]
    pub tokens: Vec<String>,
    #[pyo3(get)]
    pub offsets: Vec<(usize, usize)>,
}

#[pymethods]
impl PyEncoding {
    /// Returns a developer-readable string representation of the encoding.
    fn __repr__(&self) -> String {
        format!("Encoding(ids={:?}, tokens={:?})", self.ids, self.tokens)
    }

    /// Returns the total count of tokens in the encoded sequence.
    fn __len__(&self) -> usize {
        self.ids.len()
    }

    /// Retrieves the token ID at the specified index position.
    ///
    /// # Errors
    /// Raises `IndexError` if `index` is out of bounds.
    fn __getitem__(&self, index: usize) -> PyResult<u32> {
        self.ids
            .get(index)
            .copied()
            .ok_or_else(|| pyo3::exceptions::PyIndexError::new_err("Index out of bounds"))
    }
}

/// Native Rust tokenizer engine exposed to Python as `_leke.NativeTokenizer`.
///
/// Wraps an in-memory `tokenizers::Tokenizer` model instance loaded from a `tokenizer.json` bundle.
#[pyclass(name = "NativeTokenizer")]
pub struct PyLekeTokenizer {
    inner: tokenizers::Tokenizer,
    path: String,
}

#[pymethods]
impl PyLekeTokenizer {
    /// Loads a trained tokenizer bundle from a local file path.
    ///
    /// # Arguments
    /// * `path`: Filesystem path to `tokenizer.json`.
    ///
    /// # Returns
    /// A new [`PyLekeTokenizer`] instance ready for high-speed encoding.
    ///
    /// # Errors
    /// Raises Python `IOError` if the file cannot be opened or parsed.
    #[staticmethod]
    fn from_file(path: &str) -> PyResult<Self> {
        // Step 1: Parse and load the Tokenizer model weights and state from disk.
        let inner = tokenizers::Tokenizer::from_file(path)
            .map_err(|e| pyo3::exceptions::PyIOError::new_err(format!("Failed to load tokenizer: {e}")))?;
        // Step 2: Retain loaded tokenizer along with recorded file path.
        Ok(Self {
            inner,
            path: path.to_string(),
        })
    }

    /// Returns the filesystem path from which the tokenizer model was loaded.
    #[getter]
    fn path(&self) -> String {
        self.path.clone()
    }

    /// Returns the total vocabulary size including special tokens and byte units.
    #[getter]
    fn vocab_size(&self) -> usize {
        self.inner.get_vocab_size(true)
    }

    /// Encodes a single text string into subword token IDs, tokens, and span offsets.
    ///
    /// # Arguments
    /// * `text`: The raw input text string.
    /// * `add_special_tokens`: If `true`, injects sequence boundary tokens (such as `<s>` and `</s>`).
    ///
    /// # Returns
    /// A [`PyEncoding`] instance containing the parsed sequence data.
    ///
    /// # Errors
    /// Raises Python `RuntimeError` if internal tokenization fails.
    #[pyo3(signature = (text, add_special_tokens=true))]
    fn encode(&self, text: &str, add_special_tokens: bool) -> PyResult<PyEncoding> {
        // Step 1: Run native Rust tokenization pipeline (normalization -> pre-tokenization -> model -> post-processor).
        let enc = self
            .inner
            .encode(text, add_special_tokens)
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Encoding failed: {e}")))?;

        // Step 2: Transfer IDs, subword strings, and character slice offsets into Python wrapper struct.
        Ok(PyEncoding {
            ids: enc.get_ids().to_vec(),
            tokens: enc.get_tokens().to_vec(),
            offsets: enc.get_offsets().to_vec(),
        })
    }

    /// Encodes a batch of strings concurrently using Rust thread-level parallelism.
    ///
    /// # Arguments
    /// * `texts`: Vector of input text strings.
    /// * `add_special_tokens`: Whether to add special tokens.
    ///
    /// # Returns
    /// A vector of [`PyEncoding`] instances corresponding to the input texts.
    ///
    /// # Errors
    /// Raises Python `RuntimeError` if batch processing fails.
    #[pyo3(signature = (texts, add_special_tokens=true))]
    fn encode_batch(&self, texts: Vec<String>, add_special_tokens: bool) -> PyResult<Vec<PyEncoding>> {
        // Step 1: Execute parallel multi-threaded batch tokenization in Rust.
        let encodings = self
            .inner
            .encode_batch(texts, add_special_tokens)
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Batch encoding failed: {e}")))?;

        // Step 2: Convert batch encodings into Python-compatible vector of PyEncoding objects.
        let mut result = Vec::with_capacity(encodings.len());
        for enc in encodings {
            result.push(PyEncoding {
                ids: enc.get_ids().to_vec(),
                tokens: enc.get_tokens().to_vec(),
                offsets: enc.get_offsets().to_vec(),
            });
        }
        Ok(result)
    }

    /// Decodes a sequence of integer token IDs back into a reconstructed text string.
    ///
    /// # Arguments
    /// * `ids`: Vector of vocabulary token IDs.
    /// * `skip_special_tokens`: If `true`, omits reserved special tokens (`<s>`, `</s>`, `<pad>`, etc.).
    ///
    /// # Returns
    /// Reconstructed text string.
    ///
    /// # Errors
    /// Raises Python `RuntimeError` if ID sequence cannot be decoded.
    #[pyo3(signature = (ids, skip_special_tokens=true))]
    fn decode(&self, ids: Vec<u32>, skip_special_tokens: bool) -> PyResult<String> {
        // Step 1: Decode token ID stream through model decoder to recover UTF-8 text string.
        self.inner
            .decode(&ids, skip_special_tokens)
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Decoding failed: {e}")))
    }

    /// Decodes multiple token ID sequences in batch.
    ///
    /// # Arguments
    /// * `batch_ids`: Vector of token ID vectors.
    /// * `skip_special_tokens`: Whether to omit special tokens.
    ///
    /// # Returns
    /// Vector of decoded text strings.
    ///
    /// # Errors
    /// Raises Python `RuntimeError` if batch decoding fails.
    #[pyo3(signature = (batch_ids, skip_special_tokens=true))]
    fn decode_batch(&self, batch_ids: Vec<Vec<u32>>, skip_special_tokens: bool) -> PyResult<Vec<String>> {
        // Step 1: Convert vector of vectors into slice references for Tokenizers C++ decoder.
        let slices: Vec<&[u32]> = batch_ids.iter().map(|v| v.as_slice()).collect();
        // Step 2: Execute batch decoding.
        self.inner
            .decode_batch(&slices, skip_special_tokens)
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Batch decoding failed: {e}")))
    }

    /// Looks up the integer vocabulary ID corresponding to a subword token string.
    fn token_to_id(&self, token: &str) -> Option<u32> {
        self.inner.token_to_id(token)
    }

    /// Looks up the subword token string corresponding to an integer vocabulary ID.
    fn id_to_token(&self, id: u32) -> Option<String> {
        self.inner.id_to_token(id)
    }
}
