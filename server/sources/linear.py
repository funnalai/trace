import os
import requests

def get_linear_data():
    try:
        linear_key = os.environ["LINEAR_API_KEY"]
        headers = {
            "Content-Type": "application/json",
            "Authorization": linear_key
        }

        query = {
            "query": "{ issues { nodes { id title } } }"
        }

        response = requests.post("https://api.linear.app/graphql", headers=headers, json=query)
        print(response.json())
        return response.json()
    except Exception as ex:
        print(ex)
        return {"error": "yes"}