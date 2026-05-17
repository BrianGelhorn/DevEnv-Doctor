from pathlib import Path

from devenv_doctor.checks import compose, compose_utils


def write_compose_file(
    project_path: Path,
    content: str,
    filename: str = "compose.yaml",
):
    compose_file = project_path / filename
    compose_file.write_text(content, encoding="utf-8")
    return compose_file


def test_check_docker_compose_available_when_command_succeeds(monkeypatch):
    monkeypatch.setattr(
        compose,
        "command_output",
        lambda command: (0, "Docker Compose version 2"),
    )

    assert compose.check_docker_compose_available() == (
        True,
        "Docker Compose is available",
    )


def test_check_docker_compose_available_when_permission_is_denied(monkeypatch):
    monkeypatch.setattr(
        compose,
        "command_output",
        lambda command: (1, "permission denied"),
    )

    assert compose.check_docker_compose_available() == (
        False,
        "Docker Compose is installed but your user does not have permission "
        "to access it.",
    )


def test_find_compose_file_uses_supported_filename_priority(tmp_path):
    write_compose_file(tmp_path, "services: {}\n", filename="docker-compose.yaml")
    expected = write_compose_file(tmp_path, "services: {}\n", filename="compose.yaml")

    assert compose_utils.find_compose_file(tmp_path) == expected


def test_check_docker_compose_file_exists_when_file_is_present(tmp_path):
    write_compose_file(tmp_path, "services: {}\n", filename="docker-compose.yml")

    assert compose.check_docker_compose_file_exists(tmp_path) == (
        True,
        "Docker Compose file found: docker-compose.yml",
    )


def test_check_docker_compose_file_exists_when_file_is_missing(tmp_path):
    assert compose.check_docker_compose_file_exists(tmp_path) == (
        False,
        "No Docker Compose file was found.",
    )


def test_check_docker_compose_yaml_syntax_accepts_valid_yaml(tmp_path):
    write_compose_file(tmp_path, "services:\n  web:\n    image: nginx\n")

    assert compose.check_docker_compose_yaml_syntax(tmp_path) == (
        True,
        "Docker Compose file has valid YAML syntax.",
    )


def test_check_docker_compose_yaml_syntax_rejects_empty_file(tmp_path):
    write_compose_file(tmp_path, "")

    assert compose.check_docker_compose_yaml_syntax(tmp_path) == (
        False,
        "Docker Compose file is empty.",
    )


def test_check_docker_compose_yaml_syntax_rejects_invalid_yaml(tmp_path):
    write_compose_file(tmp_path, "services:\n  web: [\n")

    assert compose.check_docker_compose_yaml_syntax(tmp_path) == (
        False,
        "Docker Compose file YAML has syntax errors.",
    )


def test_check_docker_compose_services_section_accepts_object(tmp_path):
    write_compose_file(tmp_path, "services:\n  web:\n    image: nginx\n")

    assert compose.check_docker_compose_services_section(tmp_path) == (
        True,
        "The services section exists and is not empty.",
    )


def test_check_docker_compose_services_section_rejects_missing_section(tmp_path):
    write_compose_file(tmp_path, "name: demo\n")

    assert compose.check_docker_compose_services_section(tmp_path) == (
        False,
        "The services section does not exist.",
    )


def test_check_docker_compose_services_section_rejects_empty_section(tmp_path):
    write_compose_file(tmp_path, "services:\n")

    assert compose.check_docker_compose_services_section(tmp_path) == (
        False,
        "The services section is empty.",
    )


def test_check_docker_compose_services_section_rejects_non_object_section(tmp_path):
    write_compose_file(tmp_path, "services:\n  - web\n")

    assert compose.check_docker_compose_services_section(tmp_path) == (
        False,
        "The services section must be a YAML object.",
    )


def test_check_docker_compose_valid_build_or_image_accepts_image_or_build(tmp_path):
    write_compose_file(
        tmp_path,
        "services:\n  web:\n    image: nginx\n  api:\n    build: .\n",
    )

    assert compose.check_docker_compose_valid_build_or_image(tmp_path) == (
        True,
        "All services have either build or image tag.",
    )


def test_check_docker_compose_valid_build_or_image_lists_invalid_services(tmp_path):
    write_compose_file(
        tmp_path,
        (
            "services:\n"
            "  web:\n"
            "    ports:\n"
            "      - '80:80'\n"
            "  api:\n"
            "    image: nginx\n"
            "  worker:\n"
            "    environment:\n"
            "      FOO: bar\n"
        ),
    )

    assert compose.check_docker_compose_valid_build_or_image(tmp_path) == (
        False,
        "The following services have no build or image tag: web, worker.",
    )


def test_get_build_context_accepts_string_build_config():
    assert compose_utils.get_build_context("./api") == "./api"


def test_get_build_context_accepts_object_build_config():
    assert compose_utils.get_build_context({"context": "./api"}) == "./api"


def test_get_build_context_defaults_object_context_to_current_directory():
    assert compose_utils.get_build_context({"dockerfile": "Dockerfile.dev"}) == "."


def test_get_build_context_rejects_invalid_build_config():
    assert compose_utils.get_build_context(["./api"]) is None
    assert compose_utils.get_build_context({"context": ["./api"]}) is None


def test_get_build_dockerfile_defaults_to_dockerfile():
    assert compose_utils.get_build_dockerfile("./api") == "Dockerfile"
    assert compose_utils.get_build_dockerfile({"context": "./api"}) == "Dockerfile"


def test_get_build_dockerfile_accepts_object_dockerfile():
    assert compose_utils.get_build_dockerfile({"dockerfile": "Dockerfile.dev"}) == (
        "Dockerfile.dev"
    )


def test_get_build_dockerfile_rejects_invalid_config():
    assert compose_utils.get_build_dockerfile(["./api"]) is None
    assert compose_utils.get_build_dockerfile(
        {"dockerfile": ["Dockerfile.dev"]}
    ) is None


def test_has_build_services_detects_build_services(tmp_path):
    write_compose_file(
        tmp_path,
        "services:\n  web:\n    image: nginx\n  api:\n    build: ./api\n",
    )

    assert compose_utils.has_build_services(tmp_path) is True


def test_has_build_services_rejects_compose_without_build_services(tmp_path):
    write_compose_file(tmp_path, "services:\n  web:\n    image: nginx\n")

    assert compose_utils.has_build_services(tmp_path) is False


def test_check_docker_compose_build_contexts_accepts_existing_contexts(tmp_path):
    (tmp_path / "api").mkdir()
    (tmp_path / "worker").mkdir()
    write_compose_file(
        tmp_path,
        (
            "services:\n"
            "  api:\n"
            "    build: ./api\n"
            "  worker:\n"
            "    build:\n"
            "      context: ./worker\n"
            "  db:\n"
            "    image: postgres\n"
        ),
    )

    assert compose.check_docker_compose_build_contexts(tmp_path) == (
        True,
        "All defined build contexts exist.",
    )


def test_check_docker_compose_build_contexts_accepts_absolute_context(tmp_path):
    absolute_context = tmp_path / "api"
    absolute_context.mkdir()
    write_compose_file(
        tmp_path,
        f"services:\n  api:\n    build: {absolute_context}\n",
    )

    assert compose.check_docker_compose_build_contexts(tmp_path) == (
        True,
        "All defined build contexts exist.",
    )


def test_check_docker_compose_build_contexts_uses_compose_file_parent(tmp_path):
    project_path = tmp_path / "project"
    project_path.mkdir()
    (project_path / "api").mkdir()
    write_compose_file(
        project_path,
        "services:\n  api:\n    build: ./api\n",
    )

    assert compose.check_docker_compose_build_contexts(project_path) == (
        True,
        "All defined build contexts exist.",
    )


def test_check_docker_compose_build_contexts_lists_missing_contexts(tmp_path):
    write_compose_file(
        tmp_path,
        (
            "services:\n"
            "  api:\n"
            "    build: ./api\n"
            "  worker:\n"
            "    build:\n"
            "      context: ./worker\n"
        ),
    )

    assert compose.check_docker_compose_build_contexts(tmp_path) == (
        False,
        "The following build contexts do not exist: api (./api), worker (./worker).",
    )


def test_check_docker_compose_build_contexts_reports_invalid_contexts(tmp_path):
    write_compose_file(
        tmp_path,
        (
            "services:\n"
            "  api:\n"
            "    build:\n"
            "      context:\n"
            "        - ./api\n"
        ),
    )

    assert compose.check_docker_compose_build_contexts(tmp_path) == (
        False,
        "The following build contexts do not exist: api (invalid build context).",
    )


def test_check_docker_compose_duplicated_host_ports_accepts_unique_ports(tmp_path):
    write_compose_file(
        tmp_path,
        (
            "services:\n"
            "  web:\n"
            "    image: nginx\n"
            "    ports:\n"
            "      - '8080:80'\n"
            "  api:\n"
            "    image: nginx\n"
            "    ports:\n"
            "      - target: 8000\n"
            "        published: 8000\n"
            "  worker:\n"
            "    image: nginx\n"
        ),
    )

    assert compose.check_docker_compose_duplicated_host_ports(tmp_path) == (
        True,
        "All published host ports are unique.",
    )


def test_check_docker_compose_duplicated_host_ports_lists_duplicate_ports(tmp_path):
    write_compose_file(
        tmp_path,
        (
            "services:\n"
            "  web:\n"
            "    image: nginx\n"
            "    ports:\n"
            "      - '8080:80'\n"
            "  api:\n"
            "    image: nginx\n"
            "    ports:\n"
            "      - '127.0.0.1:8080:8000'\n"
            "  worker:\n"
            "    image: nginx\n"
            "    ports:\n"
            "      - target: 9000\n"
            "        published: 8080\n"
        ),
    )

    assert compose.check_docker_compose_duplicated_host_ports(tmp_path) == (
        False,
        "The following host ports are duplicated: "
        "8080 (web, api), 8080 (web, worker).",
    )


def test_check_docker_compose_duplicated_host_ports_ignores_container_only_ports(
    tmp_path,
):
    write_compose_file(
        tmp_path,
        (
            "services:\n"
            "  web:\n"
            "    image: nginx\n"
            "    ports:\n"
            "      - '80'\n"
            "  api:\n"
            "    image: nginx\n"
            "    ports:\n"
            "      - '80'\n"
        ),
    )

    assert compose.check_docker_compose_duplicated_host_ports(tmp_path) == (
        True,
        "All published host ports are unique.",
    )


def test_check_docker_compose_host_ports_available_accepts_available_ports(
    monkeypatch,
    tmp_path,
):
    checked_ports = []
    monkeypatch.setattr(
        compose,
        "_is_host_port_available",
        lambda host_ip, host_port: checked_ports.append((host_ip, host_port)) or True,
    )
    write_compose_file(
        tmp_path,
        (
            "services:\n"
            "  web:\n"
            "    image: nginx\n"
            "    ports:\n"
            "      - '8080:80'\n"
            "  api:\n"
            "    image: nginx\n"
            "    ports:\n"
            "      - target: 8000\n"
            "        published: 8000\n"
            "  worker:\n"
            "    image: nginx\n"
            "    ports:\n"
            "      - '80'\n"
        ),
    )

    assert compose.check_docker_compose_host_ports_available(tmp_path) == (
        True,
        "All published host ports are available.",
    )
    assert checked_ports == [(None, "8080"), (None, "8000")]


def test_check_docker_compose_host_ports_available_lists_used_ports(
    monkeypatch,
    tmp_path,
):
    monkeypatch.setattr(
        compose,
        "_is_host_port_available",
        lambda host_ip, host_port: host_port != "8080",
    )
    write_compose_file(
        tmp_path,
        (
            "services:\n"
            "  web:\n"
            "    image: nginx\n"
            "    ports:\n"
            "      - '8080:80'\n"
            "  api:\n"
            "    image: nginx\n"
            "    ports:\n"
            "      - '127.0.0.1:8000:8000'\n"
        ),
    )

    assert compose.check_docker_compose_host_ports_available(tmp_path) == (
        False,
        "The following host ports are already in use: web (8080).",
    )


def test_check_docker_compose_host_ports_available_reports_permission_denied(
    monkeypatch,
    tmp_path,
):
    def deny_port(host_ip, host_port):
        raise PermissionError

    monkeypatch.setattr(compose, "_is_host_port_available", deny_port)
    write_compose_file(
        tmp_path,
        (
            "services:\n"
            "  web:\n"
            "    image: nginx\n"
            "    ports:\n"
            "      - '443:443'\n"
        ),
    )

    assert compose.check_docker_compose_host_ports_available(tmp_path) == (
        False,
        "Insufficient permissions to inspect the following host ports: web (443).",
    )


def test_check_docker_compose_build_contexts_dockerfiles_accepts_default_dockerfile(
    tmp_path,
):
    (tmp_path / "api").mkdir()
    (tmp_path / "api" / "Dockerfile").write_text("FROM python:3.12\n", encoding="utf-8")
    write_compose_file(tmp_path, "services:\n  api:\n    build: ./api\n")

    assert compose.check_docker_compose_build_contexts_dockerfiles(tmp_path) == (
        True,
        "All defined build contexts have a Dockerfile.",
    )


def test_check_docker_compose_build_contexts_dockerfiles_accepts_custom_dockerfile(
    tmp_path,
):
    (tmp_path / "api").mkdir()
    (tmp_path / "api" / "Dockerfile.dev").write_text(
        "FROM python:3.12\n",
        encoding="utf-8",
    )
    write_compose_file(
        tmp_path,
        (
            "services:\n"
            "  api:\n"
            "    build:\n"
            "      context: ./api\n"
            "      dockerfile: Dockerfile.dev\n"
        ),
    )

    assert compose.check_docker_compose_build_contexts_dockerfiles(tmp_path) == (
        True,
        "All defined build contexts have a Dockerfile.",
    )


def test_check_docker_compose_build_contexts_dockerfiles_lists_missing_dockerfiles(
    tmp_path,
):
    (tmp_path / "api").mkdir()
    (tmp_path / "worker").mkdir()
    write_compose_file(
        tmp_path,
        (
            "services:\n"
            "  api:\n"
            "    build: ./api\n"
            "  worker:\n"
            "    build:\n"
            "      context: ./worker\n"
            "      dockerfile: Dockerfile.dev\n"
            "  db:\n"
            "    image: postgres\n"
        ),
    )

    assert compose.check_docker_compose_build_contexts_dockerfiles(tmp_path) == (
        False,
        "The following build contexts do not have a Dockerfile: "
        f"api ({tmp_path / 'api' / 'Dockerfile'}), "
        f"worker ({tmp_path / 'worker' / 'Dockerfile.dev'}).",
    )
