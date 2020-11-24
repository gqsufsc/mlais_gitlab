import glob
import io
import os
import secrets
import shutil
import json

from fastai.vision import Learner, ClassificationInterpretation

import utils as utils
import model_service as ms


def get_path() -> str :
    return os.getcwd() + '/turmas/'


def new_filename(turma: str, extension : str) -> str :
    filename = secrets.token_hex(5) + '.' + extension
    while file_exists(turma, filename):
        filename = secrets.token_hex(5) + '.' + extension
    return filename


def file_exists(turma: str, filename: str) -> bool :
    for root, dirs, files in os.walk(get_path() + turma):
       if filename in files:
           return True
    return False


# Upload image byte[]
def upload(turma: str, tag : str, data : bytearray, extension : str) -> None :
    classe = get_class_original(turma, tag)

    if classe == '':
        classe = list_classes[0]

    file = open(get_path() + turma + '/upload/train/' + classe + '/' + new_filename(turma, extension), 'wb')
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
    learner = load_learner(turma)
    predict = ms.predict(learner, io.BytesIO(data))
    return predict


def train(turma: str, epoch: int) -> None:
    if not os.path.exists(get_path() + turma):
        print('invalid turma')
        return

    learner = load_learner(turma)
    learner = ms.train(learner, get_path() + turma + '/upload/', epoch)
    save_learner(turma, learner)

    interp = ClassificationInterpretation.from_learner(learner)

    matrix = interp.confusion_matrix()
    print(matrix)

    return matrix


# Cria uma nova turma
def create_turma(model: str, descricao: str) -> None:
    if not os.path.exists(ms.get_path() + model):
        print('invalid model')
        return

    token = secrets.token_hex(3)
    while os.path.exists(get_path() + token) :
        token = secrets.token_hex(3)

    path = get_path() + token + '/upload/train/'
    os.makedirs(path)

    # Copy models
    src = ms.get_path() + model + '/' + model
    dst = get_path() + token + '/' + model
    shutil.copyfile(src + '.pkl', dst + '.pkl')

    create_classes_folders(token)
    create_description(token, descricao)
    return


def edit_turma(token: str, model: str, descricao: str) -> None:
    if not os.path.exists(ms.get_path() + model):
        print('invalid model')
        return

    if model != model_name(token):
        # Delete old model
        os.remove(get_path() + token + '/' + model_name(token) + '.pkl')
        # Copy models
        src = ms.get_path() + model + '/' + model
        dst = get_path() + token + '/' + model
        shutil.copyfile(src + '.pkl', dst + '.pkl')

    create_description(token, descricao)
    return


def create_classes_folders(turma: str) -> None:
    path = get_path() + turma + '/upload/train/'
    for classe in list_classes(turma):
        os.makedirs(path + '/' + classe)


def create_description(turma: str, descricao:str) -> None:
    path = get_path() + turma + '/'
    f = open(path + "descricao.txt", "w")
    f.write(descricao)
    f.close()


def delete_upload(turma: str) -> None:
    path = get_path() + turma + '/upload/'
    shutil.rmtree(path)

    path = get_path() + turma + '/upload/train/'
    os.makedirs(path)
    create_classes_folders(turma)


def delete_turma(turma: str) -> None:
    path = get_path() + turma
    shutil.rmtree(path)

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


def list_classes_translated(turma: str) -> list:
    list = list_classes(turma)
    dict = get_translation_dict(turma)
    translated = []
    for classe in list:
        translated.append(dict[classe])
    return translated


def get_translation_dict(turma:str) -> dict:
    return ms.get_classes_dict(model_name(turma))


def get_class_translation(turma:str, tag: str) -> str:
    dict = ms.get_classes_dict(model_name(turma))
    if tag in dict:
        return dict[tag]
    return ''


def get_class_original(turma:str, tag: str) -> str:
    dict = ms.get_classes_dict(model_name(turma))
    for key in dict:
        if dict[key] == tag:
            return key
    return ''


def uploaded_pictures(turma: str) -> list:
    list = []
    path = get_path() + turma + '/upload/'
    for r, d, f in os.walk(path):
        for file in f:
            list.append(file)
    return list


def move_picture_to_tag(turma: str, picture: str, tag: str) -> None:
    print('\tExecuting: move_picture_to_tag( ' + turma + ', ' + picture + ', ' + tag + ' )')
    tags = list_classes(turma)
    path = get_path() + turma + '/upload/train/'

    if tag not in tags:
        print('invalid tag')
        return

    if os.path.exists(path + tag + '/' + picture):
        print('Cannot move to same tag')
        return

    for t in tags:
        src = path + t + '/' + picture
        if (os.path.exists(src)):
            dst = path + tag + '/' + picture
            shutil.copyfile(src, dst)
            os.remove(src)
            return
    return


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
    tags = list_classes(turma)
    path = get_path() + turma + '/upload/train/'

    for t in tags:
        src = path + t + '/' + picture
        if (os.path.exists(src)):
            os.remove(src)
            return
    return


def model_name(turma: str) -> str :
    turmaModelPath = utils.find('*.pkl', get_path() + turma).pop(0)
    return turmaModelPath[turmaModelPath.rindex('/') + 1: -4]


def get_turma_dict(turma: str) -> dict:
    t = dict()
    t["descricao"] = open(get_path() + turma + '/' + "descricao.txt").read().replace('\n', '')
    t["classes"] = list_classes_translated(turma)
    return t


def get_all_turmas() -> dict:
    all = dict()
    for turma in list_turmas():
        all[turma] = get_turma_dict(turma)

    return all


def get_image_count_for_classe(turma: str, classe: str) -> int:
    path = get_path() + turma + '/upload/train/' + classe
    count = len(next(os.walk(path))[2])
    return count


# 0 = sem erro
# 1 = Total de imagemns menor que 10
# 2 = Total de imagens em alguma classe menor que 2
# 3 = errors 1 e 2
def get_display_error(turma: str) -> int:
    error = 0

    if (len(uploaded_pictures(turma)) <= 10):
        error += 1

    for c in list_classes(turma):
        if (get_image_count_for_classe(turma, c) <= 2):
            error += 2
            break

    return error