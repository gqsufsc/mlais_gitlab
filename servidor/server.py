import os
import json

from flask import Flask, render_template, request, jsonify, send_file, url_for
from werkzeug.utils import redirect

import servidor.turma_service as ts

# Initializing the FLASK API
flaskApp = Flask(__name__)
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


@flaskApp.route('/', methods=['GET'])
def index():
    # Main page
    return redirect(url_for('turmas'))


@flaskApp.route('/delete/<token>', methods=['POST'])
def delete_picture(token: str):
    if request.method == 'POST':
        pictures = ts.uploaded_pictures(token)
        if (request.form['pass_value'] in pictures) :
            ts.delete_picture(token, request.form['pass_value'])
            return redirect(url_for('turma', token=token))
        return jsonify({"error": "invalid picture"})
    return None

@flaskApp.route('/turma/<token>/<name>')
def get_picture(token: str, name: str):
    return send_file(ts.get_path() + token + '/upload/' + name, mimetype='image/jpg/png/jpeg', cache_timeout=0, )


@flaskApp.route('/turma/<token>', methods=['GET'])
def turma(token: str):
    uploaded = ts.uploaded_pictures(token)
    return render_template('turma.html', turma=token, uploaded=uploaded)


@flaskApp.route('/turmas', methods=['GET'])
def turmas():
    turmas = ts.list_turmas()
    return render_template('turmas.html', turmas=turmas)


@flaskApp.route('/train/<token>', methods=['GET'])
def train(token : str):
    evaluation = ts.train(token)
    return redirect(url_for('turma', token=token))


# Upload
#   Possible Status:
#       ok
#   Possible Errors:
#       Not POST method
#       invalid token
#       empty extension format
#       invalid extension
@flaskApp.route('/upload/<token>', methods = ['POST'])
def upload_file(token : str) -> json:
    if request.method == 'POST':
        extension =  request.headers.get('extension')
        error = verify(token, extension)
        if error == None :
            ts.upload(token, request.get_data(), extension)
            return jsonify({"status":"ok"})
        else :
            return jsonify(error)
    return jsonify({"error": "Not POST method"})


# Predict
#   Possible responses:
#       All classifications from model
#   Possible Errors:
#       Not POST method             Erro no componente
#       empty extension format      Erro no componente
#       invalid token               Erro na requisição
#       invalid extension           Erro na requisição
@flaskApp.route('/predict/<token>', methods=['POST'])
def predict(token : str) -> json :
    if request.method == 'POST':
        extension =  request.headers.get('extension')
        error = verify(token, extension)
        if error == None :
            prediction = ts.predict(token, request.get_data(), extension)
            return json.loads(prediction)
        else :
            return jsonify(error)
    return jsonify({"error": "Not POST method"})


@flaskApp.route('/stopserver', methods=['GET'])
def stopServer():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return jsonify({ "success": True, "message": "Server is shutting down..." })


def verify(token : str, extension) -> json :
    if not os.path.exists(ts.get_path() + token):
        return {"error": "invalid token."}
    if not extension:
        return {"error": "empty extension format."}
    if not (extension in ALLOWED_EXTENSIONS):
        return {"error": "invalid extension."}
    return None