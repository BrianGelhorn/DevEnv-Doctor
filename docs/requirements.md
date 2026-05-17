# Requirements

## Functional Requirements

- FR-001: The CLI must provide a `check` command. ✅
- FR-002: The CLI must accept a target project path. ✅
- FR-003: The CLI must detect if Docker is installed. ✅
- FR-004: The CLI must detect if the Docker daemon is running. ✅
- FR-005: The CLI must detect if Docker Compose is available. ✅
- FR-006: The CLI must detect a Compose file. ✅
- FR-007: The CLI must validate Compose YAML syntax. ✅
- FR-008: The CLI must validate that the `services` section exists and is not empty. ✅
- FR-009: The CLI must validate that each service has a valid `image` or `build`. ✅
- FR-010: The CLI must validate that build contexts referenced by Compose services exist. ✅
- FR-011: The CLI must validate that Dockerfile exists for services using build. ✅
- FR-012: The CLI must detect duplicated host ports. ✅
- FR-013: The CLI must detect if the port is already being used by another process. ✅
- FR-014: The CLI must check `.env.example` when environment variables are used. ✅
- FR-015: The CLI must show a local readiness status. ✅
- FR-016: The CLI must show warnings, failures and recommendations. ✅
- FR-017: The CLI must return exit code `0` if no blocking issues are found. ✅
- FR-018: The CLI must return exit code `1` if blocking issues are found. ✅
- FR-019: The CLI must return exit code `2` if the tool fails to execute properly. ✅
- FR-020: The CLI must detect and notify if the permissions are not enough to check the socket of Docker or scan ports. ✅
- FR-021: The CLI must validate the parity between `.env` and `.env.example` ✅
- FR-022: The CLI must be able to generate a machine-readable report file. ✅
- FR-023: The CLI must be able to run only the specified checks by the developer. ✅
- FR-024: The CLI must be able to specify a custom Docker Compose file to run the analysis with. ✅
- FR-025: The CLI must be able to filter and display only the selected severity levels. ✅
- FR-026: The CLI must show how to use the tool correctly.

## Non-Functional Requirements

- NFR-001: The CLI should provide clear and readable terminal output.
- NFR-002: The checks should be deterministic.
- NFR-003: The tool should run on Linux.
- NFR-004: The codebase should be modular enough to add new checks later.
- NFR-005: The project should include automated tests.
- NFR-006: The tool should avoid modifying user files in the MVP.
- NFR-007: The CLI should return results quickly for small and medium projects.
- NFR-008: The CLI should not require external services or internet access to run the MVP checks.
- NFR-009: The CLI should provide standard help output through `--help`.
- NFR-010: The CLI should return meaningful exit codes.

### Exit codes

- `0`: No blocking issues were found.
- `1`: Blocking issues were found.
- `2`: The tool failed to execute properly.
