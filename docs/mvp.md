# MVP

## Problem

Developers often lose time trying to understand why a Docker/Compose project does not run locally.

## Summary
CLI command `devenv-doctor check .` that checks a Docker Compose project and the local environment for common issues, then returns a local readiness status with warnings, failures and actionable recommendations.

## Features

### System checks

- Detect if Docker is installed.
- Detect if the Docker daemon is running.
- Detect if Docker Compose is available.
- Detect whether the ports used in the project are already being used.

### Project checks

- Detect if there is a Compose file.
- Validate Compose YAML syntax.
- Validate that the `services` section exists.
- Validate that each service has either `image` or `build`.
- Validate that build contexts exist.
- Validate that Dockerfiles exist for services using `build`.
- Detect duplicated host ports.

### Environment checks

- Check if `.env.example` exists when environment variables are used.
- Check if referenced `env_file` files exist.
- Check parity of keys between `.env` and `.env.example`.

### Feedback

- Show a binary local readiness status: `Ready`, `Ready with warnings` or `Not Ready`.
- Generate an optional quality score.
- Show a summary of passed checks, warnings, and failures.
- Show actionable recommendations.
- Generation of a machine-readable report JSON file to use in other tools, scripts or pipelines.

## Out of Scope

- GitHub Action integration.
- JSON reports.
- Markdown reports.
- SARIF reports.
- Auto-fix.
- Web dashboard.
- Kubernetes checks.
- Terraform checks.
- Deep Dockerfile analysis.
- Configurable rules.
- AI-based recommendations.

## Success Criteria

The MVP is complete when a user can run:

```bash
devenv-doctor check .