.PHONY: test build

test:
	source env/bin/activate && python tests/manage.py test test_app

build:
	python3 setup.py sdist bdist_wheel
	twine check dist/*

install:
	source env/bin/activate && pip install -e .