from subprocess import CompletedProcess, TimeoutExpired

from devenv_doctor.core import command as command_module


def test_command_output_returns_stdout_on_success(monkeypatch):
    def fake_run(command, capture_output, text, check, timeout):
        assert command == ["docker", "--version"]
        assert capture_output is True
        assert text is True
        assert check is False
        assert timeout == 5
        return CompletedProcess(command, 0, stdout="Docker version 1\n", stderr="")

    monkeypatch.setattr(command_module, "run", fake_run)

    assert command_module.command_output(["docker", "--version"]) == (
        0,
        "Docker version 1",
    )


def test_command_output_returns_stderr_on_failure(monkeypatch):
    def fake_run(command, capture_output, text, check, timeout):
        return CompletedProcess(command, 1, stdout="", stderr="boom\n")

    monkeypatch.setattr(command_module, "run", fake_run)

    assert command_module.command_output(["docker", "info"]) == (1, "boom")


def test_command_output_handles_missing_command(monkeypatch):
    def fake_run(command, capture_output, text, check, timeout):
        raise FileNotFoundError(command[0])

    monkeypatch.setattr(command_module, "run", fake_run)

    assert command_module.command_output(["docker"]) == (
        127,
        "Command not found: docker",
    )


def test_command_output_handles_timeout(monkeypatch):
    def fake_run(command, capture_output, text, check, timeout):
        raise TimeoutExpired(command, timeout)

    monkeypatch.setattr(command_module, "run", fake_run)

    assert command_module.command_output(["docker", "info"]) == (
        124,
        "The program timed out after 5 seconds",
    )
