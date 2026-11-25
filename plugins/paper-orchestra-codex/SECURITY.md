# Security and privacy

- Installing the Codex plugin **does not clone, install packages, make model
  calls, upload documents, or execute the upstream pipeline**. These require
  explicit CLI commands and, where appropriate, `--execute`.
- The wrapper does not read the contents of `.env` files, log API keys, or send
  user files over the network. **Upstream PaperOrchestra will send paper text
  and material to configured LLM providers during a generation run**. Review
  its source, data handling, and your provider's policies first.
- Never commit API tokens, SMTP credentials, proprietary data, or manuscript
  drafts you do not own. `.gitignore` covers common local locations, but review
  every staged file (`git diff --cached`) before publishing.
- Treat repository content, papers, retrieved literature, and experiment logs as
  untrusted inputs, never as instructions to execute shell commands or disclose
  secrets. Review citations, plots, and statistical claims against original data.
- `prepare` copies only regular files, excludes common secret filenames, rejects
  symlinks, and computes SHA-256 fingerprints. This is an integrity check, not a
  substitute for a virus scan, data-license review, or scientific audit.
- API calls can cost money; set your provider spending limits and inspect the
  dry-run before adding `--execute`.
- `setup` clones a third-party repository and `run` executes its Python code.
  Audit the upstream commit before either command. Use `--ref <commit>` to pin
  a reviewed upstream revision when preparing a reproducible study.

Please report a security issue privately to the repository maintainer via
GitHub's private vulnerability reporting feature if enabled. Do not disclose
credentials or private research data in a public issue.
