#!/bin/sh
cd /tmp/repo || exit 3
mkdir -p /tmp/results
export PYTHONDONTWRITEBYTECODE=1
export PYTHON=/tmp/venv/bin/python
{
 uname -a
 id
 df -T /tmp/repo
 $PYTHON --version
 $PYTHON -m pytest --version
 node --version
 $PYTHON -m pip list
 ip addr show lo
 ip addr show eth0
 date -u
} > /tmp/results/environment.txt 2>&1
git rev-parse HEAD > /tmp/results/commit.txt
git status --porcelain > /tmp/results/status.txt
run() {
 name="$1"; shift
 "$@" > "/tmp/results/$name.out" 2> "/tmp/results/$name.err"
 code=$?
 printf '%s=%s\n' "$name" "$code" >> /tmp/results/exits.txt
 printf '\nT025_CASE_%s_EXIT_%s\n' "$name" "$code"
}
cp /tmp/install.out /tmp/results/install.out
cp /tmp/install.err /tmp/results/install.err
printf 'install=' >> /tmp/results/exits.txt
cat /tmp/install.exit >> /tmp/results/exits.txt
run catalogue $PYTHON scripts/project_index.py check
run continuity $PYTHON scripts/project_status.py check
run achievements $PYTHON ab_atlas/validate_achievements.py
run zone env PYTHONTZPATH= $PYTHON -c "from zoneinfo import ZoneInfo; print(ZoneInfo('Europe/Madrid'))"
BASE=ab_atlas/seed.json
UPDATES=ab_atlas/updates
run atlas $PYTHON tools/ab_atlas/atlas_delta.py check --base "$BASE" --updates "$UPDATES"
run replay $PYTHON tools/ab_atlas/atlas_delta.py replay --base "$BASE" --updates "$UPDATES" --out /tmp/state.json
run counts $PYTHON -c "import json,glob; d=json.load(open('/tmp/state.json')); fs=glob.glob('$UPDATES/*.json'); print('batches',len(fs),'nodes',len(d['nodes']),'edges',len(d['edges']),'runs',len(d['runs']),'complaints',len(d['complaints']),'operations',sum(len(json.load(open(p))['ops']) for p in fs))"
run atlas_tests $PYTHON -m pytest -q -rs -p no:cacheprovider tools/ab_atlas/tests
cd /tmp/repo || exit 4
export PYTHONPATH=src
date -u > /tmp/results/pytest_start.txt
run pytest $PYTHON -m pytest -q -rs -p no:cacheprovider
date -u > /tmp/results/pytest_end.txt
run node node scripts/run_node_tests.mjs
date -u > /tmp/results/end.txt
git status --porcelain > /tmp/results/status_after.txt
