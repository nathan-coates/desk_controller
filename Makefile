format:
	@ruff check --select I --fix .
	@ruff format .

check:
	@mypy .
	@ruff check .
	