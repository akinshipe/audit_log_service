
TEST_OPTS ?=

test:
	@echo 'Running unit tests'
	pytest -s --cov=log_service --cov-report=term --cov-report=html:report/ --no-cov-on-fail \
		--junitxml report/xunit.xml $(TEST_OPTS)
	@echo "\nTo view the HTML coverage report: open report/htmlcov/index.html\n"
