"""Replay safety audit hook for offline replay runs.

Vendored from safeagents-eval xaab/runner.py (install_safety). A replay process
may only write inside its own result directory, bind nothing, and reach only
the local decision endpoint. No captured tool call is ever executed; the hook
is installed at call time, never at import time.
"""
import os
import sys
from pathlib import Path


def install_safety(output, port=18872):
    output = Path(output).resolve()
    def audit(event, args):
        if event in {'subprocess.Popen', 'os.system', 'os.exec', 'os.posix_spawn', 'ctypes.dlopen'}:
            raise RuntimeError('benchmark execution capability denied: '+event)
        if event in {'socket.bind', 'socket.getaddrinfo'}:
            # urllib may resolve the numeric loopback endpoint itself.
            if event == 'socket.getaddrinfo' and args[0] == '127.0.0.1' and args[1] == port:
                return
            raise RuntimeError('benchmark network capability denied: '+event)
        if event == 'socket.connect':
            address = args[1]
            if not isinstance(address, tuple) or address[:2] != ('127.0.0.1',port):
                raise RuntimeError('only local decision endpoint is permitted')
        if event == 'open':
            path, mode, flags = args
            writing = (isinstance(mode,str) and any(c in mode for c in 'wax+')) or flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND)
            if writing and not isinstance(path,int) and not Path(path).resolve().is_relative_to(output):
                raise RuntimeError('write outside result directory denied')
    sys.addaudithook(audit)
