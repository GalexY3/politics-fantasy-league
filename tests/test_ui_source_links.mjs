import {test} from 'node:test';
import {strict as assert} from 'node:assert';
import {readFileSync} from 'node:fs';
import {createContext, runInContext} from 'node:vm';

const source=readFileSync(new URL('../src/politics_fantasy/web/app.js',import.meta.url),'utf8');
const context=createContext({URL, document:{addEventListener(){},getElementById(){return {addEventListener(){}};}}});
runInContext(source.slice(0,source.lastIndexOf('refresh().catch')),context);
function render(url){
  context.testUrl=url;
  return runInContext(`ui.nominations={ok:true,source_url:testUrl,provinces:[]};
    ui.candidacies={ok:true,source_url:testUrl,lists:[]};
    [officialNominationAtlas(), officialListPanel()]`,context);
}
test('unsafe or deceptive source URLs cannot become links in either BOE panel',()=>{
  for(const url of ['javascript:alert(1)','data:text/html,hi','http://www.boe.es/a',
    'https://name@www.boe.es/a','https://www.boe.es.evil.invalid/a','https://www.boe.es:444/a']){
    for(const html of render(url)) assert.doesNotMatch(html,/<a\b/i, url);
  }
});
test('an official HTTPS BOE source stays clickable in both panels',()=>{
  for(const html of render('https://www.boe.es/boe/dias/2023/06/27/pdfs/BOE-A-2023-15066.pdf'))
    assert.match(html,/<a href='https:\/\/www\.boe\.es\//);
});
