import os
import json
import modelService as ms
import aplication as app

from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

# Initializing the FLASK API
flaskApp = Flask(__name__)

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
        file_path = os.path.join(basepath, 'classes/' + app.token + '/upload', secure_filename(f.filename))
        f.save(file_path)

        # Make prediction
        preds = ms.predict(app.learner, file_path)
        return json.loads(preds)
    return None