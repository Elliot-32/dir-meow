# dir-meow: directory-stack navigator for Zsh, powered by fzf.

# Record ordinary `cd` navigation in Zsh's directory stack. Respect the user's
# existing DIRSTACKSIZE and other pushd options.
setopt AUTO_PUSHD

[[ -o interactive ]] || return 0

# Resolve this file once so the preview helper works regardless of cwd or how
# the plugin was loaded (source, Sheldon, etc.). Keep these writable so sourcing
# the plugin again is harmless.
typeset -g DIR_MEOW_ROOT=${${(%):-%N}:A:h}
typeset -g DIR_MEOW_PREVIEW_HELPER="$DIR_MEOW_ROOT/bin/dir-meow-preview"

_dir_meow_widget() {
  emulate -L zsh
  setopt localoptions pipefail auto_pushd

  if (( ! $+commands[fzf] )); then
    zle -M 'dir-meow: fzf is required'
    return 1
  fi

  local -a candidates
  local -A seen
  local dir

  # `dirs -pl` yields the current directory followed by the directory stack,
  # one absolute path per line. Keep the stack order, but show each path once.
  for dir in ${(f)"$(dirs -pl)"}; do
    [[ -d $dir ]] || continue
    [[ -n ${seen[$dir]-} ]] && continue
    seen[$dir]=1
    candidates+=("$dir")
  done

  if (( ${#candidates} == 0 )); then
    zle -M 'dir-meow: directory stack is empty'
    return 1
  fi

  local state_file
  state_file=$(mktemp "${TMPDIR:-/tmp}/dir-meow.XXXXXXXX") || {
    zle -M 'dir-meow: failed to create temporary state file'
    return 1
  }

  local hidden_default
  hidden_default=$(zsh "$DIR_MEOW_PREVIEW_HELPER" hidden-default) || {
    rm -f -- "$state_file"
    zle -M "${hidden_default:-dir-meow: failed to read configuration}"
    return 1
  }

  {
    print -r -- 'mode=atuin'
    print -r -- "hidden=$hidden_default"
  } >| "$state_file"

  # fzf preview subprocesses inherit these scoped variables, avoiding fragile
  # quoting of plugin paths and the temporary state file inside action strings.
  local preview_helper=$DIR_MEOW_PREVIEW_HELPER
  local -x DIR_MEOW_PREVIEW_HELPER=$preview_helper
  local -x DIR_MEOW_STATE_FILE=$state_file

  local selected status
  selected=$(
    printf '%s\n' "${candidates[@]}" |
      fzf \
        --no-sort \
        --scheme=path \
        --layout=reverse \
        --border \
        --prompt='dir> ' \
        --header='Ctrl-O: Atuin/eza · Alt-U: hidden (eza only) · Enter: cd · Esc: cancel' \
        --preview='zsh "$DIR_MEOW_PREVIEW_HELPER" preview "$DIR_MEOW_STATE_FILE" {}' \
        --preview-label=' Atuin ' \
        --preview-window='right:60%:wrap' \
        --bind='ctrl-o:execute-silent(zsh "$DIR_MEOW_PREVIEW_HELPER" toggle-mode "$DIR_MEOW_STATE_FILE")+refresh-preview+transform-preview-label(zsh "$DIR_MEOW_PREVIEW_HELPER" label "$DIR_MEOW_STATE_FILE")' \
        --bind='alt-u:execute-silent(zsh "$DIR_MEOW_PREVIEW_HELPER" toggle-hidden "$DIR_MEOW_STATE_FILE")+refresh-preview+transform-preview-label(zsh "$DIR_MEOW_PREVIEW_HELPER" label "$DIR_MEOW_STATE_FILE")'
  )
  status=$?

  rm -f -- "$state_file"

  (( status == 0 )) || {
    zle reset-prompt
    return 0
  }

  [[ -n $selected && -d $selected ]] || {
    zle -M 'dir-meow: selected directory no longer exists'
    return 1
  }

  builtin cd -- "$selected" || return 1
  zle reset-prompt
}

zle -N dir-meow _dir_meow_widget
bindkey -M emacs '^[r' dir-meow
bindkey -M viins '^[r' dir-meow
