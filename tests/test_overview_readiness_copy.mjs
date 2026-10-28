import {test} from 'node:test';
import {strict as assert} from 'node:assert';
import {readFileSync} from 'node:fs';

const s=readFileSync(new URL('../src/politics_fantasy/web/app.js', import.meta.url),'utf8');

test('overview must not invent a three-of-five production-readiness indicator',()=>{
  assert.doesNotMatch(s,/Prototipo de producción 5 etapas/);
  assert.doesNotMatch(s,/i<3\?'on':''/);
});

test('overview directs user to documented progress, not implied release readiness',()=>{
  assert.match(s,/Preparación para publicación: NO VERIFICADA/);
  assert.match(s,/data-nav="progress">CONSULTAR PROGRESO Y GATES/);
  assert.match(s,/SIN DESCUBRIMIENTOS EMPÍRICOS CONFIRMADOS/);
});
