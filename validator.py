#!/usr/bin/env python
import json
import os
import jsonschema
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

def validate_schema(schema_name):
    relpath = 'actualschemas/{}.json'.format(schema_name)
    abspath = os.path.abspath('actualschemas/{}.json'.format(schema_name))
    absbase = os.path.dirname(abspath)

    schema   = json.load(open('actualschemas/{}.json'.format(schema_name)))
    resolver = jsonschema.RefResolver('file://' + absbase + '/', schema)

    testobjects = json.load(open('actualschemas/{}-test.json'.format(schema_name)))
    for o in testobjects:
        DefaultValidatingDraft4Validator(schema, resolver = resolver).validate(o)
    

def main():
    for s in ['stringinterp-schema','docker-enc-schema','fromattr-pub-schema','step-schema']:
        print "validating {}".format(s)
        validate_schema(s)
    
if __name__ == '__main__':
    main()
