# Handoff: Leke site redesign (Broadsheet)

## Overview
A redesign of the Leke tokenizer showcase (https://acquayefrank.com/leke/) that replaces the old colour scheme with a newsprint aesthetic: near-black serif type on a paper-white ground, with cyan used sparingly as the accent. It is a single long page with these sections: nav, hero, numbers index, interactive tokenizer playground, evaluation leaderboard, architecture/features, pipeline, quickstart code tabs, and footer.

## About the design files
The files in this bundle are **design references built in HTML**. They show the intended look and behaviour; they are not production code to ship. Recreate the design in the target codebase's environment, using its established patterns. If there is no codebase yet, plain static HTML/CSS/JS or a small Astro/Vite site would suit a GitHub Pages deploy.

To preview it, serve the folder (`npx serve .`) and open `Leke.dc.html`. It uses a small runtime (`support.js`) to render. Ignore that runtime: read the markup, the inline styles, and the `class Component` logic at the bottom of the file.

## Fidelity
**High-fidelity.** Colours, type, spacing and copy are final. Match them closely.

## Design tokens
These come from `_ds/broadsheet-*/styles.css`. Link this stylesheet or copy its `:root` block. It also defines the `.btn`, `.tag`, `.table`, `.seg`, `.input` and `.nav` classes used on the page.

- Ground `--color-bg` #f3f2f2 · Surface `--color-surface` #eae9e9 · Ink `--color-text` #201e1d
- Accent (cyan) `--color-accent` #0088b0. Ramp: 100 #e9f8ff, 200 #cbeeff, 600 #1186ac (hover), 700 #006786 (small accent text and links), 800 #004961, 900 #0a303e
- Accent 2 (magenta) `--color-accent-2` #d6006c. Used only for byte-fallback tokens: 100 #fff1f4 fill, 800 #790e3d text
- Neutral ramp: 100 #f8f4f4, 200 #eae7e7, 800 #444141, 900 #2d2b2b
- Divider: `color-mix(in srgb, #201e1d 16%, transparent)`
- Muted text: ink at 70% (labels, captions) or 78% (body paragraphs) via `color-mix`
- Font: **Source Serif 4** for everything, headings at weight 600. There is no sans-serif anywhere. Code blocks use `ui-monospace, "SF Mono", Menlo, monospace`.
- Spacing scale: 5 / 10 / 15 / 20 / 30 / 40px. Radius: 2px (`--radius-md`).
- Rules: none between sections; whitespace does the separating. The only exception is the numbers index, which sits between a thick/thin head rule (2px over 1px, full ink) and 1px ink rules.

## Layout
- Page container: `max-width: 1200px`, centred, side padding `clamp(20px, 5vw, 72px)`. Everything is flush left, with whitespace on the right.
- Sections are spaced with padding of roughly 56px above and 84px below. The hero has 112px above and 84px below.
- Section kicker: 13px, uppercase, `letter-spacing: 0.08em`, ink at 70%, 14px gap below.
- Section H2: `clamp(30px, 3.4vw, 42px)`, weight 600, line-height 1.15, `letter-spacing: -0.015em`.
- Intro paragraphs: 16px, line-height 1.7, `max-width: 58ch`, ink at 78%.

## Sections
1. **Nav** (`.nav`): "Leke." brand at 22px/600 on the left, then links to Playground, Leaderboard, Architecture and Documentation (14px), then a primary "GitHub" button linking to github.com/acquayefrank/leke. Wraps on narrow screens.
2. **Hero**: H1 "Subword tokenization" / "for Kwa languages.", one line per sentence. Size `clamp(42px, 6.4vw, 88px)`, line-height 1.08, `letter-spacing: -0.02em`, plain ink with no plate or shadow effect. Below it, a 19px subhead (max 58ch) and three buttons: primary "Try the playground", secondary "View benchmarks", ghost "Read the docs". Buttons use `white-space: nowrap`.
3. **Numbers index**: head rule, then a dateline row (13px uppercase, spread with space-between): "Byte-level fallback · Rust core · PyO3 · Hugging Face ready · Apache 2.0". Then a 1px rule and a grid (`auto-fit, minmax(min(100%,380px),1fr)`) of dot-leader rows: label, dotted leader (1px dotted, ink at 45%), and a figure at 18px/600. The first figure is accent-700. Values: 4 Kwa languages supported · 1.83× lower fertility than NLLB-200 · 0.00% hard `<unk>` rate · 356k tokens/sec single core. A closing 1px rule.
   - ⚠ Check the 1.83× claim against the README table (12–28% lower).
4. **Playground** (`#playground`): H2 "Watch a sentence come apart." Then:
   - Sample buttons (`.btn-secondary`, 32px tall, 14px text). The active sample takes an accent-100 background.
   - A textarea (`.input`): 20px text, min-height 120px.
   - Three checkboxes (accent-coloured): map lookalikes (ε→ɛ, γ→ɣ, ɳ→ŋ, ð→ɖ) on by default; strip tone marks off; collapse whitespace on.
   - A "Normalized" label and output at 20px.
   - A "Tokens" row of chips, wrapping with a 6px gap. Each chip has 6/10px padding, 2px radius, the token at 18px with `white-space: pre`, and its ID at 11px below. Chips alternate accent-100 and accent-200 fills with accent-900 text. Byte tokens (`<0xF0>`) use accent-2-100 fill with accent-2-800 text.
   - A stats grid (`auto-fit, minmax(160px,1fr)`): figures at 40px/600 with tabular numbers, labels at 14px. Stats: Words, Subword tokens, Fertility, Unknown rate.
5. **Leaderboard** (`#leaderboard`): H2 "Fewer tokens per word, in every language." Then a `.table` at 16px, scrolling horizontally below 620px, with 14px vertical cell padding. Columns: Language · Leke BPE 8k (bold) · NLLB-200 · Monolingual (muted) · vs NLLB (`.tag.tag-accent`). Rows: Twi 2.23/2.92/1.62 Goldfish/−24% · Ewe 2.77/3.15/1.71 Wikilangs/−12% · Ga 2.38/3.20/—/−26% · Fante 2.16/2.98/—/−28% · Unknown rate 0.0%/0.0%/0.4–0.6%/Guaranteed. Below the table, a link to `specs/eval_results.md`.
6. **Architecture** (`#architecture`): H2 (max 22ch). Then a six-item grid (`auto-fit, minmax(min(100%,300px),1fr)`, gap 48px by `clamp(28px,4vw,64px)`). Each item has an H3 at 22px/600 and a 15.5px paragraph (line-height 1.75, justified, hyphenated). Below it, "The pipeline": an `ol` of 6 steps with a large accent-700 numeral (44px/600) above each label: Raw text → Unicode NFC → Lookalike mapping → Tone policy → Byte-level BPE → Token IDs.
7. **Quickstart** (`#docs`): H2 "Up and running in four lines." Then a `.seg` control (Python / Rust / Hugging Face / CLI training), a ghost "Copy code" button on the right that changes to "Copied" after clicking, and a `pre` block (background ink at 5% over the ground, 2px radius, 24/28px padding, 14px mono, line-height 1.7). The exact snippets are in the `CODE` object in the logic.
8. **Footer**: 14px muted text: "Leke — tokenization for African language NLP. Apache 2.0." Links: Back to top · GitHub · License.

## Interactions and state
- State: `text`, `preset` index, `look`, `tone`, `ws`, `tab`, `copied`.
- Clicking a sample sets the text. Typing clears the active sample.
- Normalization (in this order): NFC → lookalike map (when on) → strip combining tone marks U+0300–0304 and U+030C (when on) → collapse whitespace (when on).
- **The playground tokenizer is a stand-in.** The prototype splits words with a heuristic (syllable chunks of 5 characters or fewer, a `Ġ` prefix after a space, byte fallback for non-Latin symbols) and hashes token IDs. In production, wire the playground to the real Leke tokenizer: for example a WASM build of the Rust core, or a small API that runs `LekeTokenizer.encode`. Show its tokens and IDs, and compute fertility as tokens ÷ words.
- Hover, pressed and focus states come from the DS classes: hover uses accent-600 or a 7% ink tint, and keyboard focus is a 2px accent outline. Never show the browser's default blue focus ring.
- Smooth scrolling for the in-page anchors.
- Responsive: every grid uses `auto-fit` and `minmax`, so nothing needs a fixed breakpoint. The nav wraps, and the table scrolls horizontally.

## Assets
No images. All icons are optional; if you add any, use Phosphor in the duotone weight. Load Source Serif 4 from Google Fonts (the DS stylesheet already does).

## Files
- `Leke.dc.html`: the design (markup, inline styles and logic).
- `_ds/broadsheet-*/styles.css`: tokens and component classes.
- `support.js`: preview runtime only, not needed in production.
