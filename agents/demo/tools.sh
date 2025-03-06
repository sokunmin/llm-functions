#!/usr/bin/env bash
set -e

# @env LLM_OUTPUT=/dev/stdout The output path

# @cmd Get the ip info
get_ipinfo() {
    curl -fsSL https://httpbin.org/ip >> "$LLM_OUTPUT"
}


# @cmd Get user information
get_user_info() {
    echo "username=$LLM_AGENT_VAR_USERNAME" >> "$LLM_OUTPUT"
}

# @cmd get current date time
get_current_datetime() {
    date +"%Y-%m-%d %H:%M:%S" >> "$LLM_OUTPUT"
}

# See more details at https://github.com/sigoden/argc
eval "$(argc --argc-eval "$0" "$@")"
