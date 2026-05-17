# Rules

## SYS-001 - Docker CLI installed

**Category:** System  
**Severity:** Blocking  
**Related requirement:** FR-003

### Description

Checks whether the Docker CLI is installed.

### Pass condition

The command `docker --version` returns successfully.

### Fail condition

The Docker command is not found or cannot be executed.

### Recommendation

Install Docker and make sure it is available in the system PATH.

## SYS-002 - Docker daemon is running

**Category:** System  
**Severity:** Blocking  
**Related requirement:** FR-004

### Description

Checks whether the Docker daemon is running and accessible.

### Skip condition

Skipped if Docker CLI is not installed.

### Pass condition

The command `docker info` returns successfully.

### Fail condition

Docker is installed but the daemon is not running or the current user cannot access it.

### Recommendation

Start the Docker daemon or check the Docker permissions.

## SYS-003 - Docker Compose is available

**Category:** System  
**Severity:** Blocking  
**Related requirement:** FR-005

### Description

Checks whether Docker Compose is installed and available.

### Pass condition

The command `docker compose version` returns successfully.

### Alternative pass condition

The command `docker-compose --version` returns successfully.

### Fail condition

Neither `docker compose version` nor `docker-compose --version` can be executed successfully.


### Recommendation

Install the Docker Compose plugin or update Docker to a version that includes Docker Compose.

## FILE-001 - Docker Compose file exists in project

**Category:** File  
**Severity:** Blocking  
**Related requirement:** FR-006

### Description

Checks whether a Docker Compose file exists in the project.

### Accepted filenames

- `compose.yml`
- `compose.yaml`
- `docker-compose.yml`
- `docker-compose.yaml`

### Pass condition

At least one accepted Compose file exists in the target project path.

### Fail condition

No accepted Compose file is in the target project path.

### Recommendation

Create a valid Docker Compose file or, if one already exists, rename it to one of the accepted filenames.

## FILE-002 - Dockerfile exists for services

**Category:** File  
**Severity:** Blocking  
**Related requirement:** FR-011

### Description

Checks whether a Dockerfile exists for each Compose service that uses `build`.

### Skip condition

Skipped if no valid Compose file could be loaded or if no service uses `build`.

### Pass condition

Every service using `build` has a Dockerfile in the expected build context.

### Fail condition

At least one service using `build` does not have a valid Dockerfile in the expected build context.

### Recommendation

Create a Dockerfile in the service build context or update the Compose `build` configuration to reference the correct Dockerfile path.

## CMP-001 - Docker Compose file has valid YAML syntax

**Category:** Compose  
**Severity:** Blocking  
**Related requirement:** FR-007

### Description

Checks whether the detected Docker Compose file has valid YAML syntax.

### Skip condition

Skipped if no valid Docker Compose file was found.

### Pass condition

The Docker Compose file can be parsed as valid YAML.

### Fail condition

The Docker Compose file cannot be parsed because it contains one or more YAML syntax errors.

### Recommendation

Fix the YAML syntax errors in the Docker Compose file.

## CMP-002 - Docker Compose file has a non-empty `services` section

**Category:** Compose  
**Severity:** Blocking  
**Related requirement:** FR-008

### Description

Checks whether the detected Docker Compose file has a non-empty `services` section.

### Skip condition

Skipped if no valid Docker Compose file could be loaded.

### Pass condition

The Docker Compose file has a `services` section and has at least one service defined.

### Fail condition

The Docker Compose file does not have a `services` section or the `services` section is empty.

### Recommendation

Add a `services` section and define at least one service in the Docker Compose file.

## CMP-003 - Each Docker Compose service has a valid `image` or `build`

**Category:** Compose  
**Severity:** Blocking  
**Related requirement:** FR-009

### Description

Checks whether each service of the detected Docker Compose file has a valid `build` or `image`.

### Skip condition

Skipped if no valid Docker Compose file could be loaded.

### Pass condition

Every Docker Compose service defines either `build` or `image`.

### Fail condition

At least one Docker Compose service does not define either `build` or `image`.

### Recommendation

Add an `image` reference or a `build` configuration to each service.

## CMP-004 - Each Docker Compose build context reference exists

**Category:** Compose  
**Severity:** Blocking  
**Related requirement:** FR-010

### Description

Checks whether each `build` context referenced by Docker Compose services points to an existing directory.

### Skip condition

Skipped if no valid Docker Compose file could be loaded.

### Pass condition

Every Docker Compose service using `build` references an existing build context directory.

### Fail condition

At least one Docker Compose service using `build` references a build context that does not exist.

### Recommendation

Update the `build` context path to reference an existing directory.

## CMP-005 - Defined Docker Compose services have no duplicated host ports

**Category:** Compose  
**Severity:** Blocking  
**Related requirement:** FR-012

### Description

Checks whether host ports defined in the Docker Compose file are unique across all services.

### Skip condition

Skipped if no valid Docker Compose file could be loaded.

### Pass condition

No host port is used by more than one Docker Compose service.

### Fail condition

At least one host port is used by multiple Docker Compose services.

### Recommendation

Change the duplicated host port so each exposed host port is unique.

## NET-001 - Host ports are available on the local system

**Category:** Networking  
**Severity:** Blocking  
**Related requirement:** FR-013

### Description

Checks whether host ports defined in the Docker Compose file are available on the local system.

### Skip condition

Skipped if no valid Docker Compose file could be loaded.

### Pass condition

All host ports defined in the Docker Compose file are available.

### Fail condition

At least one host port defined in the Docker Compose file is already being used by another process, or the tool cannot inspect local port usage because of insufficient permissions.

### Recommendation

Change the affected host port in the Docker Compose file or stop the process that is using the port.

## ENV-001 - `.env.example` file exists if `.env` file is being used

**Category:** Environment  
**Severity:** Recommendation  
**Related requirement:** FR-014

### Description

Checks whether `.env.example` file is present if the project is using a `.env` file.

### Skip condition

Skipped if `.env` file is missing.

### Pass condition

The `.env.example` file is not missing when using a `.env` file.

### Fail condition

The `.env.example` file is missing and the project is using a `.env` file.

### Recommendation

Create a `.env.example` file with the same variables defined in the `.env` file with example values.

## ENV-002 - `.env` and `.env.example` variables match

**Category:** Environment  
**Severity:** Warning  
**Related requirement:** FR-021

### Description

Checks whether the `.env.example` file has the same defined variables as the `.env` file.

### Skip condition

Skipped if either `.env` or `.env.example` files are missing.

### Pass condition

The defined `.env.example` variables match the defined `.env` variables.

### Fail condition

The defined `.env.example` variables do not match the defined `.env` variables.

### Recommendation

Update `.env.example` so it documents all variables required by `.env`, and remove variables that are no longer used.
