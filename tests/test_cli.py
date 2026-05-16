from typer.testing import CliRunner

from devenv_doctor import cli

runner = CliRunner()


def test_check_command_reports_ready_when_all_checks_pass(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "check_docker_cli_installed", lambda: (True, "ok"))
    monkeypatch.setattr(cli, "check_docker_daemon_accessible", lambda: (True, "ok"))
    monkeypatch.setattr(cli, "check_docker_compose_available", lambda: (True, "ok"))
    monkeypatch.setattr(
        cli,
        "check_docker_compose_file_exists",
        lambda project_path: (True, "ok"),
    )
    monkeypatch.setattr(
        cli,
        "check_docker_compose_yaml_syntax",
        lambda project_path: (True, "ok"),
    )
    monkeypatch.setattr(
        cli,
        "check_docker_compose_services_section",
        lambda project_path: (True, "ok"),
    )
    monkeypatch.setattr(
        cli,
        "check_docker_compose_valid_build_or_image",
        lambda project_path: (True, "ok"),
    )

    result = runner.invoke(cli.app, ["check", str(tmp_path)])

    assert result.exit_code == 0
    assert "Status: Ready" in result.output
    assert "Summary: 7/7 passed, 0 failed." in result.output

def fail_if_called():
    raise AssertionError("should be skipped")

def test_check_command_skips_docker_dependent_checks_when_cli_is_missing(
    monkeypatch,
    tmp_path,
):
    monkeypatch.setattr(
        cli,
        "check_docker_cli_installed",
        lambda: (False, "Docker CLI is not installed."),
    )
    monkeypatch.setattr(
        cli,
        "check_docker_daemon_accessible",
        lambda: fail_if_called,
    )
    monkeypatch.setattr(
        cli,
        "check_docker_compose_available",
        lambda: fail_if_called,
    )
    monkeypatch.setattr(
        cli,
        "check_docker_compose_file_exists",
        lambda project_path: (True, "ok"),
    )
    monkeypatch.setattr(
        cli,
        "check_docker_compose_yaml_syntax",
        lambda project_path: (True, "ok"),
    )
    monkeypatch.setattr(
        cli,
        "check_docker_compose_services_section",
        lambda project_path: (True, "ok"),
    )
    monkeypatch.setattr(
        cli,
        "check_docker_compose_valid_build_or_image",
        lambda project_path: (True, "ok"),
    )

    result = runner.invoke(cli.app, ["check", str(tmp_path)])

    assert result.exit_code == 1
    assert (
        "[FAIL] Docker daemon: skipped because Docker CLI is not installed."
        in result.output
    )
    assert (
        "[FAIL] Docker Compose: skipped because Docker CLI is not installed."
        in result.output
    )
    assert "Status: Not Ready" in result.output
    assert "Summary: 4/7 passed, 3 failed." in result.output
