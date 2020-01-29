import os
import json

from pathlib import Path
from fastai.vision import Learner, models, error_rate, cnn_learner, get_transforms, ImageDataBunch, open_image


def get_path():
    return os.getcwd() + '/models/'


def get_data(model: str) -> ImageDataBunch:
    # TODO :: verifications
    tfms = get_transforms(do_flip=True, flip_vert=True)
    return ImageDataBunch.from_folder(Path(get_path() + model + '/data'), test='test', ds_tfms=tfms, bs=16)


def predict(learner: Learner, imagePath: str) -> json:
    # TODO :: verifications
    img = open_image(imagePath)
    prediction = learner.predict(img)[0]
    return json.dumps({"result": str(prediction)})


# Save model learner as pkl and pth
def save_learner(path: str, name: str, learner: Learner) -> None:
    path = path + '/' + name
    # Create folder if it don't exists
    if not os.path.exists(path):
        os.makedirs(path)
    learner.save(path + '/' + name, with_opt=True)


# Load model learner from *.pth file
def load_learner(data: ImageDataBunch, path: str, name: str):
    learner = cnn_learner(data, models.resnet34, metrics=error_rate)
    learner.load(path + '/' + name)
    return learner


# Train model with images from path
def train(learner: Learner, imgPath: str, name: str):
    # TODO
    return learner
