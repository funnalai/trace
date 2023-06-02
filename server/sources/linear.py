import os
import requests
import json

queryStr = """
{
    issues {
        nodes {
            id
            title
            project {
                id
                name
            }
            description
            createdAt
            assignee {
                id
                name
            }
        }
    }
}
"""

def get_linear_data():
    try:
        linear_key = os.getenv("LINEAR_API_KEY")
        if not linear_key:
            return {"error": "No Linear API key found"}

        headers = {
            "Content-Type": "application/json",
            "Authorization": linear_key
        }
        query = { "query": queryStr }
        response = requests.post("https://api.linear.app/graphql", headers=headers, json=query)

        return response.json()

    except Exception as ex:
        return {"error": json.dumps(ex)}