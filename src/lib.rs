use pyo3::prelude::*;

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
    m.add_function(wrap_pyfunction!(version, m)?)?;
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
