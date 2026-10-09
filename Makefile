.PHONY: lint test test-gui check testvideos clean-testvideos benchmark examples clean-examples clean

lint:
	uv run isort --check-only src tests
	uv run flake8 src tests
	uv run basedpyright src tests

test:
	uv run pytest tests/ --verbose -m "not gui" --ignore=tests/benchmarks/

test-gui:
	uv run pytest tests/ --verbose -m "gui"

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

# Clean all generated artifacts
clean: clean-examples clean-testvideos
	rm -rf benchmark_results.csv benchmark_results.summary.txt
	rm -rf trdrop_profile.csv trdrop_profile.summary.txt
	rm -rf .pytest_cache
	rm -rf .coverage htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
