import os
import json

from pathlib import Path

from fastai.metrics import error_rate
from fastai.vision import Learner, get_transforms, ImageDataBunch, open_image, imagenet_stats, \
    ClassificationInterpretation, load_learner as ll, ImageList, cnn_learner, models


def get_path():
    return os.getcwd() + '/models/'


def get_data(model: str) -> ImageDataBunch:
    tfms = get_transforms(do_flip=True, flip_vert=True)
    return ImageDataBunch.from_folder(Path(get_path() + model + '/data'), test='test', ds_tfms=tfms, bs=16)

def test() -> None :
    tfms = get_transforms(do_flip=True, flip_vert=True)
    data = ImageDataBunch.from_folder(Path('/home/ishunter/PycharmProjects/machine-learning-app-inventor-server/servidor/turmas/087aae/upload/'), ds_tfms=tfms, bs=4)

    # learner = cnn_learner(get_data('wastesorter'), models.resnet34, metrics=error_rate)
    learner = cnn_learner(data, models.resnet34, metrics=error_rate)
    learner.load(get_path() + 'wastesorter/' + 'wastesorter')
    learner.fit(1)


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
    learner = ll(get_path() + '/' + name, name +'.pkl')
    return learner


# learn = cnn_learner(data, models.resnet34, metrics=error_rate)
# learn.save('stage-1-50')
# learn.load('stage-1-50');
def train(learner: Learner, imgPath: str) -> Learner:
    # TODO:: tests after upload changes

    tfms = get_transforms(do_flip=True, flip_vert=True)

    # data = ImageDataBunch.from_folder(imgPath, ds_tfms=tfms,num_workers=0, bs=1).split_none()

    data : ImageDataBunch = (ImageList.from_folder(imgPath + 'train')
            .split_by_rand_pct().label_from_folder()
            # .add_test_folder('../Test')  # add test set
            .transform(tfms)
            .databunch(num_workers=0, bs=2))

    learn = cnn_learner(data, learner.model , metrics=error_rate)

    # data = (ImageDataBunch.from_folder(imgPath, ds_tfms=tfms, bs=1, num_workers=0)
    #         .split_none()
    #         .label_from_folder()
    #         .databunch())

    # data2 = ImageDataBunch.create_from_ll(lls=learner.data.classes, num_workers=1,

    # sd_train = ImageDataBunch.from_folder(path=imgPath).split_none()


    # data.test_dl = learner.data.train_dl
    # data

    # create(train_ds: Dataset, valid_ds: Dataset, path:PathOrStr = '.')


    # idb = ImageDataBunch.create(train_ds=data, valid_ds=valid)

    # path = untar_data(URLs.MNIST_SAMPLE)
    # get_transforms() returns tuple: train_tfms, valid_tfms
    # data = ImageDataBunch.from_folder(path, tfms=get_transforms())
    # model = simple_cnn((3, 16, 16, 2))
    # learn = Learner(data, model, metrics=[accuracy]).to_fp16()
    # learn.fit_one_cycle(1)

    # learner.data = data
    # learner.fit(1)
    # learner.validate(data.train_dl)


    # TODO:: save
    return learner


def evaluate(learner: Learner) -> list:
    interp = ClassificationInterpretation.from_learner(learner)
    most_confused = interp.most_confused(min_val=2)
    print(most_confused)
    return most_confused