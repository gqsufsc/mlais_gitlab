from fastai.vision import get_transforms, ImageDataBunch, cnn_learner, models, error_rate, ClassificationInterpretation, DatasetType, re

import model_service as ms
import classe_service as cs
import server


def teste():
    learner = cs.load_learner('087aae')

    # lr = learner.lr_find(start_lr=1e-6, end_lr=1e1)
    # cycles = 20
    # learner.fit_one_cycle(cycles, max_lr=lr)
    # mdl.SaveDefautLearner('wastesorter', learner)

    interp = ClassificationInterpretation.from_learner(learner)
    print(interp.most_confused(min_val=2))

def main():

    # teste()

    # Running server
    server.flaskApp.run(host='0.0.0.0')

if __name__ == '__main__':
    main()
