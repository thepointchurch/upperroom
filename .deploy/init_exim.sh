#!/bin/sh

sed -i -n -e '/^root: /b;p' /etc/aliases
echo 'root: $ROOTMAIL' >>/etc/aliases
newaliases

echo '*.amazonaws.com:$AUTHUSER:$AUTHPASS' >/etc/exim4/passwd.client

cat >/etc/exim4/update-exim4.conf.conf <<EXIM_CONF
dc_eximconfig_configtype='satellite'
dc_other_hostnames='$HOST.thepoint.org.au'
dc_local_interfaces='127.0.0.1 ; ::1'
dc_readhost='$HOST.thepoint.org.au'
dc_relay_domains=''
dc_minimaldns='false'
dc_relay_nets=''
dc_smarthost='$MAILHUB::587'
CFILEMODE='644'
dc_use_split_config='true'
dc_hide_mailname='true'
dc_mailname_in_oh='true'
dc_localdelivery='mail_spool'
EXIM_CONF

/usr/sbin/update-exim4.conf
