from pathlib import Path


def has_env_file(project_path: Path) -> bool:
    return (project_path / ".env").is_file()


def check_env_example_exists(project_path: Path) -> tuple[bool, str]:
    if not has_env_file(project_path):
        return False, "No .env file was found."

    if not (project_path / ".env.example").is_file():
        return False, ".env.example is missing while .env is being used."

    return True, ".env.example exists for the .env file."
