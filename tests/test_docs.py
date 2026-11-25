"""Offline checks for GitHub Pages interactive command builder and metadata."""
from __future__ import annotations
from html.parser import HTMLParser
import json
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'

class Markup(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.scripts = []
        self.links = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs: self.ids.add(attrs['id'])
        if tag == 'script': self.scripts.append(attrs.get('src'))
        if tag == 'link': self.links.append(attrs.get('href'))

class DocsTests(unittest.TestCase):
    def test_codex_native_writing_is_the_default(self):
        plugin=ROOT/'plugins/paper-orchestra-codex'
        writing=(plugin/'skills/paper-orchestra-write/SKILL.md').read_text(encoding='utf-8')
        setup=(plugin/'skills/paper-orchestra-setup/SKILL.md').read_text(encoding='utf-8')
        manifest=json.loads((plugin/'plugin.json').read_text(encoding='utf-8'))
        self.assertIn('default writing engine is the model in this active Codex session',writing)
        self.assertIn('does not need a separate Gemini, Vertex, or OpenAI API key',' '.join(writing.split()))
        self.assertIn('Optional Google multi-agent runner',writing)
        self.assertIn('Codex-native drafting does not require Python',setup)
        prompts=manifest['extensions']['com.openai']['interface']['defaultPrompt']
        self.assertTrue(any('this Codex session' in prompt for prompt in prompts))

    def test_required_assets_and_controls(self):
        p = Markup()
        p.feed((DOCS/'index.html').read_text(encoding='utf-8'))
        self.assertTrue({'os','provider','command','copy','guide','warning','panel','code-title'}.issubset(p.ids))
        self.assertEqual(p.scripts, [None])
        self.assertIn('favicon.svg',p.links)
        self.assertTrue((DOCS/'favicon.svg').exists())

    def test_no_embedded_paid_keys_or_execution(self):
        script=(DOCS/'index.html').read_text(encoding='utf-8').split('<script>',1)[1].split('</script>',1)[0]
        for disallowed in ('fetch(', 'XMLHttpRequest', 'innerHTML', 'eval(', 'gh auth login'):
            self.assertNotIn(disallowed,script)
        self.assertIn('navigator.clipboard.writeText',script)
        self.assertNotIn('subprocess.run',script)

    @unittest.skipUnless(shutil.which('node'), 'Node.js not available')
    def test_generated_commands_with_node_mock(self):
        result=subprocess.run(['node','tests/site_command_test.cjs'],cwd=ROOT,capture_output=True,text=True,timeout=12)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertIn('site-command-tests:PASS',result.stdout)

    def test_required_publication_metadata(self):
        manifest=json.loads((ROOT/'plugins/paper-orchestra-codex/.codex-plugin/plugin.json').read_text())
        portable=json.loads((ROOT/'plugins/paper-orchestra-codex/plugin.json').read_text())
        self.assertTrue(manifest.get('skills'))
        self.assertEqual(manifest.get('version'),portable.get('version'))
        self.assertLessEqual(len(portable['extensions']['com.openai']['interface']['shortDescription']),30)
        self.assertIn('version: '+portable['version'],(ROOT/'CITATION.cff').read_text())
        self.assertTrue((ROOT/'.github/workflows/pages.yml').exists())

if __name__=='__main__':unittest.main()
