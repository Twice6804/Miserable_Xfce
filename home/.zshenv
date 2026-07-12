# Ensure ~/.local/bin is on PATH for every zsh shell (login and non-login).
# zsh does not read ~/.profile, so the PATH entry lives here instead.
case ":$PATH:" in *":$HOME/.local/bin:"*) ;; *) export PATH="$PATH:$HOME/.local/bin" ;; esac
