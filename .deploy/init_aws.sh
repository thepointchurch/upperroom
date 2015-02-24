#!/bin/sh

set -e

/opt/python/bin/pip3 install awscli boto

mkdir /root/.aws
/bin/echo -e "[default]\nregion = $(curl -s http://169.254.169.254/latest/dynamic/instance-identity/document | awk -F\" '/region/{print $4}')" >/root/.aws/config

cp -a /root/.aws /etc/skel/.aws