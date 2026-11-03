"""Closed operator-observation protocol for the synthetic PFL science beta.

Local, stdlib-only and read-only. This is NOT a human study, a live beta
diagnostic, empirical admission or a release gate. No identities are collected.

  python -B scripts/beta_science_operator_protocol.py --template
  python -B scripts/beta_science_operator_protocol.py --participant-sheet
  python -B scripts/beta_science_operator_protocol.py --blank-session
  python -B scripts/beta_science_operator_protocol.py --new-session outside_repo.json
  python -B scripts/beta_science_operator_protocol.py --evaluate input.json
  python -B scripts/beta_science_operator_protocol.py --evaluate-to input.json output.json
  python -B scripts/beta_science_operator_protocol.py --participant-handout outside_repo.html
  python -B scripts/beta_science_operator_protocol.py --template-to outside_repo_rubric.json
  python -B scripts/beta_science_operator_protocol.py --self-check
"""
from __future__ import annotations

import argparse
import hashlib
from html import escape
import json
import os
from pathlib import Path

INPUT_SCHEMA = "pfl.beta_science_operator_observations.v1"
TEMPLATE_SCHEMA = "pfl.beta_science_operator_template.v1"
PARTICIPANT_SHEET_SCHEMA = "pfl.beta_science_operator_participant_sheet.v1"
RESULT_SCHEMA = "pfl.beta_science_operator_evaluation.v1"
SELF_SCHEMA = "pfl.beta_science_operator_self_check.v1"
NEW_SESSION_SCHEMA = "pfl.beta_science_operator_session_creation.v1"
MAX_INPUT_BYTES = 16384
MAX_HANDOUT_BYTES = 65536
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


# Secondary bilingual display only: these twelve translations are an
# unvalidated human-facing aid, not a separate scored scientific instrument.
# Each tuple translates the participant action, question, and the two
# canonical meaning strings in their SPECS (correct, alternate) order.
HANDOUT_ES = {
    "OP01": ("Examina el calendario B0 y la publicación selectiva B3 del corte tardío.",
             "¿Basta la evidencia publicada para distinguir ambos mecanismos?",
             "B0 y B3 presentan evidencia publicada indistinguible.",
             "La evidencia publicada demuestra B0."),
    "OP02": ("Localiza E2 pendiente y E4 censurado por la derecha en los mecanismos.",
             "¿E2 pendiente y E4 censurado son rechazos?",
             "Ninguno de los dos estados acredita un resultado negativo definitivo.",
             "Ambos son rechazos conocidos."),
    "OP03": ("Selecciona el conocimiento tardío y examina la identificación parcial S3.",
             "¿Qué identifica el intervalo S3?",
             "El intervalo condicional [-11/52, 47/119] no es causal.",
             "S3 demuestra un efecto causal positivo."),
    "OP04": ("Cambia al conocimiento temprano y examina S3 de nuevo.",
             "¿Pueden retrotraerse las cotas S3 tardías al as_of temprano?",
             "No; el corte temprano carece de esa evidencia S3.",
             "Sí; los resultados tardíos ya eran observables en el corte temprano."),
    "OP05": ("Examina los testigos tardíos S7: CONFLICT, NEITHER e INADMISSIBLE.",
             "¿En qué se diferencian NEITHER, CONFLICT e INADMISSIBLE?",
             "NEITHER refuta ambos modelos; CONFLICT retiene evidencia rival; INADMISSIBLE carece de evidencia utilizable.",
             "Los tres son errores HTTP."),
    "OP06": ("Cambia el filtro de familia S9 de Todas a CHAIN.",
             "¿Demuestra este filtro una vinculación real de identidades?",
             "No; CHAIN es una familia sintética tipada de fuentes.",
             "Sí; las familias coincidentes autentican personas."),
    "OP07": ("Cambia valid_at y el corte de conocimiento S9; examina la comparación.",
             "¿Equivalen la vigencia histórica y el conocimiento as_of?",
             "No; vigencia y conocimiento disponible responden a preguntas distintas.",
             "Sí; ambos relojes deben coincidir siempre."),
    "OP08": ("Examina los descriptores públicos S8 y las revisiones S9.",
             "¿Añade cada revisión documental una persona o decisión única?",
             "No; una versión puede revisar el mismo evento o registro lógico.",
             "Sí; el número de revisiones equivale al de decisiones o personas."),
    "OP09": ("Examina las pestañas S9 Preadmisión, Incorporaciones y Calidad.",
             "¿Autoriza una incorporación ficticia a admitir fuentes empíricas?",
             "No; el registro estipulado no autentica derechos ni admite fuentes reales.",
             "Sí; la incorporación concede derechos sobre fuentes reales."),
    "OP10": ("Obtén los recibos S9 individual y emparejado y verifica sus SHA sin conexión.",
             "¿Qué demuestra la coincidencia de un SHA sintético?",
             "Los bytes sintéticos canónicos concuerdan con el recibo, no con autenticidad o derechos externos.",
             "El SHA autentica al emisor, los derechos y conclusiones causales."),
    "OP11": ("Compara el marcador antiguo con el origen nuevo de --science-only --port 0 verificado por el diagnóstico.",
             "¿Demuestra un marcador antiguo que el servidor sigue activo?",
             "No; es una receta de consulta que exige verificar el puerto actual.",
             "Sí; el origen antiguo sigue activo porque existe un marcador."),
    "OP12": ("Fija published_until del corte tardío a 30 de octubre y cambia al corte temprano.",
             "¿Puede conocerse una publicación del 30 de octubre el 15 de octubre gracias a un valid_at anterior?",
             "No; la visibilidad de publicaciones está limitada por el conocimiento as_of.",
             "Sí; un valid_at anterior anticipa publicaciones futuras."),
}


def _balanced_a_task_ids() -> frozenset[str]:
    """Stable balanced order without a task-number parity answer pattern.

    This ranking is public and reproducible, not a secret or participant
    randomization. It avoids a deterministic ABAB answer-key cue in the
    static handout while retaining six correct A and six correct B choices.
    """
    ids = [spec[0] for spec in SPECS]
    ranking = sorted(
        ids,
        key=lambda ident: hashlib.sha256(
            (PARTICIPANT_SHEET_SCHEMA + "|" + ident).encode("ascii")
        ).digest(),
    )
    return frozenset(ranking[: len(ids) // 2])


CORRECT_A_TASK_IDS = _balanced_a_task_ids()


def _task(spec: tuple) -> dict:
    (tid, machine, area, title, action, technical, question, correct,
     wrong, correct_meaning, wrong_meaning, explanation, usability) = spec
    # Deterministically counterbalance without the trivially predictable
    # odd/even cue. Underlying SCI_* codes and grading remain unchanged.
    options = [
        {"code": "SCI_" + tid + "_" + correct, "meaning": correct_meaning},
        {"code": "SCI_" + tid + "_" + wrong, "meaning": wrong_meaning},
    ]
    if tid not in CORRECT_A_TASK_IDS:
        options.reverse()
    return {
        "task_id": tid, "technical_task_ids": list(machine), "area": area,
        "title": title, "operator_action": action,
        "technical_success_criterion": technical,
        "scientific_question": question,
        "scientific_options": options,
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
    positions = [
        "A" if item["scientific_options"][0]["code"] == item["correct_answer_code"]
        else "B" for item in TASKS
    ]
    if (positions.count("A") != positions.count("B")
            or positions == ["A" if i % 2 == 0 else "B" for i in range(len(TASKS))]
            or positions == ["B" if i % 2 == 0 else "A" for i in range(len(TASKS))]):
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
        "task_count": len(TASKS),
        "tasks": [{
            **item,
            "participant_option_to_scientific_code": {
                label: option["code"]
                for label, option in zip(
                    ("A", "B"), item["scientific_options"], strict=True)
            },
        } for item in TASKS],
        "input_contract": {
            "schema": INPUT_SCHEMA,
            "top_level_fields": ["schema", "observations"],
            "observation_fields": ["task_id", "technical", "scientific", "usability"],
            "technical_codes": list(TECH_CODES),
            "scientific_codes": "task-specific scientific_options or NOT_OBSERVED",
            "usability_codes": list(UX_CODES),
            "omitted_task": "OPERATOR_SESSION_INCOMPLETE",
            "response_type": "CLOSED_CODES_ONLY",
            "participant_option_mapping": (
                "A and B correspond to positions 0 and 1 in the operator "
                "scientific_options array. --evaluate accepts the operator SCI_* "
                "codes, not participant A/B labels."
            ),
        },
        "instructions": (
            "Operator rubric, NOT a participant record. Use closed codes only. "
            "Do not collect identifiers, timestamps, free text, full URLs, IPs, "
            "credentials, cookies or file paths. For unknown observations use "
            "NOT_OBSERVED explicitly for each unobserved dimension in all "
            "12 tasks; never impute a participant. A blank or all-unobserved "
            "session is NOT completed. technical_task_ids are automation "
            "identifiers for alignment, NOT evidence of human work."
        ),
    }


def participant_sheet() -> dict:
    """Neutral operator-distributed task handout, with no scoring rubric.

    Only the four explicitly permitted task fields are projected. In
    particular, never copy the answer key, scientific explanation, technical
    grading criterion, machine IDs or usability rubric from the operator
    template. The handout is a blank instrument, not a participant record.
    """
    return {
        "schema": PARTICIPANT_SHEET_SCHEMA,
        "tasks": [{
            "task_id": item["task_id"],
            "operator_action": item["operator_action"],
            "scientific_question": item["scientific_question"],
            "scientific_options": [
                {"code": label, "meaning": option["meaning"]}
                for label, option in zip(
                    ("A", "B"), item["scientific_options"], strict=True)
            ],
        } for item in TASKS],
    }


def blank_session() -> dict:
    """Emit a local editable JSON skeleton; do not create a file or session."""
    return {
        "schema": INPUT_SCHEMA,
        "observations": [{
            "task_id": item["task_id"],
            "technical": MISSING,
            "scientific": MISSING,
            "usability": MISSING,
        } for item in TASKS],
    }


def _within(path: Path, root: Path) -> bool:
    """Inclusive local path containment with native Windows case handling."""
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _inside_git_worktree(parent: Path) -> bool:
    # Also refuse other checkout roots, not just this instrument's own tree.
    return any(os.path.lexists(ancestor / ".git")
               for ancestor in (parent, *parent.parents))


def _write_external_utf8(path: str, content: str, *, maximum: int,
                         error_prefix: str) -> tuple[int, str]:
    """Write a newly named, standalone UTF-8 file only outside all Git trees.

    Inspect both the lexical destination and the resolved parent so an
    in-checkout name or an external directory link into the checkout cannot
    bypass the guard. Validate before opening; no mkdir, no network, no output
    containing the supplied path or an operating-system exception.
    """
    checkout = Path(__file__).resolve(strict=True).parents[1]
    checkout_lexical = Path(os.path.abspath(__file__)).parents[1]
    if not path or "\x00" in path:
        raise ProtocolError(error_prefix + "_PATH_INVALID")
    try:
        destination = Path(os.path.abspath(path))
        # NTFS treats a name containing a colon as an alternate data stream
        # on an existing inode, not as a new standalone file. An external
        # hardlink may otherwise alias a Git-tracked file across this guard.
        if os.name == "nt" and ":" in destination.name:
            raise ProtocolError(error_prefix + "_PATH_INVALID")
        if (not destination.name or
                _within(destination, checkout) or
                _within(destination, checkout_lexical)):
            raise ProtocolError(error_prefix + "_PATH_FORBIDDEN")
        parent = destination.parent
        if not parent.is_dir():
            raise ProtocolError(error_prefix + "_PARENT_UNAVAILABLE")
        resolved_parent = parent.resolve(strict=True)
        if (_within(resolved_parent, checkout) or
                _within(resolved_parent, checkout_lexical)
                or destination.name == ".git"
                or _inside_git_worktree(parent)
                or _inside_git_worktree(resolved_parent)):
            raise ProtocolError(error_prefix + "_PATH_FORBIDDEN")
        if os.path.lexists(destination):
            raise ProtocolError(error_prefix + "_EXISTS")
    except ProtocolError:
        raise
    except (OSError, ValueError, RuntimeError) as exc:
        raise ProtocolError(error_prefix + "_PATH_INVALID") from exc
    bytes_to_write = content.encode("utf-8")
    if len(bytes_to_write) > maximum:
        raise ProtocolError("OPERATOR_INSTRUMENT_INVALID")
    created = False
    try:
        # 'xb' is mandatory: atomic create-only; never read or overwrite.
        with destination.open("xb") as stream:
            created = True
            stream.write(bytes_to_write)
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError as exc:
        raise ProtocolError(error_prefix + "_EXISTS") from exc
    except OSError as exc:
        if created:
            try:
                destination.unlink()
            except OSError:
                pass
        raise ProtocolError(error_prefix + "_WRITE_FAILED") from exc
    return len(bytes_to_write), hashlib.sha256(bytes_to_write).hexdigest()


def new_session(path: str) -> dict:
    """Create exactly the canonical blank UTF-8 JSON outside Git, write once."""
    _write_external_utf8(
        path, json_line(blank_session()) + "\n",
        maximum=MAX_INPUT_BYTES, error_prefix="OPERATOR_SESSION",
    )
    return {
        "schema": NEW_SESSION_SCHEMA,
        "status": "OPERATOR_SESSION_CREATED",
        "encoding": "UTF-8",
        "tasks_defined": len(TASKS),
        "participant_count": None,
        "participants_observed": False,
        "R5": "STOP_R5",
    }


def participant_handout() -> str:
    """Offline printable rendering of the EXISTING blind participant sheet.

    No form, telemetry, JavaScript, server URLs, or answer key. The scientific
    meanings are unchanged from --participant-sheet, which remains canonical.
    """
    sheet = participant_sheet()
    if set(HANDOUT_ES) != set(BY_ID):
        raise ProtocolError("OPERATOR_INSTRUMENT_INVALID")
    blocks = []
    for task in sheet["tasks"]:
        original = next(spec for spec in SPECS if spec[0] == task["task_id"])
        es_action, es_question, es_correct, es_wrong = HANDOUT_ES[task["task_id"]]
        meanings_es = {original[9]: es_correct, original[10]: es_wrong}
        if (set(meanings_es) != {c["meaning"] for c in task["scientific_options"]}
                or any(not text.strip() for text in HANDOUT_ES[task["task_id"]])):
            raise ProtocolError("OPERATOR_INSTRUMENT_INVALID")
        parts = [
            '<li class="task">',
            '<h2>' + escape(task["task_id"]) + '</h2>',
            '<p><strong>Action:</strong> ' + escape(task["operator_action"]) + '</p>',
            '<p lang="es"><strong>Acción:</strong> ' + escape(es_action) + '</p>',
            '<p><strong>Question:</strong> ' + escape(task["scientific_question"]) + '</p>',
            '<p lang="es"><strong>Pregunta:</strong> ' + escape(es_question) + '</p>',
        ]
        for choice in task["scientific_options"]:
            parts.append('<p class="option">' + choice["code"] + ' — '
                         + escape(choice["meaning"]) + '</p>')
            parts.append('<p class="option" lang="es">' + choice["code"] + ' — '
                         + escape(meanings_es[choice["meaning"]]) + '</p>')
        parts.append('</li>')
        blocks.append("\n".join(parts))
    return (
        '<!doctype html>\n<html lang="en"><head><meta charset="utf-8">\n'
        '<title>PFL — synthetic science beta — participant sheet</title>\n'
        '<style>body{font:16px/1.5 system-ui,sans-serif;max-width:48rem;'
        'margin:2rem auto;padding:0 1rem;color:#171717}'
        'li{margin-bottom:2rem;break-inside:avoid}'
        'h2{font-size:1.15rem}p{margin:.6rem 0}'
        '.option{padding:.4rem .7rem;border-left:2px solid #777}'
        '@media print{body{margin:0;max-width:none}}</style></head>\n'
        '<body><h1>Politics Fantasy League — synthetic science beta</h1>\n'
        '<p lang="es">Hoja bilingüe de apoyo: traducción no validada con '
        'participantes. Puedes detenerte cuando quieras; no anotes nombres, '
        'identificadores ni direcciones privadas.</p>\n'
        '<p>Participant-facing tasks only. No real institutional evidence, '
        'no participant record, no correct-answer key. '
        'Do not write personal identifiers or private URLs on this sheet. '
        'You may stop at any point.</p>\n'
        '<ol>\n' + "\n".join(blocks) + '\n</ol>\n'
        '<p>End of participant handout. Technical outcomes and optional '
        'answers are recorded separately by the supervisor, locally.</p>'
        '\n</body></html>\n'
    )


def write_participant_handout(path: str) -> dict:
    length, sha = _write_external_utf8(
        path, participant_handout(),
        maximum=MAX_HANDOUT_BYTES, error_prefix="OPERATOR_OUTPUT",
    )
    return {
        "schema": PARTICIPANT_SHEET_SCHEMA,
        "status": "OPERATOR_HANDOUT_CREATED",
        "format": "STATIC_OFFLINE_HTML_UTF8",
        "bytes": length,
        "sha256": sha,
        "participant_count": None,
        "participants_observed": False,
        "R5": "STOP_R5",
    }


def write_operator_rubric(path: str) -> dict:
    """Store the existing operator-only answer key separately, in UTF-8."""
    length, sha = _write_external_utf8(
        path, json_line(template()) + "\n",
        maximum=MAX_HANDOUT_BYTES, error_prefix="OPERATOR_OUTPUT",
    )
    return {
        "schema": TEMPLATE_SCHEMA,
        "status": "OPERATOR_RUBRIC_CREATED",
        "encoding": "UTF-8",
        "bytes": length,
        "sha256": sha,
        "participant_count": None,
        "participants_observed": False,
        "R5": "STOP_R5",
    }


def evaluate_to(source: str, destination: str) -> dict:
    """Validate all coded observations before creating a durable UTF-8 result."""
    result = evaluate(read_json(source))
    length, sha = _write_external_utf8(
        destination, json_line(result) + "\n",
        maximum=MAX_INPUT_BYTES, error_prefix="OPERATOR_OUTPUT",
    )
    return {
        "schema": RESULT_SCHEMA,
        "status": "OPERATOR_EVALUATION_EXPORTED",
        "encoding": "UTF-8",
        "bytes": length,
        "sha256": sha,
        "participant_count": None,
        "participant_identity_collected": False,
        "R5": "STOP_R5",
        "gate_eligibility": "OPERATOR_NOT_ASSESSED",
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
    if len(found) != len(TASKS):
        raise ProtocolError("OPERATOR_SESSION_INCOMPLETE")
    return found


def evaluate(value: object) -> dict:
    observations = parse_input(value)
    if not any(
        any(entry[field] != MISSING for field in
            ("technical", "scientific", "usability"))
        for entry in observations.values()
    ):
        raise ProtocolError("OPERATOR_NO_OBSERVATIONS")
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
        # Identifies the exact locally used scoring rubric and its A/B mapping.
        # This is a reproducibility fingerprint, NOT a signature or evidence
        # that any particular participant answered these questions.
        "operator_instrument_sha256": hashlib.sha256(
            (json_line(template()) + "\n").encode("utf-8")
        ).hexdigest(),
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
    exclusive.add_argument("--template-to", metavar="OPERATOR_JSON_FILE")
    exclusive.add_argument("--participant-sheet", action="store_true")
    exclusive.add_argument("--participant-handout", metavar="HTML_FILE")
    exclusive.add_argument("--blank-session", action="store_true")
    exclusive.add_argument("--new-session", metavar="JSON_FILE")
    exclusive.add_argument("--evaluate", metavar="JSON_FILE")
    exclusive.add_argument("--evaluate-to", nargs=2, metavar=("INPUT_JSON", "OUTPUT_JSON"))
    exclusive.add_argument("--self-check", action="store_true")
    try:
        args = parser.parse_args(argv)
        verify_instrument()
        if args.template:
            result = template()
        elif args.template_to is not None:
            result = write_operator_rubric(args.template_to)
        elif args.participant_sheet:
            result = participant_sheet()
        elif args.participant_handout is not None:
            result = write_participant_handout(args.participant_handout)
        elif args.blank_session:
            result = blank_session()
        elif args.new_session is not None:
            result = new_session(args.new_session)
        elif args.evaluate_to is not None:
            result = evaluate_to(*args.evaluate_to)
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
