#!/nix/store/19j43hyh37jqnn9l7rg6shk5barbn209-python3-3.9.6/bin/python3
"""Small wrapper to correctly initialize the Java DAP.

This launches the (normal) Java LSP and then tells it to initialize with the
Java DAP plugin bundle. This causes the DAP plugin to bind to a TCP port, and
once that's done, the communication with the DAP can start.

This is known to be flaky, so this retries until it succeeds.
"""

import argparse
import json
import logging
import os
import signal
import subprocess
import sys
import time

from typing import Any, IO, Dict, List, Mapping, Optional


def _send_lsp_message(msg: Dict[str, Any], lsp: IO[bytes]) -> None:
    """Sends one LSP message."""
    serialized_msg = json.dumps({
        'jsonrpc': '2.0',
        **msg,
    })
    payload = len(serialized_msg)
    lsp.write((f'Content-Length: {len(serialized_msg)}\r\n\r\n' +
               serialized_msg).encode('utf-8'))
    lsp.flush()


def _receive_lsp_message(lsp: IO[bytes]) -> Optional[Dict[str, Any]]:
    """Receives one LSP message."""
    headers = b''
    while not headers.endswith(b'\r\n\r\n'):
        byte = lsp.read(1)
        if len(byte) == 0:
            return None
        headers += byte
    content_length = 0
    for header in headers.strip().split(b'\r\n'):
        name, value = header.split(b':', maxsplit=2)
        if name.strip().lower() == b'content-length':
            content_length = int(value.strip())
    serialized = b''
    while content_length:
        chunk = lsp.read(content_length)
        if not chunk:
            raise Exception(f'short read: {serialized!r}')
        content_length -= len(chunk)
        serialized += chunk
    message: Dict[str, Any] = json.loads(serialized)
    return message


def _run(use_ephemeral_port: bool, language_server: str, debug_plugin: str) -> bool:
    """Attempts to start the DAP. Returns whether the caller should retry."""
    args = [language_server]
    if use_ephemeral_port:
        args.append('-Dcom.microsoft.java.debug.serverAddress=localhost:0')
    else:
		    args.append('-Dcom.microsoft.java.debug.serverAddress=localhost:41010')

    with subprocess.Popen(args,
                          stdout=subprocess.PIPE,
                          stdin=subprocess.PIPE,
                          preexec_fn=os.setsid) as dap:
        try:
            _send_lsp_message(
                {
                    'id': 1,
                    'method': 'initialize',
                    'params': {
                        'processId': None,
                        'initializationOptions': {
                            'bundles': [
                                debug_plugin,
                            ],
                        },
                        'trace': 'verbose',
                        'capabilities': {},
                    },
                }, dap.stdin)
            # Wait for the initialize message has been acknowledged.
            # This maximizes the probability of success.
            while True:
                message = _receive_lsp_message(dap.stdout)
                if not message:
                    return True
                if message.get('method') == 'window/logMessage':
                    print(message.get('params', {}).get('message'),
                          file=sys.stderr)
                if message.get('id') == 1:
                    break
            _send_lsp_message(
                {
                    'id': 2,
                    'method': 'workspace/executeCommand',
                    'params': {
                        'command': 'vscode.java.startDebugSession',
                    },
                }, dap.stdin)
            # Wait for the reply. If the request errored out, exit early to
            # send a clear signal to the caller.
            while True:
                message = _receive_lsp_message(dap.stdout)
                if not message:
                    return True
                if message.get('method') == 'window/logMessage':
                    print(message.get('params', {}).get('message'),
                          file=sys.stderr)
                if message.get('id') == 2:
                    if 'error' in message:
                        print(message['error'].get('message'), file=sys.stderr)
                        # This happens often during the first launch before
                        # things warm up.
                        return True
                    if use_ephemeral_port:
                        with os.fdopen(3, 'w') as port_fd:
                            port_fd.write(str(message['result']))
                    break
            # If we reached this point, the LSP and DAP have both
            # successfully initialized.
            # Keep reading to drain the queue.
            while True:
                message = _receive_lsp_message(dap.stdout)
                if not message:
                    break
                if message.get('method') == 'window/logMessage':
                    print(message.get('params', {}).get('message'),
                          file=sys.stderr)
        except Exception:
            logging.exception('failed')
        finally:
            pgrp = os.getpgid(dap.pid)
            os.killpg(pgrp, signal.SIGINT)
        return False


def _main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    # TODO: remove this flag and always use the ephemeral port.
    parser.add_argument(
        '--use-ephemeral-port',
        action='store_true',
        help='Use an ephemeral port and write the port number to fd 3')
    parser.add_argument(
        '--language-server',
        type=str,
        help='The language server to launch')
    parser.add_argument(
        '--debug-plugin',
        type=str,
        help='The path to the debug plugin')
    args = parser.parse_args()
    while True:
        retry = _run(args.use_ephemeral_port, args.language_server, args.debug_plugin)
        if not retry:
            break


if __name__ == '__main__':
    _main()
