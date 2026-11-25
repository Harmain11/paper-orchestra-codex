# Public release checklist

- [ ] Review all contents and redact user research, tokens, generated papers and proprietary assets.
- [ ] Create **public empty** `Harmain11/paper-orchestra-codex` repository.
- [ ] Push all files including dot-directories `.agents`, `.github`, `.codex-plugin`.
- [ ] Check the repository name, author, attribution and MIT license.
- [ ] Set repository description to: Evidence-first Codex plugin for Google Research PaperOrchestra — audit experiments, prepare verified research bundles, and draft LaTeX papers safely.
- [ ] Add topics: `codex`, `codex-plugin`, `paper-orchestra`, `research-tools`, `academic-writing`, `latex`, `reproducibility`, `agent-skills`, `multi-agent`, `machine-learning`.
- [ ] Enable **Issues**, **Discussions** (optional), and private vulnerability reporting if available.
- [ ] Enable **GitHub Pages** with **Source: GitHub Actions**; run Pages deployment and visit `/paper-orchestra-codex/`.
- [ ] Confirm CI passes on Windows and Ubuntu; manually test local Codex plugin installation.
- [ ] Check web documentation's command builder outputs match the wrapper help on Windows and Bash.
- [ ] Clone and audit upstream Google PaperOrchestra before any `--execute` operation.
- [ ] Check live integration with a small, **public synthetic** dataset and your own API key; avoid promising this passed until it actually passes.
- [ ] Publish a release tag after verified smoke testing. Until then, keep status "community beta".
- [ ] Optionally create a GitHub Discussion pinned to installation and scientific limitations.
