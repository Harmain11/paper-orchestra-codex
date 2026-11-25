# PaperOrchestra for Codex — plugin files

This directory is the installable plugin source. The top-level repository
contains the Codex marketplace and complete setup/publication instructions.

- `plugin.json`: Portable Agent Plugins 1.0 manifest.
- `SECURITY.md`: Setup, execution, and research-data safety guidance.
- `.codex-plugin/plugin.json`: Codex compatibility fallback.
- `skills/`: Setup, audit, and writer workflows.
- `scripts/po_bridge.py`: Python 3.11+ helper (stdlib only).
- `references/RESEARCH_INTEGRITY.md`: Scientific traceability rules.

The plugin does not bundle Google's PaperOrchestra or any external LLM API
credentials. The normal writing workflow uses the model in the active Codex
session. Only the optional upstream Google runner needs separate provider
credentials and explicit approval.

See the repository-root `README.md` for installation and usage.
