cov:
	pytest  --cov=moonbag --cov-config=.coveragerc
tests:
	pytest -vv moonbag/tests
test-utils:
	pytest -vv moonbag\tests\utils
