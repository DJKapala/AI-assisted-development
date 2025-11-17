# MCP Project — tests & helper utilities
![CI](https://github.com/DJKapala/AI-assisted-development/actions/workflows/ci.yml/badge.svg)
![coverage](https://img.shields.io/badge/coverage-unknown-lightgrey)

This repository contains a small MCP-powered test agent (`server.py`) and
pure-Python helpers extracted into `mcp_utils.py`. The project now includes
unit tests and coverage support so you can iterate quickly on logic without
installing native dependencies.

This README explains how to set up a local development environment on
Windows (PowerShell), run the test suite, produce coverage reports, and
prepare a branch/pr with your changes.

## Contents

- `server.py` — MCP server wiring and MCP tool wrappers. Import-safe when
	`fastmcp` is not installed so tests can import functions without native
	extensions.
- `mcp_utils.py` — pure-Python helper functions (testable): `add_numbers`,
	`run_cmd`, `coverage_analyzer`, `test_generator`.
- `tests/` — pytest unit tests added for helpers and server-level wrappers.

## Prerequisites

- Python 3.13+ is recommended (project pyproject.toml requires >=3.13).
- Git if you plan to create branches and push to a remote.

This guide uses PowerShell commands (your default shell). Adjust commands if
you prefer a different shell.

## Quick start (recommended)

1. Create a project-local virtual environment and activate it:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate
```

2. Upgrade pip and install test/runtime dependencies required for local
	 development. The project ships a minimal set of tests that only need
	 `pytest` and `pytest-cov` to run:

```powershell
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install pytest pytest-cov
```

3. Run the test suite (fast):

```powershell
.\.venv\Scripts\python -m pytest -q
```

4. Run tests with coverage and produce `coverage.xml`:

```powershell
.\.venv\Scripts\python -m pytest --cov=mcp_utils --cov=server --cov-report=term --cov-report=xml:coverage.xml
```

## Running the MCP server

The module `server.py` contains MCP wiring that relies on the `fastmcp`
package and its compiled dependencies (for example, `pydantic_core`). The
repository has been arranged so tests and pure-Python helpers work without
installing `fastmcp`.

To run the server in a real environment you will need to install `fastmcp`
and any platform-specific native wheels. If you have the correct
environment, start the server with:

```powershell
.\.venv\Scripts\python server.py
```

Note: if `fastmcp` is not installed, running `server.py` as above will raise
an AttributeError since `mcp` will be `None`. For local unit testing and
development you generally don't need to start the server — the tests exercise
the pure-Python logic and the MCP decorator is a no-op when `fastmcp` is
missing.

## Development notes

- Project helpers were moved into `mcp_utils.py` so they are easy to test
	and import without optional native dependencies.
- Tests are located in the `tests/` directory and use `pytest`.
- A virtualenv named `.venv` is used in examples to keep dependencies local.

## Committing and creating a PR (local flow)

1. Create and switch to a new branch:

```powershell
git checkout -b add-tests-and-coverage
```

2. Stage only the source and test files you changed (avoid adding `.venv`):

```powershell
git add server.py mcp_utils.py tests/
```

3. Commit and push the branch to your remote (replace `<remote-url>` with
	 your repository URL if `origin` is not configured):

```powershell
git commit -m "tests: extract helpers to mcp_utils and add unit tests + coverage"
git remote add origin <remote-url>        # only if you don't have origin
git push -u origin add-tests-and-coverage
```

4. (Optional) Create a GitHub PR using the `gh` CLI (if installed):

```powershell
gh pr create --fill --title "Add tests and coverage" --body "Add unit tests and extract pure-Python helpers to improve testability and coverage."
```

If `gh` is not installed you can open the PR from the repository web UI.

## Troubleshooting

- "No module named pytest": install the test deps in the virtualenv as shown
	in Quick start.
- Import errors referencing `pydantic_core` or `fastmcp`: those indicate
	native dependencies are missing; you can still run the unit tests because
	`server.py` is import-safe — tests exercise the pure-Python helpers.

## CI suggestions

- Add a GitHub Actions workflow that:
	- sets up Python 3.14 (or your target),
	- creates and activates a venv,
	- installs test dependencies (`pytest`, `pytest-cov`),
	- runs tests and uploads `coverage.xml` as an artifact or publishes
		coverage to a service.

If you'd like, I can add a ready-to-use `.github/workflows/ci.yml` that runs
tests and coverage on push/PR.

## Contact / contribution

If you want me to push the local branch and open a PR from this environment
I can do that — but the current repository does not have a configured `origin`
remote here, so I'll need a remote URL or you can push the branch yourself.

Happy to add the CI workflow or help with next tests — tell me which task to
do next.
