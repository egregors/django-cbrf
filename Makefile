.DEFAULT_GOAL := help
.PHONY: test build

install:  ## Install this pkg in editable (develop) mode
	source venv/bin/activate && pip install -e .

test:  ## Run tests (venv)
	source venv/bin/activate && python tests/manage.py test test_app

ci_test:  ## Run tests in CI (GitHub actions)
	export PYTHONPATH=$PYTHONPATH:$(pwd) && python tests/manage.py test test_app

build:  ## Build package before publication
	python3 setup.py sdist bdist_wheel
	twine check dist/*

## Help

help: ## Show help message
	@IFS=$$'\n' ; \
	help_lines=(`fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##/:/'`); \
	printf "%s\n\n" "Usage: make [task]"; \
	printf "%-20s %s\n" "task" "help" ; \
	printf "%-20s %s\n" "------" "----" ; \
	for help_line in $${help_lines[@]}; do \
		IFS=$$':' ; \
		help_split=($$help_line) ; \
		help_command=`echo $${help_split[0]} | sed -e 's/^ *//' -e 's/ *$$//'` ; \
		help_info=`echo $${help_split[2]} | sed -e 's/^ *//' -e 's/ *$$//'` ; \
		printf '\033[36m'; \
		printf "%-20s %s" $$help_command ; \
		printf '\033[0m'; \
		printf "%s\n" $$help_info; \
	done
