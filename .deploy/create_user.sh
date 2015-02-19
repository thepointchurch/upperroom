#/bin/sh

# create_user.sh thepoint 'The Point Production'
# create_user.sh thepoint_test 'The Point Testing' testing

user=${1?No username specified}
description=${2?No description specified}
environment=${3-production}

adduser --gecos "${description}" --disabled-password --home "/srv/django/${user}" ${user}
su -c "createuser -wDRS ${user}; createdb -O ${user} ${user}" postgres
su -c "git init --bare '/srv/django/${user}/git' && \
       echo '${description}' >'/srv/django/${user}/git/description' && \
       cp /usr/local/bin/git-hook-checkout /srv/django/${user}/git/hooks/post-receive && \
       chmod 755 '/srv/django/${user}/git/hooks/post-receive' && \
       mkdir '/srv/django/${user}/project' '/srv/django/${user}/service' && \
       ln -s .env_${environment} '/srv/django/${user}/project/.env'" $user
mkdir "/etc/sv/user_${user}" && cat >"/etc/sv/user_${user}/run" <<SERVICE
#!/bin/sh
RUNAS='${user}'
exec 2>&1
exec chpst -u"\${RUNAS}" runsvdir "/srv/django/\${RUNAS}/service"
SERVICE
chmod 755 "/etc/sv/user_${user}/run" && ln -s "/etc/sv/user_${user}" "/etc/service/user_${user}"
