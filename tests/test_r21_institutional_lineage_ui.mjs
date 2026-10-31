import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {runInNewContext} from 'node:vm';

const source=readFileSync(new URL('../src/politics_fantasy/web/app.js',import.meta.url),'utf8');
const match=source.match(/function institutionalLineagePanel\(\)\{[\s\S]*?\n\}/);
assert.ok(match,'Actual R21 UI renderer must exist, not a hand-written mock');
const escapeText=s=>String(s??'').replace(/[&<>"']/g,
 c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const good={
 schema:'pfl.synthetic_institutional_lineage.v1',
 evidence_class:'SYNTHETIC_LAB_ONLY',
 legal_identity_authenticated:false,registered_at_risk_certified:false,
 source_reuse_rights_verified:false,scientific_AB_cycles:0,
 snapshot_mode:'HISTORICAL_SYNTHETIC_LAB',
 status:'SYNTHETIC_LINEAGE_DOCUMENTARY_ONLY',
 distinct_active_legal_key_claims:2,complete_explicit_lineage_links:4,
 incomplete_reorganization_groups:0,
 link_classes:{LEGAL_RENAME_SAME_KEY:1,MERGER_PREDECESSOR:2,SPLIT_SUCCESSOR:0,
 COMPETENCE_TRANSFER:0,JURISDICTION_TRANSFER:0,DOCUMENTARY_REFERENCE:1},
 stage_graph:{visible_stages:{REGISTRATION:1},visible_claimed_edges:1},
 as_of:'2026-08-01T00:00:00Z',cut_on:'2023-12-31',
 legal_calendar_zone:'Europe/Madrid',
};
function render(data){
 return runInNewContext(match[0]+'\ninstitutionalLineagePanel()',{
  ui:{institutionalLineage:data},esc:escapeText,count:x=>String(x),
  stat:(a,b,c)=>'<span>'+[a,b,c].map(escapeText).join(' ')+'</span>',
  Number,encodeURIComponent,
 });
}

test('R21 real panel renders bounded fictitious N:M but not real evidence',()=>{
 const html=render(good);
 assert.match(html,/C15 · identidad institucional/);
 assert.match(html,/Fusión \(N:1\)/);
 assert.match(html,/R5 STOP/);
 assert.match(html,/0 AB científicos/);
 assert.match(html,/HISTORICAL_SYNTHETIC_LAB/);
 assert.match(html,/as_of=2026-08-01T00%3A00%3A00Z/);
 assert.ok(!html.includes('validación empírica'));
});
test('R21 untrusted or promoted claim is not rendered',()=>{
 for(const mutation of [{...good,legal_identity_authenticated:true},
   {...good,registered_at_risk_certified:true},
   {...good,source_reuse_rights_verified:true},
   {...good,scientific_AB_cycles:1},{}]){
  const html=render(mutation);
  assert.match(html,/no ha superado sus contratos/);
  assert.ok(!html.includes('Fusión (N:1)'));
 }
});
test('R21 quarantine suppresses counts, IDs, dates and unverifiable joins',()=>{
 const html=render({...good,status:'SYNTHETIC_IDENTITY_CONFLICT_QUARANTINED',
  quarantine_reason:'SYNTHETIC:<bad>',stage_graph:null,
  complete_explicit_lineage_links:null});
 assert.match(html,/cuarentena/);
 assert.ok(!html.includes('SYNTHETIC:&lt;bad&gt;'));
 assert.ok(!html.includes('Fusión (N:1)'));
});
test('R21 escaped output protects against UI injection in as_of',()=>{
 const html=render({...good,as_of:'<img src=x onerror=alert(1)>'});
 assert.ok(!html.includes('<img'));
 assert.ok(html.includes('&lt;img'));
});
