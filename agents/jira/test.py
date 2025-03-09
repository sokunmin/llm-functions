import os
from typing import List

import requests
import json

# Retrieve JIRA credentials from environment variables
JIRA_USER = "<JIRA_USER>"
JIRA_API_TOKEN = "<JIRA_API_TOKEN>"

# Check if credentials are set
if not JIRA_USER or not JIRA_API_TOKEN:
    print("❌ JIRA_USER and JIRA_API_TOKEN must be set in the environment.")
    exit(1)


def add_worklog(
    issue_id: str,
    date: str,
    time_spent: str,
    worklog_comments: List[str]
):
    """
    Adds a worklog entry to JIRA with multi-line comments and returns status messages.

    Args:
        issue_id (str): JIRA issue key/id (e.g., "SWD-3114") used in the API URL
        date (str): Start timestamp in ISO 8601 format with timezone (e.g., "2025-03-05T00:00:00.000+0800")
        time_spent (str): Time duration (e.g., "8h", "60m", "3d")
        worklog_comments (list of str): Comment lines (supports UTF-8)
    """
    # Build content elements for the comment
    content_elements = []
    for comment in worklog_comments:
        # Escape special characters in the comment
        escaped_comment = comment.replace('"', '\\"').replace('\\', '\\\\')
        content_elements.append({
            "type": "paragraph",
            "content": [{
                "type": "text",
                "text": escaped_comment
            }]
        })

    # Construct the JSON payload
    payload = {
        "timeSpent": time_spent,
        "comment": {
            "type": "doc",
            "version": 1,
            "content": content_elements
        },
        "started": date
    }

    # Serialize and validate JSON
    try:
        json_payload = json.dumps(payload, ensure_ascii=False)
        json.loads(json_payload)  # This raises an exception if JSON is invalid
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON payload: {e}")
        return 1

    # Set up authentication and headers
    auth = (JIRA_USER, JIRA_API_TOKEN)
    headers = {
        "Content-Type": "application/json; charset=UTF-8"
    }
    url = f"https://istrd.atlassian.net/rest/api/3/issue/{issue_id}/worklog"

    # Send POST request to JIRA API
    response = requests.post(url, auth=auth, headers=headers, data=json_payload)

    # Check response status
    if response.status_code == 201:
        print(f"✅ Success! Worklog added to {issue_id}")
    else:
        print(f"❌ Failed to add worklog. HTTP Status: {response.status_code}")
        print(f"Response: {response.text}")
        return 1


# Example usage with Traditional Chinese
if __name__ == "__main__":
    date_str = "2025-03-07T08:00:00.000+0800"
    add_worklog("SWD-3114", date_str, "8h", "撰寫加解密文件", "調整流程")
