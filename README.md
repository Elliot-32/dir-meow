# dir-meow

A small Zsh directory-stack navigator built around `pushd`, `fzf`, Atuin, and eza.

- `Alt-R`: open directory history from Zsh's directory stack
- `Ctrl-O`: switch the preview between Atuin history and eza
- `Alt-U`: toggle hidden files while the eza preview is active
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

Environment variables have highest priority:

```zsh
export MEOW_ICONS=true
export MEOW_TREE=true
export MEOW_LEVEL=2
export MEOW_HIDDEN=true
```

For each unset environment variable, dir-meow falls back to the corresponding value in the XDG config file:

```text
${XDG_CONFIG_HOME:-$HOME/.config}/dir-meow/config
```

If `XDG_CONFIG_HOME` is unset, empty, or not an absolute path, dir-meow falls back to `$HOME/.config`.

The config directory and file are created automatically on the first dir-meow invocation if they do not already exist. The generated file contains the built-in defaults; environment-variable overrides are not written into it.

The config file is a small plain-text `key=value` file and is **not** sourced as shell code:

```text
icons=true
tree=true
level=2
hidden=true
```

Blank lines and `#` comments are allowed.

Precedence is evaluated per option:

```text
environment -> config file -> built-in default
```

This means you can keep most settings in the file and override only one from the environment. For example, with:

```text
icons=true
tree=true
level=2
hidden=true
```

and:

```zsh
export MEOW_LEVEL=4
```

only `level` is overridden.

Options:

| Config key | Environment variable | Type | Default | Effect |
| --- | --- | --- | --- | --- |
| `icons` | `MEOW_ICONS` | boolean | `true` | Add `--icons=always` to the eza preview |
| `tree` | `MEOW_TREE` | boolean | `true` | Add `--tree` to the eza preview |
| `level` | `MEOW_LEVEL` | positive integer | `2` | Tree depth passed as `--level=N`; ignored when `tree = false` |
| `hidden` | `MEOW_HIDDEN` | boolean | `true` | Initial hidden-file visibility for each dir-meow invocation |

The eza preview shows names only, using `--oneline --group-directories-first --color=always` plus the configured icon/tree options. When hidden files are enabled, `--all` is added.

`Alt-U` changes hidden-file visibility only for the current dir-meow invocation. It works only while the eza preview is active; in Atuin mode it is a no-op and does not switch preview providers. The hidden state is preserved when switching between Atuin and eza with `Ctrl-O`.

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
