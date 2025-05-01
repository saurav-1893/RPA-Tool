# src/api/api_client.py
import requests


def make_api_request(url, method="GET", headers=None, data=None, json=None):
    """
    Makes an API request to the given URL with the specified method.
    """
    print(f"Making api request to {url} with method {method}")

    response = requests.request(method, url, headers=headers, data=data, json=json)
    response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
    return response