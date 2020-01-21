import os
import secrets
import shutil

from pathlib import Path
from fastai.vision import get_transforms, ImageDataBunch, cnn_learner, models, error_rate, ClassificationInterpretation, DatasetType, re

import modelCtrl as mdl
import server

# Create a new Class with default model
def CreateClass(model):
    modelsPath = os.getcwd() + '/data/models'
    classesPath = 'data/classes/'

    # Generate a random token
    token = secrets.token_hex(3)
    # TODO: Check if token is new on database else repeat

    # Make a main folder for the class
    tokenPath = classesPath + token
    if not os.path.exists(tokenPath):
        os.makedirs(tokenPath)
        os.makedirs(os.path.join(tokenPath, 'upload'))

        # Copy model
        src = modelsPath + '/' + model + '/' + model
        dst = os.getcwd() + '/' + tokenPath + '/model'
        shutil.copyfile(src + '.pkl', dst + '.pkl')
        shutil.copyfile(src + '.pth', dst + '.pth')

def Teste():

    # TODO :: move data inside model folder
    tfms = get_transforms(do_flip=True, flip_vert=True)
    data = ImageDataBunch.from_folder(Path(os.getcwd()) / 'data', test='test', ds_tfms=tfms, bs=16)

    # classLearner = mdl.LoadClassesLearner(data, 'adff72', '.pth')
    modelLearner = mdl.LoadDefaultLearner(data, 'wastesorter', '.pth')

    # learner = cnn_learner(data, models.resnet34, metrics=error_rate)
    # learner.lr_find(start_lr=1e-6, end_lr=1e1)

    # mdl.SaveDefautLearner('ws', classLearner)

def main():
    # modelName = 'tmp'

    # learner = LoadLearner(modelName)
    # CreateClass('wastesorter')

    Teste()

    # Running server
    server.app.run(host='0.0.0.0')

if __name__ == '__main__':
    main()