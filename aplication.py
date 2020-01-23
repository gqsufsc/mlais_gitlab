
from fastai.vision import get_transforms, ImageDataBunch, cnn_learner, models, error_rate, ClassificationInterpretation, DatasetType, re

import classeService as cs
import server

# TODO:: Definir estratégia para pasta de data default do modelo

def Teste():

    # learner = mdl.LoadDefaultLearner(data, 'wastesorter', '.pkl')
    # learner = mdl.LoadDefaultLearner(data, 'wastesorter', '.pth')

    learner = cs.loadLearner('087aae')

    # learner = cnn_learner(data, models.resnet34, metrics=error_rate)
    # learner = mdl.LoadDefaultLearner(data, 'wastesorter', '.pkl')

    # Find a learning rate for gradient descent to make sure that my neural network converges reasonably quickly
    # without missing the optimal error.
    # lr = learner.lr_find(start_lr=1e-6, end_lr=1e1)
    # lr = 5.13e-03

    # cycles = 20
    # cycles = 1

    # learner.fit_one_cycle(cycles, max_lr=lr)

    # mdl.SaveDefautLearner('wastesorter', learner)

    # TODO:: fix with pkl load
    interp = ClassificationInterpretation.from_learner(learner) # Não funciona com o load pkl
    print(interp.most_confused(min_val=2))



def main():
    # modelName = 'tmp'

    # learner = LoadLearner(modelName)
    # cs.createClass('wastesorter')

    # Teste()

    # Running server
    server.app.run(host='0.0.0.0')

if __name__ == '__main__':
    main()
