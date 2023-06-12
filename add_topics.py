import json
import requests
import sys
import os


gh_base_url = "https://api.github.com/"
gh_repos_url = gh_base_url + "users/unstoppablo/repos"
gh_add_topics_url = gh_base_url + "repos/unstoppablo/"

session = requests.Session()
token = os.getenv("PL_PAT")

access = "Bearer " + token
headers = { "Accept": "application/vnd.github+json", "Authorization": access }

def open_file(path):
    with open(path, 'r') as file:
        data = json.load(file)
    
    repo_dict = {}
    
    for entry in data:
        name = entry["name"]

        owner = entry["owner"]["login"]  # owner is a dict
        topics = entry["topics"]
        repo_dict[name] = (owner, topics)
    
    return repo_dict


def get_user_input(repos_dict):
    target_repo = input("Enter the target repo: ")
    topics = []

    if target_repo in repos_dict:
        while True:
            topic = input("Enter a topic (press Enter to finish): ")
            if topic == "":
                break
            topics.append(topic)
        
        return target_repo, topics
    else:
        # entered invalid repo name
        return -1, -1

def get_repo_and_topics_from_args(repos_dict):
    if len(sys.argv) < 2:
        print("Usage: add_topics.py <repo_name> <topic1> [<topic2> ...]")
        sys.exit(1)
    
    repo_name = sys.argv[1]

    if repo_name in repos_dict:

        topics = sys.argv[2:]
        
        if not topics:
            print("Error: At least one topic must be provided.")
            sys.exit(1)
        
        return repo_name, topics
    else:
        return -1, -1

def add_topics(repo, new_topics, existing_topics, repo_owner):
    for topic in new_topics:
        existing_topics.append(topic)
    
    if len(existing_topics) > 0:
        data = {
            "topics": existing_topics
        }
        session.put(gh_add_topics_url+repo+"/topics", headers=headers, json=data)
    else:
        print("0 topics provided. Quitting.")
        sys.exit(1)
        

def test_obtained(target_repo):
    topics_url = gh_contributors_url + repo_name + "/topics"
    topics_resp = session.get(topics_url, headers=headers)
    return topics_resp

if __name__ == "__main__":
    repo_dict = open_file("cloud_data.json")

    target_repo, topics = get_repo_and_topics_from_args(repo_dict)
    # target_repo, topics = get_user_input(repo_dict)

    if target_repo != -1:
        print("You wish to add the following topics to: ", target_repo)
        print(topics)
        
        existing_topics = repo_dict[target_repo][1]  # returns existing topics
        print("existing topics: ", existing_topics)
        print("type: ", type(existing_topics))
        repo_owner = repo_dict[target_repo][0]
        add_topics(target_repo, topics, existing_topics, repo_owner)
        
        topics_resp = test_obtained(target_repo)
        if topics_resp.status_code == 200:
            print("Topics after being added: ")
            print(topics_resp.json())
        else:
            print("Error obtaining latest topics for repo: ", target_repo)
            print("Error code: ", topics_resp)
    else:
        print("Repo could not be found.")
        
    # while True:
    #     target_repo, topics = get_user_input(repo_dict)

    #     if target_repo != -1:
    #         print("You wish to add the following topics to: ", target_repo)
    #         print(topics)
    #         choice = input("Do you wish to proceed? (Y/N)")
    #         if choice == "Y":
    #             existing_topics = repo_dict[target_repo][1]  # returns existing topics
    #             repo_owner = repo_dict[target_repo][0]
    #             add_topics(target_repo, topics, repo_dict, existing_topics, repo_owner)
    #         else:
    #             cancel = input("Restarting. Enter 'quit' to abort program.")
    #             if cancel == "quit":
    #                 break
    #     else:
    #         cancel = input("Repo could not be found, please enter 'quit' to abort or press anything else to continue.")
    #         if cancel == "quit":
    #                 break