# DevEnv Doctor

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
- Generating machine-readable JSON reports.
- Reporting detected issues with clear messages.
- Returning meaningful exit codes.
- Displaying help information for CLI usage.

## Requirements

- Linux AMD64
- Docker
- Docker Compose

## Installation

Download and install the latest Linux binary from GitHub Releases:

```bash
curl -L -o devenv-doctor-linux-amd64 \
  https://github.com/BrianGelhorn/devenv-doctor/releases/latest/download/devenv-doctor-linux-amd64

chmod +x devenv-doctor-linux-amd64
sudo mv devenv-doctor-linux-amd64 /usr/local/bin/devenv-doctor
```

Verify the installation:

```bash
devenv-doctor --help
```

## Basic usage

Analyze the current directory:

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

Filter displayed issues by severity:

```bash
devenv-doctor check . --severity Critical
```

Filter by multiple severity levels:

```bash
devenv-doctor check . --severity Critical,Warning
```

Run only specific check groups:

```bash
devenv-doctor check . --only docker,env
```

Generate a JSON report:

```bash
devenv-doctor check . --report
```

Generate a JSON report with a custom file name:

```bash
devenv-doctor check . --report result.json
```

Show help:

```bash
devenv-doctor --help
devenv-doctor check --help
```

## Example output

```bash
$ devenv-doctor check .

Checking /home/user/project
[PASS] Docker CLI: Docker CLI is installed.
[PASS] Docker daemon: Docker daemon is accessible
[PASS] Docker Compose: Docker Compose is available
[PASS] Compose file: Docker Compose file found: compose.yaml
[PASS] Compose YAML: Docker Compose file has valid YAML syntax.
[PASS] Compose services: The services section exists and is not empty.
[FAIL] Compose host ports: The following host ports are duplicated: 8000 (api, web).

Status: Not Ready
Summary: 6/7 passed, 1 failed, 0 skipped.
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

All functional requirements defined for the initial CLI scope have been implemented and tested, including command handling, project path validation, custom Docker Compose file support, severity filtering, help output, issue reporting, JSON report generation, and expected exit code behavior.

Future iterations will focus on expanding the rule engine, improving Docker Compose analysis, and adding a readiness scoring system based on detected issues and severity levels.

## Tech stack

- Python
- Typer
- Pytest
- Ruff
- Docker
- Docker Compose
- GitHub Actions

## Goal

The goal of `devenv-doctor` is to provide a practical diagnostic tool for Docker-based development environments, with clear feedback that helps developers identify and fix setup problems faster.
