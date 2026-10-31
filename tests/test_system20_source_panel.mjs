import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { runInNewContext } from 'node:vm';

const source = readFileSync(new URL('../src/politics_fantasy/web/app.js', import.meta.url), 'utf8');
const match = source.match(/function scientificSourcesPanel\(\)\{[\s\S]*?\n\}/);
assert.ok(match, 'Scientific source panel must be present');

function render(payload) {
  const ui = {scientificSources: payload};
  const escapeHtml = s => String(s ?? '').replace(/[&<>"']/g,
    c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  return runInNewContext(match[0] + '\nscientificSourcesPanel', {
    ui, esc: escapeHtml, count: n => String(n),
    stat: (title, value, explanation) => `<article>${escapeHtml(title)}:${escapeHtml(value)}:${escapeHtml(explanation)}</article>`,
  })();
}

function sample() {
  const entry = (id, rows, byYear) => ({
    id, bytes: 1024, sha256: 'a'.repeat(64),
    metadata_audit: {
      rows_in_document: rows, rows_by_year: byYear,
      observed_years: 2, first_year:'1977', last_year:'2023',
      coverage_status:'METADATA_ROWS_NOT_CERTIFIED_UNIVERSE',
    },
  });
  return {
    ok: true, distribution_count: 2, metadata_rows_scanned: 11803,
    source_aggregate_metadata_reproduced: true,
    source_data: [
      entry('INTERIOR_CONGRESO_ELECTED', 5600, {'1977':350,'2023':350}),
      entry('INTERIOR_CONGRESO_RESULTS', 6203, {'1977':192,'2023':266}),
    ],
  };
}

test('source panel renders verified documentary aggregates, not individual ratings', () => {
  const html = render(sample());
  assert.match(html, /Filas de metadatos:11803/);
  assert.match(html, /5600 filas administrativas/);
  assert.match(html, /6203 filas administrativas/);
  assert.match(html, /Explorar cobertura documental por año/);
  assert.match(html, /1977/);
  assert.match(html, /2023/);
  assert.match(html, /no equivalen al universo de procesos políticos/i);
  assert.doesNotMatch(html, /calificación de diputado|influencia causal demostrada/i);
});

test('source panel refuses a missing or unreviewed aggregate without generating totals', () => {
  const data = sample();
  data.source_aggregate_metadata_reproduced = false;
  data.metadata_rows_scanned = 0;
  data.source_data.forEach(x => {
    x.metadata_audit = {coverage_status:'AGGREGATE_UNAVAILABLE_OR_UNREVIEWED'};
  });
  const html = render(data);
  assert.match(html, /NO VALIDADO/);
  assert.match(html, /no está disponible o su hash no coincide/i);
  assert.doesNotMatch(html, /11803|5600|6203/);
});

test('untrusted source labels are escaped and cannot inject HTML', () => {
  const data = sample();
  data.source_data[0].id = '<svg onload=alert(1)>';
  const html = render(data);
  assert.doesNotMatch(html, /<svg/);
  assert.match(html, /&lt;svg/);
  assert.doesNotMatch(html, /onload=["']/);
});
