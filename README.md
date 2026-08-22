# dir-meow

A small Zsh directory-stack navigator built around `pushd`, `fzf`, Atuin, and eza.

- `Alt-R`: open directory history from Zsh's directory stack
- `Alt-P`: switch the preview between Atuin history and eza
- `Enter`: `cd` to the selected directory
- `Esc`: cancel

`dir-meow` enables Zsh's `AUTO_PUSHD`, so ordinary `cd` navigation is recorded in the directory stack. It does **not** change `DIRSTACKSIZE`, so your existing limit remains in control.

## Requirements

- Zsh
- fzf 0.37+ (for `transform-preview-label`)
- Atuin
- eza
- dasel, only when `config.toml` exists

Atuin and eza are preview providers. If one is missing, that preview shows an error message and the other mode still works.

## Install

### Sheldon

```toml
[plugins.dir-meow]
github = "Elliot-32/dir-meow"
```

### Manual

```zsh
source /path/to/dir-meow/dir-meow.plugin.zsh
```

## Configuration

The config follows the XDG Base Directory specification:

```text
${XDG_CONFIG_HOME:-$HOME/.config}/dir-meow/config.toml
```

If `XDG_CONFIG_HOME` is unset, empty, or not an absolute path, dir-meow falls back to `$HOME/.config`.

When `config.toml` exists, dir-meow reads it with `dasel` and uses the TOML values as the complete eza configuration:

```toml
[eza]
icons = true
tree = true
level = 2
```

When `config.toml` does **not** exist, dir-meow falls back to environment variables:

```zsh
export DIR_MEOW_EZA_ICONS=true
export DIR_MEOW_EZA_TREE=true
export DIR_MEOW_EZA_LEVEL=2
```

If neither a config file nor the corresponding environment variable is present, the built-in defaults are used.

Precedence:

```text
config.toml -> environment -> built-in defaults
```

The environment fallback is only used when `config.toml` does not exist. If the file exists but is unreadable, invalid, missing a required key, or `dasel` is unavailable, the eza preview displays an error instead of silently falling back to the environment.

Options:

| TOML key | Environment variable | Type | Default | Effect |
| --- | --- | --- | --- | --- |
| `eza.icons` | `DIR_MEOW_EZA_ICONS` | boolean | `true` | Add `--icons=always` to the eza preview |
| `eza.tree` | `DIR_MEOW_EZA_TREE` | boolean | `true` | Add `--tree` to the eza preview |
| `eza.level` | `DIR_MEOW_EZA_LEVEL` | positive integer | `2` | Tree depth passed as `--level=N`; ignored when `tree = false` |

The eza preview always uses `--all --long --group-directories-first --color=always`.

## How the Atuin preview is scoped

For every selected directory, dir-meow runs Atuin from that directory with both session and cwd filters:

```zsh
atuin history list --session --cwd --cmd-only
```

So the preview contains commands executed in **the current Atuin session AND the selected directory**.

## Directory ordering

Candidates come from:

```zsh
dirs -pl
```

That means the current directory is first, followed by the Zsh directory stack. Duplicate paths are removed while preserving stack order, and fzf uses `--no-sort` so fuzzy searching does not replace the stack's recency ordering.
