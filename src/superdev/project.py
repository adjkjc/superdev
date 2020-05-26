"""Manipulate and update H git repositories."""

import json
import os
from multiprocessing import Pool, cpu_count
from time import sleep

import pkg_resources
from colorama import Fore, Style, init

from superdev.shell import Git, ShellException, Tox


class Project:
    """Prepare and update a single git project."""

    def __init__(self, base_dir, name, git_url, **kwargs):
        self.base_dir = base_dir
        self.name = name
        self.git_location = git_url
        self.services = kwargs.get("services")
        self.tox_init = kwargs.get("tox_init")

    @property
    def path(self):
        """Return the path on the disk where this project is located."""
        return os.path.join(self.base_dir, self.name)

    @property
    def exists(self):
        """Determine if the project exists on the disk."""
        return os.path.exists(self.path)

    def initialise(self):
        """Get the project ready to work.

        This will clone if necessary and update if possible.
        """
        try:
            status = self._initialise()

        except ShellException as err:
            self._report(f"Failed with error: {err}")
            status = False, f"Unhandled exception: {err.__class__.__name__}:{err}"

        return self.name, status, self._get_branch()

    def _initialise(self):
        status = self._update_repo()
        status = self._update_tox(status)
        self._report("Complete")

        return status

    def _update_tox(self, status):
        try:  # pylint:disable=too-many-try-statements
            if self.tox_init:
                for env in self.tox_init:
                    self._report(f"Initialising tox env '{env}'...")
                    Tox.run(self.path, env, ["--notest"])

        except ShellException:
            return False, f"Tox prep failed for '{env}'"

        return status

    def _update_repo(self):
        if not self.exists:
            self._report("Cloning...")
            Git.clone(self.base_dir, self.git_location)
            return True, "Cloned"

        if Git.is_clean(self.path):
            self._report("Updating...")
            try:
                Git.fast_forward(self.path)

            except ShellException:
                self._report("UPDATE FAILED, CANNOT FAST FORWARD (skipping update)")
                return False, "Could not fast-forward"

            return True, "Updated"

        self._report("UNCOMMITTED CHANGES (skipping update)")
        return False, "Uncommitted changes"

    def _report(self, string):
        print(f"[{self.name}]".ljust(10) + " " + string)

    def _get_branch(self):
        try:
            return Git.get_branch(self.path)
        except ShellException:
            return "?????"


class ProjectManager:
    """Manage all H projects at once."""

    # pylint: disable=too-few-public-methods

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
        """Prepare all projects for work, in parallel."""

        # Work on the projects in parallel
        results = Pool(cpu_count()).map(self._prep_project, self.projects.values())

        all_good = self._print_results(results)

        if not all_good:
            self._issue_warning_countdown()

    # pylint: disable=no-self-use
    def _prep_project(self, project):
        return project.initialise()

    @staticmethod
    def _print_results(results):
        init()  # Initialise colourisation
        print()

        all_good = True

        for project, (success, status), branch in results:
            output = project.ljust(10)
            branch_string = f"({branch})".ljust(30)

            if branch == "master":
                output += branch_string
            else:
                output += f"{Fore.YELLOW}{branch_string}{Style.RESET_ALL}"

            if success:
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
