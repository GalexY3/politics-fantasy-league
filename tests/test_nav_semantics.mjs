import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const html=readFileSync(new URL('../src/politics_fantasy/web/index.html',import.meta.url),'utf8');
const js=readFileSync(new URL('../src/politics_fantasy/web/app.js',import.meta.url),'utf8');
test('Initial selected section is exposed semantically',()=>assert.match(html,/data-tab="overview" class="nav-item active" aria-current="page"/));
test('Dynamic navigation updates and removes the selected-state attribute',()=>{
 assert.match(js,/setAttribute\('aria-current','page'\)/);
 assert.match(js,/removeAttribute\('aria-current'\)/);
});
