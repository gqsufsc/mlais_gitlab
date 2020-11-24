import math
import os
import json
import time

import numpy as np

from flask import Flask, render_template, request, jsonify, send_file, url_for, session, flash
from werkzeug.utils import redirect

import turma_service as ts
import model_service as ms

# Initializing the FLASK API
flaskApp = Flask(__name__)
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

ADMIN_LOGIN = 'tcc'
ADMIN_PASSWORD = '1234'


@flaskApp.route('/login', methods=['POST'])
def login():
    if request.form['password'] == ADMIN_PASSWORD and request.form['username'] == ADMIN_LOGIN:
        session['logged_in'] = True
    else:
        # TODO
        flash('Usuário e/ou senha inválidos')
    return index()


@flaskApp.route("/logout")
def logout():
    session['logged_in'] = False
    return render_template('login.html')


@flaskApp.route("/cadastro_turma", methods=['POST'])
def cadastro_turma():
    if not session.get('logged_in'):
        return render_template('login.html')

    descricao = request.form['descricao']
    modelo = request.form['modelo']

    ts.create_turma(modelo, descricao)

    return turmas()


@flaskApp.route("/editar_turma/<token>", methods=['POST'])
def editar_turma(token: str):
    if not session.get('logged_in'):
        return render_template('login.html')

    descricao = request.form['descricao']
    modelo = request.form['modelo']

    ts.edit_turma(token, modelo, descricao)

    return turmas()


@flaskApp.route('/', methods=['GET'])
def index():
    if not session.get('logged_in'):
        return render_template('login.html')

    return redirect(url_for('turmas'))


@flaskApp.route('/delete/<token>', methods=['POST'])
def delete_picture(token: str):
    if not session.get('logged_in'):
        return render_template('login.html')

    if request.method == 'POST':
        pictures = ts.uploaded_pictures(token)
        if (request.form['pass_value'] in pictures) :
            ts.delete_picture(token, request.form['pass_value'])
            return redirect(url_for('turma', token=token))
        return jsonify({"error": "invalid picture"})
    return None


@flaskApp.route('/turma/<token>/<tag>/<name>')
def get_tagged_picture(token: str, tag: str, name: str):
    if not session.get('logged_in'):
        return render_template('login.html')
    # tag = ts.get_class_original(token, tag)
    return send_file(ts.get_path() + token + '/upload/train/' + tag + '/' + name, mimetype='image/jpg/png/jpeg', cache_timeout=0)


@flaskApp.route('/turma/<token>', methods=['GET'])
def turma(token: str):
    if not session.get('logged_in'):
        return render_template('login.html')

    error = ts.get_display_error(token)
    dict = ts.uploaded_pictures_dict(token)
    translation = ts.get_translation_dict(token)
    evaluation = request.args.get("evaluation")

    if evaluation:
        evaluation = eval(evaluation)

    return render_template('turma.html', turma=token, dict=dict, translation=translation, evaluation=evaluation, error=error)


@flaskApp.route("/move_picture_to_tag", methods=['GET'])
def move_picture_to_tag():
    if not session.get('logged_in'):
        return render_template('login.html')

    # TODO: validate token
    # TODO: validate picture

    token = request.args.get("token")
    picture = request.args.get("picture")
    tag = request.args.get("tag")

    if tag != "":
        ts.move_picture_to_tag(turma=token, picture=picture, tag=tag)
        return turma(token)


@flaskApp.route('/turmas', methods=['GET'])
def turmas():
    if not session.get('logged_in'):
        return render_template('login.html')

    return render_template('turmas.html', turmas=ts.get_all_turmas())


@flaskApp.route('/cadastrar', methods=['GET'])
def cadastrar():
    if not session.get('logged_in'):
        return render_template('login.html')

    modelos = ms.list_models()
    return render_template('cadastro_turma.html', modelos = modelos)


@flaskApp.route('/editar', methods=['GET'])
def editar():
    if not session.get('logged_in'):
        return render_template('login.html')

    modelos = ms.list_models()
    turmas = ts.get_all_turmas()

    turma = request.args.get("token")
    descricao = turmas[turma]['descricao']
    modelo = ts.model_name(turma)

    return render_template('editar_turma.html', modelos = modelos, turma=turma, descricao=descricao, modelo=modelo)


@flaskApp.route('/excluir', methods=['GET'])
def excluir():
    if not session.get('logged_in'):
        return render_template('login.html')

    token = request.args.get("token")

    ts.delete_turma(token)
    return turmas()


@flaskApp.route('/clean', methods=['GET'])
def clean():
    if not session.get('logged_in'):
        return render_template('login.html')

    token = request.args.get("token")

    ts.delete_upload(token)
    return turma(token)


@flaskApp.route('/train/<token>', methods=['GET', 'POST'])
def train(token : str):
    if not session.get('logged_in'):
        return render_template('login.html')

    if ts.get_display_error(token) != 0:
        return turma(token)

    epoch = request.args.get('epoch')

    classes = ts.list_classes(token)
    evaluation = ts.train(token, int(epoch))
    evaluation = np.array(evaluation, dtype=float)

    d = {}
    for x in range(evaluation.shape[0]):
        d[x] = {}
        total = ts.get_image_count_for_classe(token, classes[x]) * 0.8 # 0.2 valid
        for y in range(evaluation.shape[1]):
            if math.isnan( evaluation[x][y]):
                d[x][y] = 0.0
            else:
                d[x][y] = float("{:.2f}".format(evaluation[x][y] / total))

    print(d)

    return redirect(url_for('turma', token=token, evaluation=d))


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
        tag = request.headers.get('tagImagem')
        error = verify(token, extension)
        if error == None :
            ts.upload(token, tag, data, extension)
            return jsonify({"status":"ok"})
        else :
            time.sleep(0.05) # Evita apresentar erro 1104 no cliente, não sei o motivo
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
        else:
            time.sleep(0.05) # Evita apresentar erro 1104 no cliente, não sei o motivo
            return jsonify(error)

    return jsonify({"error": "Not POST method"})


@flaskApp.route('/classificacoes/<token>', methods=['GET'])
def classifications(token : str) -> json :
    if not os.path.exists(ts.get_path() + token):
        return {"error": "invalid token."}

    classes = ts.list_classes_translated(token)
    classes = ', '.join(classes)
    return {"classes": classes}


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


