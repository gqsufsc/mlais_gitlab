import os
import json

from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

import classe_service as cs
import model_service as ms

# Initializing the FLASK API
flaskApp = Flask(__name__)

token = '087aae'


@flaskApp.route('/', methods=['GET'])
def index():
    # Main page
    return render_template('index.html')


@flaskApp.route('/predict', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Get the file from post request
        f = request.files['file']

        # Save the file to ./upload
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(basepath, 'classes/' + token + '/upload', secure_filename(f.filename))
        f.save(file_path)

        # Make prediction
        learner = cs.load_learner(token)
        preds = ms.predict(learner, file_path)
        return json.loads(preds)
    return None