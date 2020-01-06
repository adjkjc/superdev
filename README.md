# h-supervisor-dev

A development environment for Hypothesis based on Supervisor

Usage
-----

To start the services:

  * `make dev`

To monitor and control them:

  * Use the web-interface at http://localhost:9001
  * ... or run `supervisorctl`

Caveats
-------

 * H dev services have a tendency to stay up when stopped and in general are a 
   pain as a result of being run through honcho, instead of Supervisor
 * To fix you can try:
   * Celerybeat: `rm projects/h/celerybeat.pid`
   * If all else fails reboot or run `make dev` in `h/projects` and debug manually

Hacking
-------

### Installing h-supervisor-dev in a development environment

#### You will need

* [Git](https://git-scm.com/)

* [pyenv](https://github.com/pyenv/pyenv)
  Follow the instructions in the pyenv README to install it.
  The Homebrew method works best on macOS.
  On Ubuntu follow the Basic GitHub Checkout method.

#### Clone the git repo

```terminal
git clone https://github.com/hypothesis/h-supervisor-dev.git
```

This will download the code into a `h-supervisor-dev` directory
in your current working directory. You need to be in the
`h-supervisor-dev` directory for the rest of the installation
process:

```terminal
cd h-supervisor-dev
```

#### Run the tests

```terminal
make test
```

**That's it!** You’ve finished setting up your h-supervisor-dev
development environment. Run `make help` to see all the commands that're
available for linting, code formatting, packaging, etc.

### Updating the Cookiecutter scaffolding

This project was created from the
https://github.com/hypothesis/h-cookiecutter-pypackage/ template.
If h-cookiecutter-pypackage itself has changed since this project was created, and
you want to update this project with the latest changes, you can "replay" the
cookiecutter over this project. Run:

```terminal
make template
```

**This will change the files in your working tree**, applying the latest
updates from the h-cookiecutter-pypackage template. Inspect and test the
changes, do any fixups that are needed, and then commit them to git and send a
pull request.

If you want `make template` to skip certain files, never changing them, add
these files to `"options.disable_replay"` in
[`.cookiecutter.json`](.cookiecutter.json) and commit that to git.

If you want `make template` to update a file that's listed in `disable_replay`
simply delete that file and then run `make template`, it'll recreate the file
for you.
