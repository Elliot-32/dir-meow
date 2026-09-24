# dir-meow: directory-stack navigator for Zsh, powered by Television.

# Record ordinary `cd` navigation in Zsh's directory stack. Respect the user's
# existing DIRSTACKSIZE and other pushd options.
setopt AUTO_PUSHD

[[ -o interactive ]] || return 0

# Resolve plugin resources once so the bundled Television channel and preview
# helper work regardless of cwd or how the plugin was loaded.
typeset -g DIR_MEOW_ROOT=${${(%):-%N}:A:h}
typeset -g DIR_MEOW_PREVIEW_HELPER="$DIR_MEOW_ROOT/bin/dir-meow-preview"
typeset -g DIR_MEOW_CABLE_DIR="$DIR_MEOW_ROOT/television"

_dir_meow_widget() {
  emulate -L zsh
  setopt localoptions pipefail auto_pushd

  if (( ! $+commands[tv] )); then
    zle -M 'dir-meow: Television (tv) 0.15+ is required'
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

  local source_file state_file
  source_file=$(mktemp "${TMPDIR:-/tmp}/dir-meow-source.XXXXXXXX") || {
    zle -M 'dir-meow: failed to create temporary source file'
    return 1
  }

  state_file=$(mktemp "${TMPDIR:-/tmp}/dir-meow-state.XXXXXXXX") || {
    rm -f -- "$source_file"
    zle -M 'dir-meow: failed to create temporary state file'
    return 1
  }

  printf '%s\n' "${candidates[@]}" >| "$source_file" || {
    rm -f -- "$source_file" "$state_file"
    zle -M 'dir-meow: failed to write directory candidates'
    return 1
  }

  local hidden_default
  hidden_default=$(zsh "$DIR_MEOW_PREVIEW_HELPER" hidden-default) || {
    rm -f -- "$source_file" "$state_file"
    zle -M "${hidden_default:-dir-meow: failed to read configuration}"
    return 1
  }

  print -r -- "hidden=$hidden_default" >| "$state_file"

  # Television source, preview, and action subprocesses inherit these scoped
  # variables. The bundled channel consumes them without touching user config.
  local preview_helper=$DIR_MEOW_PREVIEW_HELPER
  local -x DIR_MEOW_SOURCE_FILE=$source_file
  local -x DIR_MEOW_STATE_FILE=$state_file
  local -x DIR_MEOW_PREVIEW_HELPER=$preview_helper

  local selected tv_status
  selected=$(command tv --cable-dir "$DIR_MEOW_CABLE_DIR" dir-meow)
  tv_status=$?

  rm -f -- "$source_file" "$state_file"

  # Television also returns success with empty output when cancelled.
  (( tv_status == 0 )) && [[ -n $selected ]] || {
    zle reset-prompt
    return 0
  }

  [[ $selected != *$'\n'* && -d $selected ]] || {
    zle -M 'dir-meow: selected directory no longer exists'
    return 1
  }

  builtin cd -- "$selected" || return 1
  # reset-prompt only redraws the existing prompt. Themes such as Powerlevel10k
  # calculate directory segments in precmd, so refresh those before redrawing.
  local hook
  for hook in precmd "${precmd_functions[@]}"; do
    (( $+functions[$hook] )) && "$hook"
  done
  zle reset-prompt
}

zle -N dir-meow _dir_meow_widget
bindkey -M emacs '^[r' dir-meow
bindkey -M viins '^[r' dir-meow
