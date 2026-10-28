/** Offline dry run only. The approval object is a mock, not verification of institutional ethics. No human study deployment. */
export function validatePilotIntake(payload,approval){
 const allowed=["arm","responses","completed","consent","age_confirmed","study_fixture"];
 const arms=["control","transparency","leaderboard","both"];
 if(!approval||approval.status!=="APPROVED_BY_HUMAN_REVIEW"||typeof approval.review_ref!=="string"||approval.review_ref.length<8)throw Error("REVIEW_GATE_CLOSED");
 if(!payload||typeof payload!=="object"||Array.isArray(payload)||Object.keys(payload).some(k=>!allowed.includes(k))||Object.keys(payload).length!==allowed.length)throw Error("NO_PERSONAL_METADATA");
 if(payload.study_fixture!=="SYNTHETIC_DRY_RUN_ONLY")throw Error("NO_HUMAN_DATA_COLLECTION");
 if(payload.consent!==true||payload.age_confirmed!==true)throw Error("CONSENT_AND_ADULT_REQUIRED");
 if(!arms.includes(payload.arm))throw Error("INVALID_ARM");
 if(typeof payload.completed!=="boolean")throw Error("COMPLETION_INVALID");
 if(!payload.responses||typeof payload.responses!=="object"||Array.isArray(payload.responses)||Object.keys(payload.responses).length!==4||Object.keys(payload.responses).some(k=>!["X1","X2","X3","X4"].includes(k)))throw Error("INVALID_RESPONSES");
 for(let id of ["X1","X2","X3","X4"]){if(!["A","B","C",null].includes(payload.responses[id]))throw Error("INVALID_OPTION")}
 if(payload.completed&&Object.values(payload.responses).some(v=>v===null))throw Error("FALSE_COMPLETION");
 const safe=Object.freeze({arm:payload.arm,completed:payload.completed,responses:Object.freeze({...payload.responses}),fixture:"SYNTHETIC_ONLY"});
 const consentReceipt=Object.freeze({schema:"pfl.dryrun.consent.v1",verified_bool:true,review_ref:approval.review_ref,fixture:"SYNTHETIC_ONLY"});
 return Object.freeze({schema:"pfl.dryrun.intake.v1",safe,consentReceipt});
}
