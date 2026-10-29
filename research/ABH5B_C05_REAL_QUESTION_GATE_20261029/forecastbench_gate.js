"use strict";
// Politics Fantasy AB-H C05 / AB-P original public-question provenance and
// probability-semantics audit. No human row, no market or political scorer.
// Authored for ForecastBench-datasets CC BY-SA 4.0; does not redistribute texts.
// Source: https://github.com/forecastingresearch/forecastbench-datasets
// Requires independent source+ID join, strict temporal provenance, unit semantics.
function audit(questionSet, resolutionSet) {
  if (!questionSet || !resolutionSet ||
      typeof questionSet.forecast_due_date !== "string" ||
      questionSet.forecast_due_date !== resolutionSet.forecast_due_date ||
      questionSet.question_set !== resolutionSet.question_set ||
      !Array.isArray(questionSet.questions) || !Array.isArray(resolutionSet.resolutions)) {
    throw new Error("SOURCE_COHORT_INCONSISTENT");
  }
  const market = new Set(["kalshi", "metaculus", "manifold", "polymarket"]);
  const summary = {version: "pfl.fb.c05.original_questions.v1", date: questionSet.forecast_due_date,
    questions: questionSet.questions.length, resolution_records: resolutionSet.resolutions.length,
    accepted: 0, sources: {}, categories: {}, rejected: {},
    outcomes_yes: 0, brier_market_sum: 0, brier_uninformative_sum: 0,
    claims: ["public non-person question/outcome-level audit only",
      "the community freeze-value baseline is NOT PFL's own prediction",
      "resolved-question selection is not an all-questions outcome population",
      "market probability versus source-specific raw numeric quantities must not be conflated",
      "0.5 is a diagnostic uninformative comparator, not a competitive forecasting baseline"]};
  function reject(reason){ summary.rejected[reason] = (summary.rejected[reason] || 0) + 1; }
  const date = questionSet.forecast_due_date;
  const due = Date.parse(date + "T23:59:59Z");
  if (!Number.isFinite(due)) throw new Error("INVALID_DUE_DATE");
  const map = new Map();
  const dupQuestion = new Set();
  const key = (x) => JSON.stringify([x.source,x.id]);
  for (const q of questionSet.questions) {
    if (typeof q.source !== "string" || typeof q.id !== "string") {reject("bad_question_key");continue;}
    const k=key(q);
    if (map.has(k)) dupQuestion.add(k);
    else map.set(k,q);
  }
  const grouped = new Map();
  for (const r of resolutionSet.resolutions) {
    if (typeof r.id !== "string" || typeof r.source !== "string") {reject("bad_resolution_key");continue;}
    const k=key(r);grouped.set(k,[...(grouped.get(k)||[]),r]);
  }
  for (const [k,q] of map) {
    if (dupQuestion.has(k)){reject("duplicate_question_key");continue;}
    if (!market.has(q.source)) {reject("nonprobability_source");continue;}
    const rr=grouped.get(k)||[];
    if (!rr.length) {reject("no_resolution_record");continue;}
    if (rr.length!==1) {reject("ambiguous_multiple_resolution_records");continue;}
    const r=rr[0];
    if (r.resolved!==true || !Number.isInteger(r.resolved_to) || ![0,1].includes(r.resolved_to)) {
      reject("unresolved_or_nonbinary_outcome");continue;
    }
    const p=Number(q.freeze_datetime_value);
    if (typeof q.freeze_datetime_value !== "string" || !q.freeze_datetime_value.trim() ||
       !Number.isFinite(p) || p<0 || p>1) {reject("invalid_probability_value");continue;}
    const frozen=Date.parse(q.freeze_datetime),resolved=Date.parse(r.resolution_date + "T00:00:00Z");
    if (!Number.isFinite(frozen) || !Number.isFinite(resolved) ||
        !Number.isFinite(due) || frozen>=due || resolved<=due) {
      reject("time_order_or_resolution_date_not_after_due");continue;
    }
    summary.accepted++;
    summary.sources[q.source]=(summary.sources[q.source]||0)+1;
    summary.outcomes_yes+=r.resolved_to;
    summary.brier_market_sum+=(p-r.resolved_to)**2;
    summary.brier_uninformative_sum+=.25;
  }
  summary.rejected_total=Object.values(summary.rejected).reduce((a,b)=>a+b,0);
  if (summary.accepted+summary.rejected_total!==summary.questions)
    throw new Error("QUESTION_ACCOUNTING_INCONSISTENT");
  summary.brier_market_mean=summary.accepted ? summary.brier_market_sum/summary.accepted : null;
  summary.brier_uninformative_mean=summary.accepted ? .25 : null;
  summary.brier_market_sum=Number(summary.brier_market_sum.toFixed(8));
  summary.brier_uninformative_sum=Number(summary.brier_uninformative_sum.toFixed(8));
  summary.inference="DESCRIPTIVE_RESOLVED_SUBSET_ONLY";
  return summary;
}
return {audit};
