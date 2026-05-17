from devenv_doctor import runner


def ok_with_project(project_path, compose_file=None):
    return True, "ok"


def project_true(project_path, compose_file=None):
    return True


def project_false(project_path, compose_file=None):
    return False


def missing_compose_file(project_path, compose_file=None):
    return False, "No Docker Compose file was found."


def patch_all_checks_passing(monkeypatch):
    monkeypatch.setattr(runner, "check_docker_cli_installed", lambda: (True, "ok"))
    monkeypatch.setattr(runner, "check_docker_daemon_accessible", lambda: (True, "ok"))
    monkeypatch.setattr(runner, "check_docker_compose_available", lambda: (True, "ok"))
    monkeypatch.setattr(
        runner,
        "check_docker_compose_file_exists",
        ok_with_project,
    )
    monkeypatch.setattr(
        runner,
        "check_docker_compose_yaml_syntax",
        ok_with_project,
    )
    monkeypatch.setattr(
        runner,
        "check_docker_compose_services_section",
        ok_with_project,
    )
    monkeypatch.setattr(
        runner,
        "check_docker_compose_valid_build_or_image",
        ok_with_project,
    )
    monkeypatch.setattr(
        runner,
        "check_docker_compose_build_contexts",
        ok_with_project,
    )
    monkeypatch.setattr(
        runner,
        "check_docker_compose_duplicated_host_ports",
        ok_with_project,
    )
    monkeypatch.setattr(
        runner,
        "check_docker_compose_host_ports_available",
        ok_with_project,
    )
    monkeypatch.setattr(
        runner,
        "check_docker_compose_build_contexts_dockerfiles",
        ok_with_project,
    )
    monkeypatch.setattr(
        runner,
        "check_env_example_exists",
        ok_with_project,
    )
    monkeypatch.setattr(
        runner,
        "check_env_variables_match",
        ok_with_project,
    )
    monkeypatch.setattr(runner, "has_build_services", project_true)
    monkeypatch.setattr(runner, "has_env_file", project_true)
    monkeypatch.setattr(runner, "has_env_example_file", project_true)


def fail_if_called(*args):
    raise AssertionError("should be skipped")


def test_run_checks_returns_structured_results(monkeypatch, tmp_path):
    patch_all_checks_passing(monkeypatch)

    run = runner.run_checks(tmp_path)

    assert run.status == "Ready"
    assert run.exit_code == 0
    assert run.total == 13
    assert run.passed == 13
    assert run.failed == 0
    assert run.skipped == 0
    assert run.results[0] == runner.CheckResult("Docker CLI", "pass", "ok")


def test_check_run_exit_code_ignores_non_blocking_failures():
    run = runner.CheckRun(
        [
            runner.CheckResult("Docker CLI", "pass", "ok"),
            runner.CheckResult(
                "Environment example",
                "fail",
                ".env.example is missing while .env is being used.",
            ),
            runner.CheckResult(
                "Environment variables",
                "fail",
                ".env and .env.example variables do not match.",
            ),
        ]
    )

    assert run.status == "Ready"
    assert run.exit_code == 0
    assert run.failed == 2
    assert run.blocking_failed == 0


def test_check_run_exit_code_reports_blocking_failures():
    run = runner.CheckRun(
        [
            runner.CheckResult("Docker CLI", "pass", "ok"),
            runner.CheckResult("Compose file", "fail", "No Compose file."),
            runner.CheckResult(
                "Environment variables",
                "fail",
                ".env and .env.example variables do not match.",
            ),
        ]
    )

    assert run.status == "Not Ready"
    assert run.exit_code == 1
    assert run.failed == 2
    assert run.blocking_failed == 1


def test_check_severities_match_documented_rules():
    assert runner.CHECK_SEVERITIES == {
        "Docker CLI": "Blocking",
        "Docker daemon": "Blocking",
        "Docker Compose": "Blocking",
        "Compose file": "Blocking",
        "Compose YAML": "Blocking",
        "Compose services": "Blocking",
        "Compose build": "Blocking",
        "Compose build contexts": "Blocking",
        "Compose build context Dockerfiles": "Blocking",
        "Compose host ports": "Blocking",
        "Host port availability": "Blocking",
        "Environment example": "Recommendation",
        "Environment variables": "Warning",
    }

    assert set(runner.get_check_names()) == set(runner.CHECK_SEVERITIES)


def test_run_checks_counts_dependency_skips_separately(monkeypatch, tmp_path):
    patch_all_checks_passing(monkeypatch)
    monkeypatch.setattr(
        runner,
        "check_docker_cli_installed",
        lambda: (False, "Docker CLI is not installed."),
    )
    monkeypatch.setattr(runner, "check_docker_daemon_accessible", fail_if_called)
    monkeypatch.setattr(runner, "check_docker_compose_available", fail_if_called)

    run = runner.run_checks(tmp_path)

    assert run.status == "Not Ready"
    assert run.exit_code == 1
    assert run.passed == 10
    assert run.failed == 1
    assert run.skipped == 2
    assert run.results[0] == runner.CheckResult(
        "Docker CLI",
        "fail",
        "Docker CLI is not installed.",
    )
    assert run.results[1] == runner.CheckResult(
        "Docker daemon",
        "skip",
        "skipped because Docker CLI is not installed.",
    )


def test_run_checks_does_not_count_compose_dependency_skips_as_failures(
    monkeypatch,
    tmp_path,
):
    patch_all_checks_passing(monkeypatch)
    monkeypatch.setattr(
        runner,
        "check_docker_compose_file_exists",
        missing_compose_file,
    )
    monkeypatch.setattr(runner, "check_docker_compose_yaml_syntax", fail_if_called)
    monkeypatch.setattr(runner, "check_docker_compose_services_section", fail_if_called)
    monkeypatch.setattr(
        runner,
        "check_docker_compose_valid_build_or_image",
        fail_if_called,
    )
    monkeypatch.setattr(runner, "check_docker_compose_build_contexts", fail_if_called)
    monkeypatch.setattr(
        runner,
        "check_docker_compose_duplicated_host_ports",
        fail_if_called,
    )
    monkeypatch.setattr(
        runner,
        "check_docker_compose_host_ports_available",
        fail_if_called,
    )
    monkeypatch.setattr(
        runner,
        "check_docker_compose_build_contexts_dockerfiles",
        fail_if_called,
    )

    run = runner.run_checks(tmp_path)

    assert run.status == "Not Ready"
    assert run.passed == 5
    assert run.failed == 1
    assert run.skipped == 7
    assert run.results[4] == runner.CheckResult(
        "Compose YAML",
        "skip",
        "skipped because Compose file was not found.",
    )


def test_run_checks_can_be_ready_with_non_blocking_skips(monkeypatch, tmp_path):
    patch_all_checks_passing(monkeypatch)
    monkeypatch.setattr(runner, "has_build_services", project_false)
    monkeypatch.setattr(
        runner,
        "check_docker_compose_build_contexts_dockerfiles",
        fail_if_called,
    )

    run = runner.run_checks(tmp_path)

    assert run.status == "Ready"
    assert run.exit_code == 0
    assert run.passed == 12
    assert run.failed == 0
    assert run.skipped == 1
    assert run.results[10] == runner.CheckResult(
        "Compose build context Dockerfiles",
        "skip",
        "skipped because no service uses build.",
    )


def test_run_checks_skips_environment_checks_without_env_file(monkeypatch, tmp_path):
    patch_all_checks_passing(monkeypatch)
    monkeypatch.setattr(runner, "has_env_file", project_false)
    monkeypatch.setattr(runner, "check_env_example_exists", fail_if_called)
    monkeypatch.setattr(runner, "check_env_variables_match", fail_if_called)

    run = runner.run_checks(tmp_path)

    assert run.status == "Ready"
    assert run.passed == 11
    assert run.failed == 0
    assert run.skipped == 2
    assert run.results[11] == runner.CheckResult(
        "Environment example",
        "skip",
        "skipped because .env file was not found.",
    )
    assert run.results[12] == runner.CheckResult(
        "Environment variables",
        "skip",
        "skipped because .env file was not found.",
    )


def test_run_checks_runs_only_selected_checks(monkeypatch, tmp_path):
    patch_all_checks_passing(monkeypatch)
    monkeypatch.setattr(runner, "check_docker_compose_available", fail_if_called)

    run = runner.run_checks(tmp_path, only={"Docker CLI", "Compose file"})

    assert run.status == "Ready"
    assert run.total == 2
    assert run.passed == 2
    assert [result.name for result in run.results] == ["Docker CLI", "Compose file"]


def test_run_checks_passes_custom_compose_file_to_compose_checks(monkeypatch, tmp_path):
    compose_file = tmp_path / "custom.compose.yaml"
    calls = []

    def check_file_exists(project_path, compose_file=None):
        calls.append((project_path, compose_file))
        return True, "ok"

    monkeypatch.setattr(runner, "check_docker_compose_file_exists", check_file_exists)

    run = runner.run_checks(
        tmp_path,
        only={"Compose file"},
        compose_file=compose_file,
    )

    assert run.status == "Ready"
    assert calls == [(tmp_path, compose_file)]


def test_expand_check_groups_returns_group_checks():
    assert runner.expand_check_groups({"network"}) == {
        "Compose host ports",
        "Host port availability",
    }


def test_get_check_groups_lists_public_only_groups():
    assert runner.get_check_groups() == ("docker", "network", "env")


def test_run_checks_applies_skips_within_selected_checks(monkeypatch, tmp_path):
    patch_all_checks_passing(monkeypatch)
    monkeypatch.setattr(
        runner,
        "check_docker_cli_installed",
        lambda: (False, "Docker CLI is not installed."),
    )
    monkeypatch.setattr(runner, "check_docker_daemon_accessible", fail_if_called)

    run = runner.run_checks(tmp_path, only={"Docker CLI", "Docker daemon"})

    assert run.status == "Not Ready"
    assert run.passed == 0
    assert run.failed == 1
    assert run.skipped == 1
    assert run.results == [
        runner.CheckResult("Docker CLI", "fail", "Docker CLI is not installed."),
        runner.CheckResult(
            "Docker daemon",
            "skip",
            "skipped because Docker CLI is not installed.",
        ),
    ]
