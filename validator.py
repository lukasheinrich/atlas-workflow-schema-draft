#!/usr/bin/env python
import json
import os
import jsonschema
import jsonref
import yaml
from jsonschema import Draft4Validator, validators


def extend_with_default(validator_class):
    validate_properties = validator_class.VALIDATORS["properties"]

    def set_defaults(validator, properties, instance, schema):
        for property, subschema in properties.iteritems():
            if "default" in subschema:
                instance.setdefault(property, subschema["default"])

        for error in validate_properties(
            validator, properties, instance, schema,
        ):
            yield error

    return validators.extend(
        validator_class, {"properties" : set_defaults},
    )


DefaultValidatingDraft4Validator = extend_with_default(Draft4Validator)



def loader(base_uri):
    def load(uri):
        return jsonref.load_uri('{}/{}'.format(base_uri,uri), base_uri = base_uri)
    return load


def validate_schema(schema_name):
    relpath = 'actualschemas/{}.json'.format(schema_name)
    abspath = os.path.abspath('actualschemas/{}.json'.format(schema_name))
    absbase = os.path.dirname(abspath)
    base_uri = 'file://' + absbase + '/'
    
    
    schema   = json.load(open('actualschemas/{}.json'.format(schema_name)))
    resolver = jsonschema.RefResolver(base_uri, schema)
    refloader = loader(base_uri)
    
    testobjects = refloader('{}-test.json'.format(schema_name))

    yamlpath = 'actualschemas/{}-test.yaml'.format(schema_name)
    if os.path.exists(yamlpath):
        testobjects += yaml.load(open(yamlpath))
    for o in testobjects:
        DefaultValidatingDraft4Validator(schema, resolver = resolver).validate(o)
        print o

def main():
    for s in ['nodemap-scheduler-schema']:
        print "validating {}".format(s)
        validate_schema(s)
    
if __name__ == '__main__':
    main()
