.PHONY: lint test check testvideos clean-testvideos

lint:
	uv run isort --check-only src tests
	uv run flake8 src tests
	uv run basedpyright src tests

test:
	uv run pytest tests/ --verbose

check: lint test

testvideos:
	uv run python -m tests.generate_test_videos

clean-testvideos:
	rm -rf tests/videos
