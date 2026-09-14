#!/usr/bin/env python3
"""
Start one or more servers, wait for them to be ready, run a command, then clean up.

Usage:
    # Single server
    python scripts/with_server.py --server "npm run dev" --port 5173 -- python automation.py
    python scripts/with_server.py --server "npm start" --port 3000 -- python test.py

    # Multiple servers
    python scripts/with_server.py \
      --server "cd backend && python server.py" --port 3000 \
      --server "cd frontend && npm run dev" --port 5173 \
      -- python test.py

    # Keep server output for debugging (default: discarded)
    python scripts/with_server.py --server "npm run dev" --port 5173 --log-dir ./logs -- python test.py

Cross-platform notes:
    - Servers are started with shell=True. On Windows that spawns cmd.exe, so the
      whole process tree is killed with `taskkill /T` at cleanup; on POSIX the
      server gets its own process group and the group is signalled.
    - Server stdout/stderr are discarded by default (a never-drained PIPE would
      block the server once the buffer fills). Use --log-dir to keep them.
"""

import argparse
import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import IO

IS_WINDOWS = sys.platform == "win32"


def is_port_open(port: int) -> bool:
    """Return True if something is already accepting connections on the port."""
    try:
        with socket.create_connection(('localhost', port), timeout=1):
            return True
    except OSError:
        return False


def is_server_ready(port: int, timeout: int = 30) -> bool:
    """Wait for server to be ready by polling the port."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if is_port_open(port):
            return True
        time.sleep(0.5)
    return False


def start_server(cmd: str, log_file: IO[bytes] | None) -> subprocess.Popen[bytes]:
    """Start a server command in a shell, detached enough to be killed as a tree."""
    output = log_file if log_file is not None else subprocess.DEVNULL
    popen_kwargs: dict[str, object] = {}
    if not IS_WINDOWS:
        # Own process group so the whole tree (sh + children) can be signalled.
        popen_kwargs['start_new_session'] = True

    # Use shell=True to support commands with cd and &&
    return subprocess.Popen(
        cmd,
        shell=True,
        stdout=output,
        stderr=subprocess.STDOUT,
        **popen_kwargs,
    )


def stop_server(process: subprocess.Popen[bytes], timeout: float = 5.0) -> None:
    """Stop a server and every child it spawned (npm -> node, cmd -> python, ...)."""
    if process.poll() is not None:
        return

    if IS_WINDOWS:
        # process.terminate() would only kill cmd.exe and orphan the real server.
        subprocess.run(
            ["taskkill", "/T", "/F", "/PID", str(process.pid)],
            capture_output=True,
        )
        try:
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        return

    try:
        pgid = os.getpgid(process.pid)
    except ProcessLookupError:
        return

    os.killpg(pgid, signal.SIGTERM)
    try:
        process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(pgid, signal.SIGKILL)
        process.wait()


def main() -> None:
    parser = argparse.ArgumentParser(description='Run command with one or more servers')
    parser.add_argument('--server', action='append', dest='servers', required=True, help='Server command (can be repeated)')
    parser.add_argument('--port', action='append', dest='ports', type=int, required=True, help='Port for each server (must match --server count)')
    parser.add_argument('--timeout', type=int, default=30, help='Timeout in seconds per server (default: 30)')
    parser.add_argument('--log-dir', default=None, help='Directory to write server-N.log files to (default: discard server output)')
    parser.add_argument('command', nargs=argparse.REMAINDER, help='Command to run after server(s) ready')

    args = parser.parse_args()

    # Remove the '--' separator if present
    if args.command and args.command[0] == '--':
        args.command = args.command[1:]

    if not args.command:
        print("Error: No command specified to run")
        sys.exit(1)

    # Parse server configurations
    if len(args.servers) != len(args.ports):
        print("Error: Number of --server and --port arguments must match")
        sys.exit(1)

    servers: list[dict[str, str | int]] = []
    for cmd, port in zip(args.servers, args.ports):
        servers.append({'cmd': cmd, 'port': port})

    # A port that is already open would make is_server_ready() pass against a
    # stale/foreign process instead of the server we are about to start.
    busy_ports = [server['port'] for server in servers if is_port_open(int(server['port']))]
    if busy_ports:
        print(f"Error: Port(s) already in use before start: {', '.join(map(str, busy_ports))}")
        sys.exit(1)

    log_dir: Path | None = None
    if args.log_dir:
        log_dir = Path(args.log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)

    server_processes: list[subprocess.Popen[bytes]] = []
    log_files: list[IO[bytes]] = []
    exit_code = 0

    try:
        # Start all servers
        for i, server in enumerate(servers):
            print(f"Starting server {i+1}/{len(servers)}: {server['cmd']}")

            log_file: IO[bytes] | None = None
            if log_dir is not None:
                log_path = log_dir / f"server-{i+1}.log"
                log_file = open(log_path, 'wb')
                log_files.append(log_file)
                print(f"Server {i+1} output -> {log_path}")

            process = start_server(str(server['cmd']), log_file)
            server_processes.append(process)

            # Wait for this server to be ready
            print(f"Waiting for server on port {server['port']}...")
            if not is_server_ready(int(server['port']), timeout=args.timeout):
                raise RuntimeError(f"Server failed to start on port {server['port']} within {args.timeout}s")

            print(f"Server ready on port {server['port']}")

        print(f"\nAll {len(servers)} server(s) ready")

        # Run the command
        print(f"Running: {' '.join(args.command)}\n")
        result = subprocess.run(args.command)
        exit_code = result.returncode

    finally:
        # Clean up all servers
        print(f"\nStopping {len(server_processes)} server(s)...")
        for i, process in enumerate(server_processes):
            stop_server(process)
            print(f"Server {i+1} stopped")
        for log_file in log_files:
            log_file.close()
        print("All servers stopped")

    sys.exit(exit_code)


if __name__ == '__main__':
    main()
