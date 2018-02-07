import os
import json
import sys

def read_config():
    with open(sys.path[0]+'/config.json') as data_file:    
        data = json.load(data_file)
    return data

def set_env_vars(data):
    for k,v in data.items():
        os.environ[k] = v
    