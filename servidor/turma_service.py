import glob
import io
import os
import secrets
import shutil
import json

from fastai.vision import Learner

import utils as utils
import model_service as ms


def get_path() -> str :
    return os.getcwd() + '/turmas/'


def new_filename(extension : str) -> str :
    filename = secrets.token_hex(5) + '.' + extension
    while os.path.exists(get_path() + filename) :
        filename = secrets.token_hex(5) + '.' + extension
    return filename


# Upload image byte[]
def upload(turma: str, data : bytearray, extension : str) -> None :
    create_folders(turma) # Create folders if needed
    file = open(get_path() + turma + '/upload/' + new_filename(extension), 'wb')
    file.write(io.BytesIO(data).read())
    file.close()
    return


# Load model from turma folder
def load_learner(turma: str):
    return ms.load_learner(get_path() + turma + '/', model_name(turma))


# Save model from turma folder
def save_learner(turma: str, learner: Learner):
    ms.save_learner(get_path() + turma, model_name(turma), learner)


# Predict a image classification using the model
def predict(turma: str, data: bytearray, extension: str) -> json:
    create_folders(turma) # Create folders if needed

    learner = load_learner(turma)
    predict = ms.predict(learner, io.BytesIO(data))

    return predict


def train(turma: str) -> None:
    if not os.path.exists(get_path() + turma):
        print('invalid turma')
        return

    # if not os.path.exists(get_path() + turma + '/upload') \
    #         or len([name for name in os.listdir(get_path() + turma + '/upload/') if os.path.isfile(os.path.join(get_path() + turma + '/upload/', name))]) == 0:
    #     print('no images to train')
    #     return

    learner = load_learner(turma)
    ms.train(learner, get_path() + turma + '/upload/')
    # save_learner(turma, learner)

    # return ms.evaluate(learner)
    return


# Cria uma nova turma
def create_turma(model: str) -> None:
    if not os.path.exists(ms.get_path() + model):
        print('invalid model')
        return

    token = secrets.token_hex(3)
    while os.path.exists(get_path() + token) :
        token = secrets.token_hex(3)
    os.makedirs(get_path() + token)

    # Copy models
    src = ms.get_path() + model + '/' + model
    dst = get_path() + token + '/' + model
    shutil.copyfile(src + '.pkl', dst + '.pkl')


def create_folders(turma: str) -> str:
    path = get_path() + turma + '/'
    if not os.path.exists(path + 'upload/'):
        os.makedirs(path + 'upload/')
    return path


###############################################################################

def list_turmas() -> list:
    folders =[f for f in glob.glob(get_path() + "**/", recursive=False)]
    list = []
    for f in folders:
        splitted = f.split('/')
        splitted.pop()
        list.append(splitted.pop())

    return list


def list_classes(turma: str) -> list:
    learner = load_learner(turma)
    return learner.data.classes


# def uploaded_pictures(turma: str) -> list:
#     list = []
#     path = get_path() + turma + '/upload/'
#     for r, d, f in os.walk(path):
#         for file in f:
#             list.append(file)
#     return list


def uploaded_pictures_tag(turma: str, tag: str) -> list:
    list = []
    path = get_path() + turma + '/upload/train/' + tag
    for r, d, f in os.walk(path):
        for file in f:
            list.append(file)
    return list


def uploaded_pictures_dict(turma: str) -> list:
    tags = list_classes(turma)
    pictures = {}

    for tag in tags:
        path = get_path() + turma + '/upload/train/' + tag
        list = []
        for r, d, f in os.walk(path):
            for file in f:
                list.append(file)
        pictures[tag] = list

    return pictures


def delete_picture(turma: str, picture : str) -> None:
    print('\tExecuting: delete( ' + turma + ', ' + picture +')')
    path = get_path() + turma + '/upload/' + picture
    os.remove(path)

    while os.path.exists(path):
        print('exists :'+ path)

    return


def model_name(turma: str) -> str :
    turmaModelPath = utils.find('*.pkl', get_path() + turma).pop(0)
    return turmaModelPath[turmaModelPath.rindex('/') + 1: -4]
