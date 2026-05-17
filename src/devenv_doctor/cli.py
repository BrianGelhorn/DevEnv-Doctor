from pathlib import Path

import typer

from devenv_doctor.checks.compose import (
    check_docker_compose_available,
    check_docker_compose_build_contexts,
    check_docker_compose_build_contexts_dockerfiles,
    check_docker_compose_duplicated_host_ports,
    check_docker_compose_file_exists,
    check_docker_compose_host_ports_available,
    check_docker_compose_services_section,
    check_docker_compose_valid_build_or_image,
    check_docker_compose_yaml_syntax,
)
from devenv_doctor.checks.compose_utils import has_build_services
from devenv_doctor.checks.docker import (
    check_docker_cli_installed,
    check_docker_daemon_accessible,
)
from devenv_doctor.checks.environment import check_env_example_exists, has_env_file

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
    project_path: Path = typer.Argument(
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
    checks = [
        ("Docker CLI", lambda: check_docker_cli_installed()),
        ("Docker daemon", lambda: check_docker_daemon_accessible()),
        ("Docker Compose", lambda: check_docker_compose_available()),
        ("Compose file", lambda: check_docker_compose_file_exists(project_path)),
        ("Compose YAML", lambda: check_docker_compose_yaml_syntax(project_path)),
        (
            "Compose services",
            lambda: check_docker_compose_services_section(project_path),
        ),
        (
            "Compose build",
            lambda: check_docker_compose_valid_build_or_image(project_path),
        ),
        (
            "Compose build contexts",
            lambda: check_docker_compose_build_contexts(project_path),
        ),
        (
            "Compose host ports",
            lambda: check_docker_compose_duplicated_host_ports(project_path),
        ),
        (
            "Host port availability",
            lambda: check_docker_compose_host_ports_available(project_path),
        ),
        (
            "Compose build context Dockerfiles",
            lambda: check_docker_compose_build_contexts_dockerfiles(project_path),
        ),
        (
            "Environment example",
            lambda: check_env_example_exists(project_path),
        ),
    ]

    typer.echo(f"Checking {project_path}")
    # TODO: Implement diferenciation of blocking, warning and recommended issue levels.
    passed = 0
    failed = 0
    docker_cli_available = True
    docker_compose_file_exists = True
    docker_compose_file_syntax_is_valid = True
    docker_compose_services_section_is_valid = True

    for name, run_check in checks:
        if name in {"Docker daemon", "Docker Compose"} and not docker_cli_available:
            failed += 1
            typer.echo(f"[FAIL] {name}: skipped because Docker CLI is not installed.")
            continue
        if name == "Compose YAML" and not docker_compose_file_exists:
            failed += 1
            typer.echo(f"[FAIL] {name}: skipped because Compose file was not found.")
            continue
        if (
            name
            in {
                "Compose services",
                "Compose build",
                "Compose build contexts",
                "Compose host ports",
                "Host port availability",
            }
            and not docker_compose_file_exists
        ):
            failed += 1
            typer.echo(f"[FAIL] {name}: skipped because Compose file was not found.")
            continue
        if (
            name
            in {
                "Compose services",
                "Compose build",
                "Compose build contexts",
                "Compose host ports",
                "Host port availability",
            }
            and not docker_compose_file_syntax_is_valid
        ):
            failed += 1
            typer.echo(f"[FAIL] {name}: skipped because Compose YAML is not valid.")
            continue
        if (
            name
            in {
                "Compose build",
                "Compose build contexts",
                "Compose host ports",
                "Host port availability",
            }
            and not docker_compose_services_section_is_valid
        ):
            failed += 1
            typer.echo(
                f"[FAIL] {name}: skipped because Compose services are not valid."
            )
            continue
        if name == "Compose build context Dockerfiles":
            if not docker_compose_file_exists:
                failed += 1
                typer.echo(
                    f"[FAIL] {name}: skipped because Compose file was not found."
                )
                continue
            if not docker_compose_file_syntax_is_valid:
                failed += 1
                typer.echo(f"[FAIL] {name}: skipped because Compose YAML is not valid.")
                continue
            if not docker_compose_services_section_is_valid:
                failed += 1
                typer.echo(
                    f"[FAIL] {name}: skipped because Compose services are not valid."
                )
                continue
            if not has_build_services(project_path):
                failed += 1
                typer.echo(
                    f"[FAIL] {name}: skipped because no service uses build."
                )
                continue
        if name == "Environment example" and not has_env_file(project_path):
            failed += 1
            typer.echo(f"[FAIL] {name}: skipped because .env file was not found.")
            continue

        ok, message = run_check()

        if name == "Docker CLI":
            docker_cli_available = ok

        if name == "Compose file":
            docker_compose_file_exists = ok

        if name == "Compose YAML":
            docker_compose_file_syntax_is_valid = ok

        if name == "Compose services":
            docker_compose_services_section_is_valid = ok

        if ok:
            passed += 1
            typer.secho(f"[PASS] {name}: {message}", fg="green")
        else:
            failed += 1
            typer.secho(f"[FAIL] {name}: {message}", fg="red")

    total = len(checks)
    status = "Ready" if failed == 0 else "Not Ready"

    typer.echo()
    typer.secho(f"Status: {status}", fg="green" if status == "Ready" else "red")
    typer.echo(f"Summary: {passed}/{total} passed, {failed} failed.")

    if failed:
        raise typer.Exit(code=1)
