source /usr/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh

# Aliases
alias cls="clear"
alias gdebug="GTK_DEBUG=interactive"


autoload -U promptinit; promptinit
PURE_PROMPT_SYMBOL="❯❯❯"
prompt pure

# Exec when loading zsh
# Insert something here
case ":$PATH:" in *":$HOME/.local/bin:"*) ;; *) export PATH="$PATH:$HOME/.local/bin" ;; esac