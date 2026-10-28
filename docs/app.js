/**
 * Leke Documentation & Interactive Showcase Engine
 * High-performance Niger-Congo Kwa Subword Tokenization
 */

(function () {
  'use strict';

  // Ensure LEKE_DATA is available
  const DATA = window.LEKE_DATA || {
    charMappings: {},
    byteAlphabet: [],
    samples: [],
    leaderboard: [],
    benchmarks: {},
    vocab: {},
    merges: []
  };

  // Build reverse vocab lookup: id -> token string
  const idToToken = {};
  for (const [token, id] of Object.entries(DATA.vocab)) {
    idToToken[id] = token;
  }

  // Build merge rank map for fast BPE merge lookup: "tokenA tokenB" -> rank
  const bpeRanks = new Map();
  DATA.merges.forEach((merge, rank) => {
    bpeRanks.set(merge, rank);
  });

  // Byte level encoder mapping
  const byteToChar = DATA.byteAlphabet;
  const charToByte = {};
  byteToChar.forEach((ch, byteVal) => {
    charToByte[ch] = byteVal;
  });

  // ---------------------------------------------------------------------------
  // 1. Linguistic Normalization Engine
  // ---------------------------------------------------------------------------
  function normalizeText(text, options = {}) {
    const stripAccents = options.stripAccents || false;
    const collapseWhitespace = options.collapseWhitespace !== false;

    // Step 1: Unicode NFC
    let normalized = text.normalize('NFC');

    // Step 2: Canonical character lookalike mapping
    let mapped = '';
    for (const char of normalized) {
      mapped += DATA.charMappings[char] || char;
    }

    // Step 3: Optional tone mark / diacritic stripping
    if (stripAccents) {
      mapped = mapped
        .normalize('NFD')
        .replace(/[\u0300-\u036f\u1ab0-\u1aff\u1dc0-\u1dff]/g, '')
        .normalize('NFC');
    }

    // Step 4: Whitespace collapsing & trimming
    if (collapseWhitespace) {
      mapped = mapped.trim().replace(/\s+/g, ' ');
    }

    return mapped;
  }

  // ---------------------------------------------------------------------------
  // 2. In-Browser Byte-Level BPE Tokenizer
  // ---------------------------------------------------------------------------
  function getPairs(wordPieces) {
    const pairs = new Set();
    for (let i = 0; i < wordPieces.length - 1; i++) {
      pairs.add(`${wordPieces[i]} ${wordPieces[i + 1]}`);
    }
    return pairs;
  }

  function bpeSegmentWord(wordPiece) {
    if (wordPiece.length <= 1) return [wordPiece];

    let pieces = Array.from(wordPiece);
    while (true) {
      const pairs = getPairs(pieces);
      if (pairs.size === 0) break;

      let minPair = null;
      let minRank = Infinity;

      for (const pair of pairs) {
        if (bpeRanks.has(pair)) {
          const rank = bpeRanks.get(pair);
          if (rank < minRank) {
            minRank = rank;
            minPair = pair;
          }
        }
      }

      if (minPair === null) break;

      const [first, second] = minPair.split(' ');
      const newPieces = [];
      let i = 0;

      while (i < pieces.length) {
        if (i < pieces.length - 1 && pieces[i] === first && pieces[i + 1] === second) {
          newPieces.push(first + second);
          i += 2;
        } else {
          newPieces.push(pieces[i]);
          i += 1;
        }
      }

      pieces = newPieces;
    }

    return pieces;
  }

  function tokenizeText(inputText, options = {}) {
    const normalized = normalizeText(inputText, options);
    if (!normalized.trim()) {
      return {
        raw: inputText,
        normalized: normalized,
        tokens: [],
        ids: [],
        fertility: 0,
        wordCount: 0,
        tokenCount: 0,
        unkCount: 0
      };
    }

    // Split text into words while keeping whitespace tokens
    const textEncoder = new TextEncoder();
    const rawTokens = [];
    const tokenIds = [];

    // GPT-2 byte-level pre-tokenization split
    const words = normalized.match(/[\p{L}]+|[\p{N}]+|[^\s\p{L}\p{N}]+|\s+/gu) || [normalized];

    words.forEach((chunk, index) => {
      if (!chunk) return;

      // Handle space prefix simulation (ByteLevel adds Ġ for leading spaces)
      let byteStr = '';
      const utf8Bytes = textEncoder.encode(chunk);
      for (let b of utf8Bytes) {
        // If it's a space (0x20), ByteLevel represents it as 'Ġ' (0x120 or byte alphabet index 32)
        byteStr += byteToChar[b] || String.fromCharCode(b);
      }

      const subwords = bpeSegmentWord(byteStr);
      for (const sub of subwords) {
        rawTokens.push(sub);
        const id = DATA.vocab[sub] !== undefined ? DATA.vocab[sub] : DATA.vocab['<unk>'] || 0;
        tokenIds.push(id);
      }
    });

    const wordsOnly = normalized.trim().split(/\s+/).filter(Boolean);
    const wordCount = wordsOnly.length;
    const tokenCount = rawTokens.length;
    const fertility = wordCount > 0 ? (tokenCount / wordCount).toFixed(2) : 0;
    const unkCount = tokenIds.filter(id => id === DATA.vocab['<unk>']).length;

    return {
      raw: inputText,
      normalized: normalized,
      tokens: rawTokens,
      ids: tokenIds,
      fertility: fertility,
      wordCount: wordCount,
      tokenCount: tokenCount,
      unkCount: unkCount
    };
  }

  // ---------------------------------------------------------------------------
  // 3. UI Token Palette Generator
  // ---------------------------------------------------------------------------
  const CHIP_PALETTES = [
    { bg: 'rgba(245, 158, 11, 0.15)', border: 'rgba(245, 158, 11, 0.4)', text: '#fbbf24', glow: 'rgba(245, 158, 11, 0.2)' },
    { bg: 'rgba(16, 185, 129, 0.15)', border: 'rgba(16, 185, 129, 0.4)', text: '#34d399', glow: 'rgba(16, 185, 129, 0.2)' },
    { bg: 'rgba(6, 182, 212, 0.15)', border: 'rgba(6, 182, 212, 0.4)', text: '#38bdf8', glow: 'rgba(6, 182, 212, 0.2)' },
    { bg: 'rgba(139, 92, 246, 0.15)', border: 'rgba(139, 92, 246, 0.4)', text: '#a78bfa', glow: 'rgba(139, 92, 246, 0.2)' },
    { bg: 'rgba(236, 72, 153, 0.15)', border: 'rgba(236, 72, 153, 0.4)', text: '#f472b6', glow: 'rgba(236, 72, 153, 0.2)' }
  ];

  function renderTokenChips(result, container) {
    container.innerHTML = '';

    if (!result.tokens || result.tokens.length === 0) {
      container.innerHTML = `<div class="empty-state">Start typing above or select a language preset to see live subword segmentation.</div>`;
      return;
    }

    result.tokens.forEach((tok, i) => {
      const id = result.ids[i];
      const palette = CHIP_PALETTES[i % CHIP_PALETTES.length];

      const chip = document.createElement('div');
      chip.className = 'token-chip';
      chip.style.backgroundColor = palette.bg;
      chip.style.borderColor = palette.border;
      chip.style.boxShadow = `0 2px 8px ${palette.glow}`;

      // Convert visual 'Ġ' prefix to stylized space indicator
      const hasPrefix = tok.startsWith('Ġ');
      const cleanTok = hasPrefix ? tok.slice(1) : tok;

      chip.innerHTML = `
        ${hasPrefix ? '<span class="token-prefix" title="Leading Space">␣</span>' : ''}
        <span class="token-text" style="color: ${palette.text};">${escapeHtml(cleanTok || '␣')}</span>
        <span class="token-id" title="Vocabulary Token ID">#${id}</span>
      `;

      container.appendChild(chip);
    });
  }

  function escapeHtml(str) {
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // ---------------------------------------------------------------------------
  // 4. Playground DOM Wiring
  // ---------------------------------------------------------------------------
  function initPlayground() {
    const textInput = document.getElementById('playground-input');
    const chipContainer = document.getElementById('token-chips');
    const statWordCount = document.getElementById('stat-words');
    const statTokenCount = document.getElementById('stat-tokens');
    const statFertility = document.getElementById('stat-fertility');
    const statUnk = document.getElementById('stat-unk');
    const normDiffContainer = document.getElementById('norm-diff');

    const optStripAccents = document.getElementById('opt-strip-accents');
    const optCollapseWhitespace = document.getElementById('opt-collapse-whitespace');

    if (!textInput || !chipContainer) return;

    function runUpdate() {
      const rawText = textInput.value;
      const options = {
        stripAccents: optStripAccents ? optStripAccents.checked : false,
        collapseWhitespace: optCollapseWhitespace ? optCollapseWhitespace.checked : true
      };

      const result = tokenizeText(rawText, options);

      // Update stats
      if (statWordCount) statWordCount.textContent = result.wordCount;
      if (statTokenCount) statTokenCount.textContent = result.tokenCount;
      if (statFertility) statFertility.textContent = result.fertility;
      if (statUnk) {
        statUnk.textContent = result.unkCount === 0 ? '0.00% (0 <unk>)' : `${result.unkCount} <unk>`;
        statUnk.className = result.unkCount === 0 ? 'stat-value stat-success' : 'stat-value stat-warning';
      }

      // Normalization diff
      if (normDiffContainer) {
        if (rawText !== result.normalized && result.normalized.length > 0) {
          normDiffContainer.innerHTML = `
            <div class="diff-banner">
              <span class="diff-label">Normalized:</span>
              <span class="diff-content">${escapeHtml(result.normalized)}</span>
            </div>
          `;
          normDiffContainer.style.display = 'block';
        } else {
          normDiffContainer.style.display = 'none';
        }
      }

      renderTokenChips(result, chipContainer);
    }

    // Event listeners
    textInput.addEventListener('input', runUpdate);
    if (optStripAccents) optStripAccents.addEventListener('change', runUpdate);
    if (optCollapseWhitespace) optCollapseWhitespace.addEventListener('change', runUpdate);

    // Preset buttons
    const presetButtons = document.querySelectorAll('.preset-btn');
    presetButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        presetButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        const sampleKey = btn.dataset.sample;
        const found = DATA.samples.find(s => s.lang === sampleKey);
        if (found) {
          textInput.value = found.raw;
          runUpdate();
        }
      });
    });

    // Run initial on page load with first sample
    if (DATA.samples.length > 0) {
      textInput.value = DATA.samples[0].raw;
      runUpdate();
    }
  }

  // ---------------------------------------------------------------------------
  // 5. Leaderboard Rendering
  // ---------------------------------------------------------------------------
  function initLeaderboard() {
    const tabsContainer = document.getElementById('leaderboard-tabs');
    const tableContainer = document.getElementById('leaderboard-table-container');

    if (!tabsContainer || !tableContainer || !DATA.leaderboard.length) return;

    function renderLanguage(langData) {
      let html = `
        <div class="leaderboard-header-info">
          <h3>${langData.lang} <span class="lang-code">${langData.code}</span></h3>
          <p class="lang-desc">${langData.description}</p>
        </div>
        <div class="table-responsive">
          <table class="leaderboard-table">
            <thead>
              <tr>
                <th>Model</th>
                <th>Fertility (tok/word)</th>
                <th>Word Split >2</th>
                <th>Unknown Rate</th>
                <th>Compression (B/tok)</th>
                <th>Release Status</th>
              </tr>
            </thead>
            <tbody>
      `;

      langData.models.forEach(model => {
        const rowClass = model.isLeke ? 'leke-row' : '';
        const badgeClass = model.isLeke ? 'badge-success' : 'badge-neutral';
        const unkBadge = model.unkRate === 0 ? 'badge-pill-success' : 'badge-pill-warning';

        html += `
          <tr class="${rowClass}">
            <td class="model-name">
              <strong>${model.name}</strong>
              ${model.isLeke ? '<span class="pill-chip">Target Model</span>' : ''}
            </td>
            <td>
              <div class="metric-bar-group">
                <span class="metric-val ${model.isLeke ? 'metric-highlight' : ''}">${model.fertility}</span>
                <div class="progress-bar-bg">
                  <div class="progress-bar-fill ${model.isLeke ? 'fill-leke' : ''}" style="width: ${Math.min(100, (model.fertility / 3.5) * 100)}%;"></div>
                </div>
              </div>
            </td>
            <td>${model.splitRate}%</td>
            <td><span class="badge-pill ${unkBadge}">${model.unkRate}%</span></td>
            <td>${model.compression} bytes/tok</td>
            <td><span class="badge ${badgeClass}">${model.status}</span></td>
          </tr>
        `;
      });

      html += `
            </tbody>
          </table>
        </div>
      `;

      tableContainer.innerHTML = html;
    }

    // Render tabs
    tabsContainer.innerHTML = '';
    DATA.leaderboard.forEach((lang, idx) => {
      const btn = document.createElement('button');
      btn.className = `tab-btn ${idx === 0 ? 'active' : ''}`;
      btn.textContent = lang.lang;
      btn.addEventListener('click', () => {
        document.querySelectorAll('#leaderboard-tabs .tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        renderLanguage(lang);
      });
      tabsContainer.appendChild(btn);
    });

    // Initial render
    renderLanguage(DATA.leaderboard[0]);
  }

  // ---------------------------------------------------------------------------
  // 6. Code Tabs & Copy Tool
  // ---------------------------------------------------------------------------
  function initCodeTabs() {
    const tabButtons = document.querySelectorAll('.code-tab-btn');
    tabButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        const parent = btn.closest('.code-showcase');
        if (!parent) return;

        parent.querySelectorAll('.code-tab-btn').forEach(b => b.classList.remove('active'));
        parent.querySelectorAll('.code-panel').forEach(p => p.classList.remove('active'));

        btn.classList.add('active');
        const targetId = btn.dataset.target;
        const panel = document.getElementById(targetId);
        if (panel) panel.classList.add('active');
      });
    });

    // Copy to clipboard
    const copyButtons = document.querySelectorAll('.copy-btn');
    copyButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        const targetId = btn.dataset.code;
        const codeElement = document.getElementById(targetId);
        if (!codeElement) return;

        navigator.clipboard.writeText(codeElement.innerText).then(() => {
          const originalText = btn.innerHTML;
          btn.innerHTML = `✓ Copied!`;
          btn.classList.add('copied');
          setTimeout(() => {
            btn.innerHTML = originalText;
            btn.classList.remove('copied');
          }, 2000);
        });
      });
    });
  }

  // ---------------------------------------------------------------------------
  // 7. Initialize Application
  // ---------------------------------------------------------------------------
  document.addEventListener('DOMContentLoaded', () => {
    initPlayground();
    initLeaderboard();
    initCodeTabs();
  });
})();
