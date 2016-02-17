#!/usr/bin/env python
import json
import os
import jsonschema
import jsonref
import yaml
import urllib2
from jsonschema import Draft4Validator, validators
import click

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
    def yamlloader(uri):
        try:
            return yaml.load(requests.get(uri).content)
        except:
            try:
                return yaml.load(urllib2.urlopen(uri).read())
            except:
                print 'CANNOT FIND {}'.format(uri)
                raise RuntimeError
    def load(uri):
        return jsonref.load_uri('{}/{}'.format(base_uri,uri), base_uri = base_uri, loader = yamlloader)
    return load

def workflow_loader(workflowyml,toplevel):
    workflow_base_uri = 'file://' + os.path.abspath(toplevel) + '/'
    refloader = loader(workflow_base_uri)
    workflow = refloader(workflowyml)
    return workflow

def validator(schemadir):
    schema_name = 'workflow-schema'
    relpath     = '{}/{}.json'.format(schemadir,schema_name)
    abspath = os.path.abspath(relpath)
    absbase = os.path.dirname(abspath)
    schema_base_uri = 'file://' + absbase + '/'
    schema   = json.load(open(relpath))
    resolver = jsonschema.RefResolver(schema_base_uri, schema)
    return DefaultValidatingDraft4Validator(schema, resolver = resolver)

def validate_workflow(workflowyml, toplevel, schemadir):
    workflow = workflow_loader(workflowyml,toplevel)
    validator(schemadir).validate(workflow)
    return True

@click.command()
@click.argument('workflow')
@click.argument('toplevel')
@click.argument('schemadir')
def main(workflow,toplevel,schemadir):
    print validate_workflow(workflow.replace(toplevel.rstrip('/')+'/',''), toplevel = toplevel, schemadir = schemadir)
    
if __name__ == '__main__':
    main()
