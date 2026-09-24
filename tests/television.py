#!/usr/bin/env python3
"""Integration regression tests; run with TV_BIN=/path/to/tv python3 tests/television.py."""
import fcntl
import os
from pathlib import Path
import pty
import select
import shutil
import signal
import struct
import subprocess
import tempfile
import termios
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
TV = os.environ.get('TV_BIN') or shutil.which('tv')


class TelevisionTests(unittest.TestCase):
    def test_live_preview_and_output(self):
        self.assertTrue(TV, 'Set TV_BIN to the Television executable')
        for cancel in (False, True):
            with self.subTest(cancel=cancel), tempfile.TemporaryDirectory() as directory:
                path = Path(directory)
                target = path / "directory with spaces ' \" $HOME `false`\ttab"
                target.mkdir()
                (path / 'source').write_text(directory + '\n' + str(target) + '\n')
                (path / 'state').write_text('mode=atuin\nhidden=true\n')
                binaries = path / 'bin'
                binaries.mkdir()
                for name, body in {
                    'eza': 'printf "eza %s\\n" "$*" >> "$TEST_LOG"\n',
                    'atuin': 'echo atuin >> "$TEST_LOG"\n',
                }.items():
                    script = binaries / name
                    script.write_text('#!/bin/sh\n' + body)
                    script.chmod(0o755)
                pid, fd = pty.fork()
                if pid == 0:
                    fcntl.ioctl(0, termios.TIOCSWINSZ, struct.pack('HHHH', 30, 120, 0, 0))
                    os.environ.update(
                        TERM='xterm-256color', XDG_CONFIG_HOME=directory,
                        XDG_DATA_HOME=directory, XDG_CACHE_HOME=directory,
                        PATH=str(binaries) + ':/usr/bin:/bin', ATUIN_SESSION='test',
                        TEST_LOG=str(path / 'log'), DIR_MEOW_SOURCE_FILE=str(path / 'source'),
                        DIR_MEOW_STATE_FILE=str(path / 'state'),
                        DIR_MEOW_PREVIEW_HELPER=str(ROOT / 'bin/dir-meow-preview'),
                    )
                    os.dup2(os.open(path / 'out', os.O_CREAT | os.O_WRONLY, 0o600), 1)
                    os.execv(TV, [TV, '--cable-dir', str(ROOT / 'television'), 'dir-meow'])

                def pump(seconds=0.6):
                    deadline = time.monotonic() + seconds
                    while time.monotonic() < deadline:
                        if select.select([fd], [], [], 0.03)[0]:
                            try:
                                output = os.read(fd, 65536)
                            except OSError:
                                return
                            if b'\x1b[6n' in output:
                                os.write(fd, b'\x1b[1;1R')

                def press(key):
                    os.write(fd, key)
                    pump()

                def log():
                    return (path / 'log').read_text().splitlines()

                try:
                    pump()
                    self.assertIn('atuin', log())
                    press(b'\x1b[B')
                    press(b'\x1bu')  # Alt-U in Atuin must not change hidden state.
                    self.assertIn('hidden=true', (path / 'state').read_text())
                    press(b'\x0f')  # Ctrl-O: eza.
                    self.assertIn('--all', log()[-1])
                    count = len(log())
                    press(b'\x1bu')  # Refresh the SAME selected directory.
                    self.assertGreater(len(log()), count)
                    self.assertTrue(log()[-1].startswith('eza '))
                    self.assertNotIn('--all', log()[-1])
                    self.assertIn(str(target), log()[-1])
                    press(b'\x06')  # Ctrl-F: Atuin.
                    self.assertEqual(log()[-1], 'atuin')
                    press(b'\x0f')  # Back to eza preserves hidden=false.
                    self.assertNotIn('--all', log()[-1])
                    press(b'\x1bu')
                    self.assertIn('--all', log()[-1])
                    press(b'\x1b' if cancel else b'\r')
                    deadline = time.monotonic() + 3
                    while True:
                        done, status = os.waitpid(pid, os.WNOHANG)
                        if done:
                            pid = None
                            self.assertEqual(os.waitstatus_to_exitcode(status), 0)
                            break
                        self.assertLess(time.monotonic(), deadline, 'tv did not exit')
                        pump(0.1)
                    self.assertEqual((path / 'out').read_text(), '' if cancel else str(target) + '\n')
                finally:
                    if pid:
                        os.kill(pid, signal.SIGKILL)
                        os.waitpid(pid, 0)
                    os.close(fd)

    def test_widget_cancel_select_and_stale_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            target = path / 'directory with spaces'
            target.mkdir()
            tv = path / 'tv'
            tv.write_text('#!/bin/sh\nprintf "%s" "$TEST_SELECTION"\n')
            tv.chmod(0o755)
            for selection, error in [('', False), (str(target), False), (str(path / 'missing'), True)]:
                env = dict(os.environ, PATH=directory + ':/usr/bin:/bin',
                           XDG_CONFIG_HOME=directory, TEST_SELECTION=selection,
                           TEST_ROOT=str(ROOT), TEST_LOG=str(path / 'messages'))
                (path / 'messages').write_text('')
                result = subprocess.run(['zsh', '-fic', '''
                    zle() { [[ $1 != -M ]] || print -r -- "$2" >> "$TEST_LOG"; return 0 }
                    source "$TEST_ROOT/dir-meow.plugin.zsh"
                    precmd() { print -r -- "$PWD" > "$XDG_CONFIG_HOME/prompt" }
                    precmd_functions=(_test_prompt_hook)
                    _test_prompt_hook() { print -r -- "$PWD" > "$XDG_CONFIG_HOME/hook" }
                    _dir_meow_widget
                    print -r -- "$PWD"
                '''], env=env, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(bool((path / 'messages').read_text()), error)
                self.assertEqual(result.stdout.strip(), str(target) if selection == str(target) else os.getcwd())
                if selection == str(target):
                    self.assertEqual((path / 'prompt').read_text().strip(), str(target))
                    self.assertEqual((path / 'hook').read_text().strip(), str(target))


if __name__ == '__main__':
    unittest.main()
