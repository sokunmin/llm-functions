#!/usr/bin/env bash
set -a
source .env
set +a
set -e

# @env LLM_OUTPUT=/dev/stdout The output path


# @cmd Add new worklog to Notion page
# @option --page-id! <STRING> The Notion page id (32 ASCII characters)
# @option --date! <STRING> The date of worklog in YYYY/mm/DD format
# @option --worklog+ <STRING> The string array of worklog entries
add_worklog() {
    _sanity_check

    # Construct the Notion API request body
    local worklog_content
    worklog_content=$(printf "%s\n" "${argc_worklog[@]}")
    local endpoint="https://api.notion.com/v1/blocks/$argc_page_id/children"
    local headers=(
        -H "Authorization: Bearer $NOTION_API_TOKEN"
        -H "Content-Type: application/json; charset=UTF-8"
        -H "Notion-Version: 2022-06-28"
    )

    # Create JSON structure with jq
    local blocks
    blocks=$(jq -n \
        --arg date "$argc_date" \
        --arg worklog "$worklog_content" \
        '[
            {
                object: "block",
                type: "paragraph",
                paragraph: {
                    rich_text: [{
                        type: "text",
                        text: { content: $date },
                        annotations: { bold: true }
                    }]
                }
            },
            {
                object: "block",
                type: "quote",
                quote: {
                    rich_text: [{
                        type: "text",
                        text: { content: $worklog }
                    }]
                }
            }
        ]'
    )
    echo "body=$blocks"
    # Prepare and send request
    local payload
    payload=$(jq -n --argjson children "$blocks" '{ children: $children }')
    local response
    response=$(curl -s -X PATCH "$endpoint" "${headers[@]}" --data "$payload")

    # Check response
    if [[ "$response" == *"\"object\":\"error\""* ]]; then
        echo "❌ Error: Failed to append blocks - $response"
    else
        echo "✅ Success: $((${#argc_worklog[@]})) worklogs added for $argc_date" >> "$LLM_OUTPUT"
    fi
}


_sanity_check() {
    if [ -z "$NOTION_API_TOKEN" ]; then
        echo "❌ Error: Required environment variables (NOTION_API_TOKEN) are not set." >&2
        exit 1
    fi
}

eval "$(argc --argc-eval "$0" "$@")"
