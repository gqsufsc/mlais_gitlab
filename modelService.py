import os
import json

from flask import make_response
from pathlib import Path
from fastai.vision import models, error_rate, cnn_learner, get_transforms, ImageDataBunch, open_image

# TODO:: Create this folders if they don't exist
modelsPath = os.getcwd() + '/models/'

########################################################################################################################

def LoadDefaultLearner(data, modelName, ext):
    return __LoadPthLearner(data, modelsPath + '/' + modelName + '/', modelName, ext)

def SaveDefautLearner(name, learner):
    __SaveLearner(modelsPath, name, learner)

def predict(learner, imagePath):
    # TODO :: checks
    img = open_image(imagePath)
    prediction = learner.predict(img)[0]
    return json.dumps({ "result" : str(prediction) })

def getData(model):
    # TODO :: verifications
    tfms = get_transforms(do_flip=True, flip_vert=True)
    return ImageDataBunch.from_folder(Path(os.getcwd() +'/models/' + model + '/data'), test='test', ds_tfms=tfms, bs=16)

########################################################################################################################

# Save model learner as pkl and pth
def __SaveLearner(path, name, learner):
    path = path + '/' + name
    # Create folder if it don't exists
    if not os.path.exists(path):
        os.makedirs(path)

    learner.save(path + '/' + name, with_opt=True)
    # learner.export(path + '/' + name + '.pkl')

# Load model learner from *.pth file
def __LoadPthLearner(data, path, name):
    learner = cnn_learner(data, models.resnet34, metrics=error_rate)
    # learner.load(modelsPath + '/' + name + '/' + name)
    learner.load(path + '/' + name)
    return learner

# # Load model learner from *.pkl file
# def __LoadPklLearner(path, name):
#     return load_learner(path + '/', name + '.pkl')

# Train model with images from path
def __TrainLearner(learner, imgsPath, modelName):
    # TODO
    return learner
