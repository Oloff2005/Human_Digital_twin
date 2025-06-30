.PHONY: test coverage

test:
	pytest

coverage:
	pytest --cov=hdt --cov-report html
	@echo "HTML report saved to htmlcov/index.html"
