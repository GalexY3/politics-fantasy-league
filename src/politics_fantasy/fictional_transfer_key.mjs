/** Researcher-side only; not shipped with client materials. */
export function evaluateFictionalTransfer(responses){
 const key={X1:"B",X2:"A",X3:"B",X4:"B"};
 if(!responses||typeof responses!=="object"||Array.isArray(responses)||Object.keys(responses).length!==4||Object.keys(responses).some(x=>!Object.hasOwn(key,x)))throw Error("INVALID_RESPONSE_SHAPE");
 let score=0;for(const id of Object.keys(key)){if(typeof responses[id]!=="string"||!/^[ABC]$/.test(responses[id]))throw Error("INVALID_OPTION");if(responses[id]===key[id])score++}
 return Object.freeze({schema:"pfl.fictional.transfer.v1",correct:score,out_of:4})
}
