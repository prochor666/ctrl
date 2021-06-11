from flask import Flask, render_template, Response, request
import json
from core.ctrl import config, api, utils

app = Flask(__name__)

@app.route('/')

def index():

    conf = config.configure()
    conf['app_root'] = utils.app_root()
    if request.headers.getlist("X-Forwarded-For"):
        conf['client_ip'] = request.headers.getlist("X-Forwarded-For")[0]
    else:
        conf['client_ip'] = request.remote_addr

    return render_template('index.html', config=conf)


@app.route('/api/')
@app.route('/api/<path:key>', methods = ['POST', 'GET'])

def respond(key=None):
    key = str(key).replace('/', '')
    reason = 'API route "'+ key +'" is not supported'
    status = False
    result = None
    conf = config.configure()
    conf['app_root'] = utils.app_root()
    conf['headers'] = dict(request.headers)

    if key != None and key in dir(api):

        reason = 'API route: ' + key
        data_pass = {}

        if request.method == 'POST':
            data_pass = request.form
        else:
            data_pass = request.args

        data_pass = dict(data_pass)
        data_pass['config'] = conf
        result = getattr(api, key)(data_pass)
        status = True

    res  = json.dumps({'api': 'CTRL REST api 1.0', 'module_status': status, 'reason': reason, 'result': result})
    return Response(res, mimetype='application/json')


if __name__ == '__main__':
    # Open, any host allowed
    app.run(debug=True, host='0.0.0.0', port='5007')

    # Secure, only localhost allowed
    # app.run(debug=True, host='127.0.0.1', port='5007')
