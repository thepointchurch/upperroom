#!/bin/sh

cat <<CLOUDCONFIG
#cloud-config

apt_upgrade: true
hostname: ${HOST}
fqdn: ${HOST}.thepoint.org.au
manage_etc_hosts: true

mounts:
  - [ xvdb, /srv/django ]

mount_default_fields: [ None, None, "auto", "defaults,noatime", "0", "2" ]

packages:
  - unattended-upgrades
  - apt-listchanges
  - postgresql
  - postgresql-server-dev-all
  - git
  - build-essential
  - libbz2-dev
  - libdb-dev
  - libexpat1-dev
  - libffi-dev
  - libgdbm-dev
  - libgpm2
  - liblzma-dev
  - libncursesw5-dev
  - libreadline6-dev
  - libsqlite3-dev
  - libssl-dev
  - zlib1g-dev
  - nginx-full
  - runit
  - daemontools
  - dnsutils
  - gettext-base
  - ntp
  - exim4-daemon-light
  - curl

write_files:
  - encoding: b64
    content: |
`base64 .deploy/20auto-upgrades | sed 's/^/      /'`
    owner: root:root
    path: /etc/apt/apt.conf.d/20auto-upgrades
    permissions: '0644'
  - encoding: b64
    content: |
`base64 .deploy/50unattended-upgrades | sed 's/^/      /'`
    owner: root:root
    path: /etc/apt/apt.conf.d/50unattended-upgrades
    permissions: '0644'
  - encoding: b64
    content: |
`base64 .deploy/init_django.sh | sed 's/^/      /'`
    owner: root:root
    path: /tmp/init_django.sh
    permissions: '0750'
  - encoding: b64
    content: |
`base64 .deploy/build_python.sh | sed 's/^/      /'`
    owner: root:root
    path: /root/bin/build_python.sh
    permissions: '0750'
  - encoding: b64
    content: |
`base64 .deploy/init_aws.sh | sed 's/^/      /'`
    owner: root:root
    path: /tmp/init_aws.sh
    permissions: '0750'
  - encoding: b64
    content: |
`sed -e "s/\\\$HOST/${HOST}/g" -e "s/\\\$ROOTMAIL/${ROOTMAIL}/g" -e "s/\\\$MAILHUB/${MAILHUB}/g" -e "s/\\\$AUTHUSER/${AUTHUSER}/g" -e "s/\\\$AUTHPASS/${AUTHPASS}/g" .deploy/init_exim.sh | base64 | sed -e 's/^/      /'`
    owner: root:root
    path: /tmp/init_exim.sh
    permissions: '0750'
  - encoding: b64
    content: |
`base64 .deploy/create_user.sh | sed 's/^/      /'`
    owner: root:root
    path: /root/bin/create_user.sh
    permissions: '0750'
  - encoding: b64
    content : |
`base64 .deploy/rsyslog_django.conf | sed 's/^/      /'`
    owner: root:root
    path: /etc/rsyslog.d/90-django.conf
    permissions: '0644'
  - encoding: b64
    content : |
`base64 .deploy/logrotate_django | sed 's/^/      /'`
    owner: root:root
    path: /etc/logrotate.d/django
    permissions: '0644'
  - encoding: b64
    content : |
`base64 .deploy/logrotate_nginx | sed 's/^/      /'`
    owner: root:root
    path: /etc/logrotate.d/nginx
    permissions: '0644'
  - encoding: b64
    content : |
`base64 .deploy/log_upload | sed 's/^/      /'`
    owner: root:root
    path: /etc/cron.daily/logrotate_upload
    permissions: '0755'
  - encoding: b64
    content : |
`base64 .deploy/git-hook-checkout | sed 's/^/      /'`
    owner: root:root
    path: /usr/local/bin/git-hook-checkout
    permissions: '0755'
  - encoding: b64
    content: |
`base64 .deploy/profile | sed 's/^/      /'`
    owner: root:root
    path: /etc/skel/.profile
    permissions: '0644'

runcmd:
  - [ sh, -c, '/bin/sed -i "s/^# en_AU/en_AU/" /etc/locale.gen && /usr/sbin/locale-gen' ]
  - [ sh, -c, '/bin/echo -e "server {\n    listen [::]:80 default_server ipv6only=off;\n}" >/etc/nginx/sites-available/default' ]
  - [ sh, -c, '/bin/echo "include /srv/django/*/project/.nginx.conf;" >/etc/nginx/conf.d/django.conf' ]
  - [ sh, -c, '/bin/echo "server_tokens off;" >/etc/nginx/conf.d/00_server_tokens.conf' ]
  - [ sh, -c, '((/usr/bin/curl -s https://www.cloudflare.com/ips-v4; /bin/echo; /usr/bin/curl -s https://www.cloudflare.com/ips-v6; /bin/echo) | sed -e "s/^/set_real_ip_from /" -e "s/$/;/"; /bin/echo "real_ip_header X-Forwarded-For;"; /bin/echo "real_ip_recursive on;") >/etc/nginx/conf.d/00_real_ip.conf' ]
  - [ /tmp/init_django.sh, xvdb, '9.1', /srv/django ]
  - [ /root/bin/build_python.sh, '3.4.2' ]
  - [ /tmp/init_aws.sh ]
  - [ /tmp/init_exim.sh ]
  - [ cp, -r, /home/admin/.ssh, /etc/skel/.ssh ]
  - [ sh, -c, 'echo "Australia/Brisbane" > /etc/timezone && dpkg-reconfigure -f noninteractive tzdata' ]
  - [ sh, -c, 'echo "Deployment of ${HOST} complete" | mail -s "Deployment complete" root' ]

power_state:
  mode: reboot

CLOUDCONFIG
