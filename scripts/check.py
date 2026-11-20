#!/usr/bin/env python3
"""Run data-free regression suites; never start real models or evaluation launchers."""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SUITES = ('python', 'ui')


def commands():
    python = sys.executable
    return {
        'python': [python, '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_*.py', '-v'],
        'ui': ['node', '--test', 'tests/test_security_ui.mjs'],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--list', action='store_true', help='print the plan without running tests')
    parser.add_argument('--suite', choices=DEFAULT_SUITES, action='append',
                        help='run only selected suites')
    options = parser.parse_args(argv)
    plan = commands()
    if options.list:
        print(json.dumps({'default_suites': DEFAULT_SUITES, 'commands': plan}, indent=2))
        return 0
    selected = options.suite or DEFAULT_SUITES
    if os.name != 'posix':
        parser.error('the backend tests require Linux/WSL (POSIX ownership and fcntl)')
    if 'ui' in selected and shutil.which('node') is None:
        parser.error('Node.js 24 or newer is required for the UI regression suite')
    # Keep incidental test lookups away from actual agent homes. No shell commands,
    # live model ports, benchmark preparation, or downloaded code are invoked here.
    with tempfile.TemporaryDirectory(prefix='hermes-safeagents-check-home-') as directory:
        home = Path(directory)
        environment = dict(os.environ, HOME=str(home), HERMES_HOME=str(home / '.hermes'),
                           HERMES_PROFILE='default', PYTHONDONTWRITEBYTECODE='1')
        environment.pop('PYTHONPATH', None)
        environment.pop('PYTHONHOME', None)
        if not environment.get('TMPDIR') or not Path(environment['TMPDIR']).is_dir():
            environment['TMPDIR'] = str(home / 'tmp')
            Path(environment['TMPDIR']).mkdir()
        for name in selected:
            print(f'\n=== {name} ===', flush=True)
            result = subprocess.run(plan[name], cwd=ROOT, env=environment, check=False)
            if result.returncode:
                print(f'FAILED: {name} (exit {result.returncode})', file=sys.stderr)
                return result.returncode
    print('\nAll selected suites passed. No real-model or CUDA integration was run.', flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
