'use strict';
// Runs the actual inline documentation command builder with a minimal fake DOM.
// No browser, network, plugin installation, or model call is performed.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const html=fs.readFileSync('docs/index.html','utf8');
const source=(html.match(/<script>([\s\S]*?)<\/script>/)||[])[1];
assert.ok(source,'Inline website script missing');
const events={};
function element(id,value=''){
 return {id,value,textContent:'',dataset:{tab:id.replace('t-','')},attributes:{},
  addEventListener(type,fn){(events[id+':'+type]??=[]).push(fn)},
  setAttribute(k,v){this.attributes[k]=v},};
}
const els={os:element('os','win'),provider:element('provider','gemini'),command:element('command'),'code-title':element('code-title'),guide:element('guide'),warning:element('warning'),panel:element('panel'),copy:element('copy')};
const tabs=['install','prepare','write'].map(name=>element('t-'+name));
const document={querySelector(sel){return els[sel.slice(1)]},querySelectorAll(sel){assert.equal(sel,'[data-tab]');return tabs}};
const navigator={clipboard:{async writeText(x){navigator.lastCopied=x}}};
const ctx={document,navigator};
vm.runInNewContext(source,ctx,{timeout:2000});
function fire(id,type='click'){
 for(const fn of events[id+':'+type]||[])fn();
}
assert.match(els.command.textContent,/codex plugin marketplace add Harmain11\/paper-orchestra-codex/);
fire('t-prepare');
assert.match(els.command.textContent,/po_bridge\.py prepare/);
assert.match(els.command.textContent,/po_bridge\.py audit/);
els.os.value='unix';fire('os','change');
assert.match(els.command.textContent,/python3\.11/);
fire('t-write');
assert.match(els.command.textContent,/po_bridge\.py run/);
assert.match(els.command.textContent,/DRY RUN|Preview only|Preview/);
els.provider.value='openai';fire('provider','change');
assert.match(els.warning.textContent,/OpenAI/);
console.log('site-command-tests:PASS');
