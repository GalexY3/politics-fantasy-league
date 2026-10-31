import test from 'node:test';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const E=require('../product/showcase/engine.js');
const W=require('../product/showcase/world.js');

test('scouting previews the current synthetic event without playing the round',()=>{
  const s=E.newGame(),before=structuredClone(s);
  const scouting=E.scouting(s);
  assert.deepEqual(s,before);
  assert.equal(scouting.week,1);
  assert.equal(scouting.eventId,W.EVENTS[0].id);
  assert.equal(scouting.cards.length,s.starters.length);
  assert.equal(scouting.eventBonus,scouting.cards.reduce((a,x)=>a+x.eventBonus,0));
  assert.equal(s.rounds.length,0);
});
test('the forecast exposes a tactic affinity, not final points or future events',()=>{
  const s=E.newGame(),scouting=E.scouting(s);
  assert.equal(scouting.tactics.length,3);
  assert.ok(scouting.tactics.every(x=>x.tacticBaseBonus===x.matched*4));
  assert.ok(!Object.hasOwn(scouting,'finalPoints'));
  assert.ok(!Object.hasOwn(scouting,'futureEvents'));
  assert.equal(scouting.chosenTactic,'datos');
});
test('selection changes the preview without mutating the baseline or consuming a round',()=>{
  const s=E.newGame();
  const s2=E.change(s,'tactic',{id:'alianzas'});
  assert.equal(E.scouting(s2).chosenTactic,'alianzas');
  assert.equal(E.scouting(s).chosenTactic,'datos');
  assert.equal(s2.week,s.week);
  assert.equal(s2.rounds.length,0);
  assert.equal(E.scouting(s2).eventBonus,E.scouting(s).eventBonus);
});
test('scouting contribution reconciles to the event term in the actual round',()=>{
  const s=E.newGame(),preview=E.scouting(s),played=E.change(s,'round');
  const receipt=played.rounds[0];
  assert.equal(receipt.eventId,preview.eventId);
  for(const line of receipt.breakdown){
    const expected=preview.cards.find(x=>x.id===line.id);
    assert.equal(line.event,expected.eventBonus);
  }
});
test('past rounds and completed seasons do not leak the next outcome into scouting',()=>{
  let s=E.newGame();
  for(let week=1;week<=8;week++){
    assert.equal(E.scouting(s).eventId,W.weekEvent(week).id);
    s=E.change(s,'round');
  }
  const over=E.scouting(s);
  assert.equal(over.finished,true);
  assert.equal(over.eventId,null);
  assert.deepEqual(over.cards,[]);
});
