def prep_files(data):
    # Creates a dictionary of repos with values being contributor data and repo topics
    with open(data) as json_file:
        d = json.load(json_file)
        repo_dict = {}
        for i in d:
            repo_dict[i['name']] = i['contributors']