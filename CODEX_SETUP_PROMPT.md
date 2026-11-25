# Paste this into Codex on your own computer

You are configuring the public GitHub release of **PaperOrchestra for Codex**.

The user has downloaded and extracted the official delivery ZIP `paper-orchestra-codex-github-ready.zip`. Work only in that extracted `paper-orchestra-codex/` folder; if it is not open in Codex, ask the user to open it rather than guessing a path.

1. Audit `README.md`, `.agents/plugins/marketplace.json`, `plugins/paper-orchestra-codex/plugin.json`, the bridge code, CI workflow, license, and GitHub Pages website.
2. Run `python -m unittest discover -s tests -v` and `python plugins/paper-orchestra-codex/scripts/po_bridge.py doctor`; make no network/API requests during this step.
3. Check `git status` and `gh auth status`. Confirm `gh` is authenticated as the intended GitHub account **Harmain11**.
4. Review `python scripts/publish_to_github.py` with the user. It creates **one PUBLIC** repository and pushes these files only when invoked with `--execute`. Never publish unpublished research, local keys or tokens.
5. Once the user has approved public publication, run `python scripts/publish_to_github.py --execute`. If the repo already exists, do not overwrite it; inspect the existing repo and ask before modifying.
6. Verify the public repository contains the README, two plugin manifests, three skills, CI tests, and documentation. Confirm link and badge status.
7. Enable GitHub Pages using the GitHub Actions workflow if the user approves its settings change; verify the interactive docs URL and responsive behavior in a browser.
8. Install the plugin into local Codex using the documented marketplace command; verify installation and skills. Do not run third-party model APIs or the upstream PaperOrchestra workflow without separate explicit approval.
9. Report actual outputs and limitations; distinguish confirmed success from untested steps.

Avoid inflating the paper-writing capabilities: the plugin provides evidence hashing, preflight checks, and opt-in upstream writing; it does not guarantee statistically valid manuscripts, validated citations, or peer review.
