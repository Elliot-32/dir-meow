# dir-meow

A small Zsh directory-stack navigator powered by [Television (`tv`)](https://github.com/alexpasmantier/television), with optional Atuin and eza previews.

`dir-meow` enables Zsh's `AUTO_PUSHD`, so normal `cd` navigation is recorded in the directory stack. It does **not** change `DIRSTACKSIZE`, so your existing stack limit remains in control.

## Features

- Browse the current directory and Zsh directory stack with Television's rounded, panel-based interface
- Preserve directory-stack order instead of re-sorting candidates by fuzzy-match score
- Switch the preview between Atuin command history and eza directory contents
- Syntax-highlight Atuin command history with bat when available
- Toggle hidden files while using the eza preview
- Configure eza preview behavior through an XDG config file or environment variables
- Automatically create the default config file on first use

## Requirements

Required:

- Zsh
- Television (`tv`) 0.15+

Optional preview tools:

- Atuin
- eza
- bat (or `batcat` on Debian/Ubuntu) for Atuin history syntax highlighting

If Atuin or eza is not installed, the corresponding preview shows an explanatory message; directory selection still works. If neither `bat` nor `batcat` is installed, Atuin history is shown without syntax highlighting.

A Nerd Font is recommended for the interface icons. dir-meow ships its own Television channel but does not replace your Television theme, so your existing `tv` theme remains in control.

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
| `Ctrl-F` | Switch between Atuin and eza preview |
| `Alt-H` | Toggle hidden files used by the eza preview |
| `Ctrl-O` | Show or hide the preview panel |
| `Ctrl-H` | Toggle Television help |
| `Ctrl-X` | Open Television's action picker |
| `Enter` | `cd` to the selected directory |
| `Esc` | Cancel |

After a selection, prompt hooks are refreshed so themes such as Powerlevel10k show the new directory immediately.

The initial preview is Atuin. `Esc` cancels without changing directory or showing an error.

`Alt-H` toggles the hidden-file state used by the eza preview. If Atuin is currently active, the change becomes visible the next time you switch to eza. The hidden-file state is preserved while switching previews with `Ctrl-F`.

The interface uses Television's rounded input, results, preview, status, and help components. Television’s native arrows and dots indicate the active preview. `Ctrl-F` keeps Television's native `cycle_previews` behavior, while `Ctrl-O`, `Ctrl-H`, and `Ctrl-X` retain their native preview, help, and action-picker controls.

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

For each selected directory, dir-meow runs Atuin from that directory, with the most recently executed command first. When bat is available, the history is syntax-highlighted as Zsh with decorations and paging disabled:

```zsh
atuin history list --session --cwd --cmd-only --reverse=false | \
  bat --color=always --style=plain --paging=never --language=zsh
```

dir-meow also detects the `batcat` executable used by Debian and Ubuntu packages. Without either `bat` or `batcat`, it falls back to the plain Atuin output. The preview therefore shows commands from the current Atuin session whose working directory matches the selected directory.

If `ATUIN_SESSION` is not set, the Atuin preview displays an explanatory message instead.

## Directory ordering

Candidates come from:

```zsh
dirs -pl
```

The current directory appears first, followed by the Zsh directory stack. Duplicate paths are removed while preserving their first occurrence. The bundled Television channel sets `no_sort = true` and disables frecency, so the directory-stack order remains intact.

## License

MIT. See [LICENSE](LICENSE).
