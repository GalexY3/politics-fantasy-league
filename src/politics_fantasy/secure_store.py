"""Private, POSIX-dirfd-anchored SHA object store; not a publisher signature.

Requires a trusted directory path and parent. Refuse unsupported platforms rather
than silently downgrade confinement (notably Windows). Caller controls local root.
Every opened storage directory and file is followed by its directory descriptor,
not by a mutable string path. Existing symlinks are rejected with O_NOFOLLOW.
"""
from __future__ import annotations
from contextlib import contextmanager
import errno
import hashlib
import json
import os
from pathlib import Path
import secrets
import stat


def _require_anchored_store() -> None:
    if (os.name != "posix" or not hasattr(os, "O_NOFOLLOW")
            or not hasattr(os, "O_DIRECTORY") or os.open not in os.supports_dir_fd
            or os.mkdir not in os.supports_dir_fd
            or os.link not in os.supports_dir_fd):
        raise ValueError("SECURE_STORE_UNSUPPORTED_PLATFORM")


def _check_private_permissions(fd: int, directory: bool) -> None:
    attrs = os.fstat(fd)
    if attrs.st_uid != os.geteuid() or attrs.st_mode & 0o077:
        raise ValueError("UNSAFE_STORE_OWNERSHIP_OR_PERMISSIONS")
    if directory and not stat.S_ISDIR(attrs.st_mode):
        raise ValueError("UNSAFE_STORE_DIRECTORY_KIND")
    if not directory and not stat.S_ISREG(attrs.st_mode):
        raise ValueError("NONREGULAR_PRIVATE_FILE")


def _directory_flags() -> int:
    return os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW


@contextmanager
def _root_fd(root: Path, *, create: bool = True):
    _require_anchored_store()
    root = Path(root)
    # Root's parent is controlled by the local operator. An untrusted writer
    # to its ancestors is outside this local tool's OS boundary.
    if root.is_symlink():
        raise ValueError("SYMLINK_STORAGE_ROOT")
    if create:
        root.mkdir(parents=True, exist_ok=True, mode=0o700)
    elif not root.is_dir():
        raise ValueError("MISSING_STORE_ROOT")
    try:
        fd = os.open(root, _directory_flags())
    except OSError as exc:
        raise ValueError("UNSAFE_STORAGE_ROOT") from exc
    try:
        _check_private_permissions(fd, directory=True)
        yield fd
    finally:
        os.close(fd)


@contextmanager
def _child_directory(parent: int, name: str):
    if not name or name in (".", "..") or "/" in name or "\\" in name:
        raise ValueError("BAD_STORE_DIRECTORY")
    created = False
    try:
        os.mkdir(name, 0o700, dir_fd=parent)
        created = True
    except FileExistsError:
        pass
    try:
        fd = os.open(name, _directory_flags(), dir_fd=parent)
    except OSError as exc:
        raise ValueError("SYMLINK_OR_UNSAFE_STORE_DIRECTORY") from exc
    try:
        _check_private_permissions(fd, directory=True)
        if created:
            os.fsync(parent)  # Persist child directory entry.
        yield fd
    finally:
        os.close(fd)


def _write_all(fd: int, value: bytes) -> None:
    view = memoryview(value)
    while view:
        written = os.write(fd, view)
        if written <= 0:
            raise OSError("STORE_WRITE_DID_NOT_PROGRESS")
        view = view[written:]


def _read_stored(fd: int, max_bytes: int) -> bytes:
    out = bytearray()
    while len(out) <= max_bytes:
        part = os.read(fd, min(65536, max_bytes + 1 - len(out)))
        if not part:
            break
        out += part
    return bytes(out)


def _verify_object(folder: int, name: str, data: bytes) -> None:
    try:
        fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                     dir_fd=folder)
    except OSError as exc:
        raise ValueError("UNSAFE_EXISTING_OBJECT") from exc
    try:
        _check_private_permissions(fd, directory=False)
        if _read_stored(fd, len(data)) != data:
            raise ValueError("SHA_COLLISION_OR_CORRUPTED_STORE")
    finally:
        os.close(fd)


def store_bytes(root: Path, data: bytes, digest: str) -> str:
    """Write once by hard-link of an exclusive random temp; no clobber-on-race."""
    if not isinstance(data, bytes) or hashlib.sha256(data).hexdigest() != digest:
        raise ValueError("INVALID_STORE_DIGEST")
    if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
        raise ValueError("INVALID_STORE_DIGEST")
    with _root_fd(root) as rootfd:
        with _child_directory(rootfd, "objects") as objects:
            with _child_directory(objects, digest[:2]) as folder:
                # Fast path still checks symlink/device and bytes under fd.
                try:
                    _verify_object(folder, digest, data)
                    return "objects/" + digest[:2] + "/" + digest
                except ValueError as exc:
                    if str(exc) != "UNSAFE_EXISTING_OBJECT":
                        raise
                    # Differentiate nonexisting from an unsafe existing inode.
                    try:
                        os.stat(digest, dir_fd=folder, follow_symlinks=False)
                    except FileNotFoundError:
                        pass
                    else:
                        raise
                temp = "." + digest + "." + secrets.token_hex(12) + ".tmp"
                fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                             0o600, dir_fd=folder)
                try:
                    try:
                        _write_all(fd, data)
                        os.fsync(fd)
                    finally:
                        os.close(fd)
                    try:
                        os.link(temp, digest, src_dir_fd=folder, dst_dir_fd=folder,
                                follow_symlinks=False)
                    except FileExistsError:
                        pass
                    _verify_object(folder, digest, data)
                finally:
                    os.unlink(temp, dir_fd=folder)
    return "objects/" + digest[:2] + "/" + digest


def append_private_jsonl(root: Path, filename: str, record: dict) -> None:
    if filename not in ("manifest.jsonl", "quarantine_reviews.jsonl"):
        raise ValueError("UNSUPPORTED_PRIVATE_LEDGER")
    payload = (json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
    with _root_fd(root) as folder:
        try:
            fd = os.open(filename, os.O_WRONLY | os.O_APPEND | os.O_CREAT | os.O_NOFOLLOW,
                         0o600, dir_fd=folder)
        except OSError as exc:
            raise ValueError("UNSAFE_PRIVATE_LEDGER") from exc
        try:
            _check_private_permissions(fd, directory=False)
            # O_APPEND reserves the offset for one syscall, not an entire JSONL
            # record when _write_all must retry a partial write. Cooperating
            # POSIX processes serialize the complete record under this lock.
            import fcntl
            fcntl.flock(fd, fcntl.LOCK_EX)
            try:
                _write_all(fd, payload)
                os.fsync(fd)
            finally:
                fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os.close(fd)


def preflight_private_storage(root: Path, filename: str) -> None:
    """Before external contact, reject local symlink objects/ledger paths.

    This does not create a transaction: a concurrent malicious writer in the
    trusted root or root ancestor remains out of threat scope.
    """
    if filename not in ("manifest.jsonl", "quarantine_reviews.jsonl"):
        raise ValueError("UNSUPPORTED_PRIVATE_LEDGER")
    with _root_fd(root) as folder:
        with _child_directory(folder, "objects"):
            pass
        try:
            entry = os.stat(filename, dir_fd=folder, follow_symlinks=False)
        except FileNotFoundError:
            return
        if not stat.S_ISREG(entry.st_mode):
            raise ValueError("UNSAFE_PRIVATE_LEDGER")
