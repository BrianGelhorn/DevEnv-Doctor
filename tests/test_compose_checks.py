from pathlib import Path

from devenv_doctor.checks import compose


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

    assert compose.find_compose_file(tmp_path) == expected


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
