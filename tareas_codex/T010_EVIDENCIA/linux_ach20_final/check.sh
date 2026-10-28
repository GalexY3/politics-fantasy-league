#!/bin/sh
cd /tmp/repo || exit 3
mkdir -p /tmp/results
export PYTHONDONTWRITEBYTECODE=1
export PYTHON=/tmp/venv/bin/python
uname -a > /tmp/results/environment.txt
$PYTHON --version >> /tmp/results/environment.txt
$PYTHON -m pytest --version >> /tmp/results/environment.txt
node --version >> /tmp/results/environment.txt
$PYTHON -m pip list >> /tmp/results/environment.txt 2>&1
ip addr show lo >> /tmp/results/environment.txt
ip addr show eth0 >> /tmp/results/environment.txt
date -u >> /tmp/results/environment.txt
git status --short > /tmp/results/status.txt
git rev-parse HEAD > /tmp/results/commit.txt
PYTHONTZPATH='' $PYTHON -c "from zoneinfo import ZoneInfo; print(ZoneInfo('Europe/Madrid'))" > /tmp/results/zone.out 2> /tmp/results/zone.err
echo zone=$? > /tmp/results/exits.txt
BASE=proyectos/politics-fantasy-league/ab_atlas/seed.json
UPDATES=proyectos/politics-fantasy-league/ab_atlas/updates
$PYTHON ab_atlas/atlas_delta.py check --base "$BASE" --updates "$UPDATES" > /tmp/results/atlas.out 2> /tmp/results/atlas.err
echo atlas=$? >> /tmp/results/exits.txt
$PYTHON ab_atlas/atlas_delta.py replay --base "$BASE" --updates "$UPDATES" --out /tmp/state.json > /tmp/results/replay.out 2> /tmp/results/replay.err
echo replay=$? >> /tmp/results/exits.txt
$PYTHON -c "import json,glob; d=json.load(open('/tmp/state.json')); f=glob.glob('proyectos/politics-fantasy-league/ab_atlas/updates/*.json'); print('batches',len(f),'nodes',len(d['nodes']),'edges',len(d['edges']),'runs',len(d['runs']),'complaints',len(d['complaints']),'operations',sum(len(json.load(open(p))['ops']) for p in f))" > /tmp/results/counts.out 2> /tmp/results/counts.err
echo counts=$? >> /tmp/results/exits.txt
$PYTHON -m pytest -q -rs -p no:cacheprovider ab_atlas/tests > /tmp/results/atlas_tests.out 2> /tmp/results/atlas_tests.err
echo atlas_tests=$? >> /tmp/results/exits.txt
cd proyectos/politics-fantasy-league || exit 4
export PYTHONPATH=src
date -u > /tmp/results/pytest_start.txt
$PYTHON -m pytest -q -rs -p no:cacheprovider > /tmp/results/pytest.out 2> /tmp/results/pytest.err
echo pytest=$? >> /tmp/results/exits.txt
date -u > /tmp/results/pytest_end.txt
node --test tests/*.mjs > /tmp/results/node.out 2> /tmp/results/node.err
echo node=$? >> /tmp/results/exits.txt
date -u > /tmp/results/end.txt
cd /tmp/results
sha256sum *.txt *.out *.err > sha256.txt
printf '\nCHECK_DONE\n'