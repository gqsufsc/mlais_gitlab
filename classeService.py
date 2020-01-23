import os
import secrets
import shutil

import modelService as ms
import utils

########################################################################################################################

def getPath():
    return os.getcwd() + '/classes'

########################################################################################################################

# Load model from classe folder
def loadLearner(classe):
    classeModelPath = utils.find('*.pth', getPath() + '/' + classe).pop(0)
    modelName = classeModelPath[classeModelPath.rindex('/')+1 : -4]
    return ms.__LoadPthLearner(ms.getData(modelName), getPath() + '/' + classe + '/', modelName)

# Save model from classe folder
def saveLearner(className, learner):
    ms.__SaveLearner(getPath() + className + '/', 'model', learner)

# Predict a image classification using the model
def predict(token, image):
    # TODO
    return

def upload():
    # TODO:: acho que não vai ficar aqui
    return


# Create a new Class with default model
def createClass(model):
    modelsPath = os.getcwd() + '/models/'
    classesPath = os.getcwd() + '/classes/'

    # Generate a random token
    token = secrets.token_hex(3)
    # TODO: Check if token is new on database else repeat

    # Make a main folder for the class and a upload folder
    tokenPath = classesPath + token
    if not os.path.exists(tokenPath):
        os.makedirs(tokenPath)
        os.makedirs(os.path.join(tokenPath, 'upload'))

        # Copy models
        src = modelsPath + model + '/' + model
        dst = tokenPath + '/' + model
        shutil.copyfile(src + '.pkl', dst + '.pkl')
        shutil.copyfile(src + '.pth', dst + '.pth')


