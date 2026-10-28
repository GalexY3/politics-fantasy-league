/** Offline allocation rehearsal only; NOT concealment or secure enrolment. */
export function assignSyntheticArms(n,seed){
  if(!Number.isSafeInteger(n)||n<4||n>10000||n%4!==0)throw Error("INVALID_ALLOCATION_SIZE");
  if(!Number.isSafeInteger(seed)||seed<0||seed>4294967295)throw Error("INVALID_SEED");
  const arms=["control","transparency","leaderboard","both"];
  let state=seed>>>0;
  const next=()=>{state=(Math.imul(1664525,state)+1013904223)>>>0;return state/4294967296};
  const result=[];
  for(let b=0;b<n/4;b++){
    let block=arms.slice();
    for(let i=block.length-1;i>0;i--){let j=Math.floor(next()*(i+1));[block[i],block[j]]=[block[j],block[i]]}
    result.push(...block)
  }
  return Object.freeze(result);
}
