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
                email
            }
        }
    }
}
"""

def get_linear_data():
    """
    Fetch data from the linear API based on the query string queryStr
    """
    try:
        linear_key = os.getenv("LINEAR_API_KEY")
        if not linear_key:
            return {"status": 400, "error": "No Linear API key found"}

        headers = {
            "Content-Type": "application/json",
            "Authorization": linear_key
        }
        query = { "query": queryStr }
        response = requests.post("https://api.linear.app/graphql", headers=headers, json=query)

        data = response.json()
        data['status'] = 200
        return data

    except Exception as ex:
        print(ex)
        return {"status": 400, "error": "Linear API call failed"}