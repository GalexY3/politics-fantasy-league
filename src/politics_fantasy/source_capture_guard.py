"""Research-only bounded OOXML source-byte guard (not HTTPS provenance proof).

Input is already-retrieved raw bytes. A valid ZIP and source-looking URL do NOT
establish that the publisher served these bytes, licenses, freshness, or release time.
Do not commit original spreadsheets or person-level rows.
"""
from __future__ import annotations
import hashlib
import hmac
import io
from pathlib import PurePosixPath
from urllib.parse import urlsplit
from zipfile import BadZipFile, ZipFile

MAX_ARCHIVE_BYTES = 25_000_000
MAX_UNCOMPRESSED_BYTES = 100_000_000
OFFICIAL_HOST = 'descargas.interior.gob.es'
OFFICIAL_PREFIX = '/datasets/paridad_electoral/'


def inspect_xlsx_bytes(url: str, raw: bytes, *, declared_sha256: str | None = None) -> dict:
    """Validate byte/OOXML structure and compute checksum; *never* certify issuer origin."""
    if not isinstance(url, str):
        raise ValueError('UNSAFE_SOURCE_URL')
    u = urlsplit(url)
    if (u.scheme != 'https' or u.hostname != OFFICIAL_HOST or u.username is not None
        or u.password is not None or u.port not in (None,443)
        or u.fragment or u.query or not u.path.startswith(OFFICIAL_PREFIX)
        or not u.path.lower().endswith('.xlsx')):
        raise ValueError('UNSAFE_SOURCE_URL')
    if not isinstance(raw, bytes) or not raw:
        raise ValueError('BYTES_REQUIRED')
    if len(raw) > MAX_ARCHIVE_BYTES:
        raise ValueError('ARCHIVE_TOO_LARGE')
    if not raw.startswith(b'PK\x03\x04'):
        raise ValueError('NOT_XLSX_ARCHIVE')
    digest = hashlib.sha256(raw).hexdigest()
    if declared_sha256 is not None:
        if not isinstance(declared_sha256,str) or len(declared_sha256)!=64 or any(c not in '0123456789abcdef' for c in declared_sha256):
            raise ValueError('INVALID_DECLARED_HASH')
        if not hmac.compare_digest(digest,declared_sha256):
            raise ValueError('HASH_MISMATCH')
    # A nonempty, nonspanned ZIP must terminate in an end-of-central-directory record.
    # Detect a common fake-workbook attack with trailing HTML/error content.
    eocd_at = raw.rfind(b'PK\x05\x06')
    if eocd_at < 0 or eocd_at+22>len(raw):
        raise ValueError('NOT_XLSX_ARCHIVE')
    comment_len = int.from_bytes(raw[eocd_at+20:eocd_at+22],'little')
    if eocd_at+22+comment_len != len(raw):
        raise ValueError('TRAILING_ZIP_BYTES')
    try:
        with ZipFile(io.BytesIO(raw)) as z:
            members = z.infolist()
            names = {m.filename for m in members}
            for m in members:
                name = m.filename
                p = PurePosixPath(name)
                if ('\\' in name or name.startswith('/') or '..' in p.parts):
                    raise ValueError('UNSAFE_ZIP_MEMBER')
            if sum(m.file_size for m in members) > MAX_UNCOMPRESSED_BYTES:
                raise ValueError('ZIP_UNCOMPRESSED_TOO_LARGE')
            required={'[Content_Types].xml','_rels/.rels','xl/workbook.xml'}
            sheets=[n for n in names if n.startswith('xl/worksheets/sheet') and n.endswith('.xml')]
            if not required.issubset(names) or not sheets:
                raise ValueError('MISSING_XLSX_PART')
            if z.testzip() is not None:
                raise ValueError('ZIP_CRC_ERROR')
    except BadZipFile as e:
        raise ValueError('NOT_XLSX_ARCHIVE') from e
    return {'sha256':digest,'byte_length':len(raw),'sheets':len(sheets),
            'structure':'OOXML_XLSX_ZIP_VALID_SYNTHETIC_OR_UNVERIFIED_ORIGIN',
            'origin_authenticated':False,'first_public_at':None,
            'note':'Structure and hash only; HTTPS transport, issuer, licensing and publication date not proven'}
