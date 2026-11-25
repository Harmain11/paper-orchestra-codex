---
name: paper-orchestra-setup
description: Set up the PaperOrchestra for Codex plugin on a local computer, inspect prerequisites and configure the separate upstream PaperOrchestra checkout without automatic API calls.
---

# PaperOrchestra setup

This skill is for first-time setup and help with installation. It is a local
**skill-based plugin**, not a hosted service. The original PaperOrchestra is
not included and must be installed separately.

1. Read the plugin `README.md` and `SECURITY.md` before proposing execution.
2. Find this skill's plugin root by going up two directories from this file.
   Use `scripts/po_bridge.py doctor` first. Python 3.11 is recommended.
3. Explain the environment prerequisites: Python, optional Git, PaperOrchestra
   Python requirements, and optional LaTeX tools. On Windows prefer `python`;
   use `python3` on Unix where appropriate.
4. Run `setup --destination <user-owned-directory>` to show the exact clone
   plan; only add `--execute` after explicit approval. Recommend `--ref` to pin
   an audited upstream commit for reproducibility. Never clone into the plugin
   installation cache.
5. Follow upstream README for an isolated Python environment and package
   installation; do not use unreviewed global pip installs. Explain that API
   credentials (Gemini/Vertex or OpenAI) are needed for writing, but users
   should never paste secrets into chat. Keep `.env` local and uncommitted.
6. Run `doctor --upstream <path>` and verify `paper_writing_cli.py` and
   `templates/` exist. Offer an input snapshot with `prepare`, but do not run
   a paid model unless the user authorizes it.
7. Clarify that the wrapper only checks integrity and workflow mechanics:
   there is no guarantee of scientific correctness or journal acceptance.

Useful commands:

```bash
python scripts/po_bridge.py doctor
python scripts/po_bridge.py setup --destination ../paper-orchestra
python scripts/po_bridge.py setup --destination ../paper-orchestra --ref COMMIT --execute
python scripts/po_bridge.py doctor --upstream ../paper-orchestra
```
