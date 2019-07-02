import pprint
from flask import Flask, jsonify, request, render_template, abort, make_response
#import datetime as dt
import json
# import jsonschema
from jsonschema import Draft7Validator, FormatChecker, ValidationError, SchemaError, validate
import jsonref

# Start getting the needed stuff in place
# Read the data files to create a basic data store
with open('data/suppliers.json', 'r') as f:
    suppliers = json.load(f)
with open('data/accounts.json', 'r') as f:
    accounts = json.load(f)

# Full schema
# Some preparation work is needed, first generate the full schema from swagger with openapi2jsonschema:
#  openapi2jsonschema file:swagger.json --prefix=""
# then load this schema using jsonref to resolve the "$ref"-references
# lastly, make sure to reference the correct part of the schema in the individual endpoints, e.g. Draft7Validator(schema['definitions']['AccountEntity'])
with open('schema/schema.json', 'r') as f:
    schema = jsonref.load(f)


# Then make the helper functions
# pretty-print JSON, so it looks nice on HTML pages.
def make_pretty_json(string):
    """
    This function takes a string and returns it ready
    to be pretty-printed by a flask template

    :return:        pretty-print ready string
    """
    if string == "":
        return {}
    else:
        return json.dumps(string, sort_keys=False, indent=4, separators=(',', ': '))


# get http code
def get_http_code(errorCount):
    """
    This function takes an integer and returns an integer
    to use as HTTP response code

    :return:        200, if errorCount = 0
                    400, if errorCount > 0
                    500, if errorCount < 0
    """
    if errorCount > 0:
        return 400
    elif errorCount == 0:
        return 200
    else:
        return 500


# generic validation function
def schema_validate(data, location):
    """
    This function takes a JSON object and a schema reference
    and returns the validation result

    :return:        JSON object and 0 errors, if validation passes
                    List of errors and error count, if validation fails
    """
    validationErrors = ""
    errorCount = 0
    try:
        v = Draft7Validator(schema['definitions'][location])
        errors = sorted(v.iter_errors(data), key=lambda e: e.path)
        for error in errors:
            errorCount += 1
            validationErrors = validationErrors + str(error.message) + ', '
    except SchemaError as e:
        errorCount = -1
        print(e)
        return errorCount, e

    if errorCount > 0:
        validationErrors = validationErrors.rstrip(', ')
        print('validation error! There were ' +
              str(errorCount) + ' errors!\n' + validationErrors)
    elif errorCount == 0:
        validationErrors = data

    return errorCount, validationErrors


# Create the application instance
app = Flask(__name__)
# app = Flask(__name__, template_folder="templates")


# Basic error handling
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


# Create a URL route in our application for "/"
@app.route('/')
def index():
    """
    This function just responds to the browser URL
    localhost:80/

    we set local variables to fill into the template

    :return:        the rendered template 'home.html'
    """
    # Build a list of the available endpoints
    endpoints = []
    for rule in app.url_map.iter_rules():
        # except that we don't want to show root and /static
        if rule.rule not in ('/', '/static/<path:filename>'):
            endpoints.append(rule.rule)
    endpoints = sorted(endpoints)
    supplierdata = make_pretty_json(suppliers)
    accountdata = make_pretty_json(accounts)
    otherdata = make_pretty_json("")
    # return render_template('home.html', supplierdata = json.dumps(suppliers, sort_keys = False, indent = 4, separators = (',', ': ')))
    return render_template('home.html', **locals())


# Supplier
@app.route('/supplier', methods=['POST'])
def handle_supplier():
    """
    This function responds and validates POST calls against
    /<endpoint>

    :return:        201, if the resources passed validation
                    400, if the resources fail validation
                    500, if the schemas fail validation
    """
    schemaLocation = "VendorEntity"
    # validate the payload against the relevant schema, returns errorCount together with a validation message
    errorCount, returnMessage = schema_validate(
        request.json, schemaLocation)
    # get the corresponding HTTP response code based on the number of errors
    responseCode = get_http_code(errorCount)
    # generate the response - if errorCount = 0, the returnMessage contains the original request payload
    return jsonify({'validation_errors': errorCount, 'response': returnMessage}), responseCode


# Account
@app.route('/account', methods=['POST'])
def handle_account():
    """
    This function responds and validates POST calls against
    /<endpoint>

    :return:        201, if the resources passed validation
                    400, if the resources fail validation
                    500, if the schemas fail validation
    """
    schemaLocation = "AccountEntity"
    # validate the payload against the relevant schema, returns errorCount together with a validation message
    errorCount, returnMessage = schema_validate(
        request.json, schemaLocation)
    # get the corresponding HTTP response code based on the number of errors
    responseCode = get_http_code(errorCount)
    # generate the response - if errorCount = 0, the returnMessage contains the original request payload
    return jsonify({'validation_errors': errorCount, 'response': returnMessage}), responseCode


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
    # app.run(host='0.0.0.0', port=443, debug=False, ssl_context='adhoc')
