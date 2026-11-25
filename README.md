<div align="center">

<img src="assets/hero.svg" alt="PaperOrchestra for Codex — evidence-first research writing" width="100%" />

### From experiment logs to reviewable papers, without losing the evidence.

A community-built **Codex plugin** for [Google Research's PaperOrchestra](https://github.com/google-research/paper-orchestra). Prepare a traceable research snapshot, run integrity checks, and **optionally** orchestrate LaTeX manuscript drafting with the original PaperOrchestra agents.

[![CI](https://github.com/Harmain11/paper-orchestra-codex/actions/workflows/ci.yml/badge.svg)](https://github.com/Harmain11/paper-orchestra-codex/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.11%2B-356f9c?logo=python&logoColor=white)](https://python.org/)
[![License](https://img.shields.io/badge/License-MIT-279b88)](LICENSE)
[![Status](https://img.shields.io/badge/Status-community%20beta-d1aa65)](CHANGELOG.md)
[![Upstream](https://img.shields.io/badge/Powered%20by-PaperOrchestra-727aa6)](https://github.com/google-research/paper-orchestra)

**[Install](#install-the-plugin) · [Choose a workflow](#choose-your-workflow) · [Command reference](#command-reference) · [Interactive guide](#interactive-setup-guide) · [Science & safety](#evidence-first-by-design) · [FAQ](#faq)**

</div>

> [!IMPORTANT]
> This is an **independent community integration**, not an official Google, Google Research, OpenAI, or Codex product. The plugin does **not** automatically verify scientific claims, create new GPU results, or guarantee publication. The original PaperOrchestra Python pipeline is a separate installation; model API usage may incur charges.

## Why this exists

Writing a paper is easier than validating one. This plugin keeps **source evidence and source-derived claims** ahead of manuscript generation, and makes the costly actions deliberate.

| 🧬 Evidence first | 🔎 Checkable by default | 🎻 Original writing pipeline |
|:--|:--|:--|
| Snapshot source logs, protocols and approved figures | Verify file integrity with SHA-256 and refuse altered bundles | Use PaperOrchestra for outline, literature synthesis, drafting and LaTeX |
| Never turn example data into research findings | Separate hashes from statistical and citation verification | Run only when the user explicitly approves external model calls |

```mermaid
flowchart LR
  A[Research materials] --> B[Prepare snapshot]
  B --> C{Hash audit}
  C -->|Pass| D[Review & approve]
  C -->|Fail| X[Stop and fix inputs]
  D -->|Dry run| E[Preview upstream command]
  E -->|Execute only with approval| F[Google PaperOrchestra]
  F --> G[Draft LaTeX manuscript]
  G --> H[Human claim & citation review]
  classDef good fill:#daf8ed,color:#135544,stroke:#62b39a
  classDef caution fill:#fff4dd,color:#79551b,stroke:#dbb86c
  class C,D caution
  class B,G good
```

## Install the plugin

**Option A: Public GitHub marketplace** (once this repository is public):

```bash
codex plugin marketplace add Harmain11/paper-orchestra-codex
```

Then open Codex's **plugin marketplace**, find **PaperOrchestra for Codex**, install it, and open a new task. Adding a marketplace does not automatically install or enable its plugins. [Codex plugin documentation](https://developers.openai.com/plugins/build/plugins).

<details>
<summary><b>Option B — Local installation / before GitHub publication</b></summary>

Clone the repository or extract the source ZIP, keeping hidden folders such as `.agents` and `.codex-plugin`. From its root:

```bash
codex plugin marketplace add .
```

Install the plugin from the local marketplace UI. If your Codex build doesn't provide the marketplace command, use the [standalone CLI](#command-reference) while checking the official current installation docs.

</details>

<details>
<summary><b>What does Codex actually install?</b></summary>

It discovers the marketplace manifest at `.agents/plugins/marketplace.json`, which points to the packaged plugin. The plugin contains three reusable skills and a local Python bridge. The Google Research repository, Python packages and model API credentials are **not bundled or automatically installed**.

</details>

## Choose your workflow

<details open>
<summary><b>01 · I want to audit research before writing a paper</b> — free, offline</summary>

Start with a folder containing `idea_sparse.md`, `experimental_log.md` and optional verified figures. Use the same Python bridge from your local clone of this repository:

```bash
python plugins/paper-orchestra-codex/scripts/po_bridge.py prepare --materials examples/demo/raw_materials --bundle work/demo
python plugins/paper-orchestra-codex/scripts/po_bridge.py audit --bundle work/demo
```

The bundled demo uses **fictional materials only**. Replace it with real experiment records for genuine research work. The audit checks hashes and file inventory, **not** whether a statistical claim is true.

</details>

<details>
<summary><b>02 · I want to set up Google's upstream PaperOrchestra</b> — network action requires approval</summary>

```bash
python plugins/paper-orchestra-codex/scripts/po_bridge.py doctor
python plugins/paper-orchestra-codex/scripts/po_bridge.py setup --destination ../paper-orchestra
# Review upstream code and the clone plan, then explicitly approve:
python plugins/paper-orchestra-codex/scripts/po_bridge.py setup --destination ../paper-orchestra --execute
```

Create a **Python 3.11+** virtual environment inside the upstream project, install its `requirements.txt`, and configure your own `.env` there. Set provider-level API spending limits. See [setup walkthrough](#upstream-environment).

</details>

<details>
<summary><b>03 · I want a complete LaTeX draft</b> — API fees possible</summary>

First create and audit a bundle containing **real evidence** and install upstream PaperOrchestra. Then preview the invocation:

```bash
python plugins/paper-orchestra-codex/scripts/po_bridge.py run --upstream ../paper-orchestra --bundle work/my-study --output-dir work/manuscript --template-dir templates/cvpr2025
```

Nothing runs until you repeat the reviewed command with `--execute`. PaperOrchestra may transmit research materials to your selected model provider. Review the LaTeX output and every quantitative statement manually.

</details>

<details>
<summary><b>04 · I'm building my own research agent</b> — use the bridge as a component</summary>

The bridge is Python standard-library only; `doctor`, `prepare`, `audit`, `setup`, and `run` are callable from a terminal or agent. Keep the original upstream PaperOrchestra dependency outside this repo. Read [research integrity rules](plugins/paper-orchestra-codex/references/RESEARCH_INTEGRITY.md), [contributing](CONTRIBUTING.md), and the [test suite](tests/test_bridge.py).

</details>

## Interactive setup guide

**Want commands tailored to your operating system and model provider?** Use the **[interactive setup wizard](https://harmain11.github.io/paper-orchestra-codex/)** after GitHub Pages is enabled, or clone the repository and open [`docs/index.html`](docs/index.html) locally in your browser. It creates copyable commands without contacting model APIs or uploading data.

> GitHub README files support collapsible sections, links and Mermaid diagrams, but not custom JavaScript. The setup wizard lives in `docs/index.html` because a genuinely interactive interface needs a web page.

## Command reference

Run all examples from this repo's root. The bridge requires Python 3.11+ but only Python's standard library.

| Command | What it does | Network/API calls |
|---|---|---|
| `doctor` | Check Python, Git, LaTeX and credential *presence* | None |
| `setup --destination PATH` | Preview cloning upstream | None |
| `setup --destination PATH --execute` | Clone original PaperOrchestra | **GitHub network** |
| `prepare --materials DIR --bundle DIR` | Create a source snapshot and hash manifest | None |
| `audit --bundle DIR` | Detect missing, modified or untracked files | None |
| `run --upstream DIR --bundle DIR --output-dir DIR` | Preview Python generation command | None |
| `run ... --execute` | Start upstream manuscript-generation pipeline | **External model APIs possible** |

<details>
<summary><b>Show full input structure and real-run command</b></summary>

```text
raw_materials/
├── idea_sparse.md          # Question, motivation and testable hypothesis
├── experimental_log.md     # Provenance, methods, measured numbers, limitations
└── figures/
    ├── figure_01.png       # Verified figure, not a fabricated illustration
    └── figure_02.pdf
```

```bash
python plugins/paper-orchestra-codex/scripts/po_bridge.py prepare --materials ./my-study/raw_materials --bundle ./work/my-study
python plugins/paper-orchestra-codex/scripts/po_bridge.py audit --bundle ./work/my-study
python plugins/paper-orchestra-codex/scripts/po_bridge.py run --upstream ../paper-orchestra --bundle ./work/my-study --output-dir ./work/my-paper --template-dir templates/cvpr2025
# Add --execute to the same run command ONLY after reviewing inputs, costs and provider privacy.
```

</details>

### Upstream environment

<details>
<summary><b>Windows PowerShell</b></summary>

```powershell
cd ../paper-orchestra
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

</details>

<details>
<summary><b>macOS / Linux</b></summary>

```bash
cd ../paper-orchestra
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

</details>

Upstream credentials belong in a **local** `paper-orchestra/.env`, never in GitHub. Its CLI currently defaults to Gemini preview models and supports model-provider configuration; confirm provider compatibility and prices at runtime. Optional TeX tools are needed for PDF compilation. [Upstream README](https://github.com/google-research/paper-orchestra#readme).

## Evidence-first by design

| Safety property | Implemented behavior | Still requires human review |
|---|---|---|
| File provenance | SHA-256 hashes and sizes for source snapshots | Whether files were collected correctly |
| Integrity gates | Fail on altered, missing, added or symlinked files | Whether claims are supported by those files |
| Secrets | Ignore common `.env`, key and credential filenames | Detect secrets hidden in other file types |
| Cost control | No clone / API call without `--execute` | Provider pricing and token spending |
| Claims | Clear evidence-review instructions in skills | Citations, statistical tests and correctness |

Read [security](SECURITY.md) before sending unpublished or confidential material to model providers. This plugin cannot guarantee journal acceptance, originality, or peer review.

## Repository map

```text
.agents/plugins/marketplace.json            Marketplace catalog
plugins/paper-orchestra-codex/plugin.json  Portable plugin metadata
plugins/paper-orchestra-codex/.codex-plugin/plugin.json   Codex compatibility
plugins/paper-orchestra-codex/skills/       Setup / Audit / Write skills
plugins/paper-orchestra-codex/scripts/po_bridge.py  Safe Python bridge
docs/index.html                              Interactive setup wizard
assets/hero.svg                             README artwork
tests/test_bridge.py                        Offline regression tests
.github/workflows/ci.yml                   Ubuntu and Windows CI
```

## FAQ

<details>
<summary><b>Do I need an OpenAI API key?</b></summary>

Not necessarily. Google PaperOrchestra supports Gemini / Vertex AI and OpenAI providers with suitable credentials. **A Codex subscription is not an external API credit balance.** The plugin's offline audit commands need no API key.

</details>

<details>
<summary><b>Is this the official Google PaperOrchestra project?</b></summary>

No. This is a separate community wrapper, with attribution and license notices. [Original Google repository](https://github.com/google-research/paper-orchestra).

</details>

<details>
<summary><b>Can it write a publishable paper automatically?</b></summary>

It can invoke a workflow intended to produce submission-ready LaTeX, but **scientific validity, references, formatting and suitability require independent checks**. Do not treat model-generated text as validated scientific evidence.

</details>

<details>
<summary><b>Does installing this plugin send my research data to an API?</b></summary>

No. Setup and execution are explicit operations, and local hashing does not access external APIs. `run --execute` starts Google's upstream pipeline, which may send your provided research materials to configured model providers.

</details>

<details>
<summary><b>Can I use it without Codex?</b></summary>

Yes. The bridge CLI can be run directly from Python, and the optional website is a standalone static page.

</details>

<details>
<summary><b>Why doesn't the repository include a sample scientific paper?</b></summary>

The demo input intentionally contains no fabricated results. Use your own validated evidence and reproduce experiments before publishing claims.

</details>

## Publish your own repository (maintainer)

The maintainer can publish this source with the **dry-run-first helper** after reviewing the public file list. It requires local Git and the authenticated [GitHub CLI](https://cli.github.com/):

```bash
python scripts/publish_to_github.py                 # preview: changes nothing
python scripts/publish_to_github.py --execute       # creates a PUBLIC repo and pushes
```

It targets **Harmain11/paper-orchestra-codex** and refuses to overwrite an existing repo. Set **Settings → Pages → GitHub Actions** after publishing to activate the interactive docs site. The same steps are provided in [the ready-to-paste Codex handoff prompt](CODEX_SETUP_PROMPT.md).

## Release checklist

Publishing under `Harmain11`? Follow the [release checklist](RELEASE_CHECKLIST.md), including GitHub Pages enablement and a verified manual Codex install. This community package is not yet an official-directory listing.

## Contributing

Issues, pull requests and reproducibility improvements are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md). Run the offline tests before opening a PR:

```bash
python -m unittest discover -s tests -v
python -m compileall -q plugins/paper-orchestra-codex/scripts
```

CI runs on Ubuntu and Windows. The `docs/` static site can be published with the included GitHub Pages workflow after enabling **Settings → Pages → GitHub Actions**. A manual Codex installation and a real upstream manuscript smoke test still need to be verified separately. [Third-party notices](THIRD_PARTY_NOTICES.md) · [Changelog](CHANGELOG.md) · [MIT License](LICENSE).

---

<div align="center">

**Build from evidence. Keep the audit trail. Let the writing agents help—not decide the science.**

Made with care by [Harmain Dastgir](https://github.com/Harmain11) · Independent community integration.

</div>

