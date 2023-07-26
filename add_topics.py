import json
import sys
import os
import time
from datetime import datetime, timedelta
import requests
import re


gh_base_url = "https://api.github.com/"
gh_repos_url = gh_base_url + "users/unstoppablo/repos"
gh_add_topics_url = gh_base_url + "repos/unstoppablo/"
gh_contributors_url = gh_base_url + "repos/unstoppablo/"

session = requests.Session()
token = os.getenv("PL_PAT")

access = "Bearer " + token
headers = { "Accept": "application/vnd.github+json", "Authorization": access }

def check_str(myStr):
    open = "["
    close = "]"
    stack = []
    for i in myStr:   # check each character in the string for a [ or a ]
        if i == open: 
            stack.append(i) # if character equals [ add to stack list
        elif i == close:    # check previous character for [
            if len(stack) > 0 and open == stack[len(stack)-1]:
                stack.pop() # remove characters from stack list
            else: # if unable to find [ in stack list then brackets are not contained
                print("Items are not contained within the brackets")
                sys.exit(1)
    if len(stack) == 0:
        return 
    else: # if [ is still in list then items are not contained
        print("Items are not contained within the brackets")
        sys.exit(1)	    


def get_repo_and_topics_from_args():
    if len(sys.argv) < 2:
        print("Usage: add_topics.py [<repo_name>, <topic1>, <topic2] [<other_repo_name>, <topic1>, <topic2] ")  # Changing the format to have parenthesis and commas
        sys.exit(1)
    arg = " ".join(sys.argv[1:])  # put everything after add_topics.py into a string
    bracket_only = bool(re.search(r"[({})]", arg)) # verifying that only brackets are being used
    if bracket_only:
        print("Please only use bracket")
        sys.exit(1)
    check_str(arg)
    arg = arg.replace("[", "")  # remove ( from string
    args_list = arg.split("]")  # use ) as a delimiter for each repository

    #  [<repo_name>, <topic1>, <topic2] -->  ["<repo_name>","<topic1>","<topic2"]
    args_list = [element.strip() for element in args_list if element.strip()]  # strip spaces and filter any empty strings
    print("printing arg after split", args_list)
    repo_dict = {}  # where we store repos and their topics
    for i in args_list:
        i_list = i.split(",")  # split string into list by ,
        i_list = [element.strip() for element in i_list]  # strip spaces
        repo_key = i_list.pop(0)  # store the first value of i_list
        print("Repo Name: " + repo_key)
        repo_dict[repo_key] = []
        
        for topic in i_list:
            repo_dict[repo_key].append(topic) # add topics to repo name dictionary if it's in repo dictionary
    return repo_dict

def get_existing_topics(target_repo):
    topics_url = gh_contributors_url + target_repo + "/topics"
    topics_resp = session.get(topics_url, headers=headers)
    return topics_resp

def add_topics(repo, new_topics, existing_topics):
    existing_topics = set(existing_topics) # changing to set to avoid duplicates
    if len(new_topics) != 0:
        for topic in new_topics:
            if bool(re.search("[a-z]", topic)) == False: # check if topics only contain lowercase letters
                    print("Topics must be in all lowercase")
                    sys.exit(1)
            else:
                existing_topics.add(topic)
    else:
        print("unable to add an empty topic")
        sys.exit(1)
    existing_topics = list(existing_topics) # converting set back into a list
    if len(existing_topics) > 0:
        data = {
            "names": existing_topics
        }
        resp = session.put(gh_add_topics_url+repo+"/topics", headers=headers, json=data)
        return resp
    else:
        print("0 topics provided. Quitting.")
        sys.exit(1)

if __name__ == "__main__":
    new_repo_dict = get_repo_and_topics_from_args()
    
    for target_repo, topics in new_repo_dict.items():
        try:
            print("You wish to add the following topics to: ", target_repo)
            print(topics)
            
            topics_response = get_existing_topics(target_repo)  # returns existing topics
            if topics_resp.status_code == 200:
                existing_topics = topics_resp.json()['names']  # returns list of topics
            else:
                existing_topics = []
            
            add_topics_resp = add_topics(target_repo, topics, existing_topics['names'], )
            print("Attempted adding topics, resp code: ")
            print(add_topics_resp)
            
            topics_resp = get_existing_topics(target_repo)
            if topics_resp.status_code == 200:
                print("Topics after being added: ")
                print(topics_resp.json())
            else:
                print("Error obtaining latest topics for repo: ", target_repo)
                print("Error code: ", topics_resp)
        except Exception as e:
            print("Error during adding topic to repo process: ", e)