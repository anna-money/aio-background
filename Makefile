all: deps lint test

deps:
	@python3 -m pip install --upgrade pip && pip3 install -r requirements-dev.txt

black:
	@black --line-length 120 aio_background tests

isort:
	@isort --line-length 120 --use-parentheses --multi-line 3 --combine-as --trailing-comma aio_background tests

mypy:
	@mypy --strict --ignore-missing-imports aio_background

flake8:
	@flake8 --max-line-length 120 --ignore C901,C812,E203,E704 --extend-ignore W503 aio_background tests

lint: black isort flake8 mypy

test:
	@python3 -m pytest -vv --rootdir tests .

pyenv:
	echo aio-background > .python-version && pyenv install -s 3.12 && pyenv virtualenv -f 3.12 aio-background

pyenv-delete:
	pyenv virtualenv-delete -f aio-background
