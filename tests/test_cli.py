import json
import re

from typer.testing import CliRunner

from devenv_doctor import cli
from devenv_doctor.runner import CheckResult, CheckRun

runner = CliRunner()


def ready_run() -> CheckRun:
    return CheckRun(
        [
            CheckResult("Docker CLI", "pass", "ok"),
            CheckResult("Docker daemon", "pass", "ok"),
            CheckResult("Docker Compose", "pass", "ok"),
        ]
    )


def run_ready(project_path, only=None, compose_file=None):
    return ready_run()


def run_not_ready(project_path, only=None, compose_file=None):
    return not_ready_run()


def filtered_ready_run(project_path, only=None, compose_file=None) -> CheckRun:
    results = [
        CheckResult("Docker CLI", "pass", "ok"),
        CheckResult("Docker daemon", "pass", "ok"),
        CheckResult("Docker Compose", "pass", "ok"),
        CheckResult("Compose host ports", "pass", "ok"),
        CheckResult("Host port availability", "pass", "ok"),
        CheckResult("Environment example", "pass", "ok"),
        CheckResult("Environment variables", "pass", "ok"),
    ]
    if only is not None:
        results = [result for result in results if result.name in only]
    return CheckRun(results)


def not_ready_run() -> CheckRun:
    return CheckRun(
        [
            CheckResult("Docker CLI", "pass", "ok"),
            CheckResult("Compose file", "fail", "No Docker Compose file was found."),
            CheckResult(
                "Compose YAML",
                "skip",
                "skipped because Compose file was not found.",
            ),
        ]
    )


def severity_run(project_path, only=None, compose_file=None):
    return CheckRun(
        [
            CheckResult("Docker CLI", "pass", "ok"),
            CheckResult("Compose file", "fail", "No Docker Compose file was found."),
            CheckResult(
                "Compose YAML",
                "skip",
                "skipped because Compose file was not found.",
            ),
            CheckResult(
                "Environment example",
                "fail",
                ".env.example is missing while .env is being used.",
            ),
            CheckResult(
                "Environment variables",
                "fail",
                ".env and .env.example variables do not match.",
            ),
        ]
    )


def non_blocking_failure_run(project_path, only=None, compose_file=None):
    return CheckRun(
        [
            CheckResult("Docker CLI", "pass", "ok"),
            CheckResult(
                "Environment example",
                "fail",
                ".env.example is missing while .env is being used.",
            ),
            CheckResult(
                "Environment variables",
                "fail",
                ".env and .env.example variables do not match.",
            ),
        ]
    )


def test_check_command_reports_ready_when_all_checks_pass(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "run_checks", run_ready)

    result = runner.invoke(cli.app, ["check", str(tmp_path)])

    assert result.exit_code == 0
    assert "[PASS] Docker CLI: ok" in result.output
    assert "Status: Ready" in result.output
    assert "Summary: 3/3 passed, 0 failed, 0 skipped." in result.output


def test_root_help_shows_basic_examples_and_accepted_values():
    result = runner.invoke(cli.app, ["--help"])

    assert result.exit_code == 0
    assert "Basic examples:" in result.output
    assert "devenv-doctor check ." in result.output
    assert "devenv-doctor check . --only docker,env" in result.output
    assert "Check groups: docker, network, env" in result.output
    assert "Severity levels: Critical, Warning, Recommendations" in result.output


def test_check_help_shows_options_values_and_examples():
    result = runner.invoke(cli.app, ["check", "--help"])

    assert result.exit_code == 0
    assert "--report [PATH]" in result.output
    assert "--only GROUPS" in result.output
    assert "--compose FILE" in result.output
    assert "--severity LEVELS" in result.output
    assert "Accepted check groups:" in result.output
    assert (
        "docker    Docker CLI, daemon, Compose, Compose file and build checks"
        in result.output
    )
    assert "Accepted severity levels:" in result.output
    assert "Critical             Blocking failures" in result.output
    assert "Warning              Failed rules marked Severity: Warning" in result.output
    assert (
        "Recommendations      Failed rules marked Severity: Recommendation"
        in result.output
    )
    assert "devenv-doctor check ./api --compose docker-compose.dev.yml" in result.output
    assert "devenv-doctor check . --severity Critical,Recommendations" in result.output


def test_check_command_reports_skips_separately(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "run_checks", run_not_ready)

    result = runner.invoke(cli.app, ["check", str(tmp_path)])

    assert result.exit_code == 1
    assert "[FAIL] Compose file: No Docker Compose file was found." in result.output
    assert (
        "[SKIP] Compose YAML: skipped because Compose file was not found."
        in result.output
    )
    assert "Status: Not Ready" in result.output
    assert "Summary: 1/3 passed, 1 failed, 1 skipped." in result.output


def test_check_command_shows_failures_warnings_and_recommendations(
    monkeypatch,
    tmp_path,
):
    monkeypatch.setattr(cli, "run_checks", severity_run)

    result = runner.invoke(cli.app, ["check", str(tmp_path)])

    assert result.exit_code == 1
    assert "[FAIL] Compose file: No Docker Compose file was found." in result.output
    assert (
        "[SKIP] Compose YAML: skipped because Compose file was not found."
        in result.output
    )
    assert (
        "[RECOMMENDATION] Environment example: "
        ".env.example is missing while .env is being used."
        in result.output
    )
    assert (
        "[WARN] Environment variables: "
        ".env and .env.example variables do not match."
    ) in result.output


def test_check_command_exits_0_when_only_non_blocking_issues_are_found(
    monkeypatch,
    tmp_path,
):
    monkeypatch.setattr(cli, "run_checks", non_blocking_failure_run)

    result = runner.invoke(cli.app, ["check", str(tmp_path)])

    assert result.exit_code == 0
    assert "Status: Ready" in result.output
    assert (
        "[RECOMMENDATION] Environment example: "
        ".env.example is missing while .env is being used."
        in result.output
    )
    assert (
        "[WARN] Environment variables: "
        ".env and .env.example variables do not match."
        in result.output
    )


def test_check_command_does_not_write_report_without_report_flag(
    monkeypatch,
    tmp_path,
):
    monkeypatch.setattr(cli, "run_checks", run_ready)

    result = runner.invoke(cli.app, ["check", str(tmp_path)])

    assert result.exit_code == 0
    assert not (tmp_path / cli.DEFAULT_REPORT_FILENAME).exists()


def test_check_command_writes_default_json_report(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "run_checks", run_ready)

    result = runner.invoke(cli.app, ["check", str(tmp_path), "--report"])

    report_file = tmp_path / cli.DEFAULT_REPORT_FILENAME
    report = json.loads(report_file.read_text(encoding="utf-8"))

    assert result.exit_code == 0
    assert f"Report written to {report_file}" in result.output
    assert report["project_path"] == str(tmp_path)
    assert report["status"] == "Ready"
    assert report["exit_code"] == 0
    assert report["summary"] == {
        "total": 3,
        "passed": 3,
        "failed": 0,
        "skipped": 0,
    }
    assert report["checks"] == [
        {"name": "Docker CLI", "status": "pass", "message": "ok"},
        {"name": "Docker daemon", "status": "pass", "message": "ok"},
        {"name": "Docker Compose", "status": "pass", "message": "ok"},
    ]
    assert report["errors"] == []
    assert report["warnings"] == []
    assert report["recommendations"] == []


def test_check_command_writes_custom_json_report_name(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "run_checks", run_ready)

    result = runner.invoke(cli.app, ["check", str(tmp_path), "--report", "result.json"])

    report_file = tmp_path / "result.json"
    report = json.loads(report_file.read_text(encoding="utf-8"))

    assert result.exit_code == 0
    assert f"Report written to {report_file}" in result.output
    assert report["status"] == "Ready"


def test_check_command_writes_custom_json_report_path(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "run_checks", run_ready)
    report_dir = tmp_path / "reports"
    report_dir.mkdir()
    report_file = report_dir / "result.json"

    result = runner.invoke(
        cli.app,
        ["check", str(tmp_path), "--report", str(report_file)],
    )
    report = json.loads(report_file.read_text(encoding="utf-8"))

    assert result.exit_code == 0
    assert f"Report written to {report_file}" in result.output
    assert report["status"] == "Ready"


def test_check_command_reports_not_ready_in_json_report(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "run_checks", run_not_ready)

    result = runner.invoke(cli.app, ["check", str(tmp_path), "--report"])

    report_file = tmp_path / cli.DEFAULT_REPORT_FILENAME
    report = json.loads(report_file.read_text(encoding="utf-8"))

    assert result.exit_code == 1
    assert report["status"] == "Not Ready"
    assert report["exit_code"] == 1
    assert report["summary"] == {"total": 3, "passed": 1, "failed": 1, "skipped": 1}
    assert report["errors"] == [
        {"check": "Compose file", "message": "No Docker Compose file was found."}
    ]
    assert report["warnings"] == []
    assert report["recommendations"] == []


def test_check_command_writes_warnings_and_recommendations_in_json_report(
    monkeypatch,
    tmp_path,
):
    monkeypatch.setattr(cli, "run_checks", severity_run)

    result = runner.invoke(cli.app, ["check", str(tmp_path), "--report"])

    report_file = tmp_path / cli.DEFAULT_REPORT_FILENAME
    report = json.loads(report_file.read_text(encoding="utf-8"))

    assert result.exit_code == 1
    assert report["errors"] == [
        {"check": "Compose file", "message": "No Docker Compose file was found."}
    ]
    assert report["warnings"] == [
        {
            "check": "Environment variables",
            "message": ".env and .env.example variables do not match.",
        }
    ]
    assert report["recommendations"] == [
        {
            "check": "Environment example",
            "message": ".env.example is missing while .env is being used.",
        }
    ]


def test_check_command_writes_exit_0_report_for_non_blocking_issues(
    monkeypatch,
    tmp_path,
):
    monkeypatch.setattr(cli, "run_checks", non_blocking_failure_run)

    result = runner.invoke(cli.app, ["check", str(tmp_path), "--report"])

    report_file = tmp_path / cli.DEFAULT_REPORT_FILENAME
    report = json.loads(report_file.read_text(encoding="utf-8"))

    assert result.exit_code == 0
    assert report["status"] == "Ready"
    assert report["exit_code"] == 0
    assert report["summary"] == {"total": 3, "passed": 1, "failed": 2, "skipped": 0}
    assert report["errors"] == []
    assert report["warnings"] == [
        {
            "check": "Environment variables",
            "message": ".env and .env.example variables do not match.",
        }
    ]
    assert report["recommendations"] == [
        {
            "check": "Environment example",
            "message": ".env.example is missing while .env is being used.",
        }
    ]


def test_check_command_exits_2_when_report_parent_path_does_not_exist(
    monkeypatch,
    tmp_path,
):
    monkeypatch.setattr(cli, "run_checks", run_ready)

    result = runner.invoke(
        cli.app,
        ["check", str(tmp_path), "--report", str(tmp_path / "missing" / "report.json")],
    )

    assert result.exit_code == 2
    assert "Report path does not exist" in result.output
    assert not (tmp_path / "missing" / "report.json").exists()


def test_check_command_rejects_extra_argument_without_report(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "run_checks", run_ready)

    result = runner.invoke(cli.app, ["check", str(tmp_path), "unexpected.json"])

    assert result.exit_code == 2
    assert "Unexpected argument: unexpected.json" in result.output


def test_check_command_rejects_multiple_report_arguments(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "run_checks", run_ready)

    result = runner.invoke(
        cli.app,
        ["check", str(tmp_path), "--report", "one.json", "two.json"],
    )

    assert result.exit_code == 2
    assert "Unexpected argument: two.json" in result.output


def test_check_command_uses_custom_compose_file(monkeypatch, tmp_path):
    calls = []
    compose_file = tmp_path / "custom.compose.yaml"
    compose_file.write_text("services:\n  web:\n    image: nginx\n", encoding="utf-8")

    def fake_run_checks(project_path, only=None, compose_file=None):
        calls.append(compose_file)
        return ready_run()

    monkeypatch.setattr(cli, "run_checks", fake_run_checks)

    result = runner.invoke(
        cli.app,
        ["check", str(tmp_path), "--compose", "custom.compose.yaml"],
    )

    assert result.exit_code == 0
    assert calls == [compose_file]


def test_check_command_uses_absolute_custom_compose_file(monkeypatch, tmp_path):
    calls = []
    compose_file = tmp_path / "custom.compose.yaml"
    compose_file.write_text("services:\n  web:\n    image: nginx\n", encoding="utf-8")

    def fake_run_checks(project_path, only=None, compose_file=None):
        calls.append(compose_file)
        return ready_run()

    monkeypatch.setattr(cli, "run_checks", fake_run_checks)

    result = runner.invoke(
        cli.app,
        ["check", str(tmp_path), "--compose", str(compose_file)],
    )

    assert result.exit_code == 0
    assert calls == [compose_file]


def test_check_command_exits_2_when_custom_compose_file_is_missing(
    monkeypatch,
    tmp_path,
):
    monkeypatch.setattr(cli, "run_checks", run_ready)

    result = runner.invoke(
        cli.app,
        ["check", str(tmp_path), "--compose", "missing.compose.yaml"],
    )

    assert result.exit_code == 2
    assert "Docker Compose file does not exist" in result.output


def test_check_command_exits_2_when_compose_file_path_is_not_provided(
    monkeypatch, 
    tmp_path,
):
    monkeypatch.setenv("TYPER_USE_RICH", "0")
    result = runner.invoke(cli.app, ["check", str(tmp_path), "--compose"], color=False)

    assert result.exit_code == 2
    assert "requires an argument" in re.sub(r"\x1b\[[0-9;]*m", "", result.output)


def test_check_command_runs_only_selected_checks(monkeypatch, tmp_path):
    calls = []

    def fake_run_checks(project_path, only=None, compose_file=None):
        calls.append(only)
        return filtered_ready_run(project_path, only=only)

    monkeypatch.setattr(cli, "run_checks", fake_run_checks)

    result = runner.invoke(
        cli.app,
        ["check", str(tmp_path), "--only", "docker"],
    )

    assert result.exit_code == 0
    assert calls == [
        {
            "Docker CLI",
            "Docker daemon",
            "Docker Compose",
            "Compose file",
            "Compose YAML",
            "Compose services",
            "Compose build",
            "Compose build contexts",
            "Compose build context Dockerfiles",
        }
    ]
    assert "[PASS] Docker CLI: ok" in result.output
    assert "[PASS] Docker Compose: ok" in result.output
    assert "[PASS] Docker daemon: ok" in result.output
    assert "Summary: 3/3 passed, 0 failed, 0 skipped." in result.output


def test_check_command_rejects_invalid_only_group(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "run_checks", run_ready)

    result = runner.invoke(
        cli.app,
        ["check", str(tmp_path), "--only", "docker,nope"],
    )

    assert result.exit_code == 2
    assert "Invalid check group(s): nope" in result.output


def test_check_command_rejects_empty_only_value(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "run_checks", run_ready)

    result = runner.invoke(cli.app, ["check", str(tmp_path), "--only", ","])

    assert result.exit_code == 2
    assert "No check groups were provided for --only." in result.output


def test_check_command_writes_report_for_only_checks(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "run_checks", filtered_ready_run)

    result = runner.invoke(
        cli.app,
        ["check", str(tmp_path), "--only", "network", "--report"],
    )
    report_file = tmp_path / cli.DEFAULT_REPORT_FILENAME
    report = json.loads(report_file.read_text(encoding="utf-8"))

    assert result.exit_code == 0
    assert report["summary"] == {"total": 2, "passed": 2, "failed": 0, "skipped": 0}
    assert report["checks"] == [
        {"name": "Compose host ports", "status": "pass", "message": "ok"},
        {"name": "Host port availability", "status": "pass", "message": "ok"},
    ]


def test_check_command_accepts_multiple_only_groups(monkeypatch, tmp_path):
    calls = []

    def fake_run_checks(project_path, only=None, compose_file=None):
        calls.append(only)
        return filtered_ready_run(project_path, only=only)

    monkeypatch.setattr(cli, "run_checks", fake_run_checks)

    result = runner.invoke(
        cli.app,
        ["check", str(tmp_path), "--only", "docker,env"],
    )

    assert result.exit_code == 0
    assert calls == [
        {
            "Docker CLI",
            "Docker daemon",
            "Docker Compose",
            "Compose file",
            "Compose YAML",
            "Compose services",
            "Compose build",
            "Compose build contexts",
            "Compose build context Dockerfiles",
            "Environment example",
            "Environment variables",
        }
    ]
    assert "[PASS] Docker CLI: ok" in result.output
    assert "[PASS] Environment example: ok" in result.output
    assert "Host port availability" not in result.output


def test_check_command_filters_display_to_critical_severity(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "run_checks", severity_run)

    result = runner.invoke(
        cli.app,
        ["check", str(tmp_path), "--severity", "Critical"],
    )

    assert result.exit_code == 1
    assert "[FAIL] Compose file: No Docker Compose file was found." in result.output
    assert "[PASS] Docker CLI: ok" not in result.output
    assert "Compose YAML" not in result.output
    assert "Environment example" not in result.output
    assert "Environment variables" not in result.output
    assert "Status: Not Ready" in result.output
    assert "Summary: 1/5 passed, 3 failed, 1 skipped." in result.output


def test_check_command_filters_display_to_warning_severity(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "run_checks", severity_run)

    result = runner.invoke(
        cli.app,
        ["check", str(tmp_path), "--severity", "Warning"],
    )

    assert result.exit_code == 1
    assert (
        "[WARN] Environment variables: "
        ".env and .env.example variables do not match."
        in result.output
    )
    assert "Docker CLI" not in result.output
    assert "[FAIL] Compose file" not in result.output
    assert "Compose YAML" not in result.output
    assert "Environment example" not in result.output


def test_check_command_filters_display_to_recommendations_severity(
    monkeypatch,
    tmp_path,
):
    monkeypatch.setattr(cli, "run_checks", severity_run)

    result = runner.invoke(
        cli.app,
        ["check", str(tmp_path), "--severity", "Recommendations"],
    )

    assert result.exit_code == 1
    assert (
        "[RECOMMENDATION] Environment example: "
        ".env.example is missing while .env is being used."
    ) in result.output
    assert "Docker CLI" not in result.output
    assert "Compose file" not in result.output
    assert "Compose YAML" not in result.output
    assert "Environment variables" not in result.output


def test_check_command_accepts_multiple_severity_levels(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "run_checks", severity_run)

    result = runner.invoke(
        cli.app,
        ["check", str(tmp_path), "--severity", "Warning,Recommendations"],
    )

    assert result.exit_code == 1
    assert "Compose YAML" not in result.output
    assert "Environment example" in result.output
    assert "Environment variables" in result.output
    assert "[FAIL] Compose file" not in result.output


def test_check_command_rejects_invalid_severity_level(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "run_checks", run_ready)

    result = runner.invoke(
        cli.app,
        ["check", str(tmp_path), "--severity", "Critical,nope"],
    )

    assert result.exit_code == 2
    assert "Invalid severity level(s): nope" in result.output
    assert (
        "Accepted severity levels: Critical, Recommendations, Warning"
        in result.output
    )


def test_check_command_rejects_empty_severity_value(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "run_checks", run_ready)

    result = runner.invoke(cli.app, ["check", str(tmp_path), "--severity", ","])

    assert result.exit_code == 2
    assert "No severity levels were provided for --severity." in result.output
