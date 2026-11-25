"""Offline distribution, documentation, and publishing safety checks."""
import subprocess
import sys
from pathlib import Path
from xml.etree import ElementTree
import unittest

ROOT=Path(__file__).resolve().parents[1]

class PublicReleaseTests(unittest.TestCase):
    def test_publish_defaults_to_preview_only(self):
        r=subprocess.run([sys.executable,str(ROOT/'scripts/publish_to_github.py')],cwd=ROOT,text=True,capture_output=True)
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertIn('DRY RUN: No git, gh or network operation performed',r.stdout)

    def test_documentation_has_real_interactive_controls(self):
        html=(ROOT/'docs/index.html').read_text(encoding='utf-8')
        for marker in ['id="os"','id="provider"','id="copy"','aria-selected="true"','navigator.clipboard.writeText','role="tabpanel"']:
            self.assertIn(marker,html)
        self.assertNotIn('https://fonts.googleapis.com',html)
        self.assertNotIn('<script src="https://',html)

    def test_svg_artwork_is_valid_xml(self):
        ElementTree.parse(ROOT/'assets/hero.svg')
        ElementTree.parse(ROOT/'docs/favicon.svg')

    def test_public_repo_essentials_exist(self):
        for rel in ['README.md','CODEX_SETUP_PROMPT.md','.github/workflows/pages.yml',
                    '.github/ISSUE_TEMPLATE/bug_report.yml','.github/ISSUE_TEMPLATE/feature_request.yml',
                    '.github/PULL_REQUEST_TEMPLATE.md','docs/index.html','scripts/publish_to_github.py']:
            self.assertTrue((ROOT/rel).is_file(),rel)

if __name__=='__main__':unittest.main()
