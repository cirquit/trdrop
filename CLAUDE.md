# Claude Code Project Guidelines

## Build Commands

Always use make commands instead of running uv/pytest/linters directly:

- `make lint` - Run all linters (isort, flake8, basedpyright)
- `make test` - Run unit tests (excludes benchmarks)
- `make test-all` - Run all tests including benchmarks
- `make check` - Run lint + test
- `make benchmark` - Run performance benchmarks
- `make examples` - Generate visual examples
- `make testvideos` - Generate test video files
- `make clean` - Remove all generated artifacts
