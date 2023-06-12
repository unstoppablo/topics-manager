# Gets all repos including owner, url, and topic information.

import requests
import json
import os
import time
import csv
from csv import DictReader

gh_base_url = "https://api.github.com/"
gh_repos_url = gh_base_url + "users/unstoppablo/repos"
gh_contributors_url = gh_base_url + "repos/unstoppablo/"

session = requests.Session()
token = os.getenv("PL_PAT")

access = "Bearer " + token
headers = { "Accept": "application/vnd.github+json", "Authorization": access }


class Repo(object):
    name = None
    contributors = None
    topics = None
    owner = None

    def __init__(self, name, owner, contributors, topics):
        self.name = name
        self.contributors = contributors
        self.topics = topics
        self.owner = owner


def get_data(repo_name):
    contrib_url = gh_contributors_url + repo_name + "/contributors"
    topics_url = gh_contributors_url + repo_name + "/topics"

    contrib_resp = session.get(contrib_url, headers=headers)
    topics_resp = session.get(topics_url, headers=headers)
    return contrib_resp, topics_resp

def prep_files(path):
    with open(path, 'r') as f:
        dict_reader = DictReader(f)
        # Create a list of dictionaries for cmdb data
        pci_gh_file = list(dict_reader)
    
    return pci_gh_file

def write_file(path, data):
    data_pp = json.dumps(data, indent=2)

    # Will write to /gh-repo/scannability/inputs/ for our scannability analysis
    f = open(path+'cloud_data.json', "w")
    f.write(data_pp)
    f.close()

def get_repos():

    querystring = {"type":"all", "per_page":"100"}

    first_page = session.get(gh_repos_url, params=querystring, headers=headers)
    yield first_page

    next_page = first_page
    while get_next_page(next_page) is not None:
        try:
            next_page_url = next_page.links['next']['url']
            next_page = session.get(next_page_url, headers=headers)
            yield next_page
        except KeyError:
            print("No more github pages")
            break

def get_next_page(page):
    return page if page.headers.get('link') != None else None

if __name__ == "__main__":

    repo_list = []
    for page in get_repos():
        resp = page.json()
        start = time.time()
        for repo in resp:
            try:
                name = repo['name']
                # print(repo)
                contributors, topics = get_data(name) # returns contributors and topics for each repo

                try:
                    if contributors.status_code == 200 and topics.status_code == 200:
                        print("1")
                        owner = repo['owner']
                        print("2")
                        repo_details = Repo(name, owner.json(), contributors.json(), topics.json())
                        print("3. got repo details")
                        repo_list.append(repo_details.__dict__)
                        print("4. repo details appended to repo list")
                    else:
                        print("repo name : ", name)
                        print("contrib code: ", contributors.status_code)
                        print("topics code: ", topics.status_code)
                    print("-----------------------------")
                except:
                    print("Response code not 200, repo: ", name)
            except:
                print("Error with repo: ", repo)
                
                            
    
        end = time.time()
        elapsed = end - start
        print("time elapsed: " + str(elapsed))

    directory = os.getcwd()
    filepath = directory + "/"
    
    print("########################################")
    for entry in repo_list:
        try:
            entry['environment'] = "GitHub Cloud"
            print(entry)
        except:
            print("ERROR ADDING ENVIRONMENT INFO")
    write_file(filepath, repo_list)