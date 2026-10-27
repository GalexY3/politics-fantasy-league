import hashlib
import importlib.util
import json
from pathlib import Path
from zipfile import ZipFile

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "package_release.py"
spec = importlib.util.spec_from_file_location("package_release", SCRIPT)
package_release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(package_release)


def put(root, name, content="fixture"):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def test_package_excludes_local_data_secrets_and_previous_output(tmp_path, monkeypatch):
    root = tmp_path / "project"
    put(root, "src/app.py", "normal source")
    put(root, "README.md", "normal documentation")
    for name in ["data/raw/input.xml", "data/bronze/a", "data/silver/a", "data/gold/a",
                 "data/local_field/input.csv", "data/demo/game.sqlite", ".env", ".env.local",
                 "credentials.key", "cert.pem", ".venv/lib/a", "src/pkg.egg-info/PKG-INFO"]:
        put(root, name, "PRIVATE_FIXTURE")
    previous_manifest = put(root, "MANIFEST_SHA256.json", "previous manifest")
    target = put(root, "dist/output.zip", "previous archive")
    monkeypatch.setattr(package_release, "ROOT", root)

    package_release.pack(target)

    with ZipFile(target) as archive:
        names = set(archive.namelist())
        assert names == {"politics_fantasy_league/src/app.py", "politics_fantasy_league/README.md",
                         "politics_fantasy_league/MANIFEST_SHA256.json"}
        manifest = json.loads(archive.read("politics_fantasy_league/MANIFEST_SHA256.json"))
        for name, metadata in manifest["files"].items():
            data = archive.read("politics_fantasy_league/" + name)
            assert hashlib.sha256(data).hexdigest() == metadata["sha256"]
            assert len(data) == metadata["bytes"]
        assert not manifest.get("github_published")
        assert manifest.get("verified_tests") is None
    assert previous_manifest.read_text(encoding="utf-8") == "previous manifest"


def test_package_does_not_follow_file_symlinks(tmp_path, monkeypatch):
    root = tmp_path / "project"
    put(root, "README.md")
    outside = put(tmp_path, "outside.txt", "PRIVATE_FIXTURE")
    try:
        (root / "link.txt").symlink_to(outside)
    except OSError:
        pytest.skip("creating symlinks is unavailable on this system")
    monkeypatch.setattr(package_release, "ROOT", root)
    target = tmp_path / "release.zip"
    package_release.pack(target)
    with ZipFile(target) as archive:
        assert "politics_fantasy_league/link.txt" not in archive.namelist()
