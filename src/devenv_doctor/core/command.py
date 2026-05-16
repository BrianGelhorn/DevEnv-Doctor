from subprocess import run, TimeoutExpired

def command_output(command: list[str]) -> tuple[int, str]:
    try:
        result = run(command,
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
    except TimeoutExpired as e:
        # 124 is code in linux for timeout
        return 124, f"The program timed out after {e.timeout} seconds"