"""Offline demo launcher. No third-party runtime packages required."""
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from politics_fantasy.server import serve

if __name__=='__main__':
    serve(ROOT/'data'/'demo'/'game.db',port=8787)