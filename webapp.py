import json
from flask import Flask, render_template, Response, request
from core import compat, utils, app
from core.ctrl import api, auth

compat.check_version()
webapp = Flask(__name__)


@webapp.route('/')
def index():

    app.config['headers'] = dict(request.headers)

    if 'X-Forwarded-For' in app.config['headers'].keys():
        app.config['client_ip'] = app.config['headers']['X-Forwarded-For']
    else:
        app.config['client_ip'] = request.remote_addr

    return render_template('index.html', config=app.config)


@webapp.route('/api/')
@webapp.route('/api/<path:api_method>', methods=['POST', 'GET'])
def respond(api_method=None):

    app.config['headers'] = dict(request.headers)

    if 'X-Forwarded-For' in app.config['headers'].keys():
        app.config['client_ip'] = app.config['headers']['X-Forwarded-For']
    else:
        app.config['client_ip'] = request.remote_addr

    api_method = str(api_method).replace('/', '')
    reason = 'API route "' + api_method + '" is not supported'
    module_status = False
    result = None
    request_method = 'Unknown'

    if api_method != None and api_method in dir(api):

        reason = 'API route: ' + api_method
        data_pass = {}

        if request.method == 'POST':
            request_method = 'POST'
            data_pass = request.form
        else:
            request_method = 'GET'
            data_pass = request.args

        data_pass = dict(data_pass)
        data_pass['config'] = app.config

        logged = auth.authorization_process(api_method)
        result = logged

        if logged['status'] == True:
            # Start api request passing
            module_status = True

            if api_method != 'login':
                result = getattr(api, api_method)(data_pass)

    res = json.dumps({
        'api': app.config['full_name'] + ' REST api 1.0',
        'module_status': module_status,
        'request_method': request_method,
        'reason': reason,
        'result': result
    })

    return Response(res, mimetype='application/json')


if __name__ == '__main__':
    # Open, any host allowed
    webapp.run(debug=True, host='0.0.0.0', port='5007')

    # Secure, only localhost allowed
    # webapp.run(debug=True, host='127.0.0.1', port='5007')
