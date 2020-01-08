# superdev

A complete development environment for Hypothesis based on Supervisor

Usage
-----

To start the services:

  * `make dev` (slow the first time)

To monitor and control them:

  * Use the web-interface at http://localhost:9001
  * Take a look in `logs/`
  * ... or run `supervisorctl`

### It's kind of normal for things to fail (sometimes)

Supervisor doesn't really have a concept of things depending on each other. So 
we just run them all at once, and retry until they work. Some items are one-shot
things so you can expect:

 * Items which run once and stop are expected to end in `Exited`
 * Things should never end in `Fatal`
 * While services and other build steps are taking place, many things will 
   restart again and again
 * Just because something is `Running` doesn't mean it's happy
   * Many of our items are separately managing tasks (which could be failing)
   * Look at the uptime or logs to see things are actually ok
 

Using this in development
-------------------------

A clean checkout is made of all projects from `master` and all services 
are started for all projects.

If you want to use locally developed code instead, you should stop the
relevant services (using the Web UI or `supervisorctl`) and then run your 
version in their place.

Caveats
-------

 * H dev services have a tendency to stay up when stopped and in general are a 
   pain as a result of being run through honcho, instead of Supervisor
 * To fix you can try:
   * Celerybeat: `rm projects/h/celerybeat.pid`
   * If all else fails reboot or run `make dev` in `h/projects` and debug manually

Hacking
-------

### Installing superdev in a development environment

#### You will need

* [Git](https://git-scm.com/)

* [pyenv](https://github.com/pyenv/pyenv)
  Follow the instructions in the pyenv README to install it.
  The Homebrew method works best on macOS.
  On Ubuntu follow the Basic GitHub Checkout method.

#### Clone the git repo

```terminal
git clone https://github.com/hypothesis/superdev.git
```

This will download the code into a `superdev` directory
in your current working directory. You need to be in the
`superdev` directory for the rest of the installation
process:

```terminal
cd superdev
```

#### Run the tests

```terminal
make test
```

**That's it!** You’ve finished setting up your superdev
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
