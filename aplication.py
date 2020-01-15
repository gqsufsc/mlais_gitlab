import os

from flask import Flask, render_template
from fastai.vision import load_learner, models, error_rate, data, create_cnn

# Saving the working directory and model directory
cwd = os.getcwd()
modelsPath = cwd + '/data/models'

# Initializing the FLASK API
app = Flask(__name__)

# Loading the saved model using fastai's load_learner method
model = load_learner(modelsPath, 'tmp.pth')
# model = load_learner(path, 'model.pkl')


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





# Load model
def LoadLearner(modelName):
    # TODO
    learner = create_cnn(data, models.resnet34, metrics=error_rate)
    learner.load(modelsPath, modelName + '.pth')    # or *.pkl   -> pickle lib
    return learner

# Train model with images from path
def TrainModel(learner, imgsPath, modelName):
    # TODO

    learner.save(modelName, return_path=True)
    learner.export(modelName + '.pkl')

    return learner

# Predict
def PredictImg(learner, img):
    # TODO
    return 'error'





def main():
    modelName = 'tmp'

    learner = LoadLearner(modelName)


    # Running server
    app.run(host='0.0.0.0')

if __name__ == '__main__':
    main()