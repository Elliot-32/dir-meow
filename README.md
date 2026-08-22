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

Example:

```toml
[eza]
icons = true
tree = true
level = 2
```

Options:

| Key | Type | Default | Effect |
| --- | --- | --- | --- |
| `eza.icons` | boolean | `true` | Add `--icons=always` to the eza preview |
| `eza.tree` | boolean | `true` | Add `--tree` to the eza preview |
| `eza.level` | positive integer | `2` | Tree depth passed as `--level=N`; ignored when `tree = false` |

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
