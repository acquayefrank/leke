use std::collections::HashMap;
use serde::{Deserialize, Serialize};
use unicode_normalization::UnicodeNormalization;
use tokenizers::Normalizer;
use tokenizers::NormalizedString;

const DEFAULT_MAPPINGS_JSON: &str = include_str!("../data/char_mappings.json");

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MappingFile {
    pub description: Option<String>,
    pub version: Option<String>,
    pub mappings: HashMap<String, String>,
}

#[derive(Debug, Clone)]
pub struct KwaNormalizer {
    mappings: HashMap<char, String>,
    strip_accents: bool,
    collapse_whitespace: bool,
}

impl Default for KwaNormalizer {
    fn default() -> Self {
        Self::new(false, true).expect("Failed to initialize default KwaNormalizer")
    }
}

impl KwaNormalizer {
    /// Creates a new KwaNormalizer with the default embedded character mappings.
    pub fn new(strip_accents: bool, collapse_whitespace: bool) -> Result<Self, serde_json::Error> {
        let mapping_file: MappingFile = serde_json::from_str(DEFAULT_MAPPINGS_JSON)?;
        let mut char_map = HashMap::new();
        for (k, v) in mapping_file.mappings {
            if let Some(ch) = k.chars().next() {
                char_map.insert(ch, v);
            }
        }
        Ok(Self {
            mappings: char_map,
            strip_accents,
            collapse_whitespace,
        })
    }

    /// Creates a KwaNormalizer from a custom mapping JSON string.
    pub fn from_json(json_str: &str, strip_accents: bool, collapse_whitespace: bool) -> Result<Self, serde_json::Error> {
        let mapping_file: MappingFile = serde_json::from_str(json_str)?;
        let mut char_map = HashMap::new();
        for (k, v) in mapping_file.mappings {
            if let Some(ch) = k.chars().next() {
                char_map.insert(ch, v);
            }
        }
        Ok(Self {
            mappings: char_map,
            strip_accents,
            collapse_whitespace,
        })
    }

    /// Normalizes an input string according to the Kwa normalization pipeline:
    /// 1. Unicode NFC
    /// 2. Canonical variant mapping
    /// 3. Optional tone/diacritic stripping (if strip_accents is true)
    /// 4. Optional whitespace collapsing and trimming
    pub fn normalize_str(&self, text: &str) -> String {
        // Step 1: Unicode NFC
        let nfc_text: String = text.nfc().collect();

        // Step 2: Canonical character mapping
        let mut mapped = String::with_capacity(nfc_text.len());
        for c in nfc_text.chars() {
            if let Some(replacement) = self.mappings.get(&c) {
                mapped.push_str(replacement);
            } else {
                mapped.push(c);
            }
        }

        // Step 3: Tone mark / diacritic stripping (if configured)
        let unaccented: String = if self.strip_accents {
            mapped
                .nfd()
                .filter(|&c| !is_combining_diacritic(c))
                .nfc()
                .collect()
        } else {
            mapped.nfc().collect()
        };

        // Step 4: Whitespace collapsing
        if self.collapse_whitespace {
            collapse_whitespace(&unaccented)
        } else {
            unaccented
        }
    }
}

/// Checks if a character is a Unicode combining diacritical mark (tones, accents).
fn is_combining_diacritic(c: char) -> bool {
    // Unicode Combining Diacritical Marks block (U+0300 - U+036F)
    // and Combining Diacritical Marks Extended (U+1AB0 - U+1AFF)
    // and Combining Diacritical Marks Supplement (U+1DC0 - U+1DFF)
    matches!(c, '\u{0300}'..='\u{036F}' | '\u{1AB0}'..='\u{1AFF}' | '\u{1DC0}'..='\u{1DFF}')
}

/// Collapses runs of whitespace into a single space and trims edges.
fn collapse_whitespace(text: &str) -> String {
    let mut result = String::with_capacity(text.len());
    let mut in_whitespace = false;

    for c in text.trim().chars() {
        if c.is_whitespace() {
            if !in_whitespace {
                result.push(' ');
                in_whitespace = true;
            }
        } else {
            result.push(c);
            in_whitespace = false;
        }
    }
    result
}

impl Normalizer for KwaNormalizer {
    fn normalize(&self, normalized: &mut NormalizedString) -> tokenizers::Result<()> {
        let original = normalized.get();
        let cleaned = self.normalize_str(original);
        *normalized = NormalizedString::from(cleaned);
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_canonical_variant_replacement() {
        let norm = KwaNormalizer::default();
        // Greek epsilon -> Latin Open E (ɛ)
        assert_eq!(norm.normalize_str("ε"), "ɛ");
        // Greek gamma -> Latin Gamma (ɣ)
        assert_eq!(norm.normalize_str("γ"), "ɣ");
        // Cyrillic Ukrainian ie -> Latin Open E (ɛ)
        assert_eq!(norm.normalize_str("є"), "ɛ");
        // Alternate eng / d with tail
        assert_eq!(norm.normalize_str("ð"), "ɖ");
        assert_eq!(norm.normalize_str("ɳ"), "ŋ");
    }

    #[test]
    fn test_tone_preservation_by_default() {
        let norm = KwaNormalizer::default();
        let twi = "Wɔfrɛ no pápá.";
        assert_eq!(norm.normalize_str(twi), "Wɔfrɛ no pápá.");

        let ewe = "Mìedó gbe nɛ.";
        assert_eq!(norm.normalize_str(ewe), "Mìedó gbe nɛ.");
    }

    #[test]
    fn test_tone_stripping_when_enabled() {
        let norm = KwaNormalizer::new(true, true).unwrap();
        let twi = "Wɔfrɛ no pápá.";
        assert_eq!(norm.normalize_str(twi), "Wɔfrɛ no papa.");

        let ewe = "Mìedó gbe nɛ.";
        assert_eq!(norm.normalize_str(ewe), "Miedo gbe nɛ.");
    }

    #[test]
    fn test_whitespace_collapsing() {
        let norm = KwaNormalizer::default();
        assert_eq!(
            norm.normalize_str("   Akwaaba    ba   Ghana!   "),
            "Akwaaba ba Ghana!"
        );
    }

    #[test]
    fn test_casing_preserved() {
        let norm = KwaNormalizer::default();
        assert_eq!(norm.normalize_str("AKAN twi EWE Ga"), "AKAN twi EWE Ga");
    }

    #[test]
    fn test_idempotence() {
        let norm = KwaNormalizer::default();
        let sample = "Wɔfrɛ   no   pápá!   Mìedó gbe.";
        let once = norm.normalize_str(sample);
        let twice = norm.normalize_str(&once);
        assert_eq!(once, twice);
    }
}
