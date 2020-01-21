import os
import secrets
import shutil

from pathlib import Path
from fastai.vision import get_transforms, ImageDataBunch, cnn_learner, models, error_rate, ClassificationInterpretation, DatasetType, re

import modelCtrl as mdl
import server

# TODO :: Move classes and model folder outside data
# Create a new Class with default model
def CreateClass(model):
    modelsPath = os.getcwd() + '/models'
    classesPath = os.getcwd() + '/classes/'

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
    # modelLearner = mdl.LoadDefaultLearner(data, 'wastesorter', '.pth')

    # learner = cnn_learner(data, models.resnet34, metrics=error_rate)
    learner = mdl.LoadDefaultLearner(data, 'ws', '.pth')

    # Find a learning rate for gradient descent to make sure that my neural network converges reasonably quickly
    # without missing the optimal error.
    # lr = learner.lr_find(start_lr=1e-6, end_lr=1e1)
    lr = 5.13e-03

    # cycles = 20
    cycles = 1

    # learner.fit_one_cycle(cycles, max_lr=lr)

    mdl.SaveDefautLearner('wastesorter', learner)

    # TODO:: fix with pkl load
    # interp = ClassificationInterpretation.from_learner(learner)
    # print(interp.most_confused(min_val=2))

    # 1 cycle
    # [('glass', 'metal', 18), ('glass', 'plastic', 15), ('cardboard', 'paper', 13), ('plastic', 'metal', 12),
    #  ('trash', 'paper', 10), ('metal', 'plastic', 6), ('plastic', 'trash', 6), ('metal', 'glass', 5),
    #  ('metal', 'paper', 5), ('paper', 'plastic', 5), ('plastic', 'glass', 4), ('plastic', 'paper', 4),
    #  ('cardboard', 'plastic', 3), ('glass', 'paper', 3), ('metal', 'trash', 3), ('trash', 'plastic', 3),
    #  ('glass', 'trash', 2), ('metal', 'cardboard', 2), ('paper', 'trash', 2), ('trash', 'glass', 2)]


def main():
    # modelName = 'tmp'

    # learner = LoadLearner(modelName)
    # CreateClass('wastesorter')

    Teste()

    # Running server
    # server.app.run(host='0.0.0.0')

if __name__ == '__main__':
    main()