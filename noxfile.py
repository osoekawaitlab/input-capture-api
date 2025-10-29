"""Nox configuration file for input_capture_api project."""

import nox

nox.options.default_venv_backend = "uv"


@nox.session(python="3.12")
def tests(session: nox.Session) -> None:
    """Run tests."""
    session.install("-e", ".", "--group=dev")
    session.run("pytest", "tests/", "-v")


@nox.session(python="3.12")
def mypy(session: nox.Session) -> None:
    """Run mypy type checking (requires Azure SDK for type stubs)."""
    session.install("-e", ".", "--group=dev")
    session.run("mypy", "src/", "tests/")


@nox.session(python="3.12")
def lint(session: nox.Session) -> None:
    """Run ruff linting."""
    session.install("-e", ".", "--group=dev")
    session.run("ruff", "check", ".")


@nox.session(python="3.12")
def format_code(session: nox.Session) -> None:
    """Run ruff formatting."""
    session.install("-e", ".", "--group=dev")
    session.run("ruff", "format", ".")


@nox.session(python="3.12")
def quality(session: nox.Session) -> None:
    """Run all code quality checks (mypy, ruff)."""
    session.install("-e", ".", "--group=dev")
    session.run("mypy", "src/", "tests/")
    session.run("ruff", "check", ".")


@nox.session(python="3.12")
def check_all(session: nox.Session) -> None:
    """Run all checks and tests."""
    session.install("-e", ".", "--group=dev")
    session.run("pytest")
    session.run("mypy", "src/", "tests/")
    session.run("ruff", "check", ".")
