use pyo3::prelude::*;

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
    fn __repr__(&self) -> String {
        format!("Encoding(ids={:?}, tokens={:?})", self.ids, self.tokens)
    }

    fn __len__(&self) -> usize {
        self.ids.len()
    }

    fn __getitem__(&self, index: usize) -> PyResult<u32> {
        self.ids
            .get(index)
            .copied()
            .ok_or_else(|| pyo3::exceptions::PyIndexError::new_err("Index out of bounds"))
    }
}

#[pyclass(name = "NativeTokenizer")]
pub struct PyLekeTokenizer {
    inner: tokenizers::Tokenizer,
    path: String,
}

#[pymethods]
impl PyLekeTokenizer {
    #[staticmethod]
    fn from_file(path: &str) -> PyResult<Self> {
        let inner = tokenizers::Tokenizer::from_file(path)
            .map_err(|e| pyo3::exceptions::PyIOError::new_err(format!("Failed to load tokenizer: {e}")))?;
        Ok(Self {
            inner,
            path: path.to_string(),
        })
    }

    #[getter]
    fn path(&self) -> String {
        self.path.clone()
    }

    #[getter]
    fn vocab_size(&self) -> usize {
        self.inner.get_vocab_size(true)
    }

    #[pyo3(signature = (text, add_special_tokens=true))]
    fn encode(&self, text: &str, add_special_tokens: bool) -> PyResult<PyEncoding> {
        let enc = self
            .inner
            .encode(text, add_special_tokens)
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Encoding failed: {e}")))?;

        Ok(PyEncoding {
            ids: enc.get_ids().to_vec(),
            tokens: enc.get_tokens().to_vec(),
            offsets: enc.get_offsets().to_vec(),
        })
    }

    #[pyo3(signature = (texts, add_special_tokens=true))]
    fn encode_batch(&self, texts: Vec<String>, add_special_tokens: bool) -> PyResult<Vec<PyEncoding>> {
        let encodings = self
            .inner
            .encode_batch(texts, add_special_tokens)
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Batch encoding failed: {e}")))?;

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

    #[pyo3(signature = (ids, skip_special_tokens=true))]
    fn decode(&self, ids: Vec<u32>, skip_special_tokens: bool) -> PyResult<String> {
        self.inner
            .decode(&ids, skip_special_tokens)
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Decoding failed: {e}")))
    }

    #[pyo3(signature = (batch_ids, skip_special_tokens=true))]
    fn decode_batch(&self, batch_ids: Vec<Vec<u32>>, skip_special_tokens: bool) -> PyResult<Vec<String>> {
        let slices: Vec<&[u32]> = batch_ids.iter().map(|v| v.as_slice()).collect();
        self.inner
            .decode_batch(&slices, skip_special_tokens)
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Batch decoding failed: {e}")))
    }

    fn token_to_id(&self, token: &str) -> Option<u32> {
        self.inner.token_to_id(token)
    }

    fn id_to_token(&self, id: u32) -> Option<String> {
        self.inner.id_to_token(id)
    }
}
