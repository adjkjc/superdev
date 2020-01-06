import os
import json
import pkg_resources
from os.path import expanduser

from h_supervisor_dev.shell import Shell, Git


class Project:
    def __init__(self, base_dir, name, git_url, services=None, tox_init=None):
        self.base_dir = base_dir
        self.name = name
        self.git_location = git_url
        self.services = services
        self.tox_init = tox_init

    @property
    def path(self):
        return os.path.join(self.base_dir, self.name)

    @property
    def is_cloned(self):
        return os.path.exists(self.path)

    def initialise(self):
        if not self.is_cloned:
            print(f"Cloning '{self.name}'...")
            self.clone()
        else:
            print(f"Updating '{self.name}'...")
            self.update()

        if self.tox_init:
            for env in self.tox_init:
                print(f"Initialising '{self.name}' tox env '{env}'...")
                self.tox(env, '"python --version"')

    def update(self):
        Git.reset_head(self.path)
        Git.pull(self.path)

    def clone(self):
        Git.clone(self.base_dir, self.git_location)

    def tox(self, env, command=None):
        tox_command = ['tox', '-e', env]

        if command:
            tox_command.extend(['--run-command', command])

        Shell.run_in_dir(self.path, tox_command)

    def make(self, command):
        pyenv_dir = expanduser("~/.pyenv")

        env = dict(os.environ)
        env['PATH'] += f":{pyenv_dir}/shims:{pyenv_dir}/bin"
        env.update({
            "PYENV_SHELL": "bash",
            "PYENV_ROOT": pyenv_dir,
        })
        Shell.run_in_dir(self.path, ['make', command], env)


class ProjectManager:
    PROJECT_DATA = json.load(
        pkg_resources.resource_stream(
            'h_supervisor_dev', 'resource/git_projects.json'))

    def __init__(self, base_dir):
        self.base_dir = base_dir

        self.projects = {
            name: Project(base_dir, name, **data)
            for name, data in self.PROJECT_DATA.items()
        }

    def _prep_project(self, project):
        try:
            project.initialise()

            print(f"{project.name} complete")

        except Exception as e:
            print(f"Failed {project.name} with error: {e}")
            raise

    def _do_for_projects(self, function):
        from multiprocessing import Pool, cpu_count

        pool = Pool(cpu_count())
        pool.map(function, self.projects.values())

    def prepare_all(self):
        return self._do_for_projects(self._prep_project)