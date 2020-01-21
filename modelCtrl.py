import os
import pickle

from fastai.vision import models, error_rate, data, cnn_learner

modelsPath = os.getcwd() + '/data/models'
classesPath = os.getcwd() + '/data/classes/'

########################################################################################################################

def LoadClassesLearner(data, classesName, ext):
    return __LoadLearner(data, classesPath + classesName, 'model', ext)

def LoadDefaultLearner(data, modelName, ext):
    return __LoadLearner(data, modelsPath + '/' + modelName + '/', modelName, ext)

def SaveClassesLearner(className, learner):
    __SaveLearner(classesPath + className + '/', 'model', learner)

def SaveDefautLearner(name, learner):
    __SaveLearner(modelsPath, name, learner)

########################################################################################################################

# Save model learner as pkl and pth
def __SaveLearner(path, name, learner):
    path = path + '/' + name
    # Create folder if it don't exists
    if not os.path.exists(path ):
        os.makedirs(path)

    learner.save(path + '/' + name, with_opt=True)                 # Save *.pth
    with open(path + '/' + name +'.pkl', 'wb') as pickle_model:
        pickle.dump(learner, pickle_model)                         # Save *.pkl

# Load model learner
def __LoadLearner(data, path, name, ext):
    # TODO :: if pkl ... else
    learner = cnn_learner(data, models.resnet34, metrics=error_rate)
    learner.load(path + '/' + name)                                  # *.pth or *.pkl
    return learner

# Train model with images from path
def TrainModel(learner, imgsPath, modelName):
    # TODO
    learner.save(modelName, return_path=True)
    learner.export(modelName + '.pkl')
    return learner

# TODO Predict
def PredictImg(learner, img):
    # TODO
    return 'error'