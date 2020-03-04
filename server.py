import os
import json

from flask import Flask, render_template, request, flash, jsonify, send_file, url_for
from werkzeug.utils import redirect

import turma_service as ts

# Initializing the FLASK API
flaskApp = Flask(__name__)
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


@flaskApp.route('/', methods=['GET'])
def index():
    # Main page
    return render_template('index.html')


@flaskApp.route('/turma/<token>/<name>')
def get_picture(token: str, name: str):
    return send_file(ts.get_path() + token + '/upload/' + name, mimetype='image/jpg/png', cache_timeout=0, )


@flaskApp.route('/delete/<token>/<picture>', methods=['POST'])
def delete_picture(token: str, picture: str):
    # TODO:: Confirm action
    ts.delete_picture(token, picture)
    return redirect(url_for('turma', token=token))


@flaskApp.route('/turma/<token>', methods=['GET'])
def turma(token: str):
    uploaded = ts.uploaded_pictures(token)
    return render_template('turma.html', turma=token, uploaded=uploaded, eval='')


@flaskApp.route('/turmas', methods=['GET'])
def turmas():
    turmas = ts.list_turmas()
    return render_template('turmas.html', turmas=turmas)


@flaskApp.route('/train/<token>', methods=['GET'])
def train(token : str):
    evaluation = ts.train(token)
    # return redirect(url_for('turma', token=token, eval=evaluation))
    return redirect(url_for('turma', token=token, eval=''))


@flaskApp.route('/upload/<token>', methods = ['POST'])
def upload_file(token : str) -> json:
    if request.method == 'POST':
        if verifyToken(token) == None :
            ts.upload(token, request.files['file'])
            return jsonify({"status":"ok"})


@flaskApp.route('/predict/<token>', methods=['POST'])
def predict(token : str) -> json :
    if request.method == 'POST':
        if verifyToken(token) == None:
            preds = ts.predict(token, request.files['file'])
            return json.loads(preds)
    return None


def verifyToken(token : str) -> json :
    if not os.path.exists(ts.get_path() + token):
        return jsonify({"error": "invalid token"})

    if 'file' not in request.files:
        flash('No file part')
        return jsonify({"error": "file not found"})

    file = request.files['file']
    if not file and not allowed_file(file.filename):
        return jsonify({"error": "file format not valid or empty file"})

    return None


def allowed_file(filename : str) -> bool:
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# TODO:: Classe page
# TODO:: Classe uploaded files/train page
# TODO:: Model page