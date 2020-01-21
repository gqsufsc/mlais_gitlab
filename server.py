from flask import Flask, render_template

# Initializing the FLASK API
app = Flask(__name__)

# Defining the home page for the web service
@app.route('/')
def home():
    return render_template('upload.html')

# Writing api for inference using the loaded model
# @app.route('/predict',methods=['POST'])

# Defining the predict method get input from the html page and to predict using the trained model
def predict():
    # TODO
    return render_template('index.html', prediction_text='Prediction Err !!!')


