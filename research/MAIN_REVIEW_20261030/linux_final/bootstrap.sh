#!/bin/sh
set -eu
exec > /tmp/bootstrap.log 2>&1
stage() { printf '\nT025_STAGE_%s\n' "$1" > /dev/ttyS0; }
stage SETUP
ip link set lo up
ip link set eth0 up
udhcpc -i eth0 -q -n
printf 'https://dl-cdn.alpinelinux.org/alpine/v3.24/main\nhttps://dl-cdn.alpinelinux.org/alpine/v3.24/community\n' > /etc/apk/repositories
apk update
apk add --no-cache git python3 py3-pip py3-pytest py3-numpy nodejs tzdata py3-setuptools
python3 -m venv --without-pip --system-site-packages /tmp/venv
/tmp/venv/bin/python -m pip install tzdata pytest-subtests --break-system-packages
adduser -D pfl
su pfl -s /bin/sh -c 'git clone /mnt/repo.bundle /tmp/repo'
su pfl -s /bin/sh -c 'cd /tmp/repo && git checkout --detach 074f72e19b522e7a507045e3738609fa5f6139cc'
ip link set eth0 down
cp /mnt/check.sh /tmp/check.sh
stage TESTS
su pfl -s /bin/sh -c 'sh /tmp/check.sh'
cp /tmp/bootstrap.log /tmp/results/bootstrap.log
/tmp/venv/bin/python - <<'PY'
import hashlib,json
from pathlib import Path
p=Path('/tmp/results')
files={f.name:{'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in sorted(p.iterdir()) if f.is_file()}
(p/'MANIFEST.json').write_text(json.dumps({'schema':'pfl.t025.linux.qa.v1','commit':'074f72e19b522e7a507045e3738609fa5f6139cc','files':files},indent=2)+'\n')
PY
tar -czf /tmp/t025-results.tgz -C /tmp results
stage ARCHIVE
printf '\nT025_ARCHIVE_BEGIN\n' > /dev/ttyS0
base64 /tmp/t025-results.tgz > /dev/ttyS0
printf '\nT025_ARCHIVE_END\n' > /dev/ttyS0
sha256sum /tmp/t025-results.tgz > /dev/ttyS0
stage DONE
