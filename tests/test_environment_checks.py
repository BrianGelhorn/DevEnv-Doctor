from devenv_doctor.checks import environment


def test_has_env_file_detects_env_file(tmp_path):
    (tmp_path / ".env").write_text(
        "DATABASE_URL=postgres://example\n",
        encoding="utf-8",
    )

    assert environment.has_env_file(tmp_path) is True


def test_has_env_file_rejects_missing_env_file(tmp_path):
    assert environment.has_env_file(tmp_path) is False


def test_check_env_example_exists_passes_when_env_example_exists(tmp_path):
    (tmp_path / ".env").write_text(
        "DATABASE_URL=postgres://example\n",
        encoding="utf-8",
    )
    (tmp_path / ".env.example").write_text("DATABASE_URL=\n", encoding="utf-8")

    assert environment.check_env_example_exists(tmp_path) == (
        True,
        ".env.example exists for the .env file.",
    )


def test_check_env_example_exists_fails_when_env_example_is_missing(tmp_path):
    (tmp_path / ".env").write_text(
        "DATABASE_URL=postgres://example\n",
        encoding="utf-8",
    )

    assert environment.check_env_example_exists(tmp_path) == (
        False,
        ".env.example is missing while .env is being used.",
    )


def test_check_env_example_exists_reports_missing_env_file(tmp_path):
    assert environment.check_env_example_exists(tmp_path) == (
        False,
        "No .env file was found.",
    )
