import os
import json
import glob

from pathlib import Path

from fastai.vision import Learner, get_transforms, ImageDataBunch, open_image, ClassificationInterpretation, load_learner as ll, ImageList

ALLOWED_EXTENSIONS = {'pkl'}


def get_path():
    return os.getcwd() + '/models/'


def get_data(model: str) -> ImageDataBunch:
    tfms = get_transforms(do_flip=True, flip_vert=True)
    return ImageDataBunch.from_folder(Path(get_path() + model + '/data'), test='test', ds_tfms=tfms, bs=16)


# Obtem o dicionario de tradução das classes.txt do modelo
# original: tradução
def get_classes_dict(model: str) -> dict:
    return  { line.split()[0] : line.split()[1] for line in open(get_path() + model + '/' + "classes.txt") }


def predict(learner: Learner, data: str) -> json:
    img = open_image(data)
    prediction = learner.predict(img)[0]
    return json.dumps({"result": str(prediction)})


# Save model learner as pth
def save_learner(path: str, name: str, learner: Learner) -> None:
    # Create folder if it don't exists
    if not os.path.exists(path):
        os.makedirs(path)
    learner.export(file = Path(path, name + '.pkl'))


# Load model learner from *.pth file
def load_learner(path: str, name: str):
    learner = ll(path=get_path() + name + '/', file=name + '.pkl')
    learner.load(file=get_path() + name + '/' + name)
    return learner


def train(learner: Learner, path: str, epoch: int) -> Learner:
    tfms = get_transforms(do_flip=True, flip_vert=True)
    data : ImageDataBunch = (ImageList.from_folder(path)
            .split_by_rand_pct().label_from_folder()
            .transform(tfms)
            .databunch(num_workers=1, bs=2))
    learner.data = data

    if epoch < 1:
        epoch = 1

    learner.fit(epoch)

    save_learner(path, 'tmp', learner)
    return learner


def evaluate(learner: Learner) -> list:
    interp = ClassificationInterpretation.from_learner(learner)
    most_confused = interp.most_confused(min_val=2)
    print(most_confused)
    return most_confused


def list_models() -> list:
    folders =[f for f in glob.glob(get_path() + "**/", recursive=False)]
    list = []
    for f in folders:
        splitted = f.split('/')
        splitted.pop()
        list.append(splitted.pop())
    return list
