#!/usr/bin/env bash
set -a
source .env
set +a
set -e

# @env LLM_OUTPUT=/dev/stdout The output path

# @cmd Get the list for upcoming calendar schedule
# @option --days!   The number of days for the upcoming schedule. Default: 0 (today)
list_schedule() {
    _sanity_check

    TIME_MIN=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
     # Cross-platform compatible date command for future date
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        TIME_MAX=$(date -u -v+${argc_days}d +"%Y-%m-%dT%H:%M:%SZ")
    elif [[ "$OSTYPE" == "linux-gnu"* ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "win32" ]]; then
        # Linux or Windows with Git Bash or similar
        TIME_MAX=$(date -u -d "+${argc_days} days" +"%Y-%m-%dT%H:%M:%SZ")
    else
        # Fallback method using GNU date if available
        if command -v gdate >/dev/null 2>&1; then
            TIME_MAX=$(gdate -u -d "+${argc_days} days" +"%Y-%m-%dT%H:%M:%SZ")
        else
            echo "Error: Unsupported platform for date calculation" >&2
            exit 1
        fi
    fi
    # Get access token using refresh token <button class="citation-flag" data-index="9">
    ACCESS_TOKEN=$(curl -s -X POST \
      -H "Content-Type: application/x-www-form-urlencoded" \
      -d "client_id=${CLIENT_ID}&client_secret=${CLIENT_SECRET}&refresh_token=${REFRESH_TOKEN}&grant_type=refresh_token" \
      "https://oauth2.googleapis.com/token" | jq -r '.access_token')

    # Fetch events <button class="citation-flag" data-index="2"><button class="citation-flag" data-index="3">
    EVENTS=$(curl -s -X GET \
      "https://www.googleapis.com/calendar/v3/calendars/${CALENDAR_ID}/events?timeMin=${TIME_MIN}&timeMax=${TIME_MAX}&singleEvents=true" \
      -H "Authorization: Bearer ${ACCESS_TOKEN}")

    # Process events into JSON
    echo "${EVENTS}" >>"$LLM_OUTPUT"
}

_sanity_check() {
    if [ -z "$CALENDAR_ID" ] || [ -z "$CLIENT_ID" ] || [ -z "$CLIENT_SECRET" ] || [ -z "$REFRESH_TOKEN" ]; then
        echo "Error: Required environment variables (CALENDAR_ID, CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN) are not set." >&2
        exit 1
    fi
}

# See more details at https://github.com/sigoden/argc
eval "$(argc --argc-eval "$0" "$@")"
