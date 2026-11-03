"""Windows artifact-access and durable revision-lineage falsifiers.

Synthetic operator fixtures only. This test owns no production changes; all
paths created in pytest tmp_path outside any Git checkout.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from test_beta_operator_instrument_versioning import _prepared_v2, run_cli


ROOT = Path(__file__).resolve().parents[1]
MISSING = "NOT_OBSERVED"


def _json_bytes(path: Path) -> dict:
    return json.loads(path.read_bytes().decode("utf-8"))


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _record(source: Path, output: Path, task: str = "OP09",
            tech: str = "TECH_BLOCKED", sci: str = MISSING,
            ux: str = "UX_BLOCKED") -> tuple[int, dict, str]:
    return run_cli("--record-form", source, output, task, tech, sci, ux)


def _assert_external(path: Path) -> None:
    assert not path.resolve(strict=False).is_relative_to(ROOT.resolve())


def test_prepatch_red_recorded_successor_persists_exact_predecessor_sha(tmp_path):
    """A SHA in stdout only is not a self-contained durable revision edge."""
    _, _, _, source, _, _ = _prepared_v2(tmp_path, "lineage-prepatch")
    successor = source.parent / "version\u00f3n sint\u00e9tica sucesora.json"
    original = source.read_bytes()
    code, receipt, raw = _record(source, successor)
    assert code == 0
    assert receipt["status"] == "OPERATOR_FORM_OBSERVATION_RECORDED"
    assert receipt["source_sha256"] == hashlib.sha256(original).hexdigest()
    assert receipt["destination_sha256"] == _hash(successor)
    assert str(source) not in raw
    assert source.read_bytes() == original
    # The output file (not stdout) should carry a cryptographically verifiable
    # link to its exact predecessor bytes even after stdout receipts are lost.
    body = _json_bytes(successor)
    assert body["predecessor_sha256"] == hashlib.sha256(original).hexdigest()


@pytest.mark.skipif(os.name != "nt", reason="Windows NTFS ACL inheritance")
def test_prepatch_red_publicly_readable_supervisor_key_is_not_rejected(tmp_path):
    """Explicit Everyone/read temp ACL: directory separation != OS privacy."""
    private = tmp_path / "privado supervisor \u03a9"
    public = tmp_path / "p\u00fablico participante \u03a9"
    private.mkdir()
    public.mkdir()
    _assert_external(private)
    _assert_external(public)
    grant = subprocess.run(
        ["icacls", str(private), "/grant", "*S-1-1-0:(OI)(CI)(R)"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    assert grant.returncode == 0, "Could not construct disposable Everyone-read ACL"
    # The condition must be observed, not assumed or fabricated.
    acl = _get_acl(private)
    assert acl["everyone_read"] is True, acl
    session = private / "ficha privada sint\u00e9tica.json"
    key = private / "r\u00fabrica privada sint\u00e9tica.json"
    handout = public / "hoja p\u00fablica sint\u00e9tica.html"
    code, receipt, raw = run_cli("--prepare-form", session, handout, key)
    assert str(key) not in raw and str(session) not in raw
    if code == 0:
        # PREPATCH factual confirmation: the allegedly private key was
        # actually inherited as readable by Everyone on this disposable NTFS
        # directory, not merely in theory.
        assert key.is_file()
        assert _get_acl(key)["everyone_read"] is True
        assert _json_bytes(key)["schema"] == (
            "pfl.beta_science_operator_template.v2")
    # A key file should not be materialized under a directory with Everyone
    # read access. This documents a pre-existing unguarded ACL boundary.
    assert code != 0
    assert receipt["status"] == "OPERATOR_REJECTED"
    assert not key.exists() and not handout.exists() and not session.exists()


def _get_acl(path: Path) -> dict:
    """Observe actual Windows DACL, not an assumed security descriptor."""
    literal = str(path).replace("'", "''")
    script = (
        "$a=Get-Acl -LiteralPath '" + literal + "'; "
        "$e=@($a.Access | Where-Object {$_.AccessControlType -eq 'Allow' "
        "-and ($_.IdentityReference.Value -eq 'Everyone' -or "
        "$_.IdentityReference.Value -eq 'Todos' -or "
        "$_.IdentityReference.Value -eq 'S-1-1-0') "
        "-and ($_.FileSystemRights.ToString() -match 'Read')}); "
        "[pscustomobject]@{ inherited = -not $a.AreAccessRulesProtected; "
        "everyone_read = $e.Count -gt 0; "
        "access_entries = @($a.Access).Count } | ConvertTo-Json -Compress"
    )
    p = subprocess.run(
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
        capture_output=True, check=False, timeout=15,
    )
    assert p.returncode == 0, p.stderr.decode(errors="replace")
    return json.loads(p.stdout.decode("utf-8-sig", errors="replace"))




def test_prepatch_red_record_form_must_not_publish_private_revision_to_public_dir(
    tmp_path,
):
    """Real v2 entry path: source private, successor placed in public handout dir."""
    session, _, _, source, handout, _ = _prepared_v2(
        tmp_path, "record_public_escape")
    assert source.parent != handout.parent
    target = handout.parent / "PUBLIC_REVIEWABLE_CODED_OMEGA.json"
    assert not target.exists()
    original = source.read_bytes()
    rc, report, raw = _record(source, target)
    assert str(target) not in raw and str(source) not in raw
    # Failure must precede any private response export into public handout dir.
    assert rc != 0
    assert report["status"] == "OPERATOR_REJECTED"
    assert report["error_code"] == "OPERATOR_PRIVATE_OUTPUT_PARENT_MISMATCH"
    assert not target.exists()
    assert source.read_bytes() == original


def test_prepatch_red_evaluate_form_must_not_export_private_scores_to_public_dir(
    tmp_path,
):
    """A valid synthetic coded response is not a public scoring report."""
    session, rubric, _, source, handout, rubric_path = _prepared_v2(
        tmp_path, "evaluate_public_escape")
    correct = next(item["correct_answer_code"] for item in rubric["tasks"]
                   if item["task_id"] == "OP01")
    recorded = source.parent / "coded_private_version.json"
    rc, receipt, stdout = _record(
        source, recorded, "OP01", "TECH_COMPLETED", correct, "UX_CLEAR")
    assert rc == 0 and recorded.exists(), receipt
    assert str(recorded) not in stdout
    target = handout.parent / "PUBLIC_PRIVATE_SCORE_LEAK.json"
    assert not target.exists()
    before = recorded.read_bytes()
    rc, report, raw = run_cli("--evaluate-form", recorded, rubric_path, target)
    assert str(recorded) not in raw and str(target) not in raw
    assert rc != 0
    assert report["status"] == "OPERATOR_REJECTED"
    assert report["error_code"] == "OPERATOR_PRIVATE_OUTPUT_PARENT_MISMATCH"
    assert not target.exists()
    assert recorded.read_bytes() == before




def _secure_v2(tmp_path: Path, stem: str):
    """Prepare one *operator-only* v2 fixture in an OS-audited private folder."""
    base = tmp_path / ("caso " + stem)
    base.mkdir()
    private = base / "privado supervisor \u03a9"
    public = base / "p\u00fablico participantes \u03a9"
    public.mkdir()
    code, created, raw_created = run_cli("--new-private-dir", private)
    assert code == 0, created
    assert created["status"].startswith("OPERATOR_PRIVATE")
    assert private.is_dir()
    assert str(private) not in raw_created and private.name not in raw_created
    if os.name == "nt":
        audit = _get_acl(private)
        assert audit["inherited"] is False, audit
        assert audit["everyone_read"] is False, audit
    code, audited, raw_audit = run_cli("--audit-private-dir", private)
    assert code == 0, audited
    assert audited["status"].startswith("OPERATOR_PRIVATE")
    assert str(private) not in raw_audit

    source = private / ("source " + stem + ".json")
    rubric = private / ("rubric " + stem + ".json")
    handout = public / ("handout " + stem + ".html")
    code, created_form, stdout = run_cli("--prepare-form", source, handout, rubric)
    assert code == 0, created_form
    assert created_form["status"] == "OPERATOR_FORM_PREPARED"
    for file in (source, handout, rubric):
        assert file.is_file()
        assert str(file) not in stdout and file.name not in stdout
    assert source.parent == rubric.parent
    assert handout.parent != rubric.parent
    for file in (source, rubric, handout):
        _assert_external(file)
        assert file.read_bytes()
    if os.name == "nt":
        acl = _get_acl(rubric)
        assert acl["everyone_read"] is False, acl
    return base, private, public, source, rubric, handout


def test_new_private_dir_creates_auditable_restricted_supervisor_parent(tmp_path):
    base, private, public, source, rubric, handout = _secure_v2(
        tmp_path, "normal private")
    assert private.exists() and source.exists() and rubric.exists()
    assert not (public / rubric.name).exists()
    assert "correct_answer_code" not in handout.read_text(encoding="utf-8")
    assert "participant_option_to_scientific_code" not in (
        handout.read_text(encoding="utf-8"))
    assert _json_bytes(rubric)["schema"] == (
        "pfl.beta_science_operator_template.v2")
    assert _json_bytes(source)["schema"] == (
        "pfl.beta_science_operator_observations.v2")
    assert base.is_dir()


@pytest.mark.parametrize("case", (
    "already_existing", "missing_parent", "checkout_path", "existing_file",
))
def test_new_private_dir_denies_unsafe_destinations_without_side_effects(
    tmp_path, case,
):
    parent = tmp_path / ("mkdir_" + case)
    parent.mkdir()
    if case == "already_existing":
        dest = parent
    elif case == "missing_parent":
        dest = parent / "not_existing" / "private"
    elif case == "checkout_path":
        dest = ROOT / "__operator_private_dir_forbidden__.json"
        assert not dest.exists()
    elif case == "existing_file":
        dest = parent / "already_here.json"
        dest.write_bytes(b"DO_NOT_OVERWRITE")
    original = set(parent.iterdir())
    rc, rejected, raw = run_cli("--new-private-dir", dest)
    assert rc != 0
    assert rejected["status"] == "OPERATOR_REJECTED"
    assert rejected["error_code"].startswith("OPERATOR_")
    assert str(dest) not in raw
    assert set(parent.iterdir()) == original
    assert not (ROOT / "__operator_private_dir_forbidden__.json").exists()
    if case == "existing_file":
        assert dest.read_bytes() == b"DO_NOT_OVERWRITE"


@pytest.mark.parametrize("case", (
    "world_read", "regular_inherited",
))
def test_audit_private_dir_rejects_unisolated_windows_acl_without_writing(
    tmp_path, case,
):
    if os.name != "nt":
        pytest.skip("Windows ACL audit requires NTFS")
    private = tmp_path / ("insecure_" + case)
    private.mkdir()
    if case == "world_read":
        granted = subprocess.run(
            ["icacls", str(private), "/grant", "*S-1-1-0:(OI)(CI)(R)"],
            capture_output=True, check=False)
        assert granted.returncode == 0
        assert _get_acl(private)["everyone_read"] is True
    else:
        assert _get_acl(private)["inherited"] is True
    before = set(tmp_path.iterdir())
    rc, denied, raw = run_cli("--audit-private-dir", private)
    assert rc != 0
    assert denied["status"] == "OPERATOR_REJECTED"
    assert denied["error_code"].startswith("OPERATOR_")
    assert str(private) not in raw
    assert set(tmp_path.iterdir()) == before


def test_secure_record_and_scoring_remain_in_private_parent(tmp_path):
    _, private, public, source, rubric, _ = _secure_v2(
        tmp_path, "private revision")
    descendant = private / "revision privada 01.json"
    code, result, raw = _record(source, descendant)
    assert code == 0, result
    assert result["source_sha256"] == _hash(source)
    assert result["destination_sha256"] == _hash(descendant)
    assert str(source) not in raw
    scored = private / "private scored 01.json"
    rc, receipt, stdout = run_cli("--evaluate-form", descendant, rubric, scored)
    assert rc == 0, receipt
    assert scored.is_file()
    assert _json_bytes(scored)["coded_input_sha256"] == _hash(descendant)
    assert not list(public.glob("*.json"))
    assert str(scored) not in stdout


@pytest.mark.parametrize("stage", ("record", "evaluate"))
def test_private_artifact_public_folder_escape_denied_with_no_new_file(
    tmp_path, stage,
):
    _, private, public, source, rubric, _ = _secure_v2(
        tmp_path, "public leak " + stage)
    if stage == "record":
        target = public / "PRIVATE_CODED_LEAK.json"
        rc, rejected, raw = _record(source, target)
    else:
        coded = private / "coded allowed.json"
        assert _record(source, coded)[0] == 0
        target = public / "PRIVATE_GRADED_LEAK.json"
        rc, rejected, raw = run_cli("--evaluate-form", coded, rubric, target)
    assert rc != 0
    assert rejected["status"] == "OPERATOR_REJECTED"
    assert rejected["error_code"] == "OPERATOR_PRIVATE_OUTPUT_PARENT_MISMATCH"
    assert not target.exists()
    assert str(target) not in raw and target.name not in raw


def _two_private_revisions(tmp_path: Path, stem: str):
    base, private, public, root, rubric, handout = _secure_v2(tmp_path, stem)
    r1 = private / ("r1 " + stem + ".json")
    r2 = private / ("r2 " + stem + ".json")
    assert _record(root, r1, "OP09", "TECH_BLOCKED", MISSING, "UX_BLOCKED")[0] == 0
    form = _json_bytes(rubric)
    correct = next(t["correct_answer_code"] for t in form["tasks"]
                   if t["task_id"] == "OP01")
    assert _record(r1, r2, "OP01", "TECH_COMPLETED",
                   correct, "UX_FRICTION")[0] == 0
    graded = private / ("scored final " + stem + ".json")
    rc, receipt, raw = run_cli("--evaluate-form", r2, rubric, graded)
    assert rc == 0, receipt
    assert graded.is_file()
    assert _json_bytes(graded)["coded_input_sha256"] == _hash(r2)
    for file in (root, r1, r2, graded, rubric):
        assert str(file) not in raw
    return base, private, public, root, rubric, r1, r2, graded


def test_successor_lineage_is_self_contained_exact_hash_and_two_steps(tmp_path):
    _, _, _, root, _, r1, r2, _ = _two_private_revisions(tmp_path, "lineage")
    assert "predecessor_sha256" not in _json_bytes(root)
    a = _json_bytes(r1)
    b = _json_bytes(r2)
    assert a["predecessor_sha256"] == _hash(root)
    assert b["predecessor_sha256"] == _hash(r1)
    assert _hash(r1) != _hash(root)
    assert _hash(r2) != _hash(r1)
    for file in (root, r1, r2):
        value = _json_bytes(file)
        assert value["form_id"] == _json_bytes(root)["form_id"]
        assert value["rubric_sha256"] == _json_bytes(root)["rubric_sha256"]


def _chain_call(destination: Path, rubric: Path, graded: Path,
                *revisions: Path):
    return run_cli("--verify-chain-to", destination, rubric, graded, *revisions)


def test_verify_chain_to_writes_one_safe_local_receipt_for_real_revision_chain(
    tmp_path,
):
    _, private, public, root, rubric, r1, r2, graded = _two_private_revisions(
        tmp_path, "verified chain")
    output = private / "CHAIN_VERIFIED_SYNTHETIC.json"
    assert not output.exists()
    rc, receipt, raw = _chain_call(output, rubric, graded, root, r1, r2)
    assert rc == 0, receipt
    assert receipt["status"] == "OPERATOR_FORM_CHAIN_VERIFIED"
    assert receipt["participant_count"] is None
    assert output.is_file()
    summary = _json_bytes(output)
    assert summary["participant_count"] is None
    assert summary["R5"] == "STOP_R5"
    assert summary["final_sha256"] == _hash(r2)
    assert summary["human_observation_verified"] is False
    assert summary["task_ids_recorded"] == ["OP09", "OP01"]
    assert len(summary["edges"]) == 2
    assert summary["edges"][0]["source_sha256"] == _hash(root)
    assert summary["edges"][0]["destination_sha256"] == _hash(r1)
    assert summary["edges"][1]["source_sha256"] == _hash(r1)
    assert summary["edges"][1]["destination_sha256"] == _hash(r2)
    assert summary["links_verified"] == 2
    assert _json_bytes(graded)["coded_input_sha256"] == _hash(r2)
    assert summary["form_reference"] == _json_bytes(r2)["form_id"][:12]
    assert not list(public.glob("*.json"))
    for path in (output, rubric, graded, root, r1, r2):
        assert str(path) not in raw and path.name not in raw
    before = output.read_bytes()
    rc, rejected, _ = _chain_call(output, rubric, graded, root, r1, r2)
    assert rc != 0 and rejected["status"] == "OPERATOR_REJECTED"
    assert output.read_bytes() == before




@pytest.mark.parametrize("mutation", (
    "missing_middle",
    "wrong_order",
    "root_reencoded",
    "middle_reencoded",
    "corrupt_last_predecessor",
    "two_tasks_changed",
    "scored_result_tampered",
    "different_form_rubric",
    "repeat_link",
))
def test_verify_chain_rejects_broken_or_unbound_paths_without_creating_report(
    tmp_path, mutation,
):
    _, private, public, root, rubric, r1, r2, graded = _two_private_revisions(
        tmp_path, "bad_" + mutation)
    chain = [root, r1, r2]
    if mutation == "missing_middle":
        chain = [root, r2]
    elif mutation == "wrong_order":
        chain = [root, r2, r1]
    elif mutation == "root_reencoded":
        body = _json_bytes(root)
        root.write_bytes(
            (json.dumps(body, indent=3, ensure_ascii=True) + "\n").encode("utf-8"))
    elif mutation == "middle_reencoded":
        body = _json_bytes(r1)
        r1.write_bytes(
            (json.dumps(body, indent=3, ensure_ascii=True) + "\n").encode("utf-8"))
    elif mutation == "corrupt_last_predecessor":
        body = _json_bytes(r2)
        body["predecessor_sha256"] = "0" * 64
        r2.write_bytes(
            (json.dumps(body, sort_keys=True) + "\n").encode("utf-8"))
    elif mutation == "two_tasks_changed":
        body = _json_bytes(r2)
        extra = next(item for item in body["observations"]
                     if item["task_id"] == "OP02")
        extra["technical"] = "TECH_COMPLETED"
        r2.write_bytes(
            (json.dumps(body, sort_keys=True) + "\n").encode("utf-8"))
    elif mutation == "scored_result_tampered":
        body = _json_bytes(graded)
        body["rollup"]["technical"]["TECH_BLOCKED"] += 1
        graded.write_bytes(
            (json.dumps(body, sort_keys=True) + "\n").encode("utf-8"))
    elif mutation == "different_form_rubric":
        second_rubric = private / "other v2 supervisor rubric.json"
        second_root = private / "other v2 blank form.json"
        second_handout = public / "other public handout.html"
        code, receipt, raw = run_cli(
            "--prepare-form", second_root, second_handout, second_rubric)
        assert code == 0, receipt
        assert _json_bytes(second_root)["form_id"] != _json_bytes(root)["form_id"]
        rubric = second_rubric
    elif mutation == "repeat_link":
        chain = [root, r1, r1, r2]
    else:
        raise AssertionError("Unexpected chain mutant")

    destination = private / ("REJECT_CHAIN_" + mutation + ".json")
    assert not destination.exists()
    before_files = {path: path.read_bytes() for path in chain if path.is_file()}
    before_files[graded] = graded.read_bytes()
    before_files[rubric] = rubric.read_bytes()
    rc, rejected, stdout = _chain_call(destination, rubric, graded, *chain)
    assert rc != 0
    assert rejected["status"] == "OPERATOR_REJECTED"
    assert rejected["error_code"].startswith("OPERATOR_")
    assert not destination.exists()
    assert rejected["participant_count"] is None
    for source, original in before_files.items():
        assert source.read_bytes() == original
        assert str(source) not in stdout
    assert str(destination) not in stdout
    assert not list(public.glob("*.json"))


@pytest.mark.skipif(os.name != "nt", reason="Windows-specific NTFS junctions")
def test_windows_junction_into_checkout_denied_for_new_private_path(tmp_path):
    junction = tmp_path / "external junction into checkout"
    created = subprocess.run(
        ["cmd.exe", "/c", "mklink", "/J", str(junction), str(ROOT)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    assert created.returncode == 0, created.stderr.decode(errors="replace")
    target = junction / "__operator_artifact_security_forbidden_private__"
    assert not (ROOT / target.name).exists()
    try:
        rc, rejected, stdout = run_cli("--new-private-dir", target)
        assert rc != 0 and rejected["status"] == "OPERATOR_REJECTED"
        assert rejected["error_code"].startswith("OPERATOR_")
        assert not (ROOT / target.name).exists()
        assert str(target) not in stdout
    finally:
        junction.rmdir()
    assert not junction.exists()


@pytest.mark.skipif(os.name != "nt", reason="Windows symlink privileges")
def test_windows_symlink_to_private_folder_must_be_rejected_or_proven_denied(
    tmp_path,
):
    _, private, _, _, _, _ = _secure_v2(tmp_path, "symlink_alias")
    link = tmp_path / "private directory symlink"
    try:
        link.symlink_to(private, target_is_directory=True)
    except OSError as exc:
        # This is *not* a positive test of application symlink rejection:
        # WinError1314 means the fixture could not be created on this host.
        assert getattr(exc, "winerror", None) == 1314
        assert not os.path.lexists(link)
        print("WINDOWS_SYMLINK_PROTECTION_NOT_VERIFIED_WinError1314")
        return
    assert link.is_symlink()
    code, rejected, raw = run_cli("--audit-private-dir", link)
    assert code != 0 and rejected["status"] == "OPERATOR_REJECTED"
    assert not (link / "new_v2_secret.json").exists()
    assert str(link) not in raw


@pytest.mark.skipif(os.name != "nt", reason="NTFS hardlink alias behavior")
def test_windows_hardlink_public_alias_exposes_key_to_same_user_token_only(
    tmp_path,
):
    """Observe a same-token risk; do NOT assert independent-user access."""
    _, private, public, source, rubric, _ = _secure_v2(
        tmp_path, "same token hardlink")
    alias = public / "DISPOSABLE_same_token_key_alias.json"
    assert not alias.exists()
    os.link(rubric, alias)
    assert os.path.samefile(rubric, alias)
    assert _hash(alias) == _hash(rubric)
    assert _json_bytes(alias)["schema"] == "pfl.beta_science_operator_template.v2"
    # The OS caller could create this alias because it ALREADY held source
    # access. No conclusion is drawn about a separate participant token.
    assert _json_bytes(source)["form_id"] == _json_bytes(alias)["form_id"]
    alias.unlink()
    assert rubric.exists()
    assert not alias.exists()


@pytest.mark.skipif(os.name != "nt", reason="NTFS ADS check on Windows")
def test_windows_ntfs_ads_chain_output_is_rejected_without_hidden_stream(
    tmp_path,
):
    _, private, _, root, rubric, r1, r2, graded = _two_private_revisions(
        tmp_path, "ads_chain")
    anchor = private / "SYNTHETIC_ADS_ANCHOR.txt"
    anchor.write_bytes(b"ANCHOR_UNCHANGED")
    destination = Path(str(anchor) + ":hidden_chain_report")
    assert not os.path.lexists(destination)
    rc, rejected, raw = _chain_call(destination, rubric, graded, root, r1, r2)
    assert rc != 0 and rejected["status"] == "OPERATOR_REJECTED"
    assert rejected["error_code"].startswith("OPERATOR_")
    assert anchor.read_bytes() == b"ANCHOR_UNCHANGED"
    assert not os.path.lexists(destination)
    assert str(destination) not in raw




@pytest.mark.skipif(os.name != "nt", reason="NTFS hardlinks and Windows ACL")
def test_prepatch_red_record_form_rejects_public_acl_hardlink_under_private_parent(
    tmp_path,
):
    """A pathname inside a secure folder does NOT make a linked inode private."""
    _, private, public, source, rubric, _ = _secure_v2(
        tmp_path, "hardlink infiltration")
    grant = subprocess.run(
        ["icacls", str(public), "/grant", "*S-1-1-0:(OI)(CI)(R)"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    assert grant.returncode == 0, grant.stderr.decode(errors="replace")
    assert _get_acl(public)["everyone_read"] is True
    # Materialize valid coded v2 bytes in PUBLIC ACL context first; linking
    # into private does not change the inode security descriptor on NTFS.
    accessible = public / "PUBLIC_CODING_SHARED_ACL.json"
    accessible.write_bytes(source.read_bytes())
    assert _get_acl(accessible)["everyone_read"] is True
    alias = private / "PRIVATE_PATH_BUT_PUBLIC_INODE.json"
    os.link(accessible, alias)
    assert os.path.samefile(accessible, alias)
    assert alias.stat().st_nlink >= 2
    assert _get_acl(alias)["everyone_read"] is True
    assert _json_bytes(alias)["form_id"] == _json_bytes(source)["form_id"]
    target = private / "REJECT_SOURCE_PUBLIC_LINK.json"
    assert not target.exists()
    initial = alias.read_bytes()
    rc, rejected, stdout = _record(
        alias, target, "OP01", "TECH_COMPLETED", "A", "UX_CLEAR",
    )
    assert str(alias) not in stdout and str(target) not in stdout
    assert rc != 0
    assert rejected["status"] == "OPERATOR_REJECTED"
    assert rejected["error_code"].startswith("OPERATOR_PRIVATE")
    assert not target.exists()
    assert alias.read_bytes() == initial
