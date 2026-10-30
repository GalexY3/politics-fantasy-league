#!/bin/sh
set -e
ip link set lo up
ip link set eth0 up
udhcpc -i eth0 -q -n
setup-apkrepos -1
echo http://dl-cdn.alpinelinux.org/alpine/v3.24/community >> /etc/apk/repositories
apk update
apk add git python3 py3-pip py3-pytest py3-numpy nodejs tzdata py3-setuptools
adduser -D pfl
git clone -b fix/pfl-t010-atlas-http-20261028 /mnt/shared/repo.bundle /tmp/repo
chown -R pfl:pfl /tmp/repo
python3 -m venv --without-pip --system-site-packages /tmp/venv
/tmp/venv/bin/python -m pip install tzdata pytest-subtests -e '/tmp/repo/proyectos/politics-fantasy-league[test]' --no-build-isolation --break-system-packages > /tmp/setup.log 2>&1
ip link set eth0 down
cp /mnt/shared/check.sh /tmp/check.sh
su pfl -s /bin/sh -c 'sh /tmp/check.sh'
mkdir /mnt/shared/results
cp /tmp/results/* /mnt/shared/results/
cp /tmp/setup.log /mnt/shared/setup.log
sync
printf '\nT010_FINISHED\n'