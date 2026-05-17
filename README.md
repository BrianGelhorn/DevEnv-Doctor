# devenv-doctor

**DevEnv Doctor** is a CLI tool that analyzes Docker and Docker Compose projects to determine whether they are ready to run in a local development environment.

It checks a project against predefined operational policies and best practices, reports detected issues by severity, and provides actionable recommendations to fix local environment problems before starting development.

## Why this project exists

Local development environments often fail because of missing files, invalid Docker Compose configuration, unclear setup requirements, or inconsistent project structure.

`devenv-doctor` helps developers quickly detect common problems in Docker-based projects before wasting time debugging environment issues manually.

## Current scope

The current version completes the initial CLI scope.

It supports:

- Running checks against a target project directory.
- Running checks against the current directory.
- Using a custom Docker Compose file.
- Validating missing or invalid project paths.
- Validating missing or invalid Docker Compose files.
- Filtering issues by severity.
- Reporting detected issues with clear messages.
- Returning meaningful exit codes.
- Displaying help information for CLI usage.

## Installation

```bash
curl -L -o devenv-doctor-linux-amd64 \
  https://github.com/BrianGelhorn/devenv-doctor/releases/latest/download/devenv-doctor-linux-amd64
chmod +x devenv-doctor-linux-amd64
sudo mv devenv-doctor-linux-amd64 /usr/local/bin/devenv-doctor
```
Then execute `devenv-doctor --help` to check if it was installed succesfully.
## Basic usage

```bash
devenv-doctor check .
```

Check a specific project directory:

```bash
devenv-doctor check /path/to/project
```

Use a custom Docker Compose file:

```bash
devenv-doctor check . --compose docker-compose.dev.yml
```

Filter results by severity:

```bash
devenv-doctor check . --severity error
```

Show help:

```bash
devenv-doctor --help
```

```bash
devenv-doctor check --help
```

## Exit codes

| Exit code | Meaning |
|---|---|
| `0` | The project is ready. |
| `1` | Blocking issues were detected. |
| `2` | Invalid command usage or invalid input. |

## Documentation

- [MVP](./docs/mvp.md)
- [Use Cases](./docs/use-cases.md)
- [Requirements](./docs/requirements.md)
- [Rules](./docs/rules.md)

## Project status

The initial CLI milestone is complete.

All functional requirements defined for the initial CLI scope have been implemented and tested, including command handling, project path validation, custom Docker Compose file support, severity filtering, help output, issue reporting, and expected exit code behavior.

Future iterations will focus on expanding the rule engine, improving Docker Compose analysis, and adding a readiness scoring system based on detected issues and severity levels.

## Tech stack

- Python
- Typer
- Pytest
- Docker
- Docker Compose

## Goal

The goal of `devenv-doctor` is to provide a practical diagnostic tool for Docker-based development environments, with clear feedback that helps developers identify and fix setup problems faster.
