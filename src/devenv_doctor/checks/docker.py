import subprocess

def command_output(command: list[str]) -> tuple[int, str]:
    try:
        result = subprocess.run(command,
                                capture_output=True,
                                text=True,
                                check=False,
                                timeout=5)
        if result.returncode == 0:
            return result.returncode, result.stdout.strip()
        return result.returncode, result.stderr.strip()
    except FileNotFoundError as e:
        # 127 is code in linux for command not found
        return 127, f"Command not found: {e.filename}"
    except subprocess.TimeoutExpired as e:
        # 124 is code in linux for timeout
        return 124, f"The program timed out after {e.timeout} seconds"

def check_docker_cli_installed() -> tuple[bool, str]:
    exit_code, output = command_output(["docker", "--version"])
    if exit_code == 0:
        return True, "Docker CLI is installed."
    
    if exit_code == 127:
        return False, "Docker CLI is not installed."
    return False, output

def check_docker_daemon_accessible() -> tuple[bool, str]:
    exit_code, output = command_output(["docker", "info"])
    if exit_code == 0:
        return exit_code == 0, "Docker daemon is accessible"
    
    output_lower = output.lower()

    # This should not execute since the check_docker_cli_installed function 
    # should be called before.
    if exit_code == 127:
        return False, output
    
    if exit_code == 124:
        return False, "Docker Command timed out. Docker may be slow, stuck or not responding."
    
    if "permission denied" in output_lower:
        return False, (
            "Docker daemon may be running, "
            "but your user does not have permission to access it."
            )

    if "cannot connect to the docker daemon" in output_lower:
        return False, "Docker daemon is not running or is not reachable."
    
    return False, output