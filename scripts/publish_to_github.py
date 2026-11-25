#!/usr/bin/env python3
"""Opt-in, clearly scoped GitHub publish helper for the PaperOrchestra Codex plugin.

Run from the extracted repository root. Requires git and gh, both authenticated on
user's own computer. Default mode prints instructions and changes NOTHING.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys

OWNER = "Harmain11"
NAME = "paper-orchestra-codex"
REPO = f"{OWNER}/{NAME}"
URL = f"https://github.com/{REPO}"
SITE = f"https://{OWNER.lower()}.github.io/{NAME}/"
DESCRIPTION = "Evidence-first Codex plugin for Google PaperOrchestra: research snapshots, audit checks and opt-in LaTeX writing."
TOPICS = "codex,codex-plugin,paper-orchestra,agent-skills,reproducible-research,latex,academic-writing"
ROOT = Path(__file__).resolve().parent.parent


def run(cmd: list[str]) -> None:
    print("+", subprocess.list2cmdline(cmd), flush=True)
    subprocess.run(cmd, cwd=ROOT, check=True)


def check_root() -> None:
    expected = ["README.md", "LICENSE", ".agents/plugins/marketplace.json", "plugins/paper-orchestra-codex/plugin.json"]
    missing = [file for file in expected if not (ROOT / file).is_file()]
    if missing:
        raise SystemExit("Missing repository content: " + ", ".join(missing))
    for path in ROOT.rglob("*"):
        if ".git" in path.parts:
            continue
        if path.is_file() and (path.name in {".env", ".env.local", "credentials.json", "secrets.json"} or path.suffix in {".pem", ".p12", ".pfx"}):
            raise SystemExit("Possible secret file in public package; remove/review: " + str(path.relative_to(ROOT)))


def main() -> int:
    p = argparse.ArgumentParser(description="Publish the reviewed source on GitHub (dry-run by default)")
    p.add_argument("--execute", action="store_true", help="Actually initialize and publish a public GitHub repo")
    args = p.parse_args()
    check_root()
    print("Repository:", REPO)
    print("Visibility: PUBLIC")
    print("Source:", ROOT)
    print("Target:", URL)
    print("Action: initialize git, commit curated files, create public repo and push")
    print("Metadata: description and topics; GitHub Pages must be enabled separately")
    print("Review README, LICENSE and all files before publication. Unpublished research and secrets must not be included.")
    if not args.execute:
        print("DRY RUN: No git, gh or network operation performed. Append --execute after reviewing.")
        return 0
    if (ROOT / ".git").exists():
        raise SystemExit("Existing .git detected; refusing to change an existing repository. Publish manually or use a fresh extraction.")
    if not shutil.which("git") or not shutil.which("gh"):
        raise SystemExit("Install git and GitHub CLI (gh), then run `gh auth login` before executing.")
    run(["gh", "auth", "status"])
    # Fail early if a project with this name already exists. If this succeeds, stop.
    probe = subprocess.run(["gh", "repo", "view", REPO, "--json", "name"], cwd=ROOT,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    if probe.returncode == 0:
        raise SystemExit(f"Repository already exists: {URL}. Refusing to overwrite.")
    run(["git", "init", "-b", "main"])
    run(["git", "add", "-A"])
    # Credentials and host-local files are intentionally excluded by .gitignore.
    print("Review the staged file list above and approve publication before execution.")
    run(["git", "diff", "--cached", "--stat"])
    run(["git", "commit", "-m", "Initial public release: PaperOrchestra Codex plugin"])
    run(["gh", "repo", "create", REPO, "--public", "--source", ".", "--remote", "origin", "--push", "--description", DESCRIPTION])
    run(["gh", "repo", "edit", REPO, "--description", DESCRIPTION, "--homepage", SITE, "--add-topic", TOPICS])
    print("Published:", URL)
    print("Next: enable Settings > Pages > Build and deployment > GitHub Actions to publish docs/.")
    print("Next: test `codex plugin marketplace add " + REPO + "` from your Codex installation.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as error:
        print("FAILED: command returned", error.returncode, file=sys.stderr)
        raise SystemExit(error.returncode)
