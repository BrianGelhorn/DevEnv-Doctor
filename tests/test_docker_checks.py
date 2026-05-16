from devenv_doctor.checks import docker


def test_check_docker_cli_installed_when_command_succeeds(monkeypatch):
    monkeypatch.setattr(
        docker,
        "command_output",
        lambda command: (0, "Docker version 1"),
    )

    assert docker.check_docker_cli_installed() == (True, "Docker CLI is installed.")


def test_check_docker_cli_installed_when_command_is_missing(monkeypatch):
    monkeypatch.setattr(
        docker,
        "command_output",
        lambda command: (127, "Command not found: docker"),
    )

    assert docker.check_docker_cli_installed() == (
        False,
        "Docker CLI is not installed.",
    )


def test_check_docker_cli_installed_returns_unrecognized_error(monkeypatch):
    monkeypatch.setattr(docker, "command_output", lambda command: (1, "unexpected"))

    assert docker.check_docker_cli_installed() == (False, "unexpected")


def test_check_docker_daemon_accessible_when_command_succeeds(monkeypatch):
    monkeypatch.setattr(docker, "command_output", lambda command: (0, "ok"))

    assert docker.check_docker_daemon_accessible() == (
        True,
        "Docker daemon is accessible",
    )


def test_check_docker_daemon_accessible_when_command_times_out(monkeypatch):
    monkeypatch.setattr(docker, "command_output", lambda command: (124, "timeout"))

    assert docker.check_docker_daemon_accessible() == (
        False,
        "Docker Command timed out. Docker may be slow, stuck or not responding.",
    )


def test_check_docker_daemon_accessible_when_permission_is_denied(monkeypatch):
    monkeypatch.setattr(
        docker,
        "command_output",
        lambda command: (1, "permission denied while connecting"),
    )

    assert docker.check_docker_daemon_accessible() == (
        False,
        "Docker daemon may be running, but your user does not have permission "
        "to access it.",
    )


def test_check_docker_daemon_accessible_when_daemon_is_unreachable(monkeypatch):
    monkeypatch.setattr(
        docker,
        "command_output",
        lambda command: (1, "Cannot connect to the Docker daemon"),
    )

    assert docker.check_docker_daemon_accessible() == (
        False,
        "Docker daemon is not running or is not reachable.",
    )
