.PHONY: help
help:
	@echo "make dev               Run the development services"
	@echo "make control           Drop into an interactive shell to manage services"
	@echo "make monitor           Display basic information about running services"
	@echo "make help              Show this help message"
	@echo "make lint              Code quality analysis (pylint)"
	@echo "make format            Correctly format the code"
	@echo "make checkformatting   Crash if the code isn't correctly formatted"
	@echo "make dist              Create package in the dist/ directory for local testing"
	@echo "make release           Tag a release and trigger deployment to PyPI"
	@echo "make initialrelease    Create the first release of a package"
	@echo "make test              Run the unit tests"
	@echo "make coverage          Print the unit test coverage report"
	@echo "make clean             Delete development artefacts (cached files, "
	@echo "                       dependencies, etc)"
	@echo "make template          Replay the cookiecutter project template over this"
	@echo "                       project. Warning! This can destroy changes."

.PHONY: dev
dev: python projects
	@echo "Web interface at: http://localhost:9001"
	# This looks daft, but is required to prevent some strangeness with
	# the path when running sub-processes which caused them to pick up
	# tox (and maybe more) from our virtual env, instead of the right
	# pyenv
	@.tox/dev/bin/supervisord --nodaemon --configuration conf/supervisord.conf

.PHONY: control
control:
	@tox -qe dev --run-command supervisorctl

.PHONY: monitor
monitor:
	@watch --color -n 5 ./bin/monitor

.PHONY: projects
projects: python
	@tox -qe dev --run-command "python bin/initialise_projects.py"

.PHONY: lint
lint: python
	@tox -qe lint

.PHONY: format
format: python
	@tox -qe format

.PHONY: checkformatting
checkformatting: python
	@tox -qe checkformatting

.PHONY: dist
dist: python
	@BUILD=$(BUILD) tox -qe dist

.PHONY: release
release: python
	@tox -qe release

.PHONY: initialrelease
initialrelease: python
	@tox -qe initialrelease

.PHONY: test
test: python
	@tox -q

.PHONY: coverage
coverage: python
	@tox -qe coverage

.PHONY: template
template: python
	@tox -qe replay-cookiecutter

.PHONY: clean
clean:
	@find . -type f -name "*.py[co]" -delete
	@find . -type d -name "__pycache__" -delete
	@rm -rf build .eggs dist *.egg-info src/*.egg-info .coverage.* .coverage .pytest_cache

.PHONY: python
python:
	@./bin/install-python.sh
