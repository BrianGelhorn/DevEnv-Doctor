# Use Cases

## UC-001 - Check a local Docker/Compose project

### Principal Actor: Developer

### Secondary Actor: Docker Engine, Docker Compose, Local Filesystem

### Objective

As a Developer I want to know if the local project is `Ready` or `Not Ready` to run.

### Description:

The developer runs the CLI in a local project to analyze it and determine whether it is ready to run locally.

### Preconditions

- The CLI program is installed and available to execute.
- The Developer has access to the path of the project.

### Main flow:

1. The developer opens a terminal.
2. The developer runs `devenv-doctor check .`.
3. The CLI scans the local environment.
4. The CLI checks the Docker Compose file configurations.
5. The CLI checks the environment files.
6. The CLI checks the Dockerfiles of the used services.
7. The CLI does not detect any blocking issue or warning.
8. The CLI displays the status as `Ready`.
9. The CLI exits with code 0.

### Expected result:  
The developer understands whether the project is `Ready` or `Not Ready` to run locally.

### Alternative flows

#### AF-001: Docker is not available
- If Docker is not installed or cannot be executed, the CLI reports a blocking issue and marks the project as `Not Ready` and exits with code 1.

#### AF-002: Docker daemon is not running
- If Docker daemon is not running or cannot be accessed, the CLI reports a blocking issue and marks the project as `Not Ready` and exits with code 1.

#### AF-003: Docker Compose is not available
- If Docker Compose is not installed or cannot be accessed, the CLI reports a blocking issue and marks the project as `Not Ready` and exits with code 1.

#### AF-004: Docker Compose file is missing
- If no Docker Compose file is found, the CLI reports a blocking issue and marks the project as `Not Ready` and exits with code 1.

#### AF-005: Docker Compose file is invalid
- If the Docker Compose file cannot be parsed correctly as YAML, the CLI reports a blocking issue and marks the project as `Not Ready` and exits with code 1.

#### AF-006: Docker Compose has duplicated host ports
- If the Docker Compose defines the same host port for different services, the CLI reports a blocking issue and marks the project as `Not Ready` and exits with code 1.

#### AF-007: Docker Compose file has no services
- If the Docker Compose file does not define any service, the CLI reports a blocking issue and marks the project as `Not Ready` and exits with code 1.

#### AF-008: A service `build` or `image` is missing
- If a service does not define either a `build` path or an `image` in the Docker Compose file, the CLI reports a blocking issue and marks the project as `Not Ready` and exits with code 1.

#### AF-009: A service Dockerfile is missing
- If a service defines a build context path that exists but does not have Dockerfile, the CLI reports a blocking issue and marks the project as `Not Ready` and exits with code 1.

#### AF-010: The environment file is missing
- If a required `env_file` does not exist or cannot be accessed, the CLI reports a blocking issue and marks the project as `Not Ready` and exits with code 1.

#### AF-011: The defined port in Docker Compose is busy
- If a service defines a host port that is already being used by another process in the system, the CLI shows the used port, reports a blocking issue and marks the project as `Not Ready` and exits with code 1. 

#### AF-012: The `env.example` is missing or is not paired
- If the project does not have an `env.example`, the CLI reports a non-blocking issue and marks the project as `Ready with warnings` and exits with code 0.

#### AF-013: The CLI cannot complete the analysis due to an execution failure
- If the CLI cannot complete the analysis due to an uknown error during the execution, the CLI exits with code 2.

### Related Functional Requirements
- FR-001
- FR-002
- FR-003
- FR-004
- FR-005
- FR-006
- FR-007
- FR-008
- FR-009
- FR-010
- FR-011
- FR-012
- FR-013
- FR-014
- FR-015
- FR-016
- FR-017
- FR-018
- FR-019
- FR-020
- FR-021

---

## UC-002 - Generate a machine-readable report file

### Principal Actor: Developer

### Secondary Actor: Local Filesystem

### Objective

As a Developer I want generate a report file of the analysis in JSON format to integrate it to scripts, pipelines or other tools.

### Description:

The Developer runs the CLI in a local project and requests a JSON report file. The CLI analyzes the project and saves the result in a structured JSON file containing the final readiness status, errors, warnings, recommendations, and exit code.

### Preconditions

- The CLI program is installed and available to execute.
- The Developer has access to the path of the project.
- The Developer has write permissions in the target output path.

### Main flow:

1. The developer opens a terminal.
2. The developer runs `devenv-doctor check . --report`.
3. The CLI analyzes the local project.
4. The CLI does not detect any blocking issue or warning.
5. The CLI generates a JSON file with final status `Ready`.
6. The CLI saves the JSON file in the target project path.
7. The CLI exits with code 0.

### Expected result:  
The developer generates a machine-readable file containing the analysis result and the project readiness status.

### Alternative flows

#### AF-001: Non-blocking warnings are found
- If the CLI does not detect blocking issues but detects one or more warnings, generates the JSON file report with final status `Ready with warnings` and exits with code 0.

#### AF-002: Blocking issues are found
- If the CLI detects one or more blocking issues, generates the JSON file report with final status `Not Ready` and exits with code 1.

#### AF-003: The developer uses an existing custom path
- If the developer uses an existing custom path for saving the report file, the CLI executes the analysis and generates the JSON report file, saves it in the file path specified by the developer and exits with the corresponding exit code.

#### AF-004: The developer uses a non-existing custom path
- If the developer uses a non-existing custom path for saving the report file, the CLI tells the developer that the path does not exist and exits with code 2.

### Related Functional Requirements
- FR-001
- FR-002
- FR-017
- FR-018
- FR-019
- FR-022

---

## UC-003 - Run only selected checks 

### Principal Actor: Developer

### Objective

As a Developer I want to execute the CLI running only the checks that I select.

### Description:

The Developer runs the CLI in a local project. The CLI analyzes the project only checking what the user specified.

### Preconditions

- The CLI program is installed and available to execute.
- The Developer has access to the path of the project.

### Main flow:

1. The developer opens a terminal.
2. The developer runs `devenv-doctor check . --only` and the check names separated by commas.
3. The CLI analyzes the local project running only the selected checks.
4. The CLI does not detect any blocking issue or warning.
5. The CLI displays the status as `Ready`.
6. The CLI exits with status `Ready` and exit code 0.

### Expected result:  
The developer runs the analysis of the project only running the checks he specified.

### Alternative flows

#### AF-001: Non-blocking warnings are found
- If the CLI does not detect blocking issues but detects one or more warnings, displays the status `Ready with warnings` and exits with code 0.

#### AF-002: Blocking issues are found
- If the CLI detects one or more blocking issues, displays the status `Not Ready` and exits with code 1.

### Related Functional Requirements
- FR-001
- FR-002
- FR-017
- FR-018
- FR-019
- FR-023

---

## UC-004 - Check project using custom Docker Compose file

### Principal Actor: Developer

### Secondary Actor: Docker Engine, Docker Compose, Local Filesystem

### Objective

As a Developer I want to execute the CLI at the target project but using a custom Docker Compose file.

### Description:

The Developer runs the CLI in a local project using a custom Docker Compose file. The CLI analyzes the project using the specified Docker Compose file instead of using the default one inside the project.

### Preconditions

- The CLI program is installed and available to execute.
- The Developer has access to the path of the project.
- The Developer has access to the path of the custom Docker Compose file

### Main flow:

1. The developer opens a terminal.
2. The developer runs `devenv-doctor check . --compose` and the custom Docker Compose file path.
3. The CLI analyzes the local project using the custom Docker Compose file.
4. The CLI does not detect any blocking issue or warning.
5. The CLI displays the status as `Ready`.
6. The CLI exits with status `Ready` and exit code 0.

### Expected result:  
The developer runs the analysis of the project using a custom Docker Compose file.

### Alternative flows

#### AF-001: Non-blocking warnings are found
- If the CLI does not detect blocking issues but detects one or more warnings, displays the status `Ready with warnings` and exits with code 0.

#### AF-002: Blocking issues are found
- If the CLI detects one or more blocking issues, displays the status `Not Ready` and exits with code 1.

#### AF-003: The specified custom Docker Compose file does not exist
- If the specified custom Docker Compose file does not exist, the CLI tells the Developer the specified Docker Compose file does not exists and exits with code 2.

#### AF-004: The custom Docker Compose file path is not provided
- If the Developer uses `--compose` without providing a file path, the CLI tells the Developer that he must specify a Docker Compose file and exits with code 2.

### Related Functional Requirements
- FR-001
- FR-002
- FR-017
- FR-018
- FR-019
- FR-024

---

## UC-005 - Show only selected issue severity levels

### Principal Actor: Developer

### Objective

As a Developer I want to execute the CLI showing only the issues that match with the severity levels I selected.

### Description:

The Developer runs the CLI in a local project using the `--severity` flag followed by the severity levels separated by commas. The CLI analyzes the project and displays only the issues matching the selected severity levels.

### Preconditions

- The CLI program is installed and available to execute.
- The Developer has access to the path of the project.

### Main flow:

1. The developer opens a terminal.
2. The developer runs `devenv-doctor check . --severity` and the severity levels separated by commas.
3. The CLI analyzes the local project.
4. The CLI filters the issues by the selected severity levels.
5. The CLI displays only the issues matching the selected severity levels.
6. The CLI displays the final readiness status.
7. The CLI exits with the corresponding exit code.

### Expected result:  
The developer runs the analysis of the project and sees only the severity levels he selected.

### Alternative flows

#### AF-001: The severity levels are invalid
- If one or more severity levels indicated by the Developer are invalid, the CLI will display the invalid severity levels, will tell the Developer that they are invalid and will exit with the exit code 2.

### Related Functional Requirements
- FR-001
- FR-002
- FR-017
- FR-018
- FR-019
- FR-025

---

## UC-006 - Show CLI usage information

### Principal Actor: Developer

### Objective

As a Developer I want to see information about how to use the CLI.

### Description:

The Developer runs the CLI with the `--help` flag. The CLI will display information about the options, checknames, commands, severity levels, how to use the CLI and basic usage examples.

### Preconditions

- The CLI program is installed and available to execute.

### Main flow:

1. The developer opens a terminal.
2. The developer runs `devenv-doctor --help`.
3. The CLI displays the available commands.
4. The CLI displays the available options.
5. The CLI displays the accepted severity levels.
6. The CLI displays the accepted check names.
7. The CLI displays basic usage examples.
8. The CLI exits with exit code 0.

### Expected result:  
The developer understands how to use the CLI commands and the available options.

### Alternative flows

#### AF-001: Help for the check command
- If the user runs `devenv-doctor check --help`, the CLI will display only the help information related to the `check` command.

### Related Functional Requirements
- FR-001
- FR-017
- FR-023
- FR-025