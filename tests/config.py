"""Configuration snapshot regression tests (no Television binary required)."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ConfigTests(unittest.TestCase):
    def test_widget_snapshot_refresh_and_hidden_toggle(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            config_dir = path / 'dir-meow'
            config_dir.mkdir()
            config = config_dir / 'config'
            config.write_text('icons=false\ntree=true\nlevel=2\nhidden=true\n')
            binaries = path / 'bin'
            binaries.mkdir()
            # Mutate the file after the widget loads it. Both previews in this
            # invocation must keep the old settings, while hidden stays mutable.
            scripts = {
                'tv': '''#!/bin/zsh
print -r -- 'icons=true\ntree=true\nlevel=4\nhidden=false' > "$XDG_CONFIG_HOME/dir-meow/config"
zsh "$DIR_MEOW_PREVIEW_HELPER" preview-eza "$DIR_MEOW_STATE_FILE" "$PWD" >> "$TEST_LOG"
zsh "$DIR_MEOW_PREVIEW_HELPER" toggle-hidden "$DIR_MEOW_STATE_FILE"
zsh "$DIR_MEOW_PREVIEW_HELPER" preview-eza "$DIR_MEOW_STATE_FILE" "$PWD" >> "$TEST_LOG"
''',
                'eza': '#!/bin/sh\nprintf "%s " "$@"\nprintf "\\n"\n',
            }
            for name, script in scripts.items():
                binary = binaries / name
                binary.write_text(script)
                binary.chmod(0o755)
            env = {k: v for k, v in os.environ.items()
                   if not k.startswith(('MEOW_', 'DIR_MEOW_'))}
            env.update(PATH=str(binaries) + ':/usr/bin:/bin',
                       XDG_CONFIG_HOME=directory, TEST_ROOT=str(ROOT),
                       TEST_LOG=str(path / 'log'), MEOW_TREE='false')
            result = subprocess.run(['zsh', '-fic', '''
zle() { return 0 }
source "$TEST_ROOT/dir-meow.plugin.zsh"
_dir_meow_widget
_dir_meow_widget
'''], env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            lines = (path / 'log').read_text().splitlines()
            self.assertEqual(len(lines), 4)
            for line in lines:
                self.assertNotIn('--tree', line)  # Environment overrides file.
            self.assertNotIn('--icons=always', lines[0])
            self.assertNotIn('--icons=always', lines[1])
            self.assertIn('--all', lines[0])
            self.assertNotIn('--all', lines[1])
            self.assertIn('--icons=always', lines[2])
            self.assertNotIn('--all', lines[2])
            self.assertIn('--all', lines[3])

    def test_standalone_helper_reads_config(self):
        with tempfile.TemporaryDirectory() as directory:
            env = {k: v for k, v in os.environ.items()
                   if not k.startswith(('MEOW_', 'DIR_MEOW_'))}
            env['XDG_CONFIG_HOME'] = directory
            result = subprocess.run(['zsh', str(ROOT / 'bin/dir-meow-preview'), 'config'],
                                    env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.splitlines(), ['true', 'true', '2', 'true'])
            (Path(directory) / 'dir-meow/config').write_text('level=invalid\n')
            result = subprocess.run(['zsh', str(ROOT / 'bin/dir-meow-preview'), 'config'],
                                    env=env, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('positive integer', result.stdout)
