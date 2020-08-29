import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "thepoint.settings")

    from django.core.management import execute_from_command_line  # pylint: disable=import-outside-toplevel

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
