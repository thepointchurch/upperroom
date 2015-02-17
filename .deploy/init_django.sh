#!/bin/sh

device=${1?No device specified}
version=${2-9.1}
path=${3-/srv/django}

mkdir -p "${path}"

if [ "`/sbin/blkid -o value -s TYPE /dev/${device}`" = '' ]; then
    /sbin/mkfs.ext4 -L django -F "/dev/${device}"
fi
mount "/dev/${device}" "${path}"

set -e

/usr/bin/pg_dropcluster --stop "${version}" main
/usr/bin/pg_createcluster -d "${path}/postgres" --locale=en_AU "${version}" django

cat >"/etc/postgresql/${version}/django/postgresql.conf" <<POSTGRESQL_CONF
data_directory = '${path}/postgres'
hba_file = '/etc/postgresql/${version}/django/pg_hba.conf'
ident_file = '/etc/postgresql/${version}/django/pg_ident.conf'
external_pid_file = '/var/run/postgresql/${version}-django.pid'
listen_addresses = ''
max_connections = 100
unix_socket_directory = '/var/run/postgresql'
shared_buffers = 24MB
log_line_prefix = '%t '
datestyle = 'iso, dmy'
lc_messages = 'en_AU'
lc_monetary = 'en_AU'
lc_numeric = 'en_AU'
lc_time = 'en_AU'
default_text_search_config = 'pg_catalog.english'
POSTGRESQL_CONF

cat >"/etc/postgresql/${version}/django/pg_hba.conf" <<PG_HBA_CONF
local all postgres peer
local all all peer
PG_HBA_CONF

/usr/bin/pg_ctlcluster "${version}" django start
