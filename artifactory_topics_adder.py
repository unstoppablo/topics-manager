import requests
import json
import os
import sys

def format_key_value_pairs(args):
    if len(args) == 1:
        print("No key-value pairs provided.")
        sys.exit()

    formatted_pairs = []
    for i in range(1, len(args), 2):
        key = args[i]
        value = args[i + 1]
        formatted_pairs.append(f"{key}:{value}")

    return ";".join(formatted_pairs)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print("No key-value pairs provided.")
        sys.exit()

    property_string = format_key_value_pairs(sys.argv)
    print(property_string)
    
    url = "https://myafinstancepablo.jfrog.io/artifactory/api/storage/docker-trial/"


    api_key = os.getenv("PABLO_JFROG_TOKEN")
    session = requests.Session()

    headers = {
        'Content-Type': 'application/json',
        'X-JFrog-Art-Api': api_key
    }
    params = {
        'properties': property_string,
        'recursive': '0'
    }


    response = requests.put(url, headers=headers, params=params)

    if response.status_code == 204:
        print('Properties updated successfully.')
    else:
        print(f'Failed to update properties. Status code: {response.status_code}')
        print(response.text)
