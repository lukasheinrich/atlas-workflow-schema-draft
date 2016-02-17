import jsonref
import yaml
import json
import requests
import urllib
base_uri='file:///Users/lukas/Code/scratch/newpseudocap/test_objects/walkthrough/schemas/yamlbased/'

def loader(baseuri):
    def yamlloader(uri,**kwargs):
        try:
            return yaml.load(requests.get(uri).content)
        except:
            return yaml.load(urllib.urlopen(uri).read())
    def load(uri):
        return jsonref.load_uri('{}/{}'.format(base_uri,uri), base_uri = base_uri, loader = yamlloader)
    return load

load_uri = loader(base_uri)

print load_uri('nodemap-scheduler-schema-test.yml')
