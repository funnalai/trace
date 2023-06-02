import requests
import json
from dotenv import load_dotenv
import os
import random

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

possible_statuses = {
    "Backlog": "1ea9ca9a-0f0b-48f9-9828-c19a627ea9a3",
    "Todo": "db72454c-cab7-4977-b131-8ca491609efb",
    "In Progress": "214c932a-37bd-4ad8-9511-3b88684a3240",
    "Duplicated": "f05fc843-eb3d-49b3-9f59-1ea8facd3a12",
    "Canceled": "b83ca825-10fb-450d-976a-b011bda26f49",
    "Completed": "52d29efd-134a-47dd-8ef1-00c813fea8b8",
    "Canceled": "b83ca825-10fb-450d-976a-b011bda26f49",
}


def generate_fetch_users_query(team_id):
    query = """
    query TeamUsers {
      users {
        nodes {
          id
          name
          }
      }
    }
    """
    return query


def generate_fetch_projects_query(team_id):
    query = """
    query TeamProjects {
      projects {
        nodes {
          id
          name
        }
      }
    }
    """
    return query


def generate_mutation(title, description, team_id, project_id, status, user_id):
    # randomly pick a status from possible_statuses
    mutation = f"""
    mutation IssueCreate {{
      issueCreate(
        input: {{
          title: "{title}"
          description: "{description}"
          teamId: "{team_id}"
          stateId: "{possible_statuses[status]}"
          assigneeId: "{user_id}"
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


def create_issue():
    # read linearFakeData.json, pass in the relative path
    with open("./scripts/linearFakeData.json") as f:
        data = json.load(f)
        users = fetch_users()
        projects = fetch_projects()
        # iterate through the data and create issues
        for issue in data:
            # randomly select an index from users
            random_index = random.randint(0, len(users) - 1)
            # randomly select an index from projects
            random_project_index = random.randint(0, len(projects) - 1)
            # randomly select a user from users
            random_user = users[random_index]

            random_project = projects[random_project_index]

            mutation = generate_mutation(
                issue["title"], issue["description"], team_id, random_project["id"], issue["status"], random_user["id"])
            response = requests.post(url, headers=headers,
                                     data=json.dumps({"query": mutation}))
            # Check the response status
            if response.status_code == 200:
                print("Issue created successfully!")
                issue_data = response.json()
                print("issue data: ", issue_data)
            else:
                print("Failed to create the issue. Status code:",
                      response.status_code)
                print("Error message:", response.text)


def fetch_projects():
    query = generate_fetch_projects_query(team_id)
    response = requests.post(url, headers=headers,
                             data=json.dumps({"query": query}))
    if response.status_code == 200:
        print("Projects fetched successfully!")
        projects_data = response.json()
        print("projects data: ", projects_data)
        return projects_data["data"]["projects"]["nodes"]
    else:
        print("Failed to fetch projects. Status code:",
              response.status_code)
        print("Error message:", response.text)
        return {}


def fetch_users():
    query = generate_fetch_users_query(team_id)
    response = requests.post(url, headers=headers,
                             data=json.dumps({"query": query}))
    if response.status_code == 200:
        print("Users fetched successfully!")
        users_data = response.json()
        print("users data: ", users_data)
        return users_data["data"]["users"]["nodes"]
    else:
        print("Failed to fetch users. Status code:",
              response.status_code)
        print("Error message:", response.text)
        return {}


create_issue()
