import sys
from pathlib import Path

import semantic_version
from git import GitError, Repo


def get_version(check_migrations=False):
    try:
        repo = Repo()

        version, rev, commit = repo.git.describe("--tags", "--long").rsplit("-", 2)

        if rev == "0":
            return str(semantic_version.Version(version))

        if repo.active_branch.name.startswith("master"):
            local = ""
        else:
            local = "+" + repo.active_branch.name + "." + commit
        if version.count(".") == 1:
            version += ".0"
        version = semantic_version.Version(version + "-r" + rev + local)

        if check_migrations and any(
            map(
                lambda p: "migrations" in Path(p.a_path).parts,
                sorted(repo.tags, key=lambda t: t.commit.committed_date)[-1].commit.diff().iter_change_type("A"),
            )
        ):
            print(f"Migrations added, so a minor release is required: {version.next_minor()}", file=sys.stderr)

        return str(version)
    except GitError:
        sys.path.append(".")

        import upperroom  # pylint: disable=import-outside-toplevel

        return upperroom.__version__


def update_version(version=None):
    from tomlkit import dumps, loads  # pylint: disable=import-outside-toplevel

    with open("pyproject.toml", "r", encoding="utf-8") as config_file:
        config = loads(config_file.read())
    config["tool"]["poetry"]["version"] = version or get_version()
    with open("pyproject.toml", "w", encoding="utf-8") as config_file:
        config_file.write(dumps(config))

    return config["tool"]["poetry"]["version"]


if __name__ == "__main__":
    print(get_version(check_migrations="--check-migrations" in sys.argv))
