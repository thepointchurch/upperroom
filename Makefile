# Makefile

export ROOTMAIL ?= admin@thepoint.org.au

export APP_PATH ?= $(HOME)/project
export APP_ENVIRONMENT ?= $(APP_PATH)/.venv
export APP_MODULE ?= thepoint.wsgi
export APP_WORKERS ?= 3
export APP_THREADS ?= 12

export SECRET_KEY ?= $(shell openssl rand -base64 37 | cut -c -50)

export SVDIR = $(HOME)/service


all: install setup

install: .venv boto_fix environment .nginx.conf $(HOME)/service/django $(HOME)/.profile $(HOME)/git/hooks/post-receive

setup: migrate collectstatic

.venv: .venv/bin/activate
.venv/bin/activate: requirements.txt
	test -d .venv || /opt/python-3.4.2/bin/pyvenv .venv
	. .venv/bin/activate; pip install -Ur requirements.txt
	touch .venv/bin/activate

boto_fix: .deploy/boto_fix.patch .venv
	@grep -q "^                headers\['x-amz-security-token'\]" .venv/lib/python3.4/site-packages/boto/s3/connection.py || patch -p0 <$<

.env: .env_$(environment)
	test -L .env || ln -s .env_$(environment) .env

.env/%: | .env
	echo $($(notdir $@)) >$@

.env/VHOST:

environment: .env/APP_PATH .env/APP_ENVIRONMENT .env/APP_MODULE .env/APP_WORKERS .env/APP_THREADS .env/SECRET_KEY .env/SVDIR .env/VHOST

cron: crontab
	crontab $<

migrate: .venv
	.venv/bin/python manage.py migrate --noinput

collectstatic: .venv
	.venv/bin/python manage.py collectstatic --noinput

flush: .venv
	.venv/bin/python manage.py flush --noinput

sendrosteremails: .venv
	@.venv/bin/python manage.py sendrosteremails

.runit/run: .deploy/run.in .env/APP_PATH
	test -d .runit || mkdir .runit
	envsubst <$< >$@
	chmod 755 $@

$(HOME)/service/django: .runit/run
	test -L $@ || ln -s $(dir $(shell pwd)/$<) $@

reload: $(HOME)/service/django
	sv reload django

backup: .venv
	@.venv/bin/python manage.py dumpdata --indent=2 --exclude auth.permission --exclude contenttypes | bzip2 | .venv/bin/aws s3 cp - "s3://$(BACKUP_BUCKET)/data.json.bz2" --quiet
	@.venv/bin/aws s3 sync "s3://$(MEDIAFILES_BUCKET)/" "s3://$(BACKUP_BUCKET)/media/" --quiet --delete

restore: migrate flush all
	@.venv/bin/aws s3 sync "s3://$(BACKUP_BUCKET)/media/" "s3://$(MEDIAFILES_BUCKET)/" --quiet --delete
	@.venv/bin/aws s3 cp "s3://$(BACKUP_BUCKET)/data.json.bz2" - --quiet | bunzip2 >/tmp/data.json
	@.venv/bin/python manage.py loaddata /tmp/data.json
	@rm -f /tmp/data.json

.nginx.conf: .deploy/nginx.conf.in .env/VHOST
	sed -e 's,$$HOME,$(HOME),g' -e 's/$$VHOST/$(VHOST)/g' $< >$@

$(HOME)/.profile: .deploy/profile
	cp $< $@ && chmod 755 $@

$(HOME)/git/hooks/post-receive: .deploy/git-hook-checkout
	cp $< $@

user-data: .deploy/user-data.sh .deploy/20auto-upgrades .deploy/50unattended-upgrades .deploy/init_django.sh .deploy/build_python.sh .deploy/init_aws.sh .deploy/init_exim.sh .deploy/create_user.sh .deploy/user-data.sh .deploy/git-hook-checkout .deploy/profile
	@test "$(HOST)" != '' || (echo No HOST defined; /bin/false)
	@test "$(MAILHUB)" != '' || (echo No MAILHUB defined; /bin/false)
	@test "$(AUTHUSER)" != '' || (echo No AUTHUSER defined; /bin/false)
	@test "$(AUTHPASS)" != '' || (echo No AUTHPASS defined; /bin/false)
	sh $< | gzip >$@

user-data.iso: user-data
	cloud-localds $@ $<
