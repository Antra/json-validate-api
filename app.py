from flask import Flask, jsonify, request, render_template, abort, make_response
import datetime as dt
import json
from jsonschema import validate

# Read the data files to create a basic data store
with open('data/suppliers.json', 'r') as f:
    suppliers = json.load(f)

# Create the application instance
app = Flask(__name__)
#app = Flask(__name__, template_folder="templates")


# Basic error handling
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


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
    otherdata = make_pretty_json("")
    # return render_template('home.html', supplierdata = json.dumps(suppliers, sort_keys = False, indent = 4, separators = (',', ': ')))
    return render_template('home.html', **locals())


# Create handling for GET /suppliers:
@app.route('/api/suppliers')
def get_suppliers():
    """
    This function just responds to the browser URL
    localhost:80/api/suppliers

    :return:        the suppliers collection
    """
    # return jsonify(suppliers)
    return jsonify(get_data(suppliers))


# Create handling for GET specific supplier
# app.route accepts string (default), int, float, path (same as string plus slashes).
@app.route('/api/supplier/<supplier_id>', methods=['GET'])
def get_supplier(supplier_id):
    """
    This function just responds to the browser URL
    localhost:80/api/supplier/<supplier_id>

    :return:        the specific supplier having that id
    """
    #supplier = [supplier for supplier in suppliers['data'] if supplier['uuid'] == supplier_id]
    # if len(supplier) == 0:
    #    abort(404)
    # return jsonify({'data': supplier[0]})
    return jsonify(get_data(suppliers, supplier_id, "uuid"))


# Create handling for POST a specific supplier
# @app.route('/api/supplier/supplier_id>', methods=['POST']).
@app.route('/api/supplier', methods=['POST'])
def create_supplier():
    """
    This function just responds to the browser URL
    localhost:80/api/supplier/<supplier_id>

    :return:        201, if the resources was created
    """
    # Do we have a request with an id and name?
    if not request.json or not 'name' in request.json or not 'uuid' in request.json or len(str(request.json['uuid'])) == 0:
        abort(400)
    # Do we have an unknown id?
    if (any(d['uuid'] == request.json['uuid'] for d in suppliers['data'])):
        abort(403)
    # Read the relevant data and set the timestamp.
    newsupplier = {
        'uuid': request.json['uuid'],
        'name': request.json['name'],
        'description': request.json['description'],
        'type': request.json['type'],
        'created': dt.datetime.now().isoformat(timespec='microseconds'),
    }

    # then loop through the addresses
    newsupplier["addresses"] = []
    for entry in request.json['addresses']:
        address = {
            'addressid': entry['addressid'],
            'streetname': entry['streetname'],
            'housenumber': entry['housenumber'],
            'postcalcode': entry['postcalcode'],
            'postalarea': entry['postalarea'],
            'country': entry['country'],
            'countryId': entry['countryId']
        }
        newsupplier["addresses"].append(address)

    # and lastly add the new supplier
    suppliers['data'].append(newsupplier)
    return jsonify({'supplier': newsupplier}), 201


# Create handling for PUT a specific supplier:
@app.route('/api/supplier/<supplier_id>', methods=['PUT'])
def update_supplier(supplier_id):
    """
    This function just responds to the browser URL
    localhost:80/api/supplier/<supplier_id>

    :return:        200, if the resource was updated
    """
    supplier = [supplier for supplier in suppliers['data']
                if supplier['uuid'] == supplier_id]
    if len(supplier) == 0:
        abort(404)
    if not request.json or not 'name' in request.json or not 'uuid' in request.json or len(str(request.json['uuid'])) == 0:
        abort(400)
    if not isinstance(request.json['name'], str):
        abort(400)

    # first update the basic data
    supplier[0]['uuid'] = request.json['uuid']
    supplier[0]['name'] = request.json['name']
    supplier[0]['description'] = request.json['description']
    supplier[0]['type'] = request.json['type']
    supplier[0]['created'] = dt.datetime.now(
    ).isoformat(timespec='microseconds')

    # then loop through the addresses if they are included
    if 'addresses' in request.json and len(str(request.json['addresses'])) != 0:
        supplier[0]["addresses"] = []
        for entry in request.json['addresses']:
            address = {
                'addressid': entry['addressid'],
                'streetname': entry['streetname'],
                'housenumber': entry['housenumber'],
                'postcalcode': entry['postcalcode'],
                'postalarea': entry['postalarea'],
                'country': entry['country'],
                'countryId': entry['countryId']
            }
            supplier[0]["addresses"].append(address)
    return jsonify({'supplier': supplier[0]}), 200


# Create handling for DELETE a specific supplier
@app.route('/api/supplier/<supplier_id>', methods=['DELETE'])
def delete_supplier(supplier_id):
    """
    This function just responds to the browser URL
    localhost:80/api/supplier/<supplier_id>

    :return:        200, if the resources was deleted
    """
    supplier = [supplier for supplier in suppliers['data']
                if supplier['uuid'] == supplier_id]
    if len(supplier) == 0:
        abort(404)
    #del supplier[0]
    suppliers['data'][:] = [d for d in suppliers['data']
                            if d.get('uuid') != supplier_id]
    return jsonify({'results': True}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
    #app.run(host='0.0.0.0', port=443, debug=False, ssl_context='adhoc')
