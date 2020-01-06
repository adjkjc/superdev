from contextlib import contextmanager
from subprocess import check_output
import os


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
            return check_output(' '.join(commands), shell=True, env=env)


class Git:
    @classmethod
    def clone(cls, base_dir, git_location):
        return Shell.run_in_dir(base_dir, ['git', 'clone', git_location])

    @classmethod
    def checkout(cls, base_dir, branch='master'):
        return Shell.run_in_dir(base_dir, ['git', 'checkout', branch])

    @classmethod
    def pull(cls, base_dir):
        return Shell.run_in_dir(base_dir, ['git', 'pull'])

    @classmethod
    def reset_head(cls, base_dir):
        return Shell.run_in_dir(base_dir, ['git', 'reset', 'HEAD', '--hard'])
