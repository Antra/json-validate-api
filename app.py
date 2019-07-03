import pprint
from flask import Flask, jsonify, request, render_template, abort, make_response
#import datetime as dt
import json
# import jsonschema
from jsonschema import Draft7Validator, FormatChecker, ValidationError, SchemaError, validate
import jsonref
import urllib.request
import subprocess

# Get the swagger file in place
swaggerUrl = 'https://api.basware.com/swagger/v1/swagger.json'
tempSwagger = 'temp/swagger.json'
schemaDir = 'temp'
schemaFile = schemaDir + '/_definitions.json'
urllib.request.urlretrieve(swaggerUrl, tempSwagger)
# and extract the schema from it using openapi2jsonschema
try:
    retcode = subprocess.call(
        "openapi2jsonschema" + " file:" + tempSwagger + " -o " + schemaDir + " --prefix=''", shell=True)
    if retcode < 0:
        print("That didn't work ... ", retcode)
    else:
        print("That went okay. Proceeding.")
except OSError as e:
    print("Execution failed:", e)
# and then read it
with open(schemaFile, 'r') as f:
    schema = jsonref.load(f)

# TODO
# add handling for multiple items in the requests
# add a way to dump the generated schemas to a file (utilise elsewhere)
# add rest of relevant endpoints (mainly AccountingDocuments that needs some work)


# Start getting the needed stuff in place
# Read some example files to create a basic data store
with open('data/suppliers.json', 'r') as f:
    suppliers = json.load(f)
with open('data/accounts.json', 'r') as f:
    accounts = json.load(f)
with open('data/advancedpermissions.json', 'r') as f:
    advancedpermissions = json.load(f)
with open('data/advancedvalidations.json', 'r') as f:
    advancedvalidations = json.load(f)
with open('data/costcenters.json', 'r') as f:
    costcenters = json.load(f)
with open('data/exchangerates.json', 'r') as f:
    exchangerates = json.load(f)
with open('data/genericlists.json', 'r') as f:
    genericlists = json.load(f)
with open('data/matchingorderlines.json', 'r') as f:
    matchingorderlines = json.load(f)
with open('data/matchingorders.json', 'r') as f:
    matchingorders = json.load(f)
with open('data/paymentterms.json', 'r') as f:
    paymentterms = json.load(f)
with open('data/projects.json', 'r') as f:
    projects = json.load(f)
with open('data/taxcodes.json', 'r') as f:
    taxcodes = json.load(f)
with open('data/users.json', 'r') as f:
    users = json.load(f)
with open('data/prebookresponses.json', 'r') as f:
    prebookresponses = json.load(f)
with open('data/transferresponses.json', 'r') as f:
    transferresponses = json.load(f)
with open('data/paymentresponses.json', 'r') as f:
    paymentresponses = json.load(f)


# The let's make a dictionary of the endpoints and the corresponding schema locations
endpointList = {
    "accounts": "AccountEntity",
    "suppliers": "VendorEntity",
    "advancedPermissions": "AdvancedPermissionEntity",
    "advancedValidations": "AdvancedValidationEntity",
    "costCenters": "CostCenterEntity",
    "exchangeRates": "ExchangeRateEntity",
    "lists": "GenericListEntity",
    "matchingOrderLines": "OrderLineEntity",
    "matchingOrders": "OrderEntity",
    "paymentTerms": "PaymentTermEntity",
    "projects": "ProjectEntity",
    "taxCodes": "TaxCodeEntity",
    "users": "UserEntity",
    "accountingDocumentstransferResponses": "TransferResponseEntity",
    "accountingDocumentsacknowledge": "",
    "accountingDocumentsprebookResponses": "PrebookResponseEntity",
    "accountingDocumentspaymentResponses": "PaymentResponseEntity"
}


# Full schema
# Some preparation work is needed, first generate the full schema from swagger with openapi2jsonschema:
#  openapi2jsonschema file:swagger.json --prefix=""
# then load this schema using jsonref to resolve the "$ref"-references
# lastly, make sure to reference the correct part of the schema in the individual endpoints, e.g. Draft7Validator(schema['definitions']['AccountEntity'])

# with open('schema/schema.json', 'r') as f:
##     schema = jsonref.load(f)


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
def schema_validate(data, endpoint):
    """
    This function takes a JSON object and a schema reference
    and returns the validation result

    :return:        JSON object and 0 errors, if validation passes
                    List of errors and error count, if validation fails
    """
    schemaLocation = endpointList[endpoint]
    validationErrors = ""
    errorCount = 0
    try:
        v = Draft7Validator(schema['definitions'][schemaLocation])
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
    advancedpermissiondata = make_pretty_json(advancedpermissions)
    advancedvalidationdata = make_pretty_json(advancedvalidations)
    costcenterdata = make_pretty_json(costcenters)
    exchangeratedata = make_pretty_json(exchangerates)
    genericlistdata = make_pretty_json(genericlists)
    matchingorderlinedata = make_pretty_json(matchingorderlines)
    matchingorderdata = make_pretty_json(matchingorders)
    paymenttermdata = make_pretty_json(paymentterms)
    projectdata = make_pretty_json(projects)
    taxcodedata = make_pretty_json(taxcodes)
    userdata = make_pretty_json(users)
    transferresponsedata = make_pretty_json(transferresponses)
    prebookresponsedata = make_pretty_json(prebookresponses)
    paymentresponsedata = make_pretty_json(paymentresponses)
    # return render_template('home.html', supplierdata = json.dumps(suppliers, sort_keys = False, indent = 4, separators = (',', ': ')))
    return render_template('home.html', **locals())


@app.route('/suppliers', methods=['POST'])
def handle_suppliers():
    """
    This function responds and validates POST calls against
    /<endpoint>

    :return:        201, if the resources passed validation
                    400, if the resources fail validation
                    500, if the schemas fail validation
    """
    # get current endpoint, so we know which part of the schema to use
    endpoint = request.url_rule.rule.lstrip('/')
    # validate the payload against the relevant schema part, then use the errorCount to get the corresponding HTTP response code
    errorCount, returnMessage = schema_validate(
        request.json, endpoint)
    responseCode = get_http_code(errorCount)
    # lastly, serve the HTTP response - if errorCount = 0, the returnMessage contains the original request payload
    return jsonify({'validation_errors': errorCount, 'response': returnMessage}), responseCode


@app.route('/accounts', methods=['POST'])
def handle_accounts():
    """
    This function responds and validates POST calls against
    /<endpoint>

    :return:        201, if the resources passed validation
                    400, if the resources fail validation
                    500, if the schemas fail validation
    """
    # get current endpoint, so we know which part of the schema to use
    endpoint = request.url_rule.rule.lstrip('/')
    # validate the payload against the relevant schema part, then use the errorCount to get the corresponding HTTP response code
    errorCount, returnMessage = schema_validate(
        request.json, endpoint)
    responseCode = get_http_code(errorCount)
    # lastly, serve the HTTP response - if errorCount = 0, the returnMessage contains the original request payload
    return jsonify({'validation_errors': errorCount, 'response': returnMessage}), responseCode


@app.route('/advancedPermissions', methods=['POST'])
def handle_advancedpermissions():
    """
    This function responds and validates POST calls against
    /<endpoint>

    :return:        201, if the resources passed validation
                    400, if the resources fail validation
                    500, if the schemas fail validation
    """
    # get current endpoint, so we know which part of the schema to use
    endpoint = request.url_rule.rule.lstrip('/')
    # validate the payload against the relevant schema part, then use the errorCount to get the corresponding HTTP response code
    errorCount, returnMessage = schema_validate(
        request.json, endpoint)
    responseCode = get_http_code(errorCount)
    # lastly, serve the HTTP response - if errorCount = 0, the returnMessage contains the original request payload
    return jsonify({'validation_errors': errorCount, 'response': returnMessage}), responseCode


@app.route('/advancedValidations', methods=['POST'])
def handle_advancedvalidations():
    """
    This function responds and validates POST calls against
    /<endpoint>

    :return:        201, if the resources passed validation
                    400, if the resources fail validation
                    500, if the schemas fail validation
    """
    # get current endpoint, so we know which part of the schema to use
    endpoint = request.url_rule.rule.lstrip('/')
    # validate the payload against the relevant schema part, then use the errorCount to get the corresponding HTTP response code
    errorCount, returnMessage = schema_validate(
        request.json, endpoint)
    responseCode = get_http_code(errorCount)
    # lastly, serve the HTTP response - if errorCount = 0, the returnMessage contains the original request payload
    return jsonify({'validation_errors': errorCount, 'response': returnMessage}), responseCode


@app.route('/costCenters', methods=['POST'])
def handle_costcenters():
    """
    This function responds and validates POST calls against
    /<endpoint>

    :return:        201, if the resources passed validation
                    400, if the resources fail validation
                    500, if the schemas fail validation
    """
    # get current endpoint, so we know which part of the schema to use
    endpoint = request.url_rule.rule.lstrip('/')
    # validate the payload against the relevant schema part, then use the errorCount to get the corresponding HTTP response code
    errorCount, returnMessage = schema_validate(
        request.json, endpoint)
    responseCode = get_http_code(errorCount)
    # lastly, serve the HTTP response - if errorCount = 0, the returnMessage contains the original request payload
    return jsonify({'validation_errors': errorCount, 'response': returnMessage}), responseCode


@app.route('/exchangeRates', methods=['POST'])
def handle_exchangerates():
    """
    This function responds and validates POST calls against
    /<endpoint>

    :return:        201, if the resources passed validation
                    400, if the resources fail validation
                    500, if the schemas fail validation
    """
    # get current endpoint, so we know which part of the schema to use
    endpoint = request.url_rule.rule.lstrip('/')
    # validate the payload against the relevant schema part, then use the errorCount to get the corresponding HTTP response code
    errorCount, returnMessage = schema_validate(
        request.json, endpoint)
    responseCode = get_http_code(errorCount)
    # lastly, serve the HTTP response - if errorCount = 0, the returnMessage contains the original request payload
    return jsonify({'validation_errors': errorCount, 'response': returnMessage}), responseCode


@app.route('/lists', methods=['POST'])
def handle_lists():
    """
    This function responds and validates POST calls against
    /<endpoint>

    :return:        201, if the resources passed validation
                    400, if the resources fail validation
                    500, if the schemas fail validation
    """
    # get current endpoint, so we know which part of the schema to use
    endpoint = request.url_rule.rule.lstrip('/')
    # validate the payload against the relevant schema part, then use the errorCount to get the corresponding HTTP response code
    errorCount, returnMessage = schema_validate(
        request.json, endpoint)
    responseCode = get_http_code(errorCount)
    # lastly, serve the HTTP response - if errorCount = 0, the returnMessage contains the original request payload
    return jsonify({'validation_errors': errorCount, 'response': returnMessage}), responseCode


@app.route('/matchingOrderLines', methods=['POST'])
def handle_matchingorderlines():
    """
    This function responds and validates POST calls against
    /<endpoint>

    :return:        201, if the resources passed validation
                    400, if the resources fail validation
                    500, if the schemas fail validation
    """
    # get current endpoint, so we know which part of the schema to use
    endpoint = request.url_rule.rule.lstrip('/')
    # validate the payload against the relevant schema part, then use the errorCount to get the corresponding HTTP response code
    errorCount, returnMessage = schema_validate(
        request.json, endpoint)
    responseCode = get_http_code(errorCount)
    # lastly, serve the HTTP response - if errorCount = 0, the returnMessage contains the original request payload
    return jsonify({'validation_errors': errorCount, 'response': returnMessage}), responseCode


@app.route('/matchingOrders', methods=['POST'])
def handle_matchingorders():
    """
    This function responds and validates POST calls against
    /<endpoint>

    :return:        201, if the resources passed validation
                    400, if the resources fail validation
                    500, if the schemas fail validation
    """
    # get current endpoint, so we know which part of the schema to use
    endpoint = request.url_rule.rule.lstrip('/')
    # validate the payload against the relevant schema part, then use the errorCount to get the corresponding HTTP response code
    errorCount, returnMessage = schema_validate(
        request.json, endpoint)
    responseCode = get_http_code(errorCount)
    # lastly, serve the HTTP response - if errorCount = 0, the returnMessage contains the original request payload
    return jsonify({'validation_errors': errorCount, 'response': returnMessage}), responseCode


@app.route('/paymentTerms', methods=['POST'])
def handle_paymentterms():
    """
    This function responds and validates POST calls against
    /<endpoint>

    :return:        201, if the resources passed validation
                    400, if the resources fail validation
                    500, if the schemas fail validation
    """
    # get current endpoint, so we know which part of the schema to use
    endpoint = request.url_rule.rule.lstrip('/')
    # validate the payload against the relevant schema part, then use the errorCount to get the corresponding HTTP response code
    errorCount, returnMessage = schema_validate(
        request.json, endpoint)
    responseCode = get_http_code(errorCount)
    # lastly, serve the HTTP response - if errorCount = 0, the returnMessage contains the original request payload
    return jsonify({'validation_errors': errorCount, 'response': returnMessage}), responseCode


@app.route('/projects', methods=['POST'])
def handle_projects():
    """
    This function responds and validates POST calls against
    /<endpoint>

    :return:        201, if the resources passed validation
                    400, if the resources fail validation
                    500, if the schemas fail validation
    """
    # get current endpoint, so we know which part of the schema to use
    endpoint = request.url_rule.rule.lstrip('/')
    # validate the payload against the relevant schema part, then use the errorCount to get the corresponding HTTP response code
    errorCount, returnMessage = schema_validate(
        request.json, endpoint)
    responseCode = get_http_code(errorCount)
    # lastly, serve the HTTP response - if errorCount = 0, the returnMessage contains the original request payload
    return jsonify({'validation_errors': errorCount, 'response': returnMessage}), responseCode


@app.route('/taxCodes', methods=['POST'])
def handle_taxcodes():
    """
    This function responds and validates POST calls against
    /<endpoint>

    :return:        201, if the resources passed validation
                    400, if the resources fail validation
                    500, if the schemas fail validation
    """
    # get current endpoint, so we know which part of the schema to use
    endpoint = request.url_rule.rule.lstrip('/')
    # validate the payload against the relevant schema part, then use the errorCount to get the corresponding HTTP response code
    errorCount, returnMessage = schema_validate(
        request.json, endpoint)
    responseCode = get_http_code(errorCount)
    # lastly, serve the HTTP response - if errorCount = 0, the returnMessage contains the original request payload
    return jsonify({'validation_errors': errorCount, 'response': returnMessage}), responseCode


@app.route('/users', methods=['POST'])
def handle_users():
    """
    This function responds and validates POST calls against
    /<endpoint>

    :return:        201, if the resources passed validation
                    400, if the resources fail validation
                    500, if the schemas fail validation
    """
    # get current endpoint, so we know which part of the schema to use
    endpoint = request.url_rule.rule.lstrip('/')
    # validate the payload against the relevant schema part, then use the errorCount to get the corresponding HTTP response code
    errorCount, returnMessage = schema_validate(
        request.json, endpoint)
    responseCode = get_http_code(errorCount)
    # lastly, serve the HTTP response - if errorCount = 0, the returnMessage contains the original request payload
    return jsonify({'validation_errors': errorCount, 'response': returnMessage}), responseCode


# Accounting Document group
@app.route('/accountingDocuments/<string:document_id>/transferResponses', methods=['POST'])
def handle_accountingdocuments_transferresponses(document_id):
    """
    This function responds and validates POST calls against
    /<endpoint>

    :return:        201, if the resources passed validation
                    400, if the resources fail validation
                    500, if the schemas fail validation
    """
    # get current endpoint, so we know which part of the schema to use
    endpoint = request.url_rule.rule.lstrip(
        '/').replace('/<string:document_id>/', '')
    # validate the payload against the relevant schema part, then use the errorCount to get the corresponding HTTP response code
    errorCount, returnMessage = schema_validate(
        request.json, endpoint)
    responseCode = get_http_code(errorCount)
    # lastly, serve the HTTP response - if errorCount = 0, the returnMessage contains the original request payload
    return jsonify({'validation_errors': errorCount, 'response': returnMessage}), responseCode


@app.route('/accountingDocuments/<string:document_id>/prebookResponses', methods=['POST'])
def handle_accountingdocuments_prebookresponses(document_id):
    """
    This function responds and validates POST calls against
    /<endpoint>

    :return:        201, if the resources passed validation
                    400, if the resources fail validation
                    500, if the schemas fail validation
    """
    # get current endpoint, so we know which part of the schema to use
    endpoint = request.url_rule.rule.lstrip(
        '/').replace('/<string:document_id>/', '')
    # validate the payload against the relevant schema part, then use the errorCount to get the corresponding HTTP response code
    errorCount, returnMessage = schema_validate(
        request.json, endpoint)
    responseCode = get_http_code(errorCount)
    # lastly, serve the HTTP response - if errorCount = 0, the returnMessage contains the original request payload
    return jsonify({'validation_errors': errorCount, 'response': returnMessage}), responseCode


@app.route('/accountingDocuments/<string:document_id>/paymentResponses', methods=['POST'])
def handle_accountingdocuments_paymentResponses(document_id):
    """
    This function responds and validates POST calls against
    /<endpoint>

    :return:        201, if the resources passed validation
                    400, if the resources fail validation
                    500, if the schemas fail validation
    """
    # get current endpoint, so we know which part of the schema to use
    endpoint = request.url_rule.rule.lstrip(
        '/').replace('/<string:document_id>/', '')
    # validate the payload against the relevant schema part, then use the errorCount to get the corresponding HTTP response code
    errorCount, returnMessage = schema_validate(
        request.json, endpoint)
    responseCode = get_http_code(errorCount)
    # lastly, serve the HTTP response - if errorCount = 0, the returnMessage contains the original request payload
    return jsonify({'validation_errors': errorCount, 'response': returnMessage}), responseCode


@app.route('/accountingDocuments/<string:document_id>/acknowledge', methods=['POST'])
def handle_accountingdocuments_acknowledge(document_id):
    """
    This function responds and validates POST calls against
    /<endpoint>

    :return:        201, if the resources passed validation
                    400, if the resources fail validation
                    500, if the schemas fail validation
    """
    # this endpoint is different from the others and does not take a payload, thus there's nothing to validate.
    # lastly, serve the HTTP response - if errorCount = 0, the returnMessage contains the original request payload
    return jsonify({'validation_errors': 0, 'response': 'this endpoint takes no payload, so there is nothing to validate'}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
    # app.run(host='0.0.0.0', port=443, debug=False, ssl_context='adhoc')
