import os
import json

from pathlib import Path
from fastai.vision import Learner, models, error_rate, cnn_learner, get_transforms, ImageDataBunch, open_image, \
     imagenet_stats, ClassificationInterpretation


def get_path():
    return os.getcwd() + '/models/'


def get_data(model: str) -> ImageDataBunch:
    tfms = get_transforms(do_flip=True, flip_vert=True)
    return ImageDataBunch.from_folder(Path(get_path() + model + '/data'), test='test', ds_tfms=tfms, bs=16)


def predict(learner: Learner, imagePath: str) -> json:
    img = open_image(imagePath)
    prediction = learner.predict(img)[0]
    return json.dumps({"result": str(prediction)})


# Save model learner as pth
def save_learner(path: str, name: str, learner: Learner) -> None:
    path = path + '/' + name
    # Create folder if it don't exists
    if not os.path.exists(path):
        os.makedirs(path)
    learner.save(path + '/' + name, with_opt=True)


# Load model learner from *.pth file
def load_learner(path: str, name: str):
    learner = cnn_learner(get_data(name), models.resnet34, metrics=error_rate)
    learner.load(path + '/' + name)
    return learner


def train(learner: Learner, imgPath: str) -> Learner:
    # TODO:: tests after upload changes
    tfms = get_transforms(do_flip=True, flip_vert=True)
    data = ImageDataBunch.from_folder(
        imgPath,
        valid_pct=0,
        ds_tfms=tfms,
        num_workers=0,
        bs=1).normalize(imagenet_stats)

    learner.validate(data.train_dl)

    # TODO:: save
    return learner


def evaluate(learner: Learner) -> list:
    interp = ClassificationInterpretation.from_learner(learner)
    most_confused = interp.most_confused(min_val=2)
    print(most_confused)
    return most_confused