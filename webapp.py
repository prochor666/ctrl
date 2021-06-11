from flask import Flask, render_template, Response, request
import json
from core import compat, initialize as app
from core.ctrl import api

compat.check_version()
webapp = Flask(__name__)

@webapp.route('/')

def index():
    global app
    app.config['headers'] = dict(request.headers)

    if request.headers.getlist("X-Forwarded-For"):
        app.config['client_ip'] = request.headers.getlist("X-Forwarded-For")[0]
    else:
        app.config['client_ip'] = request.remote_addr
    return render_template('index.html', config=app.config)


@webapp.route('/api/')
@webapp.route('/api/<path:key>', methods = ['POST', 'GET'])

def respond(key=None):
    global app
    app.config['headers'] = dict(request.headers)
    if request.headers.getlist("X-Forwarded-For"):
        app.config['client_ip'] = request.headers.getlist("X-Forwarded-For")[0]
    else:
        app.config['client_ip'] = request.remote_addr

    key = str(key).replace('/', '')
    reason = 'API route "'+ key +'" is not supported'
    status = False
    result = None

    if key != None and key in dir(api):

        reason = 'API route: ' + key
        data_pass = {}

        if request.method == 'POST':
            data_pass = request.form
        else:
            data_pass = request.args

        data_pass = dict(data_pass)
        data_pass['config'] = app.config
        result = getattr(api, key)(app, data_pass)
        status = True

    res  = json.dumps({'api': 'CTRL REST api 1.0', 'module_status': status, 'reason': reason, 'result': result})
    return Response(res, mimetype='application/json')


if __name__ == '__main__':
    # Open, any host allowed
    webapp.run(debug=True, host='0.0.0.0', port='5007')

    # Secure, only localhost allowed
    # webapp.run(debug=True, host='127.0.0.1', port='5007')
