import bz2
import io
import logging
import os
import sys

import awscli.clidriver
import boto3
from django import setup
from django.conf import settings
from django.core.management import call_command


def import_file_env():
    for arg, value in os.environ.items():
        if arg.endswith("_FILE"):
            try:
                with open(value, "r") as argfile:
                    os.environ[arg[:-5]] = argfile.read().strip()
            except FileNotFoundError:
                continue
            del os.environ[arg]


def file_env(func):
    def wrapper(*args, **kwargs):
        import_file_env()
        func(*args, **kwargs)

    return wrapper


@file_env
def backup():
    logger = logging.getLogger(__name__ + ".backup")

    setup()

    try:
        media_bucket = settings.MEDIAFILES_BUCKET
        backup_bucket = settings.BACKUP_BUCKET
    except AttributeError:
        logger.debug("No buckets defined")
        sys.exit(1)

    s3_client = boto3.client("s3")

    with io.TextIOWrapper(io.BytesIO(), encoding="utf8") as data_buffer:
        call_command("dumpdata", "--all", stdout=data_buffer)
        data_buffer.seek(0)
        comp = bz2.compress(bytes(data_buffer.read(), data_buffer.encoding))
    with io.BytesIO(comp) as data_buffer:
        s3_client.upload_fileobj(data_buffer, backup_bucket, "data_test.json.bz2")

    awscli.clidriver.create_clidriver().main(
        args=["s3", "sync", "s3://%s/" % media_bucket, "s3://%s/media/" % backup_bucket, "--quiet", "--delete"]
    )


@file_env
def restore():
    logger = logging.getLogger(__name__ + ".restore")

    setup()

    try:
        media_bucket = settings.MEDIAFILES_BUCKET
        backup_bucket = settings.BACKUP_BUCKET
    except AttributeError:
        logger.debug("No buckets defined")
        sys.exit(1)

    awscli.clidriver.create_clidriver().main(
        args=["s3", "sync", "s3://%s/media/" % backup_bucket, "s3://%s/" % media_bucket, "--quiet", "--delete"]
    )

    s3_client = boto3.client("s3")

    with io.BytesIO() as data_buffer:
        s3_client.download_fileobj(backup_bucket, "data_test.json.bz2", data_buffer)
        decomp = bz2.decompress(data_buffer.getvalue())
    call_command("migrate", verbosity=0, interactive=False)
    call_command("flush", verbosity=0, interactive=False, inhibit_post_migrate=True)
    with io.BytesIO(decomp) as data_buffer:
        sys.stdin = io.TextIOWrapper(data_buffer)  # hack
        call_command("loaddata", "--format", "json", "-")


@file_env
def sendrosteremails():
    setup()
    call_command("sendrosteremails")


@file_env
def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "thepoint.settings")

    from django.core.management import execute_from_command_line  # pylint: disable=import-outside-toplevel

    execute_from_command_line(sys.argv)
