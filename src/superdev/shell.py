import os
from contextlib import contextmanager
from subprocess import CalledProcessError, check_output


class Shell:
    @classmethod
    @contextmanager
    def in_dir(cls, base_dir):
        pwd = os.getcwd()
        os.chdir(base_dir)

        try:
            yield
        finally:
            os.chdir(pwd)

    @classmethod
    def run_in_dir(cls, base_dir, commands, env=None):
        with cls.in_dir(base_dir):
            return check_output(" ".join(commands), shell=True, env=env)


class GitException(ChildProcessError):
    pass


class Git:
    @classmethod
    def clone(cls, base_dir, git_location):
        return Shell.run_in_dir(base_dir, ["git", "clone", git_location])

    @classmethod
    def checkout(cls, base_dir, branch="master"):
        return Shell.run_in_dir(base_dir, ["git", "checkout", branch])

    @classmethod
    def fast_forward(cls, base_dir):
        try:
            return Shell.run_in_dir(base_dir, ["git", "pull", "--ff-only"])
        except CalledProcessError as e:
            raise GitException(*e.args) from e

    @classmethod
    def is_clean(cls, base_dir):
        return not Shell.run_in_dir(base_dir, ["git", "status", "--porcelain"])

    @classmethod
    def get_branch(cls, base_dir):
        branch = Shell.run_in_dir(
            base_dir, ["git", "rev-parse", "--abbrev-ref", "HEAD"]
        )

        return branch.decode("utf-8").strip()
