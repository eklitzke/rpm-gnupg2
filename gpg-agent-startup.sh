#!/bin/sh

GPG_AGENT=/usr/bin/gpg-agent
## Run gpg-agent only if not already running, and available
if [ -z "${GPG_AGENT_INFO}" -a -x ${GPG_AGENT} ] ; then
  if [ -f ${HOME}/.gpg-agent-info ]; then
    export GPG_AGENT_INFO=$(cat $HOME/.gpg-agent-info)
    export GPG_TTY=$(tty)
  else
    eval "$(${GPG_AGENT} -s --daemon ${GPG_OPTIONS})"
    echo $GPG_AGENT_INFO > $HOME/.gpg-agent-info
  fi
fi
