#!/bin/sh

GPG_AGENT=/usr/bin/gpg-agent
## Run gpg-agent only if not already running, and available
if [ -z "${GPG_AGENT_INFO}" -a -x "${GPG_AGENT}" ] ; then

  # check validity of GPG_SOCKET (in case of session crash)
  if [ -f ${HOME}/.gpg-agent-info ]; then
    GPG_SOCKET=$(cat .gpg-agent-info |cut -f1 -d:)
    if ! test -S "${GPG_SOCKET}" -o ! -O "${GPG_SOCKET}" ; then
      rm -f ${HOME}/.gpg-agent-info 2>&1 >/dev/null
    fi
  fi

  if [ -f ${HOME}/.gpg-agent-info ]; then
    export GPG_AGENT_INFO=$(cat ${HOME}/.gpg-agent-info)
    export GPG_TTY=$(tty)
  else
    eval "$(${GPG_AGENT} -s --daemon ${GPG_OPTIONS})"
    echo ${GPG_AGENT_INFO} > "${HOME}/.gpg-agent-info"
  fi

fi
