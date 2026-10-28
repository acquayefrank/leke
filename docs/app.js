/**
 * Leke: Broadsheet Showcase Engine
 * Recreates the newsprint design reference from context/design/
 */

(function () {
  'use strict';

  const PRESETS = [
    ['Akan / Twi', 'Akwaaba ba Ghana man mu. Wɔfrɛ me Kofi na mefiri Kumasi.'],
    ['Ewe', 'Mìedó gbe na mi nyuie. Woezɔ loo!'],
    ['Ga', 'Ojekoo, te oyɔɔ tɛŋŋ? Mitsɛ́ ji Nii Ayi.'],
    ['Fante', 'Me dzin dze Kwesi, mefi Oguaa. Ɛte dɛn?'],
    ['Lookalikes & tone', 'Wɔfrε no pápá! Ογε ɳkɔ ðeke.'],
    ['Byte fallback', 'Akwaaba 🇬🇭 ∑x² = λ, {code}']
  ];

  const LOOK = {
    'ε': 'ɛ', 'Ε': 'Ɛ', 'є': 'ɛ', 'γ': 'ɣ', 'Γ': 'Ɣ', 'ɳ': 'ŋ', 'ð': 'ɖ', 'Ð': 'Ɖ', 'ο': 'o', 'Ο': 'O'
  };

  const COMMON = new Set([
    'akwaaba', 'ba', 'ghana', 'man', 'mu', 'me', 'na', 'kofi', 'no',
    'papa', 'pápá', 'wo', 'mi', 'gbe', 'nii', 'ji', 'te', 'dze', 'loo', 'de', 'fi'
  ]);

  const CODE = {
    python: `import leke

raw = "Wɔfrε no pápá!"
clean = leke.normalize(raw)        # 'Wɔfrɛ no pápá!'  (Greek ε → Latin ɛ)

tok = leke.LekeTokenizer.from_file("models/bpe-16k/tokenizer.json")
enc = tok.encode("Akwaaba ba Ghana man mu.")
print(enc.tokens)  # ['A', 'kwaa', 'ba', 'Ġba', 'ĠGhana', 'Ġman', 'Ġmu', '.']
print(enc.ids)     # [37, 5091, 349, 562, 450, 703, 300, 18]
print(tok.decode(enc.ids))`,

    rust: `use _leke::normalizer::KwaNormalizer;
use _leke::trainer::{train_bpe, BpeTrainingConfig, save_tokenizer_bundle};
use std::path::{Path, PathBuf};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let norm = KwaNormalizer::default();
    println!("{}", norm.normalize_str("Akwaaba   ε   Ghana"));

    let config = BpeTrainingConfig::default();
    let files = vec![PathBuf::from("data/splits/twi/train.txt")];
    let (tokenizer, receipt) = train_bpe(&files, &config)?;
    save_tokenizer_bundle(&tokenizer, &receipt, Path::new("models/bpe-16k"))?;
    Ok(())
}`,

    hf: `from transformers import PreTrainedTokenizerFast

tokenizer = PreTrainedTokenizerFast.from_pretrained("models/bpe-16k")
inputs = tokenizer("Akwaaba ba Ghana man mu.", return_tensors="pt")
print(inputs.input_ids)  # tensor([[37, 5091, 349, 562, 450, 703, 300, 18]])`,

    cli: `python -m leke.trainer \\
  --corpus data/raw/pooled_train_extended.txt \\
  --output-dir models/bpe-16k \\
  --vocab-size 16384 \\
  --algorithm bpe

python -m leke.evaluate \\
  --model models/bpe-16k/tokenizer.json \\
  --splits-dir data/splits \\
  --report-out specs/eval_results.md`
  };

  const vocab = (window.LEKE_DATA && window.LEKE_DATA.vocab) ? window.LEKE_DATA.vocab : {};

  function hashId(s) {
    if (vocab[s] !== undefined) return vocab[s];
    let h = 2166136261;
    for (const c of s) {
      h ^= c.codePointAt(0);
      h = Math.imul(h, 16777619);
    }
    return 256 + (Math.abs(h) % 7936);
  }

  function normalize(text, o) {
    let t = text.normalize('NFC');
    if (o.look) t = [...t].map(c => LOOK[c] || c).join('');
    if (o.tone) t = t.normalize('NFD').replace(/[\u0300-\u0304\u030C]/g, '').normalize('NFC');
    if (o.ws) t = t.replace(/\s+/g, ' ').trim();
    return t;
  }

  function splitWord(w) {
    if (w.length <= 4 || COMMON.has(w.toLowerCase())) return [w];
    const syl = w.match(/[^aeiouɛɔAEIOUƐƆ]*[aeiouɛɔAEIOUƐƆ\u0300-\u036f]+(?:[nmŋ](?![aeiouɛɔ]))?|.+$/g) || [w];
    const out = [];
    let cur = '';
    for (const s of syl) {
      if ((cur + s).length > 5 && cur) {
        out.push(cur);
        cur = s;
      } else {
        cur += s;
      }
    }
    if (cur) out.push(cur);
    return out;
  }

  function tokenize(t) {
    const toks = [];
    let words = 0;
    const re = /[\p{L}\p{M}]+|\p{N}+|[!-\/:-@\[-`{-~]|\S/gu;
    let m;
    while ((m = re.exec(t))) {
      const sp = m.index > 0 && /\s/.test(t[m.index - 1]) ? 'Ġ' : '';
      const s = m[0];
      if (/^[\p{L}\p{M}]+$/u.test(s)) {
        words++;
        splitWord(s).forEach((p, i) => toks.push({ text: (i === 0 ? sp : '') + p, kind: 'sub' }));
      } else if (/^[\x21-\x7e]+$/.test(s) || /^\p{N}+$/u.test(s)) {
        toks.push({ text: sp + s, kind: 'sub' });
      } else {
        [...new TextEncoder().encode(s)].forEach((b, i) => toks.push({
          text: (i === 0 && sp ? 'Ġ' : '') + '<0x' + b.toString(16).toUpperCase().padStart(2, '0') + '>',
          kind: 'byte',
          id: b
        }));
      }
    }
    return { toks, words };
  }

  // Application State
  const state = {
    text: PRESETS[0][1],
    preset: 0,
    look: true,
    tone: false,
    ws: true,
    tab: 'python',
    copied: false
  };

  // DOM Elements
  const elPresets = document.getElementById('playground-presets');
  const elInput = document.getElementById('playground-input');
  const elToggleLook = document.getElementById('toggle-look');
  const elToggleTone = document.getElementById('toggle-tone');
  const elToggleWs = document.getElementById('toggle-ws');
  const elNormalized = document.getElementById('playground-normalized');
  const elTokens = document.getElementById('playground-tokens');
  const elStatWords = document.getElementById('stat-words');
  const elStatTokens = document.getElementById('stat-tokens');
  const elStatFertility = document.getElementById('stat-fertility');
  const elStatUnk = document.getElementById('stat-unk');
  const elQuickstartCode = document.getElementById('quickstart-code');
  const elCopyBtn = document.getElementById('copy-btn');
  const elSegOpts = document.querySelectorAll('.seg-opt');

  function renderPresets() {
    if (!elPresets) return;
    elPresets.innerHTML = `<span style="font-size: 13px; color: var(--color-subtle); margin-right: 6px;">Samples</span>`;
    PRESETS.forEach(([name, txt], idx) => {
      const active = state.preset === idx;
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'btn btn-secondary';
      btn.style.minHeight = '30px';
      btn.style.padding = '4px 11px';
      btn.style.fontSize = '13px';
      btn.style.background = active ? 'var(--color-accent-100)' : '#ffffff';
      btn.style.borderColor = active ? 'var(--color-accent-600)' : 'var(--color-input-border)';
      btn.style.color = active ? 'var(--color-accent-700)' : 'var(--color-text)';
      btn.textContent = name;
      btn.addEventListener('click', () => {
        state.text = txt;
        state.preset = idx;
        elInput.value = txt;
        updatePlayground();
        renderPresets();
      });
      elPresets.appendChild(btn);
    });
  }

  function updatePlayground() {
    const norm = normalize(state.text, state);
    if (elNormalized) elNormalized.textContent = norm;

    const { toks, words } = tokenize(norm);

    if (elTokens) {
      elTokens.innerHTML = '';
      toks.forEach((t, i) => {
        const alt = i % 2 === 0;
        const isByte = t.kind === 'byte';
        const bg = isByte ? 'var(--color-accent-2-100)' : (alt ? 'var(--color-accent-100)' : 'var(--color-accent-200)');
        const fg = isByte ? 'var(--color-accent-2-800)' : 'var(--color-accent-900)';
        const id = isByte ? t.id : hashId(t.text);
        const title = isByte ? 'Byte-level fallback' : 'Subword';

        const chip = document.createElement('span');
        chip.className = 'token-chip-broadsheet';
        chip.title = title;
        chip.style.background = bg;
        chip.style.color = fg;
        chip.innerHTML = `
          <span style="font-size: 18px; line-height: 1.3; white-space: pre;">${escapeHtml(t.text)}</span>
          <span style="font-size: 11px; line-height: 1.3; opacity: 0.8; font-feature-settings: 'tnum' 1;">${id}</span>
        `;
        elTokens.appendChild(chip);
      });
    }

    const fert = words ? (toks.length / words).toFixed(2) : '0.00';
    if (elStatWords) elStatWords.textContent = String(words);
    if (elStatTokens) elStatTokens.textContent = String(toks.length);
    if (elStatFertility) elStatFertility.textContent = fert;
    if (elStatUnk) elStatUnk.textContent = '0.00%';
  }

  function escapeHtml(str) {
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  function updateCode() {
    if (elQuickstartCode) {
      elQuickstartCode.textContent = CODE[state.tab] || CODE.python;
    }
    if (elCopyBtn) {
      elCopyBtn.textContent = state.copied ? 'Copied' : 'Copy code';
    }
  }

  // Initialize Event Listeners
  if (elInput) {
    elInput.value = state.text;
    elInput.addEventListener('input', (e) => {
      state.text = e.target.value;
      state.preset = -1;
      updatePlayground();
      renderPresets();
    });
  }

  if (elToggleLook) {
    elToggleLook.checked = state.look;
    elToggleLook.addEventListener('change', (e) => {
      state.look = e.target.checked;
      updatePlayground();
    });
  }

  if (elToggleTone) {
    elToggleTone.checked = state.tone;
    elToggleTone.addEventListener('change', (e) => {
      state.tone = e.target.checked;
      updatePlayground();
    });
  }

  if (elToggleWs) {
    elToggleWs.checked = state.ws;
    elToggleWs.addEventListener('change', (e) => {
      state.ws = e.target.checked;
      updatePlayground();
    });
  }

  elSegOpts.forEach((opt) => {
    opt.addEventListener('click', () => {
      const tab = opt.dataset.tab;
      if (!tab) return;
      state.tab = tab;
      state.copied = false;
      elSegOpts.forEach(o => o.classList.remove('active'));
      opt.classList.add('active');
      const radio = opt.querySelector('input');
      if (radio) radio.checked = true;
      updateCode();
    });
  });

  if (elCopyBtn) {
    elCopyBtn.addEventListener('click', () => {
      const codeText = CODE[state.tab] || CODE.python;
      navigator.clipboard?.writeText(codeText).then(() => {
        state.copied = true;
        updateCode();
        setTimeout(() => {
          state.copied = false;
          updateCode();
        }, 2000);
      });
    });
  }

  // Initial Run
  renderPresets();
  updatePlayground();
  updateCode();
})();
