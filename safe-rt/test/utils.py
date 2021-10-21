import json

def load_rule(filename):
    with open(filename, 'rb') as f:
        rule = json.load(f)
    return rule

