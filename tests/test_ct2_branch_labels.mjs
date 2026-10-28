import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const js=readFileSync(new URL('../src/politics_fantasy/web/app.js',import.meta.url),'utf8');
test('Forecast and identity CT2 are separate dated ordinal measures',()=>{
 assert.match(js,/CT2 predicción parlamentaria \(corte histórico 25\/10\/2026\): 24\/100/);
 assert.match(js,/CT2 identidad multifuente \(28\/10\/2026\): 29\/100/);
 assert.match(js,/Son ramas distintas y escalas ordinales, no probabilidades/);
});
