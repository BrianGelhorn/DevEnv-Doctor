import socket
from pathlib import Path

from devenv_doctor.checks.compose_utils import (
    find_compose_file,
    get_build_context,
    get_build_dockerfile,
    parse_yaml_file,
    resolve_build_context,
)
from devenv_doctor.core import command_output


def _get_published_host_port(port: object) -> tuple[str | None, str | None]:
    if isinstance(port, str):
        port_parts = port.rsplit(":", 2)
        if len(port_parts) == 2:
            return None, port_parts[0]
        if len(port_parts) == 3:
            return port_parts[0].strip("[]"), port_parts[1]
    elif isinstance(port, dict):
        published = port.get("published")
        if published is not None:
            host_ip = port.get("host_ip")
            return str(host_ip) if host_ip is not None else None, str(published)

    return None, None


def _is_host_port_available(host_ip: str | None, host_port: str) -> bool:
    port = int(host_port)
    host = host_ip or ""
    family = socket.AF_INET6 if ":" in host else socket.AF_INET

    with socket.socket(family, socket.SOCK_STREAM) as probe:
        probe.bind((host, port))

    return True


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


def check_docker_compose_file_exists(project_path: Path) -> tuple[bool, str]:
    compose_file = find_compose_file(project_path)
    if compose_file is None:
        return False, "No Docker Compose file was found."
    return True, f"Docker Compose file found: {compose_file.name}"


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


def check_docker_compose_build_contexts(project_path: Path) -> tuple[bool, str]:
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

    invalid_build_contexts = []
    for service_name, service_config in parsed_yaml["services"].items():
        if not isinstance(service_config, dict) or "build" not in service_config:
            continue

        context = get_build_context(service_config["build"])
        if context is None:
            invalid_build_contexts.append(f"{service_name} (invalid build context)")
            continue

        full_build_context = resolve_build_context(compose_file, context)

        if not full_build_context.is_dir():
            invalid_build_contexts.append(f"{service_name} ({context})")

    if invalid_build_contexts:
        invalid_contexts = ", ".join(invalid_build_contexts)
        return False, f"The following build contexts do not exist: {invalid_contexts}."

    return True, "All defined build contexts exist."


def check_docker_compose_build_contexts_dockerfiles(
    project_path: Path,
) -> tuple[bool, str]:
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

    missing_dockerfiles: list[str] = []
    for service_name, service_config in parsed_yaml["services"].items():
        if not isinstance(service_config, dict) or "build" not in service_config:
            continue

        context = get_build_context(service_config["build"])
        dockerfile = get_build_dockerfile(service_config["build"])
        if context is None or dockerfile is None:
            continue

        dockerfile_path = resolve_build_context(compose_file, context) / dockerfile
        if not dockerfile_path.is_file():
            missing_dockerfiles.append(f"{service_name} ({dockerfile_path})")

    if missing_dockerfiles:
        missing = ", ".join(missing_dockerfiles)
        return (
            False,
            f"The following build contexts do not have a Dockerfile: {missing}.",
        )

    return True, "All defined build contexts have a Dockerfile."


def check_docker_compose_duplicated_host_ports(project_path: Path) -> tuple[bool, str]:
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

    host_ports: dict[str, str] = {}
    duplicated_host_ports: list[str] = []

    for service_name, service_config in parsed_yaml["services"].items():
        if not isinstance(service_config, dict) or "ports" not in service_config:
            continue

        for port in service_config["ports"]:
            _, host_port = _get_published_host_port(port)
            if not host_port:
                continue

            existing_service = host_ports.get(host_port)
            if existing_service is not None:
                duplicated_host_ports.append(
                    f"{host_port} ({existing_service}, {service_name})"
                )
                continue

            host_ports[host_port] = service_name

    if duplicated_host_ports:
        duplicated = ", ".join(duplicated_host_ports)
        return False, f"The following host ports are duplicated: {duplicated}."

    return True, "All published host ports are unique."


def check_docker_compose_host_ports_available(project_path: Path) -> tuple[bool, str]:
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

    unavailable_host_ports: list[str] = []
    permission_denied_host_ports: list[str] = []

    for service_name, service_config in parsed_yaml["services"].items():
        if not isinstance(service_config, dict) or "ports" not in service_config:
            continue

        for port in service_config["ports"]:
            host_ip, host_port = _get_published_host_port(port)
            if not host_port:
                continue

            try:
                if not _is_host_port_available(host_ip, host_port):
                    unavailable_host_ports.append(f"{service_name} ({host_port})")
            except PermissionError:
                permission_denied_host_ports.append(f"{service_name} ({host_port})")
            except OSError:
                unavailable_host_ports.append(f"{service_name} ({host_port})")
            except ValueError:
                continue

    if permission_denied_host_ports:
        ports = ", ".join(permission_denied_host_ports)
        return (
            False,
            "Insufficient permissions to scan the following host ports: "
            f"{ports}.",
        )

    if unavailable_host_ports:
        ports = ", ".join(unavailable_host_ports)
        return False, f"The following host ports are already in use: {ports}."

    return True, "All published host ports are available."
