#!/bin/sh

set -e

version=${1?No version specified}

BUILD_DIR=$(mktemp -d /var/tmp/build_python_XXXXXX)
cd "${BUILD_DIR}"

curl "https://www.python.org/ftp/python/${version}/Python-${version}.tar.xz" | tar xJ --strip-components=1

./configure --prefix="/opt/python-${version}" \
    --enable-ipv6 \
    --enable-loadable-sqlite-extensions \
    --with-dbmliborder=bdb:gdbm \
    --with-computed-gotos \
    --with-system-expat \
    --with-system-ffi \
    --enable-shared

make
make install

set +e

echo "/opt/python-${version}/lib" >"/etc/ld.so.conf.d/python-${version}.conf"
ldconfig

ln -sf "/opt/python-${version}" /opt/python

cd /tmp && rm -rf "${BUILD_DIR}"
