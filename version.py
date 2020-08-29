import subprocess


def get_version():
    try:
        branch = subprocess.check_output(("git", "rev-parse", "--abbrev-ref", "HEAD")).strip().decode()
        long_version = subprocess.check_output(("git", "describe", "--tags", "--long")).strip().decode()
        version, rev, _ = long_version.rsplit("-", 2)
        if rev == "0":
            return version
        if branch.startswith("master"):
            if version.count(".") == 1:
                return version + ".0-r" + rev
            return version + "-r" + rev
        return long_version
    except (ImportError, OSError, subprocess.CalledProcessError):
        import sys  # pylint: disable=import-outside-toplevel

        sys.path.append(".")
        import thepoint  # pylint: disable=import-outside-toplevel

        return thepoint.__version__


def update_version():
    version = get_version()
    subprocess.check_call(("sed", "-i", "s/^__version__ = .*$/__version__ = '%s'/" % version, "thepoint/__init__.py"))


if __name__ == "__main__":
    print(get_version())
