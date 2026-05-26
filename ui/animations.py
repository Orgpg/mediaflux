"""Small Rich animation helpers."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from rich.console import Console


@contextmanager
def loading(console: Console, message: str = "Working") -> Iterator[None]:
    """Show a spinner while a block of code runs."""
    with console.status(f"[bold cyan]{message}...[/bold cyan]", spinner="dots"):
        yield
