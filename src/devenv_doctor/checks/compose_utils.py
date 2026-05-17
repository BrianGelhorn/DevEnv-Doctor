import socket
from pathlib import Path

import yaml
from yaml import YAMLError

COMPOSE_FILENAMES = (
    "compose.yaml",
    "compose.yml",
    "docker-compose.yml",
    "docker-compose.yaml",
)


def find_compose_file(
    project_path: Path,
    compose_file: Path | None = None,
) -> Path | None:
    if compose_file is not None:
        if compose_file.is_file():
            return compose_file
        return None

    for filename in COMPOSE_FILENAMES:
        compose_file = project_path / filename

        if compose_file.is_file():
            return compose_file
    return None


def parse_yaml_file(file_path: Path) -> dict | None:
    try:
        with file_path.open("r", encoding="utf-8") as file:
            return yaml.safe_load(file) or {}
    except YAMLError:
        return None


def get_build_context(build_config: object) -> str | None:
    if isinstance(build_config, str):
        return build_config
    if isinstance(build_config, dict):
        context = build_config.get("context", ".")
        if isinstance(context, str):
            return context
    return None


def get_build_dockerfile(build_config: object) -> str | None:
    if isinstance(build_config, str):
        return "Dockerfile"
    if isinstance(build_config, dict):
        dockerfile = build_config.get("dockerfile", "Dockerfile")
        if isinstance(dockerfile, str):
            return dockerfile
    return None


def has_build_services(project_path: Path, compose_file: Path | None = None) -> bool:
    compose_file = find_compose_file(project_path, compose_file)
    if compose_file is None:
        return False

    parsed_yaml = parse_yaml_file(compose_file)
    if parsed_yaml is None or not isinstance(parsed_yaml.get("services"), dict):
        return False

    return any(
        isinstance(service_config, dict) and "build" in service_config
        for service_config in parsed_yaml["services"].values()
    )


def resolve_build_context(compose_file: Path, context: str) -> Path:
    context_path = Path(context)
    if context_path.is_absolute():
        return context_path
    return compose_file.parent / context_path


def get_published_host_port(port: object) -> tuple[str | None, str | None]:
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


def is_host_port_available(host_ip: str | None, host_port: str) -> bool:
    port = int(host_port)
    host = host_ip or ""
    family = socket.AF_INET6 if ":" in host else socket.AF_INET

    with socket.socket(family, socket.SOCK_STREAM) as probe:
        probe.bind((host, port))

    return True
