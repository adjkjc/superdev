import json
import os
from os.path import expanduser
from time import sleep

import pkg_resources
from colorama import Fore, Style, init

from superdev.shell import Git, GitException, Shell


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

    def _report(self, string):
        print(f"[{self.name}]".ljust(10) + " " + string)

    def initialise(self):
        try:
            if not self.is_cloned:
                self._report("Cloning...")
                self.clone()
                status = True, "Cloned"

            elif Git.is_clean(self.path):
                self._report("Updating...")
                try:
                    Git.fast_forward(self.path)
                    status = True, "Updated"

                except GitException:
                    self._report("UPDATE FAILED, CANNOT FAST FORWARD (skipping update)")
                    status = False, "Could not fast-forward"

            else:
                self._report("UNCOMMITTED CHANGES (skipping update)")
                status = False, "Uncommitted changes"

            try:
                if self.tox_init:
                    for env in self.tox_init:
                        self._report(f"Initialising tox env '{env}'...")
                        self.tox(env, ["--notest"])

            except Exception:
                status = False, f"Tox prep failed for '{env}'"

            self._report("Complete")

        except Exception as e:
            self._report(f"Failed with error: {e}")
            status = False, "Unhandled exception"

        return self.name, status, self._get_branch()

    def _get_branch(self):
        try:
            return Git.get_branch(self.path)
        except Exception:
            return "?????"

    def clone(self):
        Git.clone(self.base_dir, self.git_location)

    def tox(self, tox_env, options=None):
        tox_command = ["pyenv", "exec", "tox", "-e", tox_env]

        if options:
            tox_command.extend(options)

        Shell.run_in_dir(
            self.path,
            tox_command,
            env=dict(os.environ, PYENV_DIR=os.path.abspath(self.path)),
        )

    def make(self, command):
        pyenv_dir = expanduser("~/.pyenv")

        env = dict(os.environ)
        env["PATH"] += f":{pyenv_dir}/shims:{pyenv_dir}/bin"
        env.update({"PYENV_DIR": os.path.abspath(self.path)})

        Shell.run_in_dir(self.path, ["make", command], env=env)


class ProjectManager:
    PROJECT_DATA = json.load(
        pkg_resources.resource_stream("superdev", "resource/git_projects.json")
    )

    def __init__(self, base_dir):
        self.base_dir = base_dir

        self.projects = {
            name: Project(base_dir, name, **data)
            for name, data in self.PROJECT_DATA.items()
        }

    def prepare_all(self):
        results = self._do_for_projects(self._prep_project)

        all_good = self._print_results(results)

        if not all_good:
            self._issue_warning_countdown()

    @staticmethod
    def _print_results(results):
        init()  # Initialise colourisation
        print()

        all_good = True

        for project, (ok, status), branch in results:
            output = project.ljust(10)
            branch_string = f"({branch})".ljust(30)

            if branch == "master":
                output += branch_string
            else:
                output += f"{Fore.YELLOW}{branch_string}{Style.RESET_ALL}"

            if ok:
                output += f" {Fore.GREEN} OK: {status}"
            else:
                output += f" {Fore.RED}ERR: {status}"
                all_good = False

            print(output + Style.RESET_ALL)

        print()

        return all_good

    @staticmethod
    def _issue_warning_countdown():
        for sec in range(10, 0, -1):
            print(
                f"{Fore.RED}Something above isn't right.{Style.RESET_ALL} Pausing {sec} \r",
                end="",
            )
            sleep(1)

    def _do_for_projects(self, function):
        from multiprocessing import Pool, cpu_count

        pool = Pool(cpu_count())
        return pool.map(function, self.projects.values())

    def _prep_project(self, project):
        return project.initialise()
