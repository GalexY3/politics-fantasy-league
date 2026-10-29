/** Restricted structural audit, NOT the canonical atlas_delta.py Python replay. */
export function auditAtlasDeltaChunk(items,prior=null){
 if(!Array.isArray(items)||!items.length)throw Error('EMPTY_BATCH');
 if(prior!==null&&(typeof prior!=='string'||!prior))throw Error('BAD_PARENT_SEED');
 let parent=prior,run_ids=[],errors=[],nops=0;
 for(const item of items){
  const d=item.delta;
  if(!item.name||!d||d.schema!=='ab.atlas.delta.v1'||typeof d.batch_id!=='string'||!Array.isArray(d.ops)){errors.push({name:item.name||'',kind:'BAD_SCHEMA'});continue}
  if(parent!==null&&d.parent_batch!==parent)errors.push({name:item.name,kind:'BAD_PARENT',expected:parent,actual:d.parent_batch});
  if(!/^\d{4}-/.test(item.name)||item.name.slice(0,4)!==d.batch_id.slice(0,4))errors.push({name:item.name,kind:'FILE_BATCH_SEQUENCE_MISMATCH'});
  if(typeof d.at!=='string'||!Number.isFinite(Date.parse(d.at)))errors.push({name:item.name,kind:'BAD_TIME'});
  if(d.ops.length===0)errors.push({name:item.name,kind:'EMPTY_OPS'});
  for(const o of d.ops){nops++;if(!o||typeof o.op!=='string')errors.push({name:item.name,kind:'BAD_OP'});else if(o.op==='run.add'){if(!o.run||typeof o.run.id!=='string'||!o.run.id)errors.push({name:item.name,kind:'BAD_RUN_ID'});else run_ids.push(o.run.id)}}
  parent=d.batch_id;
 }
 const duplicates=run_ids.filter((x,i)=>run_ids.indexOf(x)!==i);
 if(duplicates.length)errors.push({name:'chunk',kind:'DUPLICATE_RUN_ID',count:duplicates.length});
 return Object.freeze({entries:items.length,ops:nops,first:items[0].name,last:items.at(-1).name,next_parent:parent,run_ids,errors,canonical_Python_executed:false});
}
