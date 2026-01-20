.PHONY: lint test check testvideos clean-testvideos benchmark examples clean-examples

lint:
	uv run isort --check-only src tests
	uv run flake8 src tests
	uv run basedpyright src tests

test:
	uv run pytest tests/ --verbose --ignore=tests/benchmarks/

test-all:
	uv run pytest tests/ --verbose

check: lint test

# Run performance benchmark (single consolidated suite)
benchmark:
	TRDROP_PROFILE=benchmark_results.csv uv run pytest tests/benchmarks/ -v -s

# Generate visual examples for manual confirmation (not part of test suite)
examples:
	uv run python -m tests.examples.generate_examples

clean-examples:
	rm -rf examples/generated/

testvideos:
	uv run python -m tests.generate_test_videos

clean-testvideos:
	rm -rf tests/videos
