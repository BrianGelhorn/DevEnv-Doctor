import json
from pathlib import Path

import typer

from devenv_doctor.runner import (
    CheckResult,
    CheckRun,
    expand_check_groups,
    get_check_groups,
    run_checks,
)

app = typer.Typer(
    name="devenv-doctor",
    help="Analyze local Docker development environments.",
    add_completion=False,
    no_args_is_help=True,
)

DEFAULT_REPORT_FILENAME = "devenv-doctor-report.json"
SEVERITY_LEVELS = {"Critical", "Warning", "Recommendations"}


@app.callback()
def root() -> None:
    pass


def _resolve_report_path(project_path: Path, report_arg: str | None) -> Path:
    if report_arg is None:
        return project_path / DEFAULT_REPORT_FILENAME

    report_path = Path(report_arg)
    if report_path.is_absolute():
        return report_path
    if report_path.parent == Path("."):
        return project_path / report_path
    return report_path


def _resolve_compose_file(project_path: Path, compose: str | None) -> Path | None:
    if compose is None:
        return None

    compose_file = Path(compose)
    if not compose_file.is_absolute():
        compose_file = project_path / compose_file

    if not compose_file.is_file():
        typer.secho(
            f"Docker Compose file does not exist: {compose_file}",
            fg="red",
            err=True,
        )
        raise typer.Exit(code=2)

    return compose_file


def _write_report(
    report_path: Path,
    project_path: Path,
    run: CheckRun,
) -> None:
    if not report_path.parent.is_dir():
        typer.secho(
            f"Report path does not exist: {report_path.parent}",
            fg="red",
            err=True,
        )
        raise typer.Exit(code=2)

    report = {
        "project_path": str(project_path),
        "status": run.status,
        "exit_code": run.exit_code,
        "summary": {
            "total": run.total,
            "passed": run.passed,
            "failed": run.failed,
            "skipped": run.skipped,
        },
        "checks": [result.to_dict() for result in run.results],
        "errors": [
            {"check": result.name, "message": result.message}
            for result in run.results
            if _issue_severity(result) == "Critical"
        ],
        "warnings": [
            {"check": result.name, "message": result.message}
            for result in run.results
            if _issue_severity(result) == "Warning"
        ],
        "recommendations": [
            {"check": result.name, "message": result.message}
            for result in run.results
            if _issue_severity(result) == "Recommendations"
        ],
    }
    report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    typer.echo(f"Report written to {report_path}")


def _print_result_line(result: CheckResult) -> None:
    if result.ok:
        typer.secho(f"[PASS] {result.name}: {result.message}", fg="green")
    elif result.skipped:
        typer.echo(f"[SKIP] {result.name}: {result.message}")
    elif _issue_severity(result) == "Recommendations":
        typer.secho(
            f"[RECOMMENDATION] {result.name}: {result.message}",
            fg="blue",
        )
    elif _issue_severity(result) == "Warning":
        typer.secho(f"[WARN] {result.name}: {result.message}", fg="yellow")
    elif result.failed:
        typer.secho(f"[FAIL] {result.name}: {result.message}", fg="red")


def _issue_severity(result: CheckResult) -> str | None:
    if not result.failed:
        return None
    if result.severity == "Recommendation":
        return "Recommendations"
    if result.severity == "Warning":
        return "Warning"
    return "Critical"


def _filter_results_by_severity(
    results: list[CheckResult],
    selected_severities: set[str] | None,
) -> list[CheckResult]:
    if selected_severities is None:
        return results

    return [
        result
        for result in results
        if _issue_severity(result) in selected_severities
    ]


def _parse_only(only: str | None) -> set[str] | None:
    if only is None:
        return None

    selected_groups = {group.strip() for group in only.split(",")}
    selected_groups.discard("")
    available_groups = set(get_check_groups())
    invalid_groups = sorted(selected_groups - available_groups)

    if invalid_groups:
        typer.secho(
            f"Invalid check group(s): {', '.join(invalid_groups)}",
            fg="red",
            err=True,
        )
        raise typer.Exit(code=2)

    if not selected_groups:
        typer.secho("No check groups were provided for --only.", fg="red", err=True)
        raise typer.Exit(code=2)

    return expand_check_groups(selected_groups)


def _parse_severity(severity: str | None) -> set[str] | None:
    if severity is None:
        return None

    selected_severities = {level.strip() for level in severity.split(",")}
    selected_severities.discard("")
    invalid_severities = sorted(selected_severities - SEVERITY_LEVELS)

    if invalid_severities:
        typer.secho(
            f"Invalid severity level(s): {', '.join(invalid_severities)}",
            fg="red",
            err=True,
        )
        typer.secho(
            f"Accepted severity levels: {', '.join(sorted(SEVERITY_LEVELS))}",
            fg="red",
            err=True,
        )
        raise typer.Exit(code=2)

    if not selected_severities:
        typer.secho(
            "No severity levels were provided for --severity.",
            fg="red",
            err=True,
        )
        raise typer.Exit(code=2)

    return selected_severities


@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def check(
    ctx: typer.Context,
    project_path: Path = typer.Argument(
        ".",
        help="Project path to analyze.",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
    ),
    report: bool = typer.Option(
        False,
        "--report",
        help="Generate a JSON report. Optionally pass a report path after the flag.",
    ),
    only: str | None = typer.Option(
        None,
        "--only",
        help=(
            "Run only the comma-separated check groups provided: "
            "docker, network, env."
        ),
    ),
    compose: str | None = typer.Option(
        None,
        "--compose",
        help="Use a custom Docker Compose file path.",
    ),
    severity: str | None = typer.Option(
        None,
        "--severity",
        help=(
            "Display only the comma-separated issue severity levels provided: "
            "Critical, Warning, Recommendations."
        ),
    ),
) -> None:
    """Run the development environment checks."""
    report_path = _resolve_report_path(project_path, ctx.args[0] if ctx.args else None)
    selected_checks = _parse_only(only)
    selected_severities = _parse_severity(severity)
    compose_file = _resolve_compose_file(project_path, compose)

    if ctx.args and not report:
        typer.secho(f"Unexpected argument: {ctx.args[0]}", fg="red", err=True)
        raise typer.Exit(code=2)
    if len(ctx.args) > 1:
        typer.secho(f"Unexpected argument: {ctx.args[1]}", fg="red", err=True)
        raise typer.Exit(code=2)

    typer.echo(f"Checking {project_path}")
    run = run_checks(project_path, only=selected_checks, compose_file=compose_file)

    for result in _filter_results_by_severity(run.results, selected_severities):
        _print_result_line(result)

    typer.echo()
    typer.secho(f"Status: {run.status}", fg="green" if run.status == "Ready" else "red")
    typer.echo(
        f"Summary: {run.passed}/{run.total} passed, "
        f"{run.failed} failed, {run.skipped} skipped."
    )

    if report:
        _write_report(report_path, project_path, run)

    if run.failed:
        raise typer.Exit(code=1)
