import os

from superdev.project import ProjectManager

if __name__ == '__main__':
    project_dir = 'projects'

    if not os.path.isdir(project_dir):
        os.mkdir(project_dir)

    ProjectManager(project_dir).prepare_all()
