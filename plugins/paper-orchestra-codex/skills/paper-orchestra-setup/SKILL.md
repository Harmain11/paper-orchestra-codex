---
name: paper-orchestra-setup
description: Set up the PaperOrchestra for Codex plugin, inspect local evidence-check prerequisites, and optionally configure Google's separate PaperOrchestra pipeline.
---

# PaperOrchestra setup

This skill is for first-time setup and help with installation. It is a local
**skill-based plugin**, not a hosted service. The default paper-writing path
uses the active Codex session. Google's original PaperOrchestra CLI is a
separate, optional multi-agent pipeline.

1. Read the plugin `README.md` and `SECURITY.md` before proposing execution.
2. Find this skill's plugin root by going up two directories from this file.
   Use `scripts/po_bridge.py doctor` to inspect local prerequisites. Python
   3.11 or newer is recommended for the helper.
3. Explain that Python is needed only for local evidence snapshots and SHA-256
   checks. Codex-native drafting does not require Python or an upstream
   checkout. On Windows use `py -3` if `python` opens a Microsoft Store shim;
   use `python3` on Unix where appropriate.
4. Git is needed only for the optional upstream checkout. LaTeX tools are
   optional and are used to compile a PDF. Never clone into the plugin cache.
5. Do not claim a separate provider API key is required for normal writing:
   Codex can draft in the active session. Only if the user opts into Google's
   upstream pipeline, follow its README for an isolated Python environment
   and package installation. Explain that provider credentials (Gemini,
   Vertex, or OpenAI) are separate from Codex and may incur charges. Never ask
   users to paste secrets into chat; keep `.env` local and uncommitted.
6. Run `doctor --upstream <path>` and verify `paper_writing_cli.py` and
   `templates/` only when the optional pipeline is requested. Do not run its
   provider model unless the user explicitly approves that execution.
7. Clarify that the local helper checks integrity and workflow mechanics; it
   does not guarantee scientific correctness or journal acceptance.

Useful local-only command:

```bash
python scripts/po_bridge.py doctor
```

Optional upstream commands (network or package installation requires explicit
approval):

```bash
python scripts/po_bridge.py setup --destination ../paper-orchestra
python scripts/po_bridge.py setup --destination ../paper-orchestra --ref COMMIT --execute
python scripts/po_bridge.py doctor --upstream ../paper-orchestra
```
