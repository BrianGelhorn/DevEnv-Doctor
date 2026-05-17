from pathlib import Path

from devenv_doctor.checks.environment_utils import (
    has_env_example_file,
    has_env_file,
    parse_env_keys,
)


def check_env_example_exists(project_path: Path) -> tuple[bool, str]:
    if not has_env_file(project_path):
        return False, "No .env file was found."

    if not has_env_example_file(project_path):
        return False, ".env.example is missing while .env is being used."

    return True, ".env.example exists for the .env file."


def check_env_variables_match(project_path: Path) -> tuple[bool, str]:
    if not has_env_file(project_path):
        return False, "No .env file was found."
    if not has_env_example_file(project_path):
        return False, ".env.example file was not found."

    env_keys = parse_env_keys(project_path / ".env")
    env_example_keys = parse_env_keys(project_path / ".env.example")

    missing_in_example = sorted(env_keys - env_example_keys)
    extra_in_example = sorted(env_example_keys - env_keys)

    if missing_in_example or extra_in_example:
        issues = []
        if missing_in_example:
            issues.append(f"missing in .env.example: {', '.join(missing_in_example)}")
        if extra_in_example:
            issues.append(f"extra in .env.example: {', '.join(extra_in_example)}")
        issue_text = "; ".join(issues)
        return False, f".env and .env.example variables do not match ({issue_text})."

    return True, ".env and .env.example variables match."
