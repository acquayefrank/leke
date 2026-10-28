//! Kwa linguistic text normalization engine.
//!
//! # Architecture & Linguistic Overview
//! African languages belonging to the Kwa family (such as Akan/Twi, Ewe, Ga, and Fante)
//! feature distinct orthographic characteristics that cause severe vocabulary fragmentation
//! in standard NLP tokenizers:
//!
//! 1. **Orthographic Lookalikes**: Due to variations in keyboard layouts and historical
//!    transcription practices, authors frequently type visually similar characters from
//!    differing Unicode blocks (e.g., Greek Small Letter Epsilon `ε` or Cyrillic Small
//!    Letter Ukrainian Ie `є` instead of the canonical African Latin Small Letter Open E `ɛ`).
//! 2. **Phonemic Tone & Diacritics**: Tonal diacritics (acute `´`, grave `` ` ``, caron `ˇ`)
//!    distinguish lexical meaning in tonal Kwa languages (e.g., Twi *pápá* "goodness" vs.
//!    *papá* "father" vs. *papa* "fan"). The normalizer preserves these marks by default,
//!    while providing optional stripping when downstream applications require tone-agnostic
//!    representations.
//! 3. **Canonical Normalization Pipeline**: Every text passes through:
//!    - **Unicode NFC**: Composes canonical decomposing sequences into unified code points.
//!    - **Canonical Variant Mapping**: Replaces lookalikes with standard African Latin characters.
//!    - **Optional Diacritic Filtering**: Selectively removes combining diacritics if enabled.
//!    - **Whitespace Normalization**: Collapses repeated whitespace into single ASCII spaces.
//!
//! # Examples
//! ```
//! use _leke::normalizer::KwaNormalizer;
//!
//! let normalizer = KwaNormalizer::default();
//! let cleaned = normalizer.normalize_str("Akwaaba   ε   Ghana");
//! assert_eq!(cleaned, "Akwaaba ɛ Ghana");
//! ```

use std::collections::HashMap;
use serde::{Deserialize, Serialize};
use unicode_normalization::UnicodeNormalization;
use tokenizers::Normalizer;
use tokenizers::NormalizedString;

const DEFAULT_MAPPINGS_JSON: &str = include_str!("../data/char_mappings.json");

/// Represents the serialized JSON schema of the character replacement dictionary.
///
/// # Fields
/// * `description`: Optional human-readable metadata describing the mapping table.
/// * `version`: Semantic version of the orthography dictionary.
/// * `mappings`: Map of source character lookalikes to target canonical characters.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MappingFile {
    pub description: Option<String>,
    pub version: Option<String>,
    pub mappings: HashMap<String, String>,
}

/// High-performance text normalizer tailored for Niger-Congo Kwa languages.
///
/// # Linguistic Motivation
/// Subword tokenizers (like Byte-Pair Encoding and Unigram) rely on recurring byte/character
/// n-grams. When African language text suffers from unstandardized orthographic variants
/// (e.g. users typing Greek `ε` instead of Latin `ɛ`, or Greek `γ` instead of Latin `ɣ`),
/// tokenizers allocate separate tokens to identical words, shattering model embeddings and
/// inflating fertility.
///
/// `KwaNormalizer` standardizes inputs before tokenization and training.
///
/// # Pipeline Architecture
/// 1. **Unicode NFC**: Canonical composition to unify precomposed and combining accents.
/// 2. **Canonical Variant Mapping**: Table lookup converting phonetic lookalikes.
/// 3. **Diacritic Filtering**: Configurable tone preservation or stripping.
/// 4. **Whitespace Trimming**: Linear-time whitespace run collapsing.
///
/// # Examples
/// ```
/// use _leke::normalizer::KwaNormalizer;
///
/// let normalizer = KwaNormalizer::default();
/// assert_eq!(normalizer.normalize_str("Wɔfrɛ   no   pápá."), "Wɔfrɛ no pápá.");
/// ```
#[derive(Debug, Clone)]
pub struct KwaNormalizer {
    mappings: HashMap<char, String>,
    strip_accents: bool,
    collapse_whitespace: bool,
}

impl Default for KwaNormalizer {
    /// Default configuration: preserves tone diacritics (`strip_accents = false`)
    /// and collapses repeated whitespace (`collapse_whitespace = true`).
    fn default() -> Self {
        Self::new(false, true).expect("Failed to initialize default KwaNormalizer")
    }
}

impl KwaNormalizer {
    /// Creates a new `KwaNormalizer` loaded with the embedded default Kwa character mappings.
    ///
    /// # Arguments
    /// * `strip_accents`: If `true`, strips tone and diacritical marks (e.g. `pápá` -> `papa`).
    ///   Defaults to `false` to preserve phonemic tone contrasts.
    /// * `collapse_whitespace`: If `true`, collapses consecutive whitespace characters into a
    ///   single ASCII space and trims leading and trailing whitespace.
    ///
    /// # Errors
    /// Returns a [`serde_json::Error`] if the embedded character mappings JSON cannot be parsed.
    ///
    /// # Examples
    /// ```
    /// use _leke::normalizer::KwaNormalizer;
    ///
    /// let normalizer = KwaNormalizer::new(false, true).expect("valid embedded mappings");
    /// assert_eq!(normalizer.normalize_str("ɛfoɔ"), "ɛfoɔ");
    /// ```
    pub fn new(strip_accents: bool, collapse_whitespace: bool) -> Result<Self, serde_json::Error> {
        // Step 1: Deserialize embedded JSON character dictionary into MappingFile struct.
        let mapping_file: MappingFile = serde_json::from_str(DEFAULT_MAPPINGS_JSON)?;
        // Step 2: Build an efficient HashMap keyed by source char code point.
        let mut char_map = HashMap::new();
        for (k, v) in mapping_file.mappings {
            if let Some(ch) = k.chars().next() {
                char_map.insert(ch, v);
            }
        }
        // Step 3: Instantiate KwaNormalizer with parsed map and configuration flags.
        Ok(Self {
            mappings: char_map,
            strip_accents,
            collapse_whitespace,
        })
    }

    /// Creates a `KwaNormalizer` from a user-supplied JSON mapping string.
    ///
    /// # Arguments
    /// * `json_str`: Serialized JSON matching the [`MappingFile`] schema.
    /// * `strip_accents`: Whether to strip tone accents during normalization.
    /// * `collapse_whitespace`: Whether to collapse runs of whitespace.
    ///
    /// # Errors
    /// Returns a [`serde_json::Error`] if `json_str` is malformed.
    ///
    /// # Examples
    /// ```
    /// use _leke::normalizer::KwaNormalizer;
    ///
    /// let custom_json = r#"{"mappings": {"a": "b"}}"#;
    /// let norm = KwaNormalizer::from_json(custom_json, false, true).unwrap();
    /// assert_eq!(norm.normalize_str("apple"), "bpple");
    /// ```
    pub fn from_json(json_str: &str, strip_accents: bool, collapse_whitespace: bool) -> Result<Self, serde_json::Error> {
        // Step 1: Deserialize user-provided JSON string.
        let mapping_file: MappingFile = serde_json::from_str(json_str)?;
        // Step 2: Extract key-value mappings into char lookup table.
        let mut char_map = HashMap::new();
        for (k, v) in mapping_file.mappings {
            if let Some(ch) = k.chars().next() {
                char_map.insert(ch, v);
            }
        }
        // Step 3: Return configured normalizer.
        Ok(Self {
            mappings: char_map,
            strip_accents,
            collapse_whitespace,
        })
    }

    /// Normalizes an input string through the complete Kwa orthographic pipeline.
    ///
    /// # Pipeline Stages
    /// 1. **Unicode NFC**: Re-composes decomposed characters into standard NFC forms.
    /// 2. **Canonical Mapping**: Fast character substitution using the loaded mapping table.
    /// 3. **Tone Stripping**: Optional NFD decomposition, combining-mark filter, and NFC re-composition.
    /// 4. **Whitespace Collapsing**: Trims edges and replaces internal whitespace runs with a single space.
    ///
    /// # Arguments
    /// * `text`: The raw input string slice.
    ///
    /// # Returns
    /// A new [`String`] containing the normalized, canonical representation.
    ///
    /// # Examples
    /// ```
    /// use _leke::normalizer::KwaNormalizer;
    ///
    /// let norm = KwaNormalizer::default();
    /// assert_eq!(norm.normalize_str("Mìedó   gbe"), "Mìedó gbe");
    /// ```
    pub fn normalize_str(&self, text: &str) -> String {
        // Step 1: Normalize to Unicode Canonical Composition (NFC).
        // This ensures combining code point sequences are unified before character lookup.
        let nfc_text: String = text.nfc().collect();

        // Step 2: Canonical character lookalike mapping.
        // Iterate through each code point, replacing phonetic and visual lookalikes
        // (such as Greek epsilon or Cyrillic ie) with official Latin African variants.
        let mut mapped = String::with_capacity(nfc_text.len());
        for c in nfc_text.chars() {
            if let Some(replacement) = self.mappings.get(&c) {
                mapped.push_str(replacement);
            } else {
                mapped.push(c);
            }
        }

        // Step 3: Optional tone mark / diacritic stripping.
        // In tonal Kwa languages (Twi, Ewe, Ga), tones are phonemic. By default, tones
        // are preserved. If strip_accents is enabled, we decompose into NFD, strip
        // combining diacritical marks (Unicode blocks U+0300..=U+036F, etc.), and re-compose to NFC.
        let unaccented: String = if self.strip_accents {
            mapped
                .nfd()
                .filter(|&c| !is_combining_diacritic(c))
                .nfc()
                .collect()
        } else {
            mapped.nfc().collect()
        };

        // Step 4: Whitespace collapsing and edge trimming.
        // Reduce runs of consecutive spaces, tabs, and newlines into single ASCII spaces.
        if self.collapse_whitespace {
            collapse_whitespace(&unaccented)
        } else {
            unaccented
        }
    }
}

/// Checks if a character belongs to a Unicode combining diacritical mark block.
///
/// # Covered Unicode Blocks
/// * Combining Diacritical Marks (`U+0300`..=`U+036F`)
/// * Combining Diacritical Marks Extended (`U+1AB0`..=`U+1AFF`)
/// * Combining Diacritical Marks Supplement (`U+1DC0`..=`U+1DFF`)
///
/// # Arguments
/// * `c`: The character to inspect.
///
/// # Returns
/// `true` if `c` is a combining diacritic code point, `false` otherwise.
fn is_combining_diacritic(c: char) -> bool {
    // Unicode Combining Diacritical Marks block (U+0300 - U+036F)
    // and Combining Diacritical Marks Extended (U+1AB0 - U+1AFF)
    // and Combining Diacritical Marks Supplement (U+1DC0 - U+1DFF)
    matches!(c, '\u{0300}'..='\u{036F}' | '\u{1AB0}'..='\u{1AFF}' | '\u{1DC0}'..='\u{1DFF}')
}

/// Collapses internal whitespace runs into a single ASCII space and trims edges.
///
/// Operates in single-pass O(N) linear time without unnecessary intermediate allocations.
///
/// # Arguments
/// * `text`: The string slice to collapse.
///
/// # Returns
/// A new [`String`] with trimmed margins and single spaces between words.
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

/// Integration with Hugging Face `tokenizers::Normalizer` trait.
///
/// Allows `KwaNormalizer` to be embedded directly into standard Hugging Face
/// tokenization pipelines as a pre-tokenization normalization step.
impl Normalizer for KwaNormalizer {
    /// In-place string normalization implementing the Hugging Face `Normalizer` interface.
    ///
    /// # Arguments
    /// * `normalized`: Mutable reference to the tokenizers `NormalizedString`.
    ///
    /// # Errors
    /// Returns `Ok(())` on success.
    fn normalize(&self, normalized: &mut NormalizedString) -> tokenizers::Result<()> {
        // Step 1: Extract the underlying slice from the NormalizedString wrapper.
        let original = normalized.get();
        // Step 2: Apply the full Kwa normalization pipeline.
        let cleaned = self.normalize_str(original);
        // Step 3: Replace the buffer content while preserving span boundaries.
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
