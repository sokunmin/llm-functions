#!/bin/bash

JIRA_USER="<JIRA_USER>"
JIRA_API_TOKEN="<JIRA_API_TOKEN>"

add_worklog() {
    local issue_id="$1"
    local date="$2"
    local time_spent="$3"
    local worklog_array=("${@:4}")

    # Build JSON content with escaped characters
    local content_elements=""
    for ((i=0; i<${#worklog_array[@]}; i++)); do
        item="${worklog_array[i]}"
        escaped_item=$(echo "$item" | sed 's/"/\\"/g; s/\\/\\\\/g')
        content_elements+="{\"type\":\"paragraph\",\"content\":[{\"type\":\"text\",\"text\":\"${escaped_item}\"}]}"
        if [ $i -lt $((${#worklog_array[@]}-1)) ]; then
            content_elements+=","  # Add comma between elements
        fi
    done

    # Build JSON payload
    local json_payload=$(cat <<EOF
{
  "timeSpent": "$time_spent",
  "comment": {
    "type": "doc",
    "version": 1,
    "content": [
      ${content_elements}
    ]
  },
  "started": "$date"
}
EOF
)

    # Validate JSON syntax
    if ! echo "$json_payload" | jq . > /dev/null 2>&1; then
        echo "❌ Invalid JSON payload. Exiting."
        return 1
    fi

    response=$(curl -s -w "\n%{http_code}" -o - \
        -u "$JIRA_USER:$JIRA_API_TOKEN" \
        -X POST \
        -H "Content-Type: application/json; charset=UTF-8" \
        -d "$json_payload" \
        "https://istrd.atlassian.net/rest/api/3/issue/$issue_id/worklog")

    http_code=$(tail -n1 <<< "$response")
    response_body=$(head -n -1 <<< "$response")
    echo "json_payload=$json_payload"
    echo "response=$response"

    if [[ "$http_code" -eq 201 ]]; then
        echo "✅ Success! Worklog added to $issue_id"
    else
        echo "❌ Failed. Status: $http_code"
        echo "Error: $response_body"
        return 1
    fi
}

# Example usage with Traditional Chinese:
date_str="2025-03-07T08:00:00.000+0800"
add_worklog "SWD-3114" "$date_str" "8h" \
    "撰寫加解密檔案" \
    "調整流程"