from pathlib import Path

import yaml
from yaml import YAMLError

from devenv_doctor.core import command_output


def check_docker_compose_available() -> tuple[bool, str]:
    exit_code, output = command_output(["docker", "compose", "version"])
    if exit_code == 0:
        return True, "Docker Compose is available"

    output_lower = output.lower()

    if "permission denied" in output_lower:
        return (
            False,
            "Docker Compose is installed but your user does not have permission "
            "to access it.",
        )

    return False, output


COMPOSE_FILENAMES = (
    "compose.yaml",
    "compose.yml",
    "docker-compose.yml",
    "docker-compose.yaml",
)


def find_compose_file(project_path: Path) -> Path | None:
    for filename in COMPOSE_FILENAMES:
        compose_file = project_path / filename

        if compose_file.is_file():
            return compose_file
    return None


def check_docker_compose_file_exists(project_path: Path) -> tuple[bool, str]:
    compose_file = find_compose_file(project_path)
    if compose_file is None:
        return False, "No Docker Compose file was found."
    return True, f"Docker Compose file found: {compose_file.name}"


def parse_yaml_file(file_path: Path) -> dict | None:
    try:
        with file_path.open("r", encoding="utf-8") as file:
            return yaml.safe_load(file) or {}
    except YAMLError:
        return None


def check_docker_compose_yaml_syntax(project_path: Path) -> tuple[bool, str]:
    compose_file = find_compose_file(project_path)

    # This should not run since the check_docker_compose_file_exists function
    # should be called before.
    if compose_file is None:
        return False, "No Docker Compose file was found."
    parsed_yaml = parse_yaml_file(compose_file)
    if parsed_yaml == {}:
        return False, "Docker Compose file is empty."
    if parsed_yaml is None:
        return False, "Docker Compose file YAML has syntax errors."
    return True, "Docker Compose file has valid YAML syntax."


def check_docker_compose_services_section(project_path: Path) -> tuple[bool, str]:
    compose_file = find_compose_file(project_path)

    # This should not run since the check_docker_compose_file_exists function
    # should be called before.
    if compose_file is None:
        return False, "No Docker Compose file was found."

    parsed_yaml = parse_yaml_file(compose_file)

    # This should not run since the check_docker_compose_yaml_syntax function
    # should be called before.
    if parsed_yaml is None:
        return False, "Docker Compose file YAML has syntax errors."
    if "services" not in parsed_yaml.keys():
        return False, "The services section does not exist."
    if parsed_yaml["services"] is None:
        return False, "The services section is empty."
    if not isinstance(parsed_yaml["services"], dict):
        return False, "The services section must be a YAML object."
    return True, "The services section exists and is not empty."


def check_docker_compose_valid_build_or_image(project_path: Path) -> tuple[bool, str]:
    compose_file = find_compose_file(project_path)
    # This should not run since the check_docker_compose_file_exists function
    # should be called before.
    if compose_file is None:
        return False, "No Docker Compose file was found."

    parsed_yaml = parse_yaml_file(compose_file)

    # This should not run since the check_docker_compose_yaml_syntax function
    # should be called before.
    if parsed_yaml is None:
        return False, "Docker Compose file YAML has syntax errors."
    services_with_error = []
    for service in parsed_yaml["services"].keys():
        service_keys = parsed_yaml["services"][service].keys()
        if "build" not in service_keys and "image" not in service_keys:
            services_with_error.append(service)

    if not len(services_with_error) == 0:
        output = "The following services have no build or image tag: "
        for service in services_with_error:
            output += f"{service}, "
        # Delete last space and comma and add final dot
        output = f"{output[0:len(output)-2]}."

        return False, output
    return True, "All services have either build or image tag."
