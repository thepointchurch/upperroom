import subprocess


def get_version():
    try:
        branch = subprocess.check_output(("git", "rev-parse", "--abbrev-ref", "HEAD")).strip().decode()
        long_version = subprocess.check_output(("git", "describe", "--tags", "--long")).strip().decode()
        version, rev, commit = long_version.rsplit("-", 2)
        if rev == "0":
            return version

        if branch.startswith("master"):
            local = ""
        else:
            local = "+" + branch + "." + commit
        if version.count(".") == 1:
            version += ".0"
        return version + "-r" + rev + local
    except (ImportError, OSError, subprocess.CalledProcessError):
        import sys  # pylint: disable=import-outside-toplevel

        sys.path.append(".")

        import thepoint  # pylint: disable=import-outside-toplevel

        return thepoint.__version__


def update_version(version=None):
    from tomlkit import dumps, loads  # pylint: disable=import-outside-toplevel

    with open("pyproject.toml") as config_file:
        config = loads(config_file.read())
    config["tool"]["poetry"]["version"] = version or get_version()
    with open("pyproject.toml", "w") as config_file:
        config_file.write(dumps(config))

    return config["tool"]["poetry"]["version"]


if __name__ == "__main__":
    print(get_version())
