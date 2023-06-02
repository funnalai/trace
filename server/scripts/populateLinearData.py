import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

# Set up the necessary information
team_id = "8eb40e26-8d37-4c1c-9818-a3fcc74cb36c"
project_id = "e93d6499-b3e2-492e-a401-f4b25db91752"

# Define the API endpoint for issue creation
url = f"https://api.linear.app/graphql"

# Create the headers with the API token
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {os.getenv('LINEAR_API_KEY')}"
}

# Create the issue payload
payload = {
    "title": "New Issue",
    "description": "This is a new issue created via the Linear API",
    "team_id": team_id,
    "project_id": project_id,
    "labels": ["bug"],
    "priority": 2
}

# Convert the payload to JSON
json_payload = json.dumps(payload)


def generate_mutation(title, description, team_id, project_id):
    mutation = f"""
    mutation IssueCreate {{
      issueCreate(
        input: {{
          title: "{title}"
          description: "{description}"
          teamId: "{team_id}"
          projectId: "{project_id}"
        }}
      ) {{
        success
        issue {{
          id
          title
        }}
      }}
    }}
    """
    return mutation

# Send the POST request


def create_issue():
    mutation = generate_mutation(
        payload["title"], payload["description"], payload["team_id"], payload["project_id"])
    response = requests.post(url, headers=headers,
                             data=json.dumps({"query": mutation}))
    # Check the response status
    if response.status_code == 200:
        print("Issue created successfully!")
        issue_data = response.json()
        print("issue data: ", issue_data)
    else:
        print("Failed to create the issue. Status code:", response.status_code)
        print("Error message:", response.text)


create_issue()
