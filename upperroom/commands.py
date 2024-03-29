import sys

import environ
from django import setup
from django.core.management import call_command


def import_file_env():
    environ.Env.read_env(".env")
    for arg, value in environ.Env.ENVIRON.items():
        if arg.endswith("_FILE") and not arg.startswith("GIT_"):
            try:
                with open(value, "r", encoding="utf-8") as argfile:
                    environ.Env.ENVIRON[arg[:-5]] = argfile.read().strip()
            except FileNotFoundError:
                continue
            del environ.Env.ENVIRON[arg]


def file_env(func):
    def wrapper(*args, **kwargs):
        import_file_env()
        func(*args, **kwargs)

    return wrapper


@file_env
def sendrosteremails():
    setup()
    call_command("sendrosteremails")


@file_env
def restore_fixtures():
    setup()
    call_command("migrate", verbosity=0, interactive=False)
    call_command("flush", verbosity=0, interactive=False, inhibit_post_migrate=True)
    call_command("loaddata", "--format", "json", "-")


@file_env
def main():
    from django.core.management import execute_from_command_line  # pylint: disable=import-outside-toplevel

    execute_from_command_line(sys.argv)
