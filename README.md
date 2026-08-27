# dir-meow

A small Zsh directory-stack navigator powered by `fzf`, with optional Atuin and eza previews.

`dir-meow` enables Zsh's `AUTO_PUSHD`, so normal `cd` navigation is recorded in the directory stack. It does **not** change `DIRSTACKSIZE`, so your existing stack limit remains in control.

## Features

- Browse the current directory and Zsh directory stack with `fzf`
- Preserve directory-stack order instead of re-sorting candidates by fuzzy-match score
- Switch the preview between Atuin command history and eza directory contents
- Toggle hidden files while using the eza preview
- Configure eza preview behavior through an XDG config file or environment variables
- Automatically create the default config file on first use

## Requirements

Required:

- Zsh
- fzf 0.37+ (`transform-preview-label` is used)

Optional preview providers:

- Atuin
- eza

If Atuin or eza is not installed, the corresponding preview shows an explanatory message; directory selection still works.

## Installation

### Sheldon

```toml
[plugins.dir-meow]
github = "Elliot-32/dir-meow"
```

### Manual

```zsh
source /path/to/dir-meow/dir-meow.plugin.zsh
```

## Usage

| Key | Action |
| --- | --- |
| `Alt-R` | Open dir-meow |
| `Ctrl-O` | Switch between Atuin and eza preview |
| `Alt-U` | Toggle hidden files in eza preview |
| `Enter` | `cd` to the selected directory |
| `Esc` | Cancel |

`Alt-U` only affects the eza preview. In Atuin mode it is a no-op and does not switch preview providers. The hidden-file state is preserved when switching previews with `Ctrl-O`.

## Configuration

The config file is located at:

```text
${XDG_CONFIG_HOME:-$HOME/.config}/dir-meow/config
```

If `XDG_CONFIG_HOME` is unset, empty, or not an absolute path, dir-meow uses `$HOME/.config`.

The config directory and file are created automatically on the first dir-meow invocation. The generated file contains the built-in defaults:

```text
icons=true
tree=true
level=2
hidden=true
```

The file uses a small `key=value` format and is **not** sourced as shell code. Blank lines and `#` comments are allowed.

### Options

| Config key | Environment variable | Type | Default | Effect |
| --- | --- | --- | --- | --- |
| `icons` | `MEOW_ICONS` | boolean | `true` | Add `--icons=always` to the eza preview |
| `tree` | `MEOW_TREE` | boolean | `true` | Add `--tree` to the eza preview |
| `level` | `MEOW_LEVEL` | positive integer | `2` | Tree depth passed as `--level=N`; used only when `tree=true` |
| `hidden` | `MEOW_HIDDEN` | boolean | `true` | Initial hidden-file visibility for each invocation |

Environment variables override the corresponding config-file values individually:

```text
environment variable -> config file -> built-in default
```

For example:

```zsh
export MEOW_LEVEL=4
```

only overrides `level`; the remaining options still come from the config file or built-in defaults.

The eza preview always uses:

```text
--oneline --group-directories-first --color=always
```

Depending on the configuration and current hidden-file state, dir-meow additionally uses `--icons=always`, `--tree`, `--level=N`, and `--all`.

## Atuin preview

For each selected directory, dir-meow runs:

```zsh
atuin history list --session --cwd --cmd-only
```

from that directory. The preview therefore shows commands from the current Atuin session whose working directory matches the selected directory.

If `ATUIN_SESSION` is not set, the Atuin preview displays an explanatory message instead.

## Directory ordering

Candidates come from:

```zsh
dirs -pl
```

The current directory appears first, followed by the Zsh directory stack. Duplicate paths are removed while preserving their first occurrence, and fzf runs with `--no-sort` so the directory-stack order remains intact.

## License

MIT. See [LICENSE](LICENSE).
