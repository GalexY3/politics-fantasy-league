"""Offline demo launcher. No third-party runtime packages required."""
import argparse
from pathlib import Path
import re
import sys
from urllib.parse import parse_qsl, urlencode, urlsplit

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from politics_fantasy.server import serve
from politics_fantasy.scientific_registry import (
    FAMILY_FILTERS, PUBLICATION_FILTERS, VALID_DAYS,
)
from politics_fantasy.scientific_integration_lab import CUTS, SCENARIOS

GUEST_QUERY_KEYS = (
    'pfl_guest', 'cut', 'valid_at', 'family',
    'published_until', 'scenario', 'view',
)
GUEST_QUERY_LIMIT = 640


def resume_guest_query(value: str) -> str:
    """Accept a filter recipe, never an identity, credential or old origin.

    Output is reconstructed exclusively from seven validated, public fixture
    selectors; browser receipts are fetched and checked anew by app.js.
    """
    def invalid() -> ValueError:
        return ValueError('Enlace de consulta científica no válido')

    if not isinstance(value, str) or len(value) > 1024 or not value:
        raise invalid()
    if any(ord(char) < 33 or ord(char) > 126 for char in value):
        raise invalid()
    if '\\' in value or '#' in value or re.search(r'%(?![0-9a-fA-F]{2})', value):
        raise invalid()
    if value.startswith('?'):
        query = value[1:]
    else:
        if not value.startswith('http://'):
            raise invalid()
        try:
            parts = urlsplit(value)
            if (parts.scheme != 'http' or parts.hostname not in
                    ('127.0.0.1', 'localhost') or parts.username is not None
                    or parts.password is not None or parts.path != '/'
                    or parts.fragment or parts.port is None
                    or not 1 <= parts.port <= 65535
                    or parts.netloc != f'{parts.hostname}:{parts.port}'):
                raise invalid()
        except (ValueError, UnicodeError) as exc:
            raise invalid() from exc
        query = parts.query
    if (not query or len(query) > GUEST_QUERY_LIMIT
            or query.count('&') != len(GUEST_QUERY_KEYS) - 1
            or any(not part or '=' not in part or part.startswith('=')
                   for part in query.split('&'))):
        raise invalid()
    try:
        pairs = parse_qsl(query, keep_blank_values=True,
                          strict_parsing=True, encoding='utf-8', errors='strict')
    except (ValueError, UnicodeError) as exc:
        raise invalid() from exc
    if (len(pairs) != len(GUEST_QUERY_KEYS)
            or set(key for key, _ in pairs) != set(GUEST_QUERY_KEYS)
            or len({key for key, _ in pairs}) != len(pairs)):
        raise invalid()
    fields = dict(pairs)
    if (fields['pfl_guest'] != 'v1'
            or fields['cut'] not in CUTS
            or fields['valid_at'] not in VALID_DAYS
            or fields['family'] not in FAMILY_FILTERS
            or fields['published_until'] not in PUBLICATION_FILTERS
            or (fields['published_until'] != 'as_of' and
                fields['published_until'] > CUTS[fields['cut']])
            or fields['scenario'] not in SCENARIOS
            or fields['view'] not in ('sources', 'compare')):
        raise invalid()
    return urlencode([(key, fields[key]) for key in GUEST_QUERY_KEYS])


def port_number(value: str) -> int:
    try:
        port = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError('El puerto debe ser un entero entre 0 y 65535') from exc
    if not 0 <= port <= 65535:
        raise argparse.ArgumentTypeError('El puerto debe estar entre 0 y 65535')
    return port


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description='Inicia la demo sintética local de PFL.')
    parser.add_argument('--port', type=port_number, default=8787,
                        help='Puerto de loopback (0 = elegir puerto libre; por defecto: 8787)')
    parser.add_argument('--db', type=Path, default=None,
                        help='Ruta de la base de datos local de la demo')
    parser.add_argument('--science-only', action='store_true',
                        help='Observatorio y Laboratorio en localhost, sin cuentas Fantasy ni POST')
    parser.add_argument('--resume-guest-query', metavar='URL_O_QUERY',
                        help='Solo --science-only: reanuda una consulta ficticia S9 permitida')
    args = parser.parse_args(argv)
    if args.resume_guest_query is not None and not args.science_only:
        parser.error('--resume-guest-query requiere --science-only')
    try:
        restored_query = (resume_guest_query(args.resume_guest_query)
                          if args.resume_guest_query is not None else None)
    except ValueError:
        parser.error('Enlace de consulta científica no válido')
    # The scientific-only default is in a DIFFERENT directory, preventing
    # accidental sharing with demo accounts when --db is omitted.
    default_db=(ROOT/'data'/'science_beta'/'science.db' if args.science_only
                else ROOT/'data'/'demo'/'game.db')
    db=args.db if args.db is not None else default_db
    if args.science_only:
        if restored_query is None:
            serve(db,port=args.port,scientific_only=True)
        else:
            serve(db,port=args.port,scientific_only=True,
                  resume_guest_query=restored_query)
    else:
        serve(db,port=args.port)


if __name__=='__main__':
    main()
