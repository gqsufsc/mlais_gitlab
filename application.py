import server
import turma_service as ts

def teste():
    return
    # ts.train('087aae')

    # learner = ts.load_learner('087aae')

    # lr = learner.lr_find(start_lr=1e-6, end_lr=1e1)
    # cycles = 20
    # learner.fit_one_cycle(cycles, max_lr=lr)
    # mdl.SaveDefautLearner('wastesorter', learner)

    # interp = ClassificationInterpretation.from_learner(learner)
    # print(interp.most_confused(min_val=2))

def main():
    # teste()
    # ts.uploaded_pictures('087aae')

    # Running server
    server.flaskApp.secret_key = 'super secret key'
    server.flaskApp.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    server.flaskApp.config['SESSION_TYPE'] = 'filesystem'
    server.flaskApp.run(host='0.0.0.0')


if __name__ == '__main__':
    main()
