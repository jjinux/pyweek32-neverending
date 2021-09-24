PACKAGE=pw32n

# See http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: run
run:  ## Run the game
	./run_game.py

.PHONY: test
test:  ## Run tests
	python -m unittest discover -s ${PACKAGE} -p "*_test.py"

.PHONY: lint
lint: lint_mypy lint_black  ## Run all the linters

.PHONY: lint_mypy
lint_mypy:  ## Run mypy to check types
	mypy ${PACKAGE} --strict --no-strict-optional

.PHONY: lint_black
lint_black:  ## Run black with --check to check the code formatting
	black --check .

.PHONY: lint_black_reformat
lint_black_reformat:  ## Run black and reformat the code
	black .

.PHONY: iterate
iterate: lint_black_reformat lint_mypy test run  ## Run lint_black_reformat, lint_mypy, test, and run

.PHONY: setup_githooks
setup_githooks:  ## Setup githooks
	rm -rf .git/hooks
	ln -sf ../hooks .git/hooks
