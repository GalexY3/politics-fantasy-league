/** Researcher-side only; not shipped with client materials. */
export function evaluateFictionalTransfer(responses){
 const exact=(obj,fields)=>{if(!obj||typeof obj!=="object"||Array.isArray(obj))return false;const proto=Object.getPrototypeOf(obj);if(proto!==Object.prototype&&proto!==null)return false;const keys=Reflect.ownKeys(obj);return keys.length===fields.length&&fields.every(k=>Object.hasOwn(obj,k)&&Object.hasOwn(Object.getOwnPropertyDescriptor(obj,k),"value"));};
 const key={X1:"B",X2:"A",X3:"B",X4:"B"};
 if(!exact(responses,Object.keys(key)))throw Error("INVALID_RESPONSE_SHAPE");
 let score=0;for(const id of Object.keys(key)){if(typeof responses[id]!=="string"||!/^[ABC]$/.test(responses[id]))throw Error("INVALID_OPTION");if(responses[id]===key[id])score++}
 return Object.freeze({schema:"pfl.fictional.transfer.v1",correct:score,out_of:4})
}
