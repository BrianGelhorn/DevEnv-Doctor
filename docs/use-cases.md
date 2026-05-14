# Use Cases

## UC-001 - Check a local Docker/Compose project

### Actor: Developer

### Description:
The developer runs the CLI in a local project to determine whether it is ready to run locally.

### Main flow:

1. The developer opens a terminal.
2. The developer runs `devenv-doctor check .`.
3. The CLI scans the local environment.
4. The CLI checks the Docker Compose file configurations.
5. The CLI checks the enviroment files.
6. The CLI checks the Dockerfiles of the used services.
7. The CLI exits with a meaningful exit code.

### Expected result:  
The developer understands whether the project is `Ready` or `Not Ready` tu run locally.

### Alternative flows

#### AF-001: Docker is not available
- If Docker is not installed or cannot be executed, the CLI reports a blocking issue and marks the project as `Not Ready`.

#### AF-002: Docker daemon is not running
- If Docker daemon is not running or cannot be accessed, the CLI reports a blocking issue and mark the project as `Not Ready`.

#### AF-003: Docker Compose is not available
- If Docker Compose is not installed or cannot be accessed, the CLI reports a blocking issue and mark the project as `Not Ready`.

#### AF-004: Docker Compose File is missing
- If no Docker Compose file is found, the CLI reports a blocking issue and mark the project as `Not Ready`.

#### AF-005: Docker Compose File is invalid
- If the Docker Compose file cannot be parsed correctly as YAML, the CLI reports a blocking issue and mark the project as `Not Ready`.

#### AF-006: Docker Compose has duplicated host ports
- If the Docker Compose defines the same host port for different services, the CLI reports a blocking issue and mark the project as `Not Ready`.
