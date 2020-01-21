import os

from fastai.vision import models, error_rate, data, cnn_learner, load_learner

# TODO:: Create this folders if they don't exist
modelsPath = os.getcwd() + '/models'
classesPath = os.getcwd() + '/classes/'

########################################################################################################################

# TODO:: Rename methods
def LoadClassesLearner(data, classesName, ext):
    return __LoadLearner(data, classesPath + classesName, 'model', ext)

def LoadDefaultLearner(data, modelName, ext):
    return __LoadLearner(data, modelsPath + '/' + modelName + '/', modelName, ext)

def SaveClassesLearner(className, learner):
    __SaveLearner(classesPath + className + '/', 'model', learner)

def SaveDefautLearner(name, learner):
    __SaveLearner(modelsPath, name, learner)

def Predict(token, image):
    # TODO
    return

########################################################################################################################

# Save model learner as pkl and pth
def __SaveLearner(path, name, learner):
    path = path + '/' + name
    # Create folder if it don't exists
    if not os.path.exists(path ):
        os.makedirs(path)

    learner.save(path + '/' + name, with_opt=True)
    learner.export(path + '/' + name + '.pkl')

# Load model learner
def __LoadLearner(data, path, name, extension):
    # TODO:: split into two methods for load and load_learner
    if (extension == '.pth'):
        learner = cnn_learner(data, models.resnet34, metrics=error_rate)
        learner.load(path + '/' + name)
        return learner

    return load_learner(path + '/' , name + extension)

# Train model with images from path
def __TrainLearner(learner, imgsPath, modelName):
    # TODO
    return learner

# TODO Predict
def __PredictImage(learner, img):
    # TODO
    # img_data = await request.form()
    # img_bytes = await (img_data['file'].read())
    # img = open_image(BytesIO(img_bytes))
    # prediction = learner.predict(img)[0]
    # return JSONResponse({'result': str(prediction)})
    return 'error'