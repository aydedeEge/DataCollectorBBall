import os
import json

def read_config():
    with open("{cwd}/../template_config.json".format(cwd = os.getcwd())) as data_file:    
        data = json.load(data_file)
    return data

def set_env_vars(data):
    for k,v in data.items():
        os.environ[k] = v
    