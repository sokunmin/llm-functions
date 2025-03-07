#!/bin/bash

# Configuration (replace with your values)
NOTION_TOKEN="<NOTION_TOKEN>"
NOTION_PAGE_ID="<NOTION_PAGE_ID>"

# Function to append worklog to Notion page
append_worklog() {
    local target_date="$1"
    shift
    local worklogs=("$@")
    local worklog_content
    worklog_content=$(printf "%s\n" "${worklogs[@]}")

    local endpoint="https://api.notion.com/v1/blocks/$NOTION_PAGE_ID/children"
    local headers=(
        -H "Authorization: Bearer $NOTION_TOKEN"
        -H "Content-Type: application/json"
        -H "Notion-Version: 2022-06-28"
    )

    # Create JSON structure with jq <button class="citation-flag" data-index="3">
    local blocks
    blocks=$(jq -n \
        --arg date "$target_date" \
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

    # Prepare and send request <button class="citation-flag" data-index="4">
    local payload
    payload=$(jq -n --argjson children "$blocks" '{ children: $children }')
    local response
    response=$(curl -s -X PATCH "$endpoint" "${headers[@]}" --data "$payload")

    # Check response <button class="citation-flag" data-index="1"><button class="citation-flag" data-index="2">
    if [[ "$response" == *"\"object\":\"error\""* ]]; then
        echo "Error: Failed to append blocks - $response"
        return 1
    else
        echo "Success: $((${#worklogs[@]})) worklogs added for $target_date"
        return 0
    fi
}

# Example usage
# append_worklog "2025/03/02" "AAA" "BBB" "CCC"