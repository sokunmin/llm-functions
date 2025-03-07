#!/bin/bash

set -a
source .env
set +a
set -e

# @env LLM_OUTPUT=/dev/stdout The output path

# @cmd Add new worklog to JIRA issue
# @option --issue-id! <STRING> JIRA issue key/id (e.g., "SWD-3114") used in the API URL
# @option --date! <STRING> Start timestamp in ISO 8601 format with timezone (e.g., "2025-03-05T00:00:00.000+0800")
# @option --time-spent! <STRING> Time spent in duration format (e.g., "60m", "3h", "5d")
# @option --worklog+ <STRING> The string array of worklog entries
add_worklog() {
    _sanity_check
    # Build JSON content with escaped characters
    local content_elements=""
    for ((i=0; i<${#argc_worklog[@]}; i++)); do
        item="${argc_worklog[i]}"
        escaped_item=$(echo "$item" | sed 's/"/\\"/g; s/\\/\\\\/g')
        content_elements+="{\"type\":\"paragraph\",\"content\":[{\"type\":\"text\",\"text\":\"${escaped_item}\"}]}"
        if [ $i -lt $((${#argc_worklog[@]}-1)) ]; then
            content_elements+=","  # Add comma between elements
        fi
    done

    # Build JSON payload
    local json_payload=$(cat <<EOF
{
  "timeSpent": "$argc_time_spent",
  "comment": {
    "type": "doc",
    "version": 1,
    "content": [
      ${content_elements}
    ]
  },
  "started": "$argc_date"
}
EOF
)

    # Validate JSON syntax
    if ! echo "$json_payload" | jq . > /dev/null 2>&1; then
        echo "❌ Invalid JSON payload. Exiting."
        return 1
    fi

    # Execute cURL with error handling
    response=$(curl -s -w "\n%{http_code}" -o - \
        -u "$JIRA_USER:$JIRA_API_TOKEN" \
        -X POST \
        -H "Content-Type: application/json; charset=UTF-8" \
        -d "$json_payload" \
        "https://istrd.atlassian.net/rest/api/3/issue/$argc_issue_id/worklog")

    http_code=$(tail -n1 <<< "$response")
    response_body=$(head -n -1 <<< "$response")
    echo "argc_worklog=${argc_worklog[*]}"
    echo "content_elements=$content_elements"
    echo "issue_id=$argc_issue_id"
    echo "json_payload=$json_payload"
    echo "http_code=$http_code"
    echo "response=$response"
    echo "response_body=$response_body"

    if [[ "$http_code" -eq 201 ]]; then
        echo "✅ Success! Worklog added to $argc_issue_id"
    else
        echo "❌ Failed. Status: $http_code"
        echo "Error: $response_body"
        return 1
    fi
}

_sanity_check() {
    if [ -z "$JIRA_USER" ] || [ -z "$JIRA_API_TOKEN" ]; then
        echo "❌ Error: Required environment variables (JIRA_USER, JIRA_API_TOKEN) are not set." >&2
        exit 1
    fi
}
eval "$(argc --argc-eval "$0" "$@")"
