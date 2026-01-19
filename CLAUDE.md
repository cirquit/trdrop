# Claude Code Project Guidelines

## Build Commands

Always use make commands instead of running uv/pytest/linters directly:

- `make lint` - Run all linters (isort, flake8, basedpyright)
- `make test` - Run all tests
- `make check` - Run lint + test
- `make testvideos` - Generate test video files
- `make clean-testvideos` - Remove test video files
