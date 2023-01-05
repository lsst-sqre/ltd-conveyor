.PHONY: init
init:
	pip install -e ".[dev]"
	pip install --upgrade tox pre-commit
	rm -rf .tox
	pre-commit install
