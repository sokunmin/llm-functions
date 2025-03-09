#!/usr/bin/env bash
set -e

# @env LLM_OUTPUT=/dev/stdout The output path

ROOT_DIR="${LLM_ROOT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"

# @cmd List all Ollama models
list_models() {
    ollama list >> "$LLM_OUTPUT"
}

eval "$(argc --argc-eval "$0" "$@")"
