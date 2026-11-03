"""Closed operator-observation protocol for the synthetic PFL science beta.

Local, stdlib-only and read-only. This is NOT a human study, a live beta
diagnostic, empirical admission or a release gate. No identities are collected.

  python -B scripts/beta_science_operator_protocol.py --template
  python -B scripts/beta_science_operator_protocol.py --participant-sheet
  python -B scripts/beta_science_operator_protocol.py --evaluate input.json
  python -B scripts/beta_science_operator_protocol.py --self-check
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

INPUT_SCHEMA = "pfl.beta_science_operator_observations.v1"
TEMPLATE_SCHEMA = "pfl.beta_science_operator_template.v1"
PARTICIPANT_SHEET_SCHEMA = "pfl.beta_science_operator_participant_sheet.v1"
RESULT_SCHEMA = "pfl.beta_science_operator_evaluation.v1"
SELF_SCHEMA = "pfl.beta_science_operator_self_check.v1"
MAX_INPUT_BYTES = 16384
MISSING = "NOT_OBSERVED"
TECH_CODES = ("TECH_COMPLETED", "TECH_BLOCKED", "TECH_FAILED", MISSING)
UX_CODES = ("UX_CLEAR", "UX_FRICTION", "UX_BLOCKED", MISSING)
SCI_CLASSES = ("SCI_CORRECT", "SCI_INCORRECT", MISSING)
AREAS = ("OBSERVATORY", "LABORATORY", "OFFLINE")

# Each item defines task ID, reference machine IDs (NOT evidence of
# participation), area, operator instructions, technical criterion, scientific
# question, correct/wrong closed-code suffixes and their meaning, explanation,
# and UX observation criterion. The answer key is for the operator only.
SPECS = (
    ("OP01", ("LAB_B0_B3",), "LABORATORY", "B0/B3 observational equivalence",
     "Inspect late B0 calendar and B3 selective publication.",
     "Both fictional mechanisms and identical public source/revision evidence display.",
     "Can the published evidence alone distinguish the mechanism?",
     "EQUIVALENT", "B0_PROVEN",
     "B0 and B3 have indistinguishable published evidence.",
     "The published evidence establishes B0.",
     "Matching published SHA and typed revisions cannot identify the unobserved DGP.",
     "Both explanations and their caveats are findable."),
    ("OP02", ("LAB_B0_B3",), "LABORATORY", "Pending and right censoring",
     "Find E2 pending and E4 right-censored in the mechanisms discussion.",
     "The two cases are distinct from documented negative decisions.",
     "Are pending E2 and censored E4 rejections?",
     "NONNEGATIVE_UNKNOWN", "REJECTED",
     "Neither status establishes a terminal negative outcome.",
     "Both are known rejections.",
     "Pending means unresolved; right censoring does not establish a terminal decision.",
     "The nonterminal status of E2/E4 is understandable."),
    ("OP03", ("LAB_S3_TEMPORAL",), "LABORATORY", "S3 exact rational bounds",
     "Select late knowledge and inspect the S3 partial-identification panel.",
     "Bounds -11/52 and 47/119 are visible as exact fractions.",
     "What does the S3 interval identify?",
     "NONCAUSAL_BOUNDS", "CAUSAL_EFFECT",
     "The assumption-conditional change interval [-11/52,47/119] is noncausal.",
     "S3 proves a positive causal effect.",
     "Rational partial identification is not a point or causal estimate.",
     "Both fractions and assumptions can be located."),
    ("OP04", ("LAB_S3_TEMPORAL",), "LABORATORY", "No early S3 lookahead",
     "Switch to early knowledge and revisit S3.",
     "No late-only S3 interval is shown for the early cut.",
     "Can a late S3 bound be backdated to early as_of?",
     "NO_LOOKAHEAD", "BACKDATE",
     "No; the early knowledge cut lacks that S3 evidence.",
     "Yes; late findings were already observable early.",
     "Knowledge as_of is distinct from an event's historical validity.",
     "The absent early result is explained rather than silently filled."),
    ("OP05", ("LAB_S7_20",), "LABORATORY", "S7 twenty sets and six states",
     "Inspect late S7 CONFLICT, NEITHER and INADMISSIBLE witness details.",
     "Twenty sets and all six states are available with reasons.",
     "How do NEITHER, CONFLICT and INADMISSIBLE differ?",
     "DISTINCT_STATES", "HTTP_FAILURES",
     "NEITHER refutes both models; CONFLICT retains competing evidence; INADMISSIBLE lacks usable evidence.",
     "All three are HTTP failures.",
     "S7 states are epistemic witness classifications, not network status codes.",
     "Status, justification and individual witness details can be found."),
    ("OP06", ("S9_FAMILY_SCOPE",), "OBSERVATORY", "S9 family filter",
     "Change S9 family from all to CHAIN.",
     "The selected family filters the public registry and its new SHA receipt.",
     "Does family filtering establish a real identity crosswalk?",
     "FILTER_ONLY", "CROSSWALK_PROVEN",
     "No; CHAIN is a typed synthetic source family.",
     "Yes; matching source families authenticates persons.",
     "Neither source-local families nor matching labels authenticate identity or denominator.",
     "The operator can locate the filter and explain its scope."),
    ("OP07", ("S9_TEMPORAL_COMPARE",), "OBSERVATORY", "Bitemporal clocks",
     "Change S9 valid_at and knowledge cut; inspect the temporal comparison.",
     "valid_at is retained; as_of remains the chosen knowledge cut with verified receipt.",
     "Is historical validity identical to knowledge as_of?",
     "TWO_CLOCKS", "ONE_CLOCK",
     "No; validity and available knowledge answer different questions.",
     "Yes; both clocks must always be equal.",
     "Bitemporal projection separates past validity from evidence known at the cut.",
     "Both temporal selectors and their effects are understandable."),
    ("OP08", ("LAB_S8_DESCRIPTORS",), "OBSERVATORY", "Public source revisions",
     "Inspect S8 public descriptors and S9 revision details.",
     "Public SHA and version metadata are visible without private source bytes.",
     "Does each documentary revision add a unique person or decision?",
     "REVISION_NOT_EVENT", "EACH_REVISION_NEW",
     "No; a version can revise the same logical event or record.",
     "Yes; revision count equals decision/person count.",
     "Documentary revisions must not inflate actors, events or decisions.",
     "Source versions and logical entity counts are distinguishable."),
    ("OP09", ("S9_EIGHT_TABS",), "OBSERVATORY", "Admission and synthetic intake",
     "Inspect the admission, intake and quality S9 tabs.",
     "Synthetic intake, denial and amendment details remain R5 STOP.",
     "Does fixture intake authorize empirical source admission?",
     "R5_NOT_ADMISSION", "REAL_RIGHTS",
     "No; author-closed intake neither authenticates rights nor admits real sources.",
     "Yes; intake alone grants real-source rights.",
     "Synthetic records and documentary revisions cannot replace independent rights or source checks.",
     "Registered/rejected/validated statuses are distinguishable."),
    ("OP10", ("S9_SINGLE_EXPORT_OFFLINE", "S9_PAIR_EXPORT_OFFLINE"),
     "OFFLINE", "S9 offline receipts",
     "Obtain S9 single/pair public export receipts and verify SHA offline.",
     "The closed synthetic receipts can be checked without private bytes.",
     "What does a matching fixture SHA establish?",
     "LOCAL_INTEGRITY", "RIGHTS_CERTIFIED",
     "Canonical synthetic bytes match the receipt, not external authenticity or rights.",
     "The SHA authenticates the publisher, reuse rights and causal findings.",
     "Cryptographic consistency does not establish publisher identity, denominator or causality.",
     "The operator can find export/verification affordances and limits."),
    ("OP11", ("RESTART_DOCTOR_GUEST_LINK",), "OFFLINE",
     "Reboot and verified guest link",
     "Inspect old bookmarked port and fresh --science-only --port 0 origin with doctor opt-in.",
     "PASS after current-origin GET, early/late SHA and R5 gives a seven-key current-port link.",
     "Does an old bookmark prove the old server is still live?",
     "CURRENT_PORT_ONLY", "OLD_PORT_LIVE",
     "No; old link is a query recipe; availability requires verifying the current port.",
     "Yes; old origin remains valid merely because a bookmark exists.",
     "A verified current origin is necessary; never infer live availability from stale URL.",
     "The current link can be located and distinguished from stale origin."),
    ("OP12", ("S9_TEMPORAL_COMPARE",), "OBSERVATORY",
     "Publication ceiling versus knowledge",
     "Set late published_until to 30 October, then change to early cut.",
     "Early cut never exposes information first published after its as_of.",
     "Can 30 October publication be known by 15 October due to earlier valid_at?",
     "NO_FUTURE_PUBLICATION", "FUTURE_VISIBLE",
     "No; publication visibility is capped by knowledge as_of.",
     "Yes; an earlier valid_at makes future publication known early.",
     "The publication clock is not interchangeable with event validity.",
     "The reason for capping or resetting the publication selection is clear."),
)


def _task(spec: tuple) -> dict:
    (tid, machine, area, title, action, technical, question, correct,
     wrong, correct_meaning, wrong_meaning, explanation, usability) = spec
    return {
        "task_id": tid, "technical_task_ids": list(machine), "area": area,
        "title": title, "operator_action": action,
        "technical_success_criterion": technical,
        "scientific_question": question,
        "scientific_options": [
            {"code": "SCI_" + tid + "_" + correct, "meaning": correct_meaning},
            {"code": "SCI_" + tid + "_" + wrong, "meaning": wrong_meaning},
        ],
        "correct_answer_code": "SCI_" + tid + "_" + correct,
        "scientific_explanation": explanation,
        "usability_observation_criterion": usability,
    }


TASKS = tuple(_task(spec) for spec in SPECS)
BY_ID = {task["task_id"]: task for task in TASKS}
INPUT_KEYS = frozenset(("task_id", "technical", "scientific", "usability"))


class ProtocolError(Exception):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def _pairs_unique(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ProtocolError("OPERATOR_JSON_INVALID")
        result[key] = value
    return result


def _no_constant(value: str) -> None:
    del value
    raise ProtocolError("OPERATOR_JSON_INVALID")


def json_line(value: object) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=True,
                      allow_nan=False, separators=(",", ":"))


def verify_instrument() -> None:
    expected_machine = {
        "S9_TEMPORAL_COMPARE", "S9_PAIR_EXPORT_OFFLINE",
        "S9_SINGLE_EXPORT_OFFLINE", "S9_FAMILY_SCOPE",
        "RESTART_DOCTOR_GUEST_LINK", "LAB_B0_B3", "LAB_S7_20",
        "LAB_S8_DESCRIPTORS", "LAB_S3_TEMPORAL", "S9_EIGHT_TABS",
    }
    mapped = {m for t in TASKS for m in t["technical_task_ids"]}
    if (not 8 <= len(TASKS) <= 12 or len(BY_ID) != len(TASKS)
            or {t["area"] for t in TASKS} != set(AREAS)
            or mapped != expected_machine):
        raise ProtocolError("OPERATOR_INSTRUMENT_INVALID")
    for t in TASKS:
        codes = [option["code"] for option in t["scientific_options"]]
        if (not t["task_id"].startswith("OP") or len(codes) != 2
                or len(set(codes)) != 2
                or any(not x.startswith("SCI_" + t["task_id"] + "_") for x in codes)
                or t["correct_answer_code"] not in codes
                or any(not isinstance(t[key], str) or not t[key].strip()
                       for key in ("title", "operator_action",
                                   "technical_success_criterion",
                                   "scientific_question", "scientific_explanation",
                                   "usability_observation_criterion"))):
            raise ProtocolError("OPERATOR_INSTRUMENT_INVALID")


def template() -> dict:
    return {
        "schema": TEMPLATE_SCHEMA,
        "status": "OPERATOR_TEMPLATE_ONLY", "R5": "STOP_R5",
        "scope": "LOCAL_SYNTHETIC_BETA_NO_GATE",
        "task_count": len(TASKS), "tasks": list(TASKS),
        "input_contract": {
            "schema": INPUT_SCHEMA,
            "top_level_fields": ["schema", "observations"],
            "observation_fields": ["task_id", "technical", "scientific", "usability"],
            "technical_codes": list(TECH_CODES),
            "scientific_codes": "task-specific scientific_options or NOT_OBSERVED",
            "usability_codes": list(UX_CODES),
            "omitted_task": MISSING,
            "response_type": "CLOSED_CODES_ONLY",
        },
        "instructions": (
            "Operator rubric, NOT a participant record. Use closed codes only. "
            "Do not collect identifiers, timestamps, free text, full URLs, IPs, "
            "credentials, cookies or file paths. For unknown observations use "
            "NOT_OBSERVED; never impute a participant. technical_task_ids are "
            "automation identifiers for alignment, NOT evidence of human work."
        ),
    }


def participant_sheet() -> dict:
    """Neutral operator-distributed task handout, with no scoring rubric.

    Only the four explicitly permitted task fields are projected. In
    particular, never copy the answer key, scientific explanation, technical
    grading criterion, machine IDs or usability rubric from the operator
    template. The handout is a blank instrument, not a participant record.
    """
    fields = ("task_id", "operator_action",
              "scientific_question", "scientific_options")
    return {
        "schema": PARTICIPANT_SHEET_SCHEMA,
        "tasks": [{key: item[key] for key in fields} for item in TASKS],
    }


def parse_input(value: object) -> dict[str, dict]:
    if type(value) is not dict or set(value) != {"schema", "observations"}:
        raise ProtocolError("OPERATOR_SCHEMA_INVALID")
    if value["schema"] != INPUT_SCHEMA or type(value["observations"]) is not list:
        raise ProtocolError("OPERATOR_SCHEMA_INVALID")
    if len(value["observations"]) > len(TASKS):
        raise ProtocolError("OPERATOR_INPUT_INVALID")
    found = {}
    for item in value["observations"]:
        if type(item) is not dict or set(item) != INPUT_KEYS:
            raise ProtocolError("OPERATOR_INPUT_INVALID")
        ident = item["task_id"]
        if type(ident) is not str or ident not in BY_ID or ident in found:
            raise ProtocolError("OPERATOR_INPUT_INVALID")
        if (type(item["technical"]) is not str
                or item["technical"] not in TECH_CODES
                or type(item["usability"]) is not str
                or item["usability"] not in UX_CODES):
            raise ProtocolError("OPERATOR_INPUT_INVALID")
        codes = {x["code"] for x in BY_ID[ident]["scientific_options"]}
        if (type(item["scientific"]) is not str
                or item["scientific"] not in codes | {MISSING}):
            raise ProtocolError("OPERATOR_INPUT_INVALID")
        # Scientific comprehension is not evaluated on an uncompleted
        # technical task. Even an otherwise valid answer must be rejected,
        # rather than counting a failure or imputing a correct response.
        if (item["technical"] != "TECH_COMPLETED"
                and item["scientific"] != MISSING):
            raise ProtocolError("OPERATOR_INPUT_INVALID")
        found[ident] = item
    return found


def evaluate(value: object) -> dict:
    observations = parse_input(value)
    counts = {
        "technical": {code: 0 for code in TECH_CODES},
        "scientific": {code: 0 for code in SCI_CLASSES},
        "usability": {code: 0 for code in UX_CODES},
    }
    rows = []
    any_recorded = 0
    for spec in TASKS:
        ident = spec["task_id"]
        entry = observations.get(ident)
        tech = entry["technical"] if entry else MISSING
        answer = entry["scientific"] if entry else MISSING
        ux = entry["usability"] if entry else MISSING
        sci = (MISSING if answer == MISSING else
               ("SCI_CORRECT" if answer == spec["correct_answer_code"]
                else "SCI_INCORRECT"))
        if any(code != MISSING for code in (tech, answer, ux)):
            any_recorded += 1
        counts["technical"][tech] += 1
        counts["scientific"][sci] += 1
        counts["usability"][ux] += 1
        rows.append({"task_id": ident, "technical": tech,
                     "scientific": sci, "usability": ux})
    return {
        "schema": RESULT_SCHEMA, "status": "OPERATOR_EVALUATION_COMPLETE",
        "evidence_class": "OPERATOR_CODED_OBSERVATION_ONLY",
        "R5": "STOP_R5", "gate_eligibility": "OPERATOR_NOT_ASSESSED",
        "participant_count": None, "participant_identity_collected": False,
        "tasks_defined": len(TASKS),
        "tasks_with_any_coded_observation": any_recorded,
        "rollup": counts, "tasks": rows,
    }


def read_json(path: str) -> object:
    try:
        with Path(path).open("rb") as stream:
            raw = stream.read(MAX_INPUT_BYTES + 1)
    except OSError as exc:
        raise ProtocolError("OPERATOR_FILE_UNAVAILABLE") from exc
    if len(raw) > MAX_INPUT_BYTES:
        raise ProtocolError("OPERATOR_FILE_TOO_LARGE")
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs_unique,
                          parse_constant=_no_constant)
    except ProtocolError:
        raise
    except (ValueError, UnicodeError, TypeError, RecursionError) as exc:
        raise ProtocolError("OPERATOR_JSON_INVALID") from exc


class SafeParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        del message
        raise ProtocolError("OPERATOR_ARGUMENTS_INVALID")


def main(argv: list[str] | None = None) -> int:
    parser = SafeParser(description="Local closed PFL science operator protocol")
    exclusive = parser.add_mutually_exclusive_group(required=True)
    exclusive.add_argument("--template", action="store_true")
    exclusive.add_argument("--participant-sheet", action="store_true")
    exclusive.add_argument("--evaluate", metavar="JSON_FILE")
    exclusive.add_argument("--self-check", action="store_true")
    try:
        args = parser.parse_args(argv)
        verify_instrument()
        if args.template:
            result = template()
        elif args.participant_sheet:
            result = participant_sheet()
        elif args.self_check:
            result = {
                "schema": SELF_SCHEMA, "status": "OPERATOR_INSTRUMENT_VALID",
                "R5": "STOP_R5", "tasks_defined": len(TASKS),
                "participant_count": None, "participants_observed": False,
                "evaluation_executed": False, "live_beta_checked": False,
                "release_gate_changed": False,
            }
        else:
            result = evaluate(read_json(args.evaluate))
        rc = 0
    except ProtocolError as exc:
        result = {
            "schema": RESULT_SCHEMA, "status": "OPERATOR_REJECTED",
            "error_code": exc.code, "participant_count": None,
        }
        rc = 1
    except (KeyError, TypeError, ValueError, RecursionError, OverflowError):
        result = {
            "schema": RESULT_SCHEMA, "status": "OPERATOR_REJECTED",
            "error_code": "OPERATOR_INPUT_INVALID", "participant_count": None,
        }
        rc = 1
    print(json_line(result))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
