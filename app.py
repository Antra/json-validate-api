from flask import Flask, jsonify, request, render_template, abort, make_response
import datetime as dt
import json
# import jsonschema
from jsonschema import Draft7Validator, FormatChecker, ValidationError, SchemaError, validate
from os.path import join, dirname


# Read the data files to create a basic data store
with open('data/suppliers.json', 'r') as f:
    suppliers = json.load(f)


# Load the schemas - and make a list of them for the html page
schemaList = ['suppliers']
with open('schema/supplier.json', 'r') as f:
    supplierSchema = json.load(f)


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


# generic function for getting data
def get_data(datastore, id="", idtype=""):
    """
    This function takes a datastore and returns
    either the indicated entry or the full datastore

    :return:        specific data entry (when id and idtype are given)
    :return:        the full datastore (when id and/or idtype are not given)
    """
    # if id and idtype are present, then we return that entry from the datastore
    if len(str(id)) > 0 and len(str(idtype)) > 0:
        item = [item for item in datastore['data'] if item[idtype] == id]
        if len(item) == 0:
            abort(404)
        return(item[0])
    # otherwise we return the full datastore
    else:
        return(datastore)


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
    supplierdata = make_pretty_json(suppliers)
    endpoints = sorted(schemaList)
    otherdata = make_pretty_json("")
    # return render_template('home.html', supplierdata = json.dumps(suppliers, sort_keys = False, indent = 4, separators = (',', ': ')))
    return render_template('home.html', **locals())


# Supplier
@app.route('/supplier', methods=['POST'])
def handle_supplier():
    """
    This function just responds to the browser URL
    localhost:80/api/supplier/<supplier_id>

    :return:        201, if the resources passed validation
                    400, if the resources fail validation
                    500, if the schemas fail validation
    """
    # Do we have a request with an id and name?
    # if not request.json or not 'name' in request.json or not 'externalCode' in request.json or len(str(request.json['externalCode'])) == 0:
    #   abort(400)

    # Do we have a valid request?
    # This works!
    # try:
    #    jsonschema.validate(request.json, supplierSchema)
    #    print('schema validation ok!')
    #    return jsonify(request.json), 201
    # except jsonschema.ValidationError as e:
    #    print(e.message)
    #    return ('validation_error:' + e.message), 400
    # except jsonschema.SchemaError as e:
    #    print(e)
    #    return ('schema_error:' + e), 500

    validationErrors = ""
    errorCount = 0
    try:
        v = Draft7Validator(supplierSchema)
        errors = sorted(v.iter_errors(request.json), key=lambda e: e.path)
        for error in errors:
            errorCount += 1
            validationErrors = validationErrors + str(error.message) + ', '
    except SchemaError as e:
        print(e)
        return ('schema_error:' + e), 500

    if errorCount == 0:
        print('schema validation ok!')
        return jsonify(request.json), 200
    else:
        validationErrors = validationErrors.rstrip(', ')
        print('validation error! There were ' +
              str(errorCount) + ' errors!\n' + validationErrors)
        return jsonify({'validation_error': errorCount, 'validation_errors': validationErrors}), 400
        # return (str(errorCount) + ' validation errors!\n' + validationErrors), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
    # app.run(host='0.0.0.0', port=443, debug=False, ssl_context='adhoc')
