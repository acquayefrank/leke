pub mod normalizer;

use normalizer::KwaNormalizer;
use pyo3::prelude::*;

/// Python wrapper for KwaNormalizer
#[pyclass(name = "KwaNormalizer")]
pub struct PyKwaNormalizer {
    inner: KwaNormalizer,
}

#[pymethods]
impl PyKwaNormalizer {
    #[new]
    #[pyo3(signature = (strip_accents=false, collapse_whitespace=true, custom_mappings_json=None))]
    fn new(
        strip_accents: bool,
        collapse_whitespace: bool,
        custom_mappings_json: Option<&str>,
    ) -> PyResult<Self> {
        let inner = if let Some(json_str) = custom_mappings_json {
            KwaNormalizer::from_json(json_str, strip_accents, collapse_whitespace)
                .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Invalid mapping JSON: {e}")))?
        } else {
            KwaNormalizer::new(strip_accents, collapse_whitespace)
                .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Failed to initialize: {e}")))?
        };
        Ok(Self { inner })
    }

    /// Normalizes a single string according to Kwa normalization rules.
    fn normalize(&self, text: &str) -> String {
        self.inner.normalize_str(text)
    }

    /// Normalizes a batch of strings.
    fn normalize_batch(&self, texts: Vec<String>) -> Vec<String> {
        texts.into_iter().map(|t| self.inner.normalize_str(&t)).collect()
    }
}

/// Convenience standalone function for normalizing text.
#[pyfunction]
#[pyo3(signature = (text, strip_accents=false, collapse_whitespace=true))]
fn normalize(text: &str, strip_accents: bool, collapse_whitespace: bool) -> PyResult<String> {
    let norm = KwaNormalizer::new(strip_accents, collapse_whitespace)
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))?;
    Ok(norm.normalize_str(text))
}

/// Returns the version string of the leke engine.
pub fn leke_version() -> &'static str {
    env!("CARGO_PKG_VERSION")
}

#[pyfunction]
fn version() -> PyResult<&'static str> {
    Ok(leke_version())
}

#[pymodule]
fn _leke(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyKwaNormalizer>()?;
    m.add_function(wrap_pyfunction!(version, m)?)?;
    m.add_function(wrap_pyfunction!(normalize, m)?)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_version() {
        assert_eq!(leke_version(), "0.1.0");
    }
}
