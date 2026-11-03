"""Independent post-hardlink cleanup TOCTOU under real disposable NTFS files.

No human responses, other account, administrator, persistent writes, or
production monkeypatch. Interleavings happen AFTER the real os.link succeeded,
unlike prelink stage-inode/byte mutation tests.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest

from test_beta_operator_instrument_versioning import _prepared_v2
from test_beta_operator_private_write_race import _main, protocol


NTFS_ONLY = pytest.mark.skipif(os.name != "nt", reason="Real NTFS rename/link race")


@NTFS_ONLY
def test_prepatch_red_postlink_destination_replacement_is_not_deleted_on_failure(
    tmp_path, monkeypatch, protocol,
):
    """Cleanup must not mistake a replacement inode for our linked output."""
    _, _, _, source, _, _ = _prepared_v2(tmp_path, "after link destination Ω")
    original_source = source.read_bytes()
    destination = source.parent / "coded successor stolen filename.json"
    third_party = source.parent / "independent important synthetic file.json"
    other_bytes = b'{"third_party_important":"retain unchanged"}\n'
    third_party.write_bytes(other_bytes)
    other_id = (third_party.stat().st_dev, third_party.stat().st_ino)
    assert not destination.exists() and third_party.stat().st_nlink == 1
    original_link = os.link
    events = []

    def link_then_replace(stage, published, *args, **kwargs):
        result = original_link(stage, published, *args, **kwargs)
        if Path(published) == destination and not events:
            source_stage_id = (Path(stage).stat().st_dev, Path(stage).stat().st_ino)
            assert destination.stat().st_ino == source_stage_id[1]
            third_party.replace(destination)
            assert (destination.stat().st_dev, destination.stat().st_ino) == other_id
            events.append(source_stage_id)
        return result

    monkeypatch.setattr(os, "link", link_then_replace)
    code, receipt, stdout = _main(
        protocol, "--record-form", source, destination,
        "OP01", "TECH_COMPLETED", "A", "UX_CLEAR",
    )
    assert len(events) == 1, "Must interpose after successful real os.link"
    assert code != 0 and receipt["status"] == "OPERATOR_REJECTED"
    # Critical: failure cleanup must NOT unlink a later third-party inode
    # merely because its identity was first sampled *after* the hardlink.
    assert destination.exists(), "Cleanup deleted the third-party replacement!"
    assert (destination.stat().st_dev, destination.stat().st_ino) == other_id
    assert destination.read_bytes() == other_bytes
    assert source.read_bytes() == original_source
    assert str(destination) not in stdout and str(source) not in stdout


@NTFS_ONLY
def test_prepatch_red_postlink_stage_name_swap_does_not_delete_third_party(
    tmp_path, monkeypatch, protocol,
):
    """Swap stage immediately before its deletion, at the actual implementation hook.

    Older publisher calls Path.unlink directly; newer publisher calls the
    native, identity-bound _unlink_matching_inode.  Both exercise the same
    deterministic race, rather than bypassing the newer cleanup path.
    """
    _, _, _, source, _, rubric_path = _prepared_v2(
        tmp_path, "after link stage Ω")
    recorded = source.parent / "valid coded for postlink score.json"
    prereq, _, _ = _main(
        protocol, "--record-form", source, recorded,
        "OP01", "TECH_COMPLETED", "A", "UX_CLEAR")
    assert prereq == 0
    destination = source.parent / "private score successful with data loss.json"
    third_party = source.parent / "unrelated protected synthetic.json"
    other_bytes = b'{"third_party_important":"do not unlink"}\n'
    third_party.write_bytes(other_bytes)
    other_id = (third_party.stat().st_dev, third_party.stat().st_ino)
    before_source = recorded.read_bytes()
    real_unlink = Path.unlink
    events = []

    def swap_once(path):
        path = Path(path)
        if (path.parent != source.parent
                or not path.name.startswith(".pfl-stage-") or events):
            return
        assert destination.exists()
        assert path.stat().st_ino == destination.stat().st_ino
        parked = source.parent / "parked secure stage after audit Ω.tmp"
        path.rename(parked)
        third_party.replace(path)
        assert (path.stat().st_dev, path.stat().st_ino) == other_id
        events.append((parked, path))

    if hasattr(protocol, "_unlink_matching_inode"):
        real_matching_unlink = protocol._unlink_matching_inode

        def intercepted_matching_unlink(path, expected):
            # Exactly one injection before the *real* native-handle helper.
            # The immutable expected identity still refers to the moved
            # original stage, not to the unrelated replacement.
            if (Path(path).parent == source.parent
                    and Path(path).name.startswith(".pfl-stage-") and not events):
                assert (Path(path).stat().st_dev, Path(path).stat().st_ino) == expected
                swap_once(path)
            return real_matching_unlink(path, expected)

        monkeypatch.setattr(
            protocol, "_unlink_matching_inode", intercepted_matching_unlink)
    else:
        # Genuine historical PREPATCH RED: Path.unlink followed the pathname
        # blindly, deleting the third-party replacement and returning success.
        def intercepted_path_unlink(path, *args, **kwargs):
            swap_once(path)
            return real_unlink(path, *args, **kwargs)

        monkeypatch.setattr(Path, "unlink", intercepted_path_unlink)
    try:
        code, receipt, stdout = _main(
            protocol, "--evaluate-form", recorded, rubric_path, destination)
    finally:
        if events:
            parked, stage_name = events[0]
            # Restrained test-only cleanup of the remnant of OUR own stage.
            if parked.exists():
                real_unlink(parked)
    assert len(events) == 1, "Must reach the real post-audit stage cleanup"
    assert third_party.exists() or events[0][1].exists(), (
        "Third-party file was deleted under swapped stage pathname")
    surviving = third_party if third_party.exists() else events[0][1]
    assert surviving.read_bytes() == other_bytes
    assert (surviving.stat().st_dev, surviving.stat().st_ino) == other_id
    assert recorded.read_bytes() == before_source
    # A changed stage alias must cause a rejected publication, never a
    # successful receipt or cleanup of unrelated files.
    assert code != 0 and receipt["status"] == "OPERATOR_REJECTED"
    assert not destination.exists()
    assert str(destination) not in stdout


@NTFS_ONLY
def test_postlink_private_record_normal_success_and_clean_staging(
    tmp_path, protocol,
):
    """Control: without a race, publication should remain usable and clean."""
    _, _, _, source, _, _ = _prepared_v2(tmp_path, "after link normal control")
    destination = source.parent / "safe successor after normal os.link.json"
    before = source.read_bytes()
    rc, response, stdout = _main(
        protocol, "--record-form", source, destination,
        "OP01", "TECH_COMPLETED", "A", "UX_CLEAR")
    assert rc == 0 and response["status"] == "OPERATOR_FORM_OBSERVATION_RECORDED"
    assert destination.is_file() and destination.stat().st_nlink == 1
    assert protocol._windows_dacl_safe(destination, require_protected=False)
    assert response["destination_sha256"] == hashlib.sha256(destination.read_bytes()).hexdigest()
    assert not tuple(source.parent.glob(".pfl-stage-*.tmp"))
    assert source.read_bytes() == before
    assert str(destination) not in stdout
