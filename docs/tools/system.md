# System Operations

Nyro MCP allows execution of system-level commands, providing a controlled way for AI agents to interact with the OS environment.

## ⚙️ Command Execution

### `run_command(cmd, cwd=".", timeout=120)`
Executes a shell command.

- **`cmd`**: The full command string.
- **`cwd`**: Working directory (resolved within the ROOT sandbox).
- **`timeout`**: Maximum execution time in seconds. Default is 120s.

### Security Features
1.  **Sandbox Boundary**: Commands are executed within the specified `cwd`, which is strictly verified to be within the `ROOT` path.
2.  **Output Capture**: Standard Output (`stdout`) and Standard Error (`stderr`) are captured and returned to the agent.
3.  **Timeout Protection**: Prevents "infinite" or hanging processes from blocking the server. If a timeout occurs, the process is terminated and an error status is returned.
4.  **Error Handling**: If a command returns a non-zero exit code, it is reported as a warning in the server logs but the output is still returned for debugging.

## Usage Example
An agent might use this tool to build a project:
```bash
run_command(cmd="npm run build", cwd="frontend")
```
