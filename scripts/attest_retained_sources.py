"""SHA-only source preservation audit; never parses restricted original rows."""
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from politics_fantasy.retained_source_integrity import write_receipt

if __name__=="__main__":
    result=write_receipt(path=ROOT/"data/source_manifests/r9_retained_sources_integrity_20261031.json")
    print("PASS preserved originals", result["official_original_files"],
          "private metadata derivatives", result["private_derivatives_files"])
    print("No source content parsed; no rights or historical population promoted.")
