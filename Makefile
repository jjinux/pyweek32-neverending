PACKAGE=pw32n

# See http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: test
test:  ## Run tests
	python -m unittest discover -s ${PACKAGE} -p "*_test.py"

.PHONY: lint
lint: mypy  ## Run linters (mypy, etc.)

.PHONY: mypy
mypy:  ## Run mypy to check types
	mypy ${PACKAGE} --strict
