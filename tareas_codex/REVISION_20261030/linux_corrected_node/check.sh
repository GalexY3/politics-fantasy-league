#!/bin/sh
cd /tmp/repo/proyectos/politics-fantasy-league || exit 3
mkdir -p /tmp/results
node --version > /tmp/results/environment.txt
uname -a >> /tmp/results/environment.txt
git rev-parse HEAD > /tmp/results/commit.txt
git status --porcelain > /tmp/results/status.txt
node scripts/run_node_tests.mjs > /tmp/results/node.out 2> /tmp/results/node.err
printf 'node=%s\n' "$?" > /tmp/results/exits.txt