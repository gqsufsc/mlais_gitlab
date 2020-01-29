import os
import secrets
import shutil
import utils
import json

from fastai.vision import Learner

import model_service as ms


def get_path() -> str:
    return os.getcwd() + '/classes'


# Load model from classe folder
def load_learner(classe: str):
    classeModelPath = utils.find('*.pth', get_path() + '/' + classe).pop(0)
    modelName = classeModelPath[classeModelPath.rindex('/') + 1: -4]
    return ms.load_learner(ms.get_data(modelName), get_path() + '/' + classe + '/', modelName)


# Save model from classe folder
def save_learner(className: str, learner: Learner):
    ms.save_learner(get_path() + className + '/', 'model', learner)


# Predict a image classification using the model
def predict(token:str, image: str) -> json:
    # TODO
    return


def upload(token: str, image: str) -> None:
    # TODO
    return


def train(token: str) -> None:
    # TODO
    return


# Create a new Class with default model
def createClass(model):
    # Generate a random token
    token = secrets.token_hex(3)
    # TODO: Check if token is new on database else repeat

    # Make a main folder for the class and a upload folder
    tokenPath = get_path() + token
    if not os.path.exists(tokenPath):
        os.makedirs(tokenPath)
        os.makedirs(os.path.join(tokenPath, 'upload'))

        # Copy models
        src = ms.get_path() + model + '/' + model
        dst = tokenPath + '/' + model
        # shutil.copyfile(src + '.pkl', dst + '.pkl')
        shutil.copyfile(src + '.pth', dst + '.pth')
