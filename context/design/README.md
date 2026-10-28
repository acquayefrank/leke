# Handoff: Leke documentation home

## Overview
The landing page for the Leke docs site (https://acquayefrank.com/leke/). It has a sticky sidebar, a top bar with search, an intro with four entry cards, and two link grids (by language and by binding). Build it as the home page of a docs framework, then reuse the shell (sidebar and top bar) on every docs page.

## About the design files
`Leke Docs.dc.html` is a **design reference built in HTML**, not production code. Recreate it in the target stack; good fits for a static docs site are Astro Starlight, Nextra, VitePress or Docusaurus with a custom theme. To preview, serve the folder (`npx serve .`) and open the file. `support.js` is the preview runtime only: read the markup, the inline styles and the `class Component` logic, and ignore the runtime.

## Fidelity
**High-fidelity.** Match the colours, type, spacing and copy.

## Tokens
- Background #ffffff · Text #131316 · Muted text #5e5f6e · Subtle labels #7a7b88
- Borders: sidebar and header #ececef · cards #e8e8ec (hover #d4d4da) · inputs and badges #e3e3e7 · hero decoration #f0f0f2
- Hover/active fill #f4f4f5
- Accent: link #006786, hover #0088b0, focus ring `2px solid #0088b0`, offset 2px. Language badges in the sidebar: #eef9fe fill with #006786 text.
- Font: **Geist** (400/500/600), with Geist Mono for code. Turn on `-webkit-font-smoothing: antialiased`.
- Icons: Phosphor, **duotone** weight (`@phosphor-icons/web`).
- Radii: cards 10px · inputs 8px · nav items 7px · badges 5–6px · decorative shapes 40px.
- Shadows: rest `0 1px 2px rgba(19,19,22,.04)`; card hover `0 4px 14px rgba(19,19,22,.07)`, 150ms transition.

## Layout
- Two columns. The sidebar is 240–280px wide, `position: sticky; top: 0; height: 100vh`, scrolls on its own, and has a 1px right border. The main column takes the rest. Below about 820px the columns stack; in production, turn the sidebar into a drawer opened by a menu button.
- Top bar: 60px tall, sticky, `rgba(255,255,255,.92)` with an 8px backdrop blur and a 1px bottom border. Search sits on the left; on the right are a "Playground" text link and a "GitHub" link with an icon.
- Main content: max-width 1040px, side padding `clamp(20px, 5vw, 76px)`, 96px bottom padding.

## Components
**Sidebar**
- Brand row (60px tall): a 22px black rounded square with a white "L", the word "leke" (20px/600, −0.02em tracking) and a "Docs" pill (11.5px/500, 1px border, 5px radius).
- Top nav items: an 18px muted icon, 10px gap, then the label at 14px. Padding 7px 10px, 7px radius. The active item gets a #f4f4f5 fill and weight 600; hover gets the same fill.
- Groups: a title at 12.5px #7a7b88 with 24px above it, then items styled like the top nav but without icons.
  - Core concepts: Introduction, Unicode normalization, Lookalike mapping, Tone policy, Byte-level BPE, Training a vocabulary
  - Languages: Twi, Ewe, Ga, Fante, each with an 18px tinted badge (Tw/Ee/Ga/Fa)
  - Reference: Python API, Rust API, Tokenizer config, Evaluation results

**Search**
- 34px tall, 260px max width, 1px border, 8px radius. A magnifier icon, a borderless input ("Search documentation", 13.5px) and a "⌘K" hint. ⌘K / Ctrl+K focuses the input.
- Wire it to the docs framework's search (Pagefind, Algolia DocSearch, etc.).

**Intro**
- Kicker "Get set up" (13px, muted), then the H1 "Leke documentation" (`clamp(28px, 3.2vw, 34px)`/600, −0.025em, line-height 1.2), then a 15px muted subtitle (max 60ch).
- 68px top padding.

**Entry cards**
- Grid `repeat(auto-fit, minmax(min(100%,210px),1fr))` with a 20px gap, 44px below the intro.
- Each card has 24/22px padding: a 30px muted duotone icon, then the title (15px/600) 36px below it, then the body (14px, line-height 1.6, muted). The whole card is the link.
- Cards: Quickstart (play-circle) · Pretrained tokenizers (cube) · Benchmarks (chart-bar) · API Reference (brackets-angle).

**Link grids** ("Explore by language" / "Explore by binding")
- An H2 at 22px/600, −0.02em, with 80px above it, a 15px muted subtitle, then a grid `repeat(auto-fit, minmax(min(100%,280px),1fr))` with gaps of 34px vertical and 40px horizontal.
- Each item: a 32px leading mark, 16px gap, then the name (15px/600) and the description (14px muted, 6px above it). On hover the text turns #006786.
- Languages use a black circle with a white 2-letter code. Bindings use 32px duotone icons: file-py, gear-six, smiley (stand in with a real Hugging Face logo if licensing allows), terminal-window.
- All copy is in `renderVals()` in the source file.

**Hero decoration**
- Three absolutely positioned 1px #f0f0f2 outlined rectangles with 40px radius, behind the intro, clipped by `overflow: hidden` on the main column, with `pointer-events: none`.
- Positions: left 52px / top −40px, 280×280 · right −60px / top −30px, 300×210 · right −120px / top 200px, 220×160.

## Behaviour
- The active sidebar item tracks the current route.
- Card and grid links are wired to functional routes:
  - Quickstart -> `Leke.dc.html#docs`
  - Field Manual -> `manual.html` (Interactive Field Manual)
  - Benchmarks -> `Leke.dc.html#leaderboard`
  - API Reference -> Python/Rust repository documentation
  - Languages -> `Leke.dc.html#leaderboard` / `#playground`
  - Bindings -> Python / Rust / HF / CLI repository docs
- "Playground" links to the interactive tokenizer on the main site (`Leke.dc.html#playground` or `/leke/#playground`).
- Search input supports instant ⌘K / Ctrl+K keyboard shortcut and displays interactive matching results dropdown.
- Every interactive element has a hover state and the cyan focus-visible ring.

## Files
- `Leke Docs.dc.html`: the design.
- `support.js`: preview runtime only.
