"""Wrappers for various shell commands."""
# pylint: disable=too-few-public-methods

import os
from contextlib import contextmanager
from subprocess import CalledProcessError, check_output


class ShellException(ChildProcessError):
    """Any error encountered during a shell operation."""


class Shell:
    """Perform arbitrary shell commands in a directory."""

    @classmethod
    def run_in_dir(cls, base_dir, commands, env=None):
        """Run a command inside a directory and return the result.

        :param base_dir: The directory to run in
        :param commands: The parts of the command as a list
        :param env: A dict for environment variables
        :raise ShellException: If anything goes wrong
        :return: The output of the command
        """
        with cls._in_dir(base_dir):
            try:
                return check_output(" ".join(commands), shell=True, env=env)
            except CalledProcessError as err:
                raise ShellException(*err.args) from None

    @classmethod
    @contextmanager
    def _in_dir(cls, base_dir):
        pwd = os.getcwd()
        os.chdir(base_dir)

        try:
            yield
        finally:
            os.chdir(pwd)


class Tox:
    """Run tox commands.

    All items:

    :raise ShellException: If anything goes wrong
    """

    @classmethod
    def run(cls, base_dir, tox_env, options=None):
        """Run arbitrary tox commands in an environment.

        :param base_dir: The base directory to run in
        :param tox_env: The tox environment to run in
        :param options: List of options to add to the end of the command
        """
        tox_command = ["pyenv", "exec", "tox", "-e", tox_env]

        if options:
            tox_command.extend(options)

        Shell.run_in_dir(
            base_dir,
            tox_command,
            env=dict(os.environ, PYENV_DIR=os.path.abspath(base_dir)),
        )


class Git:
    """Perform various git actions in directories.

    All items:

    :raise ShellException: If anything goes wrong
    """

    @classmethod
    def clone(cls, base_dir, git_location):
        """Clone a repository.

        :param base_dir: The directory to run the command in
        :param git_location: The git URL to clone
        :return: Git command output
        """
        return cls._git(base_dir, "clone", git_location)

    @classmethod
    def checkout(cls, base_dir, branch="master"):
        """Checkout a particular branch in a repository.

        :param base_dir: The directory to run the command in
        :param branch: The branch to checkout
        :return: Git command output
        """
        return cls._git(base_dir, "checkout", branch)

    @classmethod
    def fast_forward(cls, base_dir):
        """Fast-forward the branch if possible.

        :param base_dir: The directory to run the command in
        :return: Git command output
        """
        return cls._git(base_dir, "pull", "--ff-only")

    @classmethod
    def is_clean(cls, base_dir):
        """Determine if the checkout is completely clean.

        No uncommitted changes and no untracked files.

        :param base_dir: The directory to run the command in
        :return: Git command output
        """
        return not cls._git(base_dir, "status", "--porcelain")

    @classmethod
    def get_branch(cls, base_dir):
        """Get the currently checked out branch.

        :param base_dir: The directory to run the command in
        :return: The branch name
        """

        return (
            cls._git(base_dir, "rev-parse", "--abbrev-ref", "HEAD")
            .decode("utf-8")
            .strip()
        )

    @classmethod
    def _git(cls, base_dir, *args):
        command = ["git"]
        command.extend(args)

        return Shell.run_in_dir(base_dir, command)
