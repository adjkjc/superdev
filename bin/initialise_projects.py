"""Initialise all of the projects."""

import os

from superdev.project import ProjectManager

PROJECT_DIR = "../"

if __name__ == "__main__":
    if not os.path.isdir(PROJECT_DIR):
        os.mkdir(PROJECT_DIR)

    ProjectManager(PROJECT_DIR).prepare_all()
