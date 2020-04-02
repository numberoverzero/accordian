SHELL := /bin/bash
.PHONY: cov publish venv

cov:
	source .venv/bin/activate && tox -- -vv

venv:
	python3.8 -m venv --copies .venv
	source .venv/bin/activate && pip install -U pip -q
	source .venv/bin/activate && pip install -r requirements.txt -q

publish:
	- rm -fr build dist .egg accordian.egg-info
	python setup.py sdist bdist_wheel
	twine check dist/*
	twine upload dist/*
