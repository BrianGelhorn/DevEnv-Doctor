from pathlib import Path
from typing import Optional

import typer


app = typer.Typer(
    name="devenv-doctor",
    help="Analyze local Docker development environments.",
    add_completion=False,
    no_args_is_help=True,
)

@app.callback()
def root() -> None:
    pass

@app.command()
def check(
    project_path: Optional[Path] = typer.Argument(
        ".",
        help="Project path to analyze.",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
    ),
) -> None:
    """Run the development environment checks."""

    typer.echo(f"Running DevEnv Doctor checks on: {project_path}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
