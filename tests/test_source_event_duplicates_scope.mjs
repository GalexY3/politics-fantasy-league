import test from 'node:test';
import assert from 'node:assert/strict';
import {eventDuplicates} from '../src/politics_fantasy/evidence_warehouse.mjs';
test('Same external vote ID in different independent sources is not silently merged',()=>{
 const reg={events:[{id:'E1',source_id:'S:congreso',external_event_id:'V001'},{id:'E2',source_id:'S:senado',external_event_id:'V001'}]};
 assert.deepEqual(eventDuplicates(reg),[]);
});
test('Same source and external ID still prompts manual duplicate review',()=>{
 const reg={events:[{id:'E1',source_id:'S:congreso',external_event_id:'V001'},{id:'E2',source_id:'S:congreso',external_event_id:'V001'}]};
 assert.deepEqual(eventDuplicates(reg),[{source_id:'S:congreso',external_event_id:'V001',event_ids:['E1','E2'],needs_review:true}]);
});
test('Absent external reference cannot certify duplicates',()=>{
 assert.deepEqual(eventDuplicates({events:[{id:'E1',source_id:'S:congreso',external_event_id:null}]}),[]);
});
