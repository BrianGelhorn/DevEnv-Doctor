from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

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
from devenv_doctor.checks.environment import (
    check_env_example_exists,
    check_env_variables_match,
    has_env_example_file,
    has_env_file,
)

CheckStatus = Literal["pass", "fail", "skip"]

CHECK_GROUPS = {
    "docker": {
        "Docker CLI",
        "Docker daemon",
        "Docker Compose",
        "Compose file",
        "Compose YAML",
        "Compose services",
        "Compose build",
        "Compose build contexts",
        "Compose build context Dockerfiles",
    },
    "network": {
        "Compose host ports",
        "Host port availability",
    },
    "env": {
        "Environment example",
        "Environment variables",
    },
}


@dataclass(frozen=True)
class CheckResult:
    name: str
    status: CheckStatus
    message: str

    @property
    def ok(self) -> bool:
        return self.status == "pass"

    @property
    def failed(self) -> bool:
        return self.status == "fail"

    @property
    def skipped(self) -> bool:
        return self.status == "skip"

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class CheckRun:
    results: list[CheckResult]

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def passed(self) -> int:
        return sum(result.ok for result in self.results)

    @property
    def failed(self) -> int:
        return sum(result.failed for result in self.results)

    @property
    def skipped(self) -> int:
        return sum(result.skipped for result in self.results)

    @property
    def status(self) -> str:
        return "Ready" if self.failed == 0 else "Not Ready"

    @property
    def exit_code(self) -> int:
        return 1 if self.failed else 0


def get_check_names() -> tuple[str, ...]:
    return tuple(name for name, _ in _build_checks(Path(".")))


def get_check_groups() -> tuple[str, ...]:
    return tuple(CHECK_GROUPS)


def expand_check_groups(groups: set[str]) -> set[str]:
    checks: set[str] = set()
    for group in groups:
        checks.update(CHECK_GROUPS[group])
    return checks


def run_checks(
    project_path: Path,
    only: set[str] | None = None,
    compose_file: Path | None = None,
) -> CheckRun:
    checks = _build_checks(project_path, compose_file)

    if only is not None:
        checks = [(name, run_check) for name, run_check in checks if name in only]

    results: list[CheckResult] = []
    docker_cli_available = True
    docker_compose_file_exists = True
    docker_compose_file_syntax_is_valid = True
    docker_compose_services_section_is_valid = True

    for name, run_check in checks:
        skip_message = _get_skip_message(
            name,
            project_path,
            compose_file,
            docker_cli_available,
            docker_compose_file_exists,
            docker_compose_file_syntax_is_valid,
            docker_compose_services_section_is_valid,
        )
        if skip_message is not None:
            results.append(CheckResult(name, "skip", skip_message))
            continue

        ok, message = run_check()
        status: CheckStatus = "pass" if ok else "fail"
        results.append(CheckResult(name, status, message))

        if name == "Docker CLI":
            docker_cli_available = ok
        elif name == "Compose file":
            docker_compose_file_exists = ok
        elif name == "Compose YAML":
            docker_compose_file_syntax_is_valid = ok
        elif name == "Compose services":
            docker_compose_services_section_is_valid = ok

    return CheckRun(results)


def _build_checks(
    project_path: Path,
    compose_file: Path | None = None,
) -> list[tuple[str, Callable[[], tuple[bool, str]]]]:
    return [
        ("Docker CLI", lambda: check_docker_cli_installed()),
        ("Docker daemon", lambda: check_docker_daemon_accessible()),
        ("Docker Compose", lambda: check_docker_compose_available()),
        (
            "Compose file",
            lambda: check_docker_compose_file_exists(project_path, compose_file),
        ),
        (
            "Compose YAML",
            lambda: check_docker_compose_yaml_syntax(project_path, compose_file),
        ),
        (
            "Compose services",
            lambda: check_docker_compose_services_section(project_path, compose_file),
        ),
        (
            "Compose build",
            lambda: check_docker_compose_valid_build_or_image(
                project_path,
                compose_file,
            ),
        ),
        (
            "Compose build contexts",
            lambda: check_docker_compose_build_contexts(project_path, compose_file),
        ),
        (
            "Compose host ports",
            lambda: check_docker_compose_duplicated_host_ports(
                project_path,
                compose_file,
            ),
        ),
        (
            "Host port availability",
            lambda: check_docker_compose_host_ports_available(
                project_path,
                compose_file,
            ),
        ),
        (
            "Compose build context Dockerfiles",
            lambda: check_docker_compose_build_contexts_dockerfiles(
                project_path,
                compose_file,
            ),
        ),
        (
            "Environment example",
            lambda: check_env_example_exists(project_path),
        ),
        (
            "Environment variables",
            lambda: check_env_variables_match(project_path),
        ),
    ]


def _get_skip_message(
    name: str,
    project_path: Path,
    compose_file: Path | None,
    docker_cli_available: bool,
    docker_compose_file_exists: bool,
    docker_compose_file_syntax_is_valid: bool,
    docker_compose_services_section_is_valid: bool,
) -> str | None:
    if name in {"Docker daemon", "Docker Compose"} and not docker_cli_available:
        return "skipped because Docker CLI is not installed."

    if name == "Compose YAML" and not docker_compose_file_exists:
        return "skipped because Compose file was not found."

    compose_file_checks = {
        "Compose services",
        "Compose build",
        "Compose build contexts",
        "Compose host ports",
        "Host port availability",
    }
    if name in compose_file_checks and not docker_compose_file_exists:
        return "skipped because Compose file was not found."

    if name in compose_file_checks and not docker_compose_file_syntax_is_valid:
        return "skipped because Compose YAML is not valid."

    compose_services_checks = {
        "Compose build",
        "Compose build contexts",
        "Compose host ports",
        "Host port availability",
    }
    if name in compose_services_checks and not docker_compose_services_section_is_valid:
        return "skipped because Compose services are not valid."

    if name == "Compose build context Dockerfiles":
        if not docker_compose_file_exists:
            return "skipped because Compose file was not found."
        if not docker_compose_file_syntax_is_valid:
            return "skipped because Compose YAML is not valid."
        if not docker_compose_services_section_is_valid:
            return "skipped because Compose services are not valid."
        if not has_build_services(project_path, compose_file):
            return "skipped because no service uses build."

    if name == "Environment example" and not has_env_file(project_path):
        return "skipped because .env file was not found."

    if name == "Environment variables":
        if not has_env_file(project_path):
            return "skipped because .env file was not found."
        if not has_env_example_file(project_path):
            return "skipped because .env.example file was not found."

    return None
