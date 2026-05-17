from pathlib import Path

from dotenv import dotenv_values


def has_env_file(project_path: Path) -> bool:
    return (project_path / ".env").is_file()


def has_env_example_file(project_path: Path) -> bool:
    return (project_path / ".env.example").is_file()


def parse_env_keys(env_file: Path) -> set[str]:
    return set(dotenv_values(env_file).keys())
