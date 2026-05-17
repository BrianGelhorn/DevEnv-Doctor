from devenv_doctor.checks import environment, environment_utils


def test_has_env_file_detects_env_file(tmp_path):
    (tmp_path / ".env").write_text(
        "DATABASE_URL=postgres://example\n",
        encoding="utf-8",
    )

    assert environment_utils.has_env_file(tmp_path) is True


def test_has_env_file_rejects_missing_env_file(tmp_path):
    assert environment_utils.has_env_file(tmp_path) is False


def test_has_env_example_file_detects_env_example_file(tmp_path):
    (tmp_path / ".env.example").write_text("DATABASE_URL=\n", encoding="utf-8")

    assert environment_utils.has_env_example_file(tmp_path) is True


def test_has_env_example_file_rejects_missing_env_example_file(tmp_path):
    assert environment_utils.has_env_example_file(tmp_path) is False


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


def test_check_env_variables_match_accepts_matching_variables(tmp_path):
    (tmp_path / ".env").write_text(
        (
            "# local values\n"
            "DATABASE_URL=postgres://example\n"
            "export REDIS_URL=redis://localhost\n"
            'QUOTED_VALUE="hello=world"\n'
        ),
        encoding="utf-8",
    )
    (tmp_path / ".env.example").write_text(
        "REDIS_URL=\nDATABASE_URL=\nQUOTED_VALUE=\n",
        encoding="utf-8",
    )

    assert environment.check_env_variables_match(tmp_path) == (
        True,
        ".env and .env.example variables match.",
    )


def test_check_env_variables_match_lists_missing_and_extra_variables(tmp_path):
    (tmp_path / ".env").write_text(
        "DATABASE_URL=postgres://example\nSECRET_KEY=abc123\n",
        encoding="utf-8",
    )
    (tmp_path / ".env.example").write_text(
        "DATABASE_URL=\nREDIS_URL=\n",
        encoding="utf-8",
    )

    assert environment.check_env_variables_match(tmp_path) == (
        False,
        ".env and .env.example variables do not match ("
        "missing in .env.example: SECRET_KEY; extra in .env.example: REDIS_URL).",
    )


def test_check_env_variables_match_reports_missing_env_file(tmp_path):
    (tmp_path / ".env.example").write_text("DATABASE_URL=\n", encoding="utf-8")

    assert environment.check_env_variables_match(tmp_path) == (
        False,
        "No .env file was found.",
    )


def test_check_env_variables_match_reports_missing_env_example_file(tmp_path):
    (tmp_path / ".env").write_text(
        "DATABASE_URL=postgres://example\n",
        encoding="utf-8",
    )

    assert environment.check_env_variables_match(tmp_path) == (
        False,
        ".env.example file was not found.",
    )
