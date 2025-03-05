#!/usr/bin/env bash
set -e

# @meta require-tools docker
# @env LLM_OUTPUT=/dev/stdout The output path

ROOT_DIR="${LLM_ROOT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"


# @cmd List all Docker images on the system
# @flag --all Show all images (including intermediate)
list_images() {
    _check_docker
    if [[ -n "$argc_all" ]]; then
        docker images -a >> "$LLM_OUTPUT"
    else
        docker images >> "$LLM_OUTPUT"
    fi
}

# @cmd List all Docker containers
# @flag --all Show all containers (including stopped)
list_containers() {
    _check_docker
    if [[ -n "$argc_all" ]]; then
        docker ps -a >> "$LLM_OUTPUT"
    else
        docker ps >> "$LLM_OUTPUT"
    fi
}

_check_docker() {
    # Redirect docker version output to /dev/null and suppress errors
    docker version > /dev/null 2>&1

    # Check the exit status of the last command
    if [ $? -ne 0 ]; then
        echo "Docker is not running! Please start Docker and try again." >&2
        exit 1
    fi

}

eval "$(argc --argc-eval "$0" "$@")"