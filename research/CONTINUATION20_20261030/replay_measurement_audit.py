"""Replay local originals; emits aggregates only. Raw inputs stay outside Git."""
import argparse
import importlib.util
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('csv', type=Path)
parser.add_argument('minute_html', type=Path)
args = parser.parse_args()
path = Path(__file__).parents[1] / 'R0_INSTITUTIONAL_PETITIONS_20261030/committee_measurement_audit.py'
spec = importlib.util.spec_from_file_location('measurement_audit', path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
print(json.dumps(module.audit(args.csv.read_bytes(), args.minute_html.read_bytes()), sort_keys=True))
