"""Offline demo launcher. No third-party runtime packages required."""
import argparse
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from politics_fantasy.server import serve


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
    args = parser.parse_args(argv)
    # The scientific-only default is in a DIFFERENT directory, preventing
    # accidental sharing with demo accounts when --db is omitted.
    default_db=(ROOT/'data'/'science_beta'/'science.db' if args.science_only
                else ROOT/'data'/'demo'/'game.db')
    db=args.db if args.db is not None else default_db
    if args.science_only:
        serve(db,port=args.port,scientific_only=True)
    else:
        serve(db,port=args.port)


if __name__=='__main__':
    main()
