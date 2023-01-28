.PHONY: test build

test:
	source venv/bin/activate && python tests/manage.py test test_app

ci_test:
	export PYTHONPATH=$PYTHONPATH:$(pwd) && python tests/manage.py test test_app

build:
	python3 setup.py sdist bdist_wheel
	twine check dist/*

install:
	source env/bin/activate && pip install -e .